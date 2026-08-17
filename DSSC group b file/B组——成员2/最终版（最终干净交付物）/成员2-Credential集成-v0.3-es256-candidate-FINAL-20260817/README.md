# 成员2 Credential 集成最终交接包（v0.3 ES256 Candidate）

## 交付结论

成员2当前范围内的任务已经完成，并通过本地一致性、签名和哈希检查。

| 任务 | 结果 | 主要文件 |
|---|---|---|
| 更新 LegalPerson | PASS | `04-credential-source/legal-person.jsonld` |
| 更新 ServiceOffering | PASS | `04-credential-source/service-offering.jsonld` |
| 生成两份有效 VC-JWT | PASS | `05-signed/es256-candidate/` |
| 生成包含上述两份 VC 的 VP-JWT | PASS | `05-signed/es256-candidate/presentation.es256-candidate.vp.jwt` |
| 准备 Credential/VP 无效用例 | PASS | `06-invalid-tests/` |
| 准备 JWT 解码、DID 解析及验签证据 | PASS | `07-evidence/` |

这是本地验签通过的 `ES256 candidate`，不等同于 Gaia-X Compliance API 已经接受。成员3仍需提交 API，并保存服务端响应。

## 成员3从这里开始

先阅读 `07-evidence/member2-handoff-summary.md`，再使用：

```text
05-signed/es256-candidate/presentation.es256-candidate.vp.jwt
```

该 VP 中恰好包含两份 Credential：

1. LegalPerson VC-JWT；
2. ServiceOffering VC-JWT。

本轮不包含 LRN Credential，也不包含 Terms and Conditions Credential。

## 固定参数

| 项目 | 最终值 |
|---|---|
| Provider/Holder DID | `did:web:shenyousota.github.io:dssc-toolbox` |
| `kid` | `did:web:shenyousota.github.io:dssc-toolbox#key-1` |
| 算法 | `ES256` |
| 密钥类型 | `EC P-256` |
| VC Header | `typ=vc+jwt`，`cty=vc` |
| VP Header | `typ=vp+jwt`，`cty=vp` |
| Dataset URI | `https://example.org/dssc-energy/datasets/building-energy-hourly-v1` |
| DID Document | `https://shenyousota.github.io/dssc-toolbox/did.json` |
| D组 Shape SHA-256 | `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E` |

## 文件结构

- `02-config/`：最终配置，以及A组公开的教学 Demo JWK。
- `03-normalized-metadata/`：项目实际 Dataset Metadata。
- `04-credential-source/`：有效 LegalPerson、ServiceOffering JSON-LD 源文件。
- `05-signed/es256-candidate/`：两份有效 VC-JWT 和一份有效 VP-JWT。
- `06-invalid-tests/`：无效用例、清单及对应材料。
- `07-evidence/`：JWT 解码、签名验证、SHACL 和 SHA-256 证据；`v03-final-deliverable-sha256.csv` 可校验本包内除清单自身外的全部文件。
- `scripts/`：重建、检查和验签脚本。

无效用例边界：INV-01～INV-04 是签名有效但内容故意无效的 VC/VP；INV-07 是签名故意损坏的 VP；INV-05～INV-06 是 Metadata/SHACL 源文件负例，不是 VP-JWT。准确路径及预期结果见 `06-invalid-tests/es256-candidate-manifest.json`。

## 本地复核命令

在解压后的项目根目录打开 PowerShell：

```powershell
py -c "import cryptography; print(cryptography.__version__)"
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-consistency.ps1
py .\scripts\build-es256-candidate-jwts.py
py .\scripts\verify-es256-candidate-jwts.py
```

如果第一条提示没有 `cryptography`：

```powershell
py -m pip install cryptography
```

注意：重建脚本会按照运行时间生成新的 30 天 VP 有效期并重新签名，同时更新 `07-evidence/es256-candidate-jwt-sha256.csv`。因此，新签名的哈希不要求与压缩包中的原始哈希相同；应在重建后再次运行验签脚本，并以新生成的哈希清单为准。若只做成员3的 API 提交，请不要先运行重建脚本，直接使用包内现成 VP。

## 安全与范围说明

- `02-config/a-group-public-demo-key/provider-key.private.jwk.json` 是A组已经公开的虚构主体教学 Demo 私钥。为保证同学能够完整复现而保留，文件也标注了仅限教学；不得用于真实主体或生产环境。
- `.gitignore` 用于阻止误提交其他本地真实密钥，应该保留。其 `*.jwk` 规则不会匹配本包中以 `.jwk.json` 结尾的教学文件。
- 本包只保留当前 ES256 交付所需的源文件、JWT、无效用例、证据和复核脚本。
- 公网 DID 的 JWK 能通过本地 ES256 验签；如果 Compliance 服务还要求证书信任链、LRN 或 T&C，成员3应把服务端返回如实记录为集成结果。
