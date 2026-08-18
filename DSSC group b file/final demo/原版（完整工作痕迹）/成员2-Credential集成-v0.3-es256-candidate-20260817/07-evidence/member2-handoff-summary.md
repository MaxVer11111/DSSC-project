# 成员2向成员3交接摘要

## 请优先使用

1. `05-signed/es256-candidate/presentation.es256-candidate.vp.jwt`
2. Compliance endpoint：`https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance`
3. Query：`vcid=https://gaia-x.eu/.well-known/compliance-credential.jwt`
4. Header：`Content-Type: application/vp+jwt`
5. Body：原始VP-JWT文本，不要包JSON外壳。

## 本地已证明

- DID：`did:web:shenyousota.github.io:dssc-toolbox`
- kid：`did:web:shenyousota.github.io:dssc-toolbox#key-1`
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
