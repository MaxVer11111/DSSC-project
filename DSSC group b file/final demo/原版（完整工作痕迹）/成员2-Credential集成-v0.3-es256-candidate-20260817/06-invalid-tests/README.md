# 无效测试集

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
