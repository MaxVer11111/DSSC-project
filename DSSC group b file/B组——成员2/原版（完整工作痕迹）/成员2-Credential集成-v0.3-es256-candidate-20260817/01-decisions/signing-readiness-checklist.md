# v0.3签名就绪检查表

| 检查项 | 状态 | 证据 |
|---|---|---|
| JSON / JSON-LD语法 | PASS | 生成和验签脚本已读取 |
| 未签名跨文件一致性 | PASS | `07-evidence/unsigned-consistency-report.md` |
| Dataset Metadata SHACL | PASS | `Conforms: True` |
| Provider DID公网解析 | PASS | `did:web:shenyousota.github.io:dssc-toolbox` |
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
