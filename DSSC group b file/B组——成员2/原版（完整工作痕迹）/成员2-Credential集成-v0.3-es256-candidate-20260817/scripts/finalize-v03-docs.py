from __future__ import annotations

import csv
import hashlib
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FINAL_DID = "did:web:shenyousota.github.io:dssc-toolbox"
FINAL_KID = f"{FINAL_DID}#key-1"
A_COMMIT = "89d40ccf0bd43af22f2129f81d0ba0214f5c327c"
SHAPE_SHA = "E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E"


def read_json(relative_path: str) -> dict:
    with (ROOT / relative_path).open("r", encoding="utf-8-sig") as file:
        return json.load(file)


def write_json(relative_path: str, value: object) -> None:
    write_text(relative_path, json.dumps(value, ensure_ascii=False, indent=2) + "\n")


def write_text(relative_path: str, value: str) -> None:
    path = ROOT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as file:
        file.write(value)


def preserve_original(relative_path: str) -> None:
    source = ROOT / relative_path
    if not source.exists():
        return
    destination = ROOT / "07-evidence/archive/v0.2-docs" / relative_path
    if not destination.exists():
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def archive_legacy(relative_path: str) -> None:
    source = ROOT / relative_path
    if not source.exists():
        return
    destination = ROOT / "07-evidence/archive/v0.2-evidence" / Path(relative_path).name
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        if source.is_file() and destination.is_file():
            if source.read_bytes() != destination.read_bytes():
                raise RuntimeError(f"Archive collision: {destination}")
            source.unlink()
            return
        if source.is_dir() and destination.is_dir():
            shutil.rmtree(source)
            return
        raise RuntimeError(f"Archive type collision: {destination}")
    shutil.move(str(source), str(destination))


