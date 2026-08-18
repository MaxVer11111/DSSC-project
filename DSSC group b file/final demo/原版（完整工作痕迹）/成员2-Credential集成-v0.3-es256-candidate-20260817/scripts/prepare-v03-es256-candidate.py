from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL_DID = "did:web:shenyousota.github.io:dssc-toolbox"
FINAL_KID = f"{FINAL_DID}#key-1"
LEGAL_CREDENTIAL_ID = "urn:dssc:credential:legal-person:energy-data-provider:v0.3"
SERVICE_CREDENTIAL_ID = (
    "urn:dssc:credential:service-offering:building-energy-hourly-v1:v0.3"
)
A_REPOSITORY_COMMIT = "89d40ccf0bd43af22f2129f81d0ba0214f5c327c"


def read_json(relative_path: str) -> dict:
    path = ROOT / relative_path
    if not path.is_file():
        raise FileNotFoundError(f"Required file not found: {path}")
    with path.open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def write_json(relative_path: str, value: object) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def main() -> None:
    if not (ROOT / "02-config/demo-config.json").is_file():
        raise RuntimeError(
            "Script is not inside the member2 project. Put it in the project's scripts folder."
        )

    config = read_json("02-config/demo-config.json")
    config["configVersion"] = "0.3"
    config["configStatus"] = "es256-candidate-prepared"
    config["lastUpdated"] = "2026-08-17"
    config["provider"]["did"] = FINAL_DID
    config["provider"]["legalPersonId"] = FINAL_DID
    config["provider"]["legalPersonCredentialId"] = LEGAL_CREDENTIAL_ID
    config["provider"]["status"] = "ES256_CANDIDATE_READY"
    config["serviceOffering"]["credentialId"] = SERVICE_CREDENTIAL_ID
    config["serviceOffering"]["providedBy"] = FINAL_DID
    config["serviceOffering"]["vpPackaging"] = "LEGAL_PERSON_PLUS_SERVICE_OFFERING"
    config["serviceOffering"]["status"] = "ES256_CANDIDATE_READY"
    config["dataset"]["status"] = "D_E5F_SHACL_PASS"
    config["metadata"]["status"] = (
        "C_V0_4_D_E5F_SHACL_PASS_C_REPOSITORY_SYNC_PENDING"
    )
    config["validation"]["requiresProjectMetadataRevalidation"] = False
    config["validation"]["status"] = "D_E5F_PROJECT_METADATA_SHACL_PASS"
    config["credentialRequirements"]["status"] = "CURRENT_TWO_VC_SCOPE_CONFIRMED"
    config["signing"]["issuerDid"] = FINAL_DID
    config["signing"]["holderDid"] = FINAL_DID
    config["signing"]["kid"] = FINAL_KID
    config["signing"]["status"] = "READY_FOR_ES256_CANDIDATE_SIGNING"
    config["developmentSigning"]["enabled"] = False
    config["developmentSigning"]["replacementRequired"] = []
    config["developmentSigning"]["status"] = "ARCHIVED_V0_2_RS256"
    write_json("02-config/demo-config.json", config)

    credential_files = [
        (
            "04-credential-source/legal-person.jsonld",
            LEGAL_CREDENTIAL_ID,
        ),
        (
            "06-invalid-tests/sources/legal-person.missing-name.jsonld",
            LEGAL_CREDENTIAL_ID,
        ),
        (
            "06-invalid-tests/sources/legal-person.expired.jsonld",
            LEGAL_CREDENTIAL_ID,
        ),
        (
            "04-credential-source/service-offering.jsonld",
            SERVICE_CREDENTIAL_ID,
        ),
        (
            "06-invalid-tests/sources/service-offering.provider-mismatch.jsonld",
            SERVICE_CREDENTIAL_ID,
        ),
        (
            "06-invalid-tests/sources/service-offering.dataset-mismatch.jsonld",
            SERVICE_CREDENTIAL_ID,
        ),
    ]
    for relative_path, credential_id in credential_files:
        document = read_json(relative_path)
        document["id"] = credential_id
        document["issuer"] = FINAL_DID
        write_json(relative_path, document)

    for relative_path in (
        "06-invalid-tests/sources/service-offering.provider-mismatch.jsonld",
        "06-invalid-tests/sources/service-offering.dataset-mismatch.jsonld",
    ):
        document = read_json(relative_path)
        provided_by = document["credentialSubject"]["gx:providedBy"]
        if not isinstance(provided_by, list):
            document["credentialSubject"]["gx:providedBy"] = [provided_by]
        write_json(relative_path, document)

    report_path = ROOT / "07-evidence/a-group-final-did-verification.md"
    report = report_path.read_text(encoding="utf-8-sig")
    lines = []
    replaced = False
    for line in report.splitlines():
        if line.startswith("- A组仓库Commit："):
            lines.append(f"- A组仓库Commit：`{A_REPOSITORY_COMMIT}`")
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        raise RuntimeError("A-group commit placeholder line was not found")
    with report_path.open("w", encoding="utf-8", newline="\n") as file:
        file.write("\n".join(lines) + "\n")

    required_values = {
        "Provider DID": config["provider"]["did"] == FINAL_DID,
        "issuer DID": config["signing"]["issuerDid"] == FINAL_DID,
        "holder DID": config["signing"]["holderDid"] == FINAL_DID,
        "kid": config["signing"]["kid"] == FINAL_KID,
        "algorithm": config["signing"]["algorithm"] == "ES256",
        "key type": config["signing"]["keyType"] == "EC",
        "curve": config["signing"]["curve"] == "P-256",
        "SHACL status": not config["validation"]["requiresProjectMetadataRevalidation"],
    }
    failed = [name for name, passed in required_values.items() if not passed]
    if failed:
        raise RuntimeError("Preparation checks failed: " + ", ".join(failed))

    print("v0.3 ES256 candidate preparation: PASS")
    print(f"Provider DID: {FINAL_DID}")
    print(f"kid: {FINAL_KID}")
    print("Credential IDs upgraded to v0.3")
    print("INV-03 and INV-04 now differ from valid input only at their target value")
    print(f"A-group evidence commit: {A_REPOSITORY_COMMIT}")


if __name__ == "__main__":
    main()
