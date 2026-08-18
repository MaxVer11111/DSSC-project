# 成员2向成员3交接摘要

## 交接方式

请以完整清理版 ZIP 作为唯一交付版本，不要只转发聊天中零散的 JWT。完整包同时保留源文件、无效用例、验签证据、哈希和复核脚本，能够避免版本混用。

成员3收到后，主测试输入只有这个文件：

```text
05-signed/es256-candidate/presentation.es256-candidate.vp.jwt
```

两份独立 VC-JWT 位于同目录，供解码、单独检查或定位问题使用：

```text
05-signed/es256-candidate/legal-person.es256-candidate.vc.jwt
05-signed/es256-candidate/service-offering.es256-candidate.vc.jwt
```

## Compliance API 提交参数

| 参数 | 值 |
|---|---|
| Endpoint | `https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance` |
| Method | `POST` |
| Query | `vcid=https://gaia-x.eu/.well-known/compliance-credential.jwt` |
| Content-Type | `application/vp+jwt` |
| Body | 上述 VP-JWT 的原始文本，不加 JSON 外壳、不加引号 |

## 本地已经验证

- DID：`did:web:shenyousota.github.io:dssc-toolbox`
- `kid`：`did:web:shenyousota.github.io:dssc-toolbox#key-1`
- 有效 VC/VP 的 ES256 签名与公网 DID 公钥匹配：PASS
- VP 内 Credential 数量：2（LegalPerson + ServiceOffering）
- 项目 Dataset Metadata 对 D 组 E5F Shape：`Conforms: True`
- 有效 JWT 的 SHA-256：见 `es256-candidate-jwt-sha256.csv`

## 无效测试

以 `06-invalid-tests/es256-candidate-manifest.json` 为唯一索引：

- INV-01～INV-04：签名有效，Credential 内容故意无效；同时提供对应 VP-JWT。
- INV-07：有效 VP 的签名位被故意篡改，预期密码学验签失败。
- INV-05～INV-06：仅用于 Metadata/SHACL 负例，不是 Compliance API 的 VP-JWT 输入。

不要预设所有无效用例都会到达内容规则层。如果服务先因 DID/证书信任、缺少 LRN/T&C 等原因拒绝，请照实保存响应。

## 成员3应保存的证据

- 请求时间、endpoint、query 和 Content-Type；
- 使用的 VP-JWT SHA-256；
- HTTP 状态码；
- 完整响应头和响应体；
- 结论：成功，或失败发生在 DID/证书、JWT 格式、Credential Shape、缺少 Credential、跨文件一致性等哪一层。

## Demo 私钥说明

`02-config/a-group-public-demo-key/provider-key.private.jwk.json` 是A组已经公开的教学 Demo 私钥，仅用于同学复现本包签名，不应发送到 Compliance API，也不得用于生产或真实主体。
