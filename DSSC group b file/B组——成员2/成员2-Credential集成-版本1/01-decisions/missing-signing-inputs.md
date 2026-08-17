# 当前缺失的签名和身份材料

| 材料 | 当前状态 | 为什么需要 |
|---|---|---|
| 确认Provider DID | 暂定为did:web:mp-operations.org | 确定LegalPerson真实身份 |
| DID Document | 缺失 | 让验证器找到公钥 |
| DID Document公开地址 | 缺失 | did:web需要能够解析 |
| kid | 缺失 | 指明使用DID Document中的哪把公钥 |
| 签名算法alg | 缺失 | 确定RS256、PS256或其他算法 |
| 私钥保管人 | 缺失 | 确定由谁执行签名 |
| Legal Registration Number | 缺失 | 补充LegalPerson法定身份 |
| LRN Credential | 缺失 | 证明注册号码经过可信签发 |
| Headquarters Address | 缺失 | 满足LegalPerson字段要求 |
| Legal Address | 缺失 | 满足LegalPerson字段要求 |
| Terms and Conditions VC | 缺失 | 证明Issuer接受Gaia-X条款 |
| ServiceOffering提交方式 | 未确认 | 确认是否放入同一个VP或单独提交 |