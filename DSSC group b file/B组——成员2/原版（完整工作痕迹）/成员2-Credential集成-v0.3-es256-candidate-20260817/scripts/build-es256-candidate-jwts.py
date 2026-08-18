from __future__ import annotations

import base64
import csv
import hashlib
import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import decode_dss_signature


ROOT = Path(__file__).resolve().parents[1]
VC_CONTEXT = "https://www.w3.org/ns/credentials/v2"


def read_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def write_text(relative_path: str, value: str) -> Path:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(value)
    return path


def write_json(relative_path: str, value: object) -> Path:
    return write_text(
        relative_path,
        json.dumps(value, ensure_ascii=False, indent=2) + "\n",
    )


def b64url_encode(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode("ascii")


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def compact_json(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        separators=(",", ":"),
    ).encode("utf-8")


def load_private_key(jwk: dict) -> ec.EllipticCurvePrivateKey:
    if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        raise ValueError("Demo private JWK must be EC P-256")

    for name in ("x", "y", "d"):
        if not isinstance(jwk.get(name), str) or not jwk[name]:
            raise ValueError(f"Demo private JWK is missing {name}")

    private_value = int.from_bytes(b64url_decode(jwk["d"]), "big")
    key = ec.derive_private_key(private_value, ec.SECP256R1())
    public = key.public_key().public_numbers()
    expected_x = int.from_bytes(b64url_decode(jwk["x"]), "big")
    expected_y = int.from_bytes(b64url_decode(jwk["y"]), "big")
    if public.x != expected_x or public.y != expected_y:
        raise ValueError("Demo private JWK d does not match its x/y public coordinates")
    return key


def sign_jwt(
    payload: dict,
    token_type: str,
    content_type: str,
    issuer: str,
    kid: str,
    private_key: ec.EllipticCurvePrivateKey,
) -> tuple[str, dict]:
    header = {
        "alg": "ES256",
        "typ": token_type,
        "cty": content_type,
        "iss": issuer,
        "kid": kid,
    }
    encoded_header = b64url_encode(compact_json(header))
    encoded_payload = b64url_encode(compact_json(payload))
    signing_input = f"{encoded_header}.{encoded_payload}".encode("ascii")
    der_signature = private_key.sign(signing_input, ec.ECDSA(hashes.SHA256()))
    r, s = decode_dss_signature(der_signature)
    raw_signature = r.to_bytes(32, "big") + s.to_bytes(32, "big")
    token = f"{encoded_header}.{encoded_payload}.{b64url_encode(raw_signature)}"
    return token, header


def envelope(token: str) -> dict:
    return {
        "@context": VC_CONTEXT,
        "id": f"data:application/vc+jwt,{token}",
        "type": "EnvelopedVerifiableCredential",
    }


def build_presentation(
    credential_tokens: list[str],
    issuer: str,
    valid_from: str,
    valid_until: str,
) -> dict:
    return {
        "@context": [VC_CONTEXT],
        "type": ["VerifiablePresentation"],
        "id": "urn:dssc:presentation:building-energy-hourly-v1:es256-candidate",
        "issuer": issuer,
        "validFrom": valid_from,
        "validUntil": valid_until,
        "verifiableCredential": [envelope(token) for token in credential_tokens],
    }


def require_equal(actual: object, expected: object, message: str) -> None:
    if actual != expected:
        raise ValueError(f"{message}: expected {expected!r}, got {actual!r}")


def main() -> None:
    config = read_json("02-config/demo-config.json")
    signing = config["signing"]
    issuer_did = signing["issuerDid"]
    holder_did = signing["holderDid"]
    kid = signing["kid"]

    require_equal(signing.get("algorithm"), "ES256", "Signing algorithm mismatch")
    require_equal(signing.get("keyType"), "EC", "Signing key type mismatch")
    require_equal(signing.get("curve"), "P-256", "Signing curve mismatch")
    require_equal(issuer_did, config["provider"]["did"], "Provider/issuer DID mismatch")
    require_equal(holder_did, issuer_did, "This demo expects one DID as issuer and holder")
    require_equal(kid, f"{issuer_did}#key-1", "kid mismatch")

    private_jwk = read_json(signing["privateKeyPath"])
    private_key = load_private_key(private_jwk)

    legal_person = read_json("04-credential-source/legal-person.jsonld")
    service_offering = read_json("04-credential-source/service-offering.jsonld")
    require_equal(legal_person.get("issuer"), issuer_did, "LegalPerson issuer mismatch")
    require_equal(service_offering.get("issuer"), issuer_did, "ServiceOffering issuer mismatch")
    require_equal(
        legal_person["credentialSubject"].get("id"),
        issuer_did,
        "LegalPerson subject mismatch",
    )
    require_equal(
        service_offering["credentialSubject"]["gx:providedBy"][0].get("id"),
        issuer_did,
        "ServiceOffering providedBy mismatch",
    )
    require_equal(
        service_offering["credentialSubject"]["gx:aggregationOf"][0].get("id"),
        config["dataset"]["canonicalUri"],
        "ServiceOffering Dataset reference mismatch",
    )

    legal_token, vc_header = sign_jwt(
        legal_person, "vc+jwt", "vc", issuer_did, kid, private_key
    )
    service_token, _ = sign_jwt(
        service_offering, "vc+jwt", "vc", issuer_did, kid, private_key
    )

    now = datetime.now(timezone.utc).replace(microsecond=0)
    vp_valid_from = now.isoformat().replace("+00:00", "Z")
    vp_valid_until = (now + timedelta(days=30)).isoformat().replace("+00:00", "Z")
    presentation = build_presentation(
        [legal_token, service_token], holder_did, vp_valid_from, vp_valid_until
    )
    presentation_token, vp_header = sign_jwt(
        presentation, "vp+jwt", "vp", holder_did, kid, private_key
    )

    signed_files: list[Path] = []
    signed_files.append(
        write_text(
            "05-signed/es256-candidate/legal-person.es256-candidate.vc.jwt",
            legal_token + "\n",
        )
    )
    signed_files.append(
        write_text(
            "05-signed/es256-candidate/service-offering.es256-candidate.vc.jwt",
            service_token + "\n",
        )
    )
    signed_files.append(
        write_text(
            "05-signed/es256-candidate/presentation.es256-candidate.vp.jwt",
            presentation_token + "\n",
        )
    )

    inspection_root = "07-evidence/es256-candidate-jwt-inspection"
    write_json(f"{inspection_root}/legal-person.header.json", vc_header)
    write_json(f"{inspection_root}/legal-person.payload.json", legal_person)
    write_json(f"{inspection_root}/service-offering.header.json", vc_header)
    write_json(f"{inspection_root}/service-offering.payload.json", service_offering)
    write_json(f"{inspection_root}/presentation.header.json", vp_header)
    write_json(f"{inspection_root}/presentation.payload.json", presentation)

    invalid_cases = [
        (
            "INV-01",
            "legal-person.missing-name",
            "06-invalid-tests/sources/legal-person.missing-name.jsonld",
            "LegalPerson",
            "missing gx:legalName",
        ),
        (
            "INV-02",
            "legal-person.expired",
            "06-invalid-tests/sources/legal-person.expired.jsonld",
            "LegalPerson",
            "expired validUntil",
        ),
        (
            "INV-03",
            "service-offering.provider-mismatch",
            "06-invalid-tests/sources/service-offering.provider-mismatch.jsonld",
            "ServiceOffering",
            "providedBy DID mismatch",
        ),
        (
            "INV-04",
            "service-offering.dataset-mismatch",
            "06-invalid-tests/sources/service-offering.dataset-mismatch.jsonld",
            "ServiceOffering",
            "Dataset URI mismatch",
        ),
    ]
    manifest_cases: list[dict] = []
    for case_id, name, source, kind, expected_failure in invalid_cases:
        invalid_payload = read_json(source)
        invalid_token, _ = sign_jwt(
            invalid_payload, "vc+jwt", "vc", issuer_did, kid, private_key
        )
        credential_relative = (
            f"06-invalid-tests/signed-es256-candidate/{name}.es256-candidate.vc.jwt"
        )
        signed_files.append(write_text(credential_relative, invalid_token + "\n"))

        if kind == "LegalPerson":
            vp_credentials = [invalid_token, service_token]
        else:
            vp_credentials = [legal_token, invalid_token]
        invalid_presentation = build_presentation(
            vp_credentials, holder_did, vp_valid_from, vp_valid_until
        )
        invalid_vp_token, _ = sign_jwt(
            invalid_presentation, "vp+jwt", "vp", holder_did, kid, private_key
        )
        presentation_relative = (
            f"06-invalid-tests/signed-es256-candidate/presentation."
            f"{case_id.lower()}.es256-candidate.vp.jwt"
        )
        signed_files.append(write_text(presentation_relative, invalid_vp_token + "\n"))
        manifest_cases.append(
            {
                "id": case_id,
                "source": source,
                "credentialJwt": credential_relative,
                "presentationJwt": presentation_relative,
                "signatureExpected": "VALID",
                "expectedFailure": expected_failure,
            }
        )

    parts = presentation_token.split(".")
    replacement = "A" if parts[2][0] != "A" else "B"
    parts[2] = replacement + parts[2][1:]
    tampered_token = ".".join(parts)
    tampered_relative = (
        "06-invalid-tests/signed-es256-candidate/"
        "presentation.inv-07.tampered-signature.es256-candidate.vp.jwt"
    )
    signed_files.append(write_text(tampered_relative, tampered_token + "\n"))
    manifest_cases.append(
        {
            "id": "INV-07",
            "source": "05-signed/es256-candidate/presentation.es256-candidate.vp.jwt",
            "presentationJwt": tampered_relative,
            "signatureExpected": "INVALID",
            "expectedFailure": "VP signature verification",
        }
    )
    manifest_cases.extend(
        [
            {
                "id": "INV-05",
                "source": "06-invalid-tests/sources/dataset.wrong-format.jsonld",
                "signatureExpected": "NOT_APPLICABLE",
                "expectedFailure": "SHACL format rule",
            },
            {
                "id": "INV-06",
                "source": "06-invalid-tests/sources/dataset.reversed-dates.jsonld",
                "signatureExpected": "NOT_APPLICABLE",
                "expectedFailure": "SHACL temporal rule",
            },
        ]
    )
    write_json(
        "06-invalid-tests/es256-candidate-manifest.json",
        {
            "status": "ES256_CANDIDATE",
            "issuerDid": issuer_did,
            "kid": kid,
            "cases": manifest_cases,
        },
    )

    hash_path = ROOT / "07-evidence/es256-candidate-jwt-sha256.csv"
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    with hash_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["relativePath", "sha256"])
        for path in sorted(signed_files):
            writer.writerow(
                [
                    path.relative_to(ROOT).as_posix(),
                    hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                ]
            )

    print("ES256 candidate JWT generation: PASS")
    print(f"Valid JWTs: {ROOT / '05-signed/es256-candidate'}")
    print(f"Invalid test JWTs: {ROOT / '06-invalid-tests/signed-es256-candidate'}")
    print(f"SHA-256 manifest: {hash_path}")
    print("This key is a public teaching-demo key and must not be used in production.")


if __name__ == "__main__":
    main()
