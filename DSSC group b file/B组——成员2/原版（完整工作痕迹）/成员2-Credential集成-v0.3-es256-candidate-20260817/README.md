# 成员2 Credential集成 v0.3 ES256 Candidate

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
| Provider DID | `did:web:shenyousota.github.io:dssc-toolbox` |
| kid | `did:web:shenyousota.github.io:dssc-toolbox#key-1` |
| 算法 | `ES256` |
| 密钥 | `EC P-256` |
| DID Document | `https://shenyousota.github.io/dssc-toolbox/did.json` |
| A组证据Commit | `89d40ccf0bd43af22f2129f81d0ba0214f5c327c` |
| Dataset URI | `https://example.org/dssc-energy/datasets/building-energy-hourly-v1` |
| D组Shape SHA-256 | `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E` |

## 重现命令

在项目根目录打开PowerShell，依次运行：

```powershell
py -c "import cryptography; print(cryptography.__version__)"
py .\scripts\prepare-v03-es256-candidate.py
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\check-consistency.ps1
py .\scripts\build-es256-candidate-jwts.py
py .\scripts\verify-es256-candidate-jwts.py
py .\scripts\finalize-v03-docs.py
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