def main() -> None:
    verification_path = ROOT / "07-evidence/es256-candidate-jwt-verification.md"
    if not verification_path.is_file():
        raise RuntimeError("Run verify-es256-candidate-jwts.py before finalizing docs")
    verification = verification_path.read_text(encoding="utf-8-sig")
    if "总体本地密码学验证：**PASS**" not in verification:
        raise RuntimeError("ES256 verification report does not contain overall PASS")

    required_outputs = [
        "05-signed/es256-candidate/legal-person.es256-candidate.vc.jwt",
        "05-signed/es256-candidate/service-offering.es256-candidate.vc.jwt",
        "05-signed/es256-candidate/presentation.es256-candidate.vp.jwt",
        "06-invalid-tests/es256-candidate-manifest.json",
        "07-evidence/project-metadata-shacl-validation.txt",
    ]
    missing = [path for path in required_outputs if not (ROOT / path).is_file()]
    if missing:
        raise RuntimeError("Required finalization inputs are missing: " + ", ".join(missing))
    shacl_text = (ROOT / "07-evidence/project-metadata-shacl-validation.txt").read_text(
        encoding="utf-8-sig"
    )
    if "Conforms: True" not in shacl_text:
        raise RuntimeError("Project metadata SHACL result is not Conforms: True")

    for path in (
        "README.md",
        "01-decisions/provisional-decisions.md",
        "01-decisions/missing-signing-inputs.md",
        "01-decisions/signing-readiness-checklist.md",
        "06-invalid-tests/README.md",
    ):
        preserve_original(path)

    for path in (
        "07-evidence/did-resolution-check.md",
        "07-evidence/official-vp-local-validation.md",
        "07-evidence/provisional-jwt-verification.md",
        "07-evidence/development-did-document.unpublished.json",
        "07-evidence/provisional-jwt-inspection",
    ):
        archive_legacy(path)

    config = read_json("02-config/demo-config.json")
    config["configVersion"] = "0.3"
    config["configStatus"] = "es256-candidate-local-verified"
    config["lastUpdated"] = "2026-08-17"
    config["provider"]["status"] = "ES256_CANDIDATE_LOCAL_VERIFIED"
    config["serviceOffering"]["status"] = "ES256_CANDIDATE_LOCAL_VERIFIED"
    config["signing"]["status"] = "LOCAL_ES256_VERIFICATION_PASS"
    write_json("02-config/demo-config.json", config)

    readme = f"""# 成员2 Credential集成 v0.3 ES256 Candidate

## 当前结论

成员2的本地候选交付已完成：

- Provider DID、kid与A组教学Demo密钥一致；
- 项目Dataset Metadata通过D组E5F Shape本地SHACL预检；
- LegalPerson、ServiceOffering和VP已生成ES256候选JWT；
- 公网DID Document已用于本地验签，结果PASS；
- INV-01至INV-07测试材料已准备。

这是 `ES256 candidate` ，不表示Gaia-X Compliance API已经接受。成员3负责最终API提交、保存响应并分析失败层级。

## 固定身份和验证参数

| 项目 | 当前值 |
|---|---|
| Provider DID | `{FINAL_DID}` |
| kid | `{FINAL_KID}` |
| 算法 | `ES256` |
| 密钥 | `EC P-256` |
| DID Document | `https://shenyousota.github.io/dssc-toolbox/did.json` |
| A组证据Commit | `{A_COMMIT}` |
| Dataset URI | `https://example.org/dssc-energy/datasets/building-energy-hourly-v1` |
| D组Shape SHA-256 | `{SHAPE_SHA}` |

## 重现命令

在项目根目录打开PowerShell，依次运行：

```powershell
py -c "import cryptography; print(cryptography.__version__)"
py .\\scripts\\prepare-v03-es256-candidate.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\\scripts\\check-consistency.ps1
py .\\scripts\\build-es256-candidate-jwts.py
py .\\scripts\\verify-es256-candidate-jwts.py
py .\\scripts\\finalize-v03-docs.py
```

如果第一条报 `No module named cryptography` ，只需先运行：

```powershell
py -m pip install cryptography
```

## 主要交付物

- `05-signed/es256-candidate/`：两份VC-JWT和一份VP-JWT。
- `06-invalid-tests/signed-es256-candidate/`：签名有效但内容无效的用例，以及签名被篡改的INV-07。
- `07-evidence/es256-candidate-jwt-verification.md`：公网DID验签证据。
- `07-evidence/project-metadata-shacl-validation.md`：项目Metadata的SHACL证据。
- `07-evidence/v03-active-deliverable-sha256.csv`：活跃交付文件哈希。
- `07-evidence/member2-handoff-summary.md`：给成员3的交接说明。

## 范围与边界

- 当前VP只包含LegalPerson VC和ServiceOffering VC。LRN与Terms and Conditions不在成员2当前范围内。
- `02-config/a-group-public-demo-key/provider-key.private.jwk.json` 是A组已公开的虚构主体教学Demo密钥，本项目为了可重现性故意保留；严禁用于生产。
- `.gitignore` 应继续保留。`*.jwk` 不会匹配上述以 `.jwk.json` 结尾的教学文件，但仍能防止其他真实本地秘密被误提交。
- C组仓库对D组E5F Shape的同步仍是外部待办项，不阻塞本次本地候选签名。
- 当前公网DID方法只发布了JWK公钥；如Compliance Engine按当前Gaia-X规则要求信任服务商证书，API可能因此拒绝。这属于成员3需记录的集成结果，不是本地ES256验签失败。
"""
    write_text("README.md", readme)

    decisions = f"""# v0.3候选决定记录

当前状态：`ES256_CANDIDATE_LOCAL_VERIFIED`  
更新日期：`2026-08-17`

## 已固定的决定

| 项目 | 决定 | 状态 |
|---|---|---|
| VC Data Model | W3C VC Data Model 2.0 | CONFIRMED |
| VC Context | `https://www.w3.org/ns/credentials/v2` | CONFIRMED |
| Gaia-X Context | `https://w3id.org/gaia-x/development#` | CONFIRMED FOR CANDIDATE |
| VP组成 | LegalPerson VC + ServiceOffering VC | CURRENT SCOPE |
| Provider DID | `{FINAL_DID}` | CONFIRMED BY A REPOSITORY |
| kid | `{FINAL_KID}` | CONFIRMED |
| 签名 | `ES256 / EC P-256` | LOCAL VERIFIED |
| Dataset URI | `https://example.org/dssc-energy/datasets/building-energy-hourly-v1` | CONFIRMED |
| 权威Shape | D组E5F | PROJECT METADATA PASS |
| C/D仓库字节同步 | C组待更新 | EXTERNAL PENDING |
| Compliance API | 成员3执行 | HANDOFF PENDING |

## 明确不在当前范围

- Terms and Conditions Credential；
- Mock Legal Registration Number Credential；
- Compliance Credential的签发；
- 生产级私钥或信任服务商证书。

## 状态规则

本地验签PASS只证明JWT结构、ES256签名与公网DID公钥一致。只有成员3保存了Compliance API实际响应后，才能记录API是否接受。
"""
    write_text("01-decisions/provisional-decisions.md", decisions)

    remaining = f"""# 本地签名输入状态与剩余外部依赖

## 本地ES256候选签名

成员2当前范围内不再缺少密码学输入：

- DID：`{FINAL_DID}`；
- kid：`{FINAL_KID}`；
- 算法：`ES256`；
- 曲线：`P-256`；
- A组公开教学Demo私钥：已包含；
- 公网DID公钥匹配：PASS；
- D组E5F Shape项目Metadata预检：`Conforms: True`。

## 剩余外部依赖

1. 成员3调用Compliance API并保存完整请求参数、HTTP状态和响应。
2. C组将仓库Shape同步到D组E5F版本。
3. 如API要求LRN、Terms and Conditions或信任服务商证书，由项目负责人扩大范围后再补齐。

以上是最终合规集成依赖，不是成员2当前本地ES256签名的阻塞项。
"""
    write_text("01-decisions/missing-signing-inputs.md", remaining)

    checklist = f"""# v0.3签名就绪检查表

| 检查项 | 状态 | 证据 |
|---|---|---|
| JSON / JSON-LD语法 | PASS | 生成和验签脚本已读取 |
| 未签名跨文件一致性 | PASS | `07-evidence/unsigned-consistency-report.md` |
| Dataset Metadata SHACL | PASS | `Conforms: True` |
| Provider DID公网解析 | PASS | `{FINAL_DID}` |
| DID公钥与Demo私钥匹配 | PASS | `07-evidence/a-group-final-did-verification.md` |
| LegalPerson ES256 VC-JWT | PASS | `05-signed/es256-candidate/` |
| ServiceOffering ES256 VC-JWT | PASS | `05-signed/es256-candidate/` |
| ES256 VP-JWT | PASS | `05-signed/es256-candidate/` |
| 公网DID本地验签 | PASS | `07-evidence/es256-candidate-jwt-verification.md` |
| INV-01至INV-07材料 | PASS | `06-invalid-tests/es256-candidate-manifest.json` |
| C组Shape仓库同步 | WAITING EXTERNAL | C组负责 |
| Compliance API测试 | HANDOFF | 成员3负责 |

## 结论

成员2可以交付v0.3 ES256 candidate。不应把“本地PASS”改写为“Gaia-X Compliance PASS”，除非已有Compliance API的真实成功响应。
"""
    write_text("01-decisions/signing-readiness-checklist.md", checklist)

    invalid_readme = """# 无效测试集

| 编号 | 测试内容 | 材料 | 预期失败层级 |
|---|---|---|---|
| INV-01 | 缺少 `gx:legalName` | 已签名VC和VP | 凭证内容 |
| INV-02 | LegalPerson已过期 | 已签名VC和VP | 时间有效性 |
| INV-03 | `providedBy` DID不一致 | 已签名VC和VP | 跨文件一致性 |
| INV-04 | Dataset URI不一致 | 已签名VC和VP | 跨文件一致性 |
| INV-05 | Metadata format为 `text/csv` | JSON-LD源文件 | SHACL |
| INV-06 | 时间范围倒序 | JSON-LD源文件 | SHACL时间规则 |
| INV-07 | VP签名位被篡改 | VP-JWT | 密码学验签 |

INV-01至INV-04的JWT签名本身有效，用于隔离“内容无效”。INV-07的内容来自有效VP，但签名已被故意破坏。详细路径见 `es256-candidate-manifest.json`。
"""
    write_text("06-invalid-tests/README.md", invalid_readme)

    handoff = f"""# 成员2向成员3交接摘要

## 请优先使用

1. `05-signed/es256-candidate/presentation.es256-candidate.vp.jwt`
2. Compliance endpoint：`https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance`
3. Query：`vcid=https://gaia-x.eu/.well-known/compliance-credential.jwt`
4. Header：`Content-Type: application/vp+jwt`
5. Body：原始VP-JWT文本，不要包JSON外壳。

## 本地已证明

- DID：`{FINAL_DID}`
- kid：`{FINAL_KID}`
- ES256签名与公网DID公钥匹配：PASS
- 项目Dataset Metadata对D组E5F Shape：`Conforms: True`

## 请保存的API证据

- 请求时间、endpoint、query和Content-Type；
- HTTP状态码；
- 完整响应头和响应体；
- 使用的VP-JWT SHA-256；
- 如失败，记录是DID/证书、JWT格式、Credential Shape、缺少LRN/T&C，还是ServiceOffering内容层。

## 无效测试

按 `06-invalid-tests/es256-candidate-manifest.json` 选择INV-01至INV-07。不要预设所有失败都能达到内容规则层；如基础信任或必需Credential先失败，请照实记录。
"""
    write_text("07-evidence/member2-handoff-summary.md", handoff)

    hash_relative = Path("07-evidence/v03-active-deliverable-sha256.csv")
    hash_path = ROOT / hash_relative
    candidates = []
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT)
        parts = relative.parts
        if relative == hash_relative:
            continue
        if parts[0] in {"00-original", ".git"}:
            continue
        if "__pycache__" in parts or path.suffix == ".pyc":
            continue
        if parts[:2] == ("05-signed", "provisional"):
            continue
        if parts[:2] == ("07-evidence", "archive"):
            continue
        candidates.append(path)
    hash_path.parent.mkdir(parents=True, exist_ok=True)
    with hash_path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.writer(file, lineterminator="\n")
        writer.writerow(["relativePath", "sha256"])
        for path in sorted(candidates):
            writer.writerow(
                [
                    path.relative_to(ROOT).as_posix(),
                    hashlib.sha256(path.read_bytes()).hexdigest().upper(),
                ]
            )

    print("v0.3 documentation and handoff finalization: PASS")
    print(f"Active deliverable hashes: {hash_path}")
    print("Member2 local ES256 candidate is ready for packaging and member3 handoff.")


if __name__ == "__main__":
    main()
