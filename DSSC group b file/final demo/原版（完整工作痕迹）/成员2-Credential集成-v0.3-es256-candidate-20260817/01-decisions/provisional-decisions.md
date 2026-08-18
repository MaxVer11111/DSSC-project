# v0.3候选决定记录

当前状态：`ES256_CANDIDATE_LOCAL_VERIFIED`  
更新日期：`2026-08-17`

## 已固定的决定

| 项目 | 决定 | 状态 |
|---|---|---|
| VC Data Model | W3C VC Data Model 2.0 | CONFIRMED |
| VC Context | `https://www.w3.org/ns/credentials/v2` | CONFIRMED |
| Gaia-X Context | `https://w3id.org/gaia-x/development#` | CONFIRMED FOR CANDIDATE |
| VP组成 | LegalPerson VC + ServiceOffering VC | CURRENT SCOPE |
| Provider DID | `did:web:shenyousota.github.io:dssc-toolbox` | CONFIRMED BY A REPOSITORY |
| kid | `did:web:shenyousota.github.io:dssc-toolbox#key-1` | CONFIRMED |
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
