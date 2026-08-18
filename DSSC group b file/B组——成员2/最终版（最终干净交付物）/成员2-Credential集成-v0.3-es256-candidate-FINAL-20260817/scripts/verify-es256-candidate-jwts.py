from __future__ import annotations

import base64
import json
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import Request, urlopen

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives.asymmetric.utils import encode_dss_signature


ROOT = Path(__file__).resolve().parents[1]
VC_CONTEXT = "https://www.w3.org/ns/credentials/v2"
VALID_DIRECTORY = ROOT / "05-signed/es256-candidate"
INVALID_DIRECTORY = ROOT / "06-invalid-tests/signed-es256-candidate"
REPORT_PATH = ROOT / "07-evidence/es256-candidate-jwt-verification.md"


def read_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def read_token(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def b64url_decode(value: str) -> bytes:
    return base64.urlsafe_b64decode(value + "=" * (-len(value) % 4))


def decode_jwt(token: str) -> tuple[list[str], dict, dict]:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError(f"JWT must contain exactly 3 segments; found {len(parts)}")
    header = json.loads(b64url_decode(parts[0]).decode("utf-8"))
    payload = json.loads(b64url_decode(parts[1]).decode("utf-8"))
    return parts, header, payload


def verify_signature(token: str, public_key: ec.EllipticCurvePublicKey) -> bool:
    parts = token.split(".")
    if len(parts) != 3:
        return False
    try:
        signature = b64url_decode(parts[2])
        if len(signature) != 64:
            return False
        r = int.from_bytes(signature[:32], "big")
        s = int.from_bytes(signature[32:], "big")
        der_signature = encode_dss_signature(r, s)
        public_key.verify(
            der_signature,
            f"{parts[0]}.{parts[1]}".encode("ascii"),
            ec.ECDSA(hashes.SHA256()),
        )
        return True
    except (InvalidSignature, ValueError):
        return False


def fetch_did_document(url: str) -> dict:
    request = Request(url, headers={"User-Agent": "DSSC-member2-ES256-verifier/0.3"})
    with urlopen(request, timeout=20) as response:
        if response.status != 200:
            raise ValueError(f"DID document HTTP status is {response.status}, not 200")
        return json.loads(response.read().decode("utf-8-sig"))


def public_key_from_jwk(jwk: dict) -> ec.EllipticCurvePublicKey:
    if jwk.get("kty") != "EC" or jwk.get("crv") != "P-256":
        raise ValueError("DID publicKeyJwk must be EC P-256")
    x = int.from_bytes(b64url_decode(jwk["x"]), "big")
    y = int.from_bytes(b64url_decode(jwk["y"]), "big")
    return ec.EllipticCurvePublicNumbers(x, y, ec.SECP256R1()).public_key()


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def check_header(header: dict, token_type: str, issuer: str, kid: str) -> None:
    expected = {
        "alg": "ES256",
        "typ": token_type,
        "cty": "vc" if token_type == "vc+jwt" else "vp",
        "iss": issuer,
        "kid": kid,
    }
    for key, value in expected.items():
        require(header.get(key) == value, f"Header {key} mismatch")


def check_envelope(envelope: dict, expected_token: str) -> None:
    require(envelope.get("@context") == VC_CONTEXT, "Envelope context mismatch")
    require(
        envelope.get("type") == "EnvelopedVerifiableCredential",
        "Envelope type mismatch",
    )
    prefix = "data:application/vc+jwt,"
    require(envelope.get("id") == prefix + expected_token, "Envelope JWT mismatch")


def iso_time(value: object) -> datetime:
    require(isinstance(value, str), "Validity value must be a string")
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def main() -> None:
    config = read_json("02-config/demo-config.json")
    signing = config["signing"]
    issuer = signing["issuerDid"]
    holder = signing["holderDid"]
    kid = signing["kid"]
    did_url = signing["didDocumentUrl"]

    did_document = fetch_did_document(did_url)
    require(did_document.get("id") == issuer, "DID document id mismatch")
    methods = [
        method
        for method in did_document.get("verificationMethod", [])
        if method.get("id") == kid
    ]
    require(len(methods) == 1, f"Expected one verificationMethod for {kid}")
    public_jwk = methods[0].get("publicKeyJwk", {})
    public_key = public_key_from_jwk(public_jwk)
    require(kid in did_document.get("assertionMethod", []), "kid missing from assertionMethod")

    private_jwk = read_json(signing["privateKeyPath"])
    for coordinate in ("kty", "crv", "x", "y"):
        require(
            private_jwk.get(coordinate) == public_jwk.get(coordinate),
            f"Public DID key/private JWK {coordinate} mismatch",
        )

    valid_cases = [
        {
            "file": VALID_DIRECTORY / "legal-person.es256-candidate.vc.jwt",
            "type": "vc+jwt",
            "source": "04-credential-source/legal-person.jsonld",
        },
        {
            "file": VALID_DIRECTORY / "service-offering.es256-candidate.vc.jwt",
            "type": "vc+jwt",
            "source": "04-credential-source/service-offering.jsonld",
        },
        {
            "file": VALID_DIRECTORY / "presentation.es256-candidate.vp.jwt",
            "type": "vp+jwt",
            "source": None,
        },
    ]
    results: list[dict] = []
    decoded_valid: dict[str, tuple[str, dict]] = {}
    for case in valid_cases:
        token = read_token(case["file"])
        parts, header, payload = decode_jwt(token)
        check_header(
            header,
            case["type"],
            issuer if case["type"] == "vc+jwt" else holder,
            kid,
        )
        signature_valid = verify_signature(token, public_key)
        require(signature_valid, f"Signature failed: {case['file'].name}")
        if case["source"]:
            require(payload == read_json(case["source"]), "Signed VC payload/source mismatch")
            require(payload.get("issuer") == issuer, "Credential issuer mismatch")
        decoded_valid[case["type"] + case["file"].stem] = (token, payload)
        results.append(
            {
                "file": case["file"].relative_to(ROOT).as_posix(),
                "segments": len(parts),
                "alg": header.get("alg"),
                "typ": header.get("typ"),
                "kid": header.get("kid") == kid,
                "signature": signature_valid,
                "result": "PASS",
            }
        )

    legal_token = read_token(VALID_DIRECTORY / "legal-person.es256-candidate.vc.jwt")
    service_token = read_token(VALID_DIRECTORY / "service-offering.es256-candidate.vc.jwt")
    vp_token = read_token(VALID_DIRECTORY / "presentation.es256-candidate.vp.jwt")
    _, _, vp_payload = decode_jwt(vp_token)
    require("VerifiablePresentation" in vp_payload.get("type", []), "VP type mismatch")
    require(vp_payload.get("issuer") == holder, "VP issuer mismatch")
    require(iso_time(vp_payload.get("validFrom")) < iso_time(vp_payload.get("validUntil")), "VP validity range is reversed")
    envelopes = vp_payload.get("verifiableCredential", [])
    require(len(envelopes) == 2, "VP must contain exactly two credentials")
    check_envelope(envelopes[0], legal_token)
    check_envelope(envelopes[1], service_token)

    manifest = read_json("06-invalid-tests/es256-candidate-manifest.json")
    for case in manifest["cases"]:
        signature_expectation = case["signatureExpected"]
        if signature_expectation == "NOT_APPLICABLE":
            continue
        path = ROOT / case["presentationJwt"]
        token = read_token(path)
        parts, header, _ = decode_jwt(token)
        check_header(header, "vp+jwt", holder, kid)
        signature_valid = verify_signature(token, public_key)
        expected_valid = signature_expectation == "VALID"
        require(
            signature_valid == expected_valid,
            f"{case['id']} signature expectation mismatch",
        )
        results.append(
            {
                "file": path.relative_to(ROOT).as_posix(),
                "segments": len(parts),
                "alg": header.get("alg"),
                "typ": header.get("typ"),
                "kid": header.get("kid") == kid,
                "signature": signature_valid,
                "result": "PASS",
            }
        )

        if "credentialJwt" in case:
            credential_path = ROOT / case["credentialJwt"]
            credential_token = read_token(credential_path)
            credential_parts, credential_header, credential_payload = decode_jwt(
                credential_token
            )
            check_header(credential_header, "vc+jwt", issuer, kid)
            require(
                verify_signature(credential_token, public_key),
                f"{case['id']} content-invalid VC must retain a valid signature",
            )
            require(
                credential_payload == read_json(case["source"]),
                f"{case['id']} signed payload/source mismatch",
            )
            results.append(
                {
                    "file": credential_path.relative_to(ROOT).as_posix(),
                    "segments": len(credential_parts),
                    "alg": credential_header.get("alg"),
                    "typ": credential_header.get("typ"),
                    "kid": credential_header.get("kid") == kid,
                    "signature": True,
                    "result": "PASS",
                }
            )

    lines = [
        "# ES256候选JWT本地验签报告",
        "",
        "## 结论",
        "",
        "- 公网DID Document解析：**PASS**",
        "- 公网EC P-256公钥与教学Demo私钥匹配：**PASS**",
        "- 有效VC/VP与无效测试JWT的预期签名状态：**PASS**",
        "- 总体本地密码学验证：**PASS**",
        "",
        "## 签名参数",
        "",
        f"- DID：`{issuer}`",
        f"- kid：`{kid}`",
        "- 算法：`ES256`",
        f"- DID Document：`{did_url}`",
        "",
        "## 逐文件结果",
        "",
        "| 文件 | 分段 | alg | typ | kid匹配 | 实际签名有效 | 结果 |",
        "|---|---:|---|---|---|---|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result['file']}` | {result['segments']} | `{result['alg']}` | "
            f"`{result['typ']}` | {result['kid']} | {result['signature']} | "
            f"{result['result']} |"
        )
    lines.extend(
        [
            "",
            "## 边界",
            "",
            "本报告证明本地JWT结构、ES256签名、公网DID公钥匹配以及源文件封装正确。",
            "它不等于Gaia-X Compliance API已经接受这些候选凭证；API测试由成员3执行。",
            "教学Demo私钥为公开演示材料，不得用于生产环境。",
            "",
        ]
    )
    REPORT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with REPORT_PATH.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines))

    print("Public DID resolution and key match: PASS")
    print("ES256 candidate JWT verification: PASS")
    print(f"Report: {REPORT_PATH}")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"ES256 candidate JWT verification: FAIL\n{error}", file=sys.stderr)
        raise SystemExit(1)
