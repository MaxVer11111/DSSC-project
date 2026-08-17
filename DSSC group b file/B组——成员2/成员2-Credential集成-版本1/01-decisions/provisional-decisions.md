# Credential集成临时决策记录

## 1. 当前状态

- 决策版本：0.1
- 状态：临时冻结，等待组长确认
- 数据范围：A组、C组、D组
- 用途：制作未签名LegalPerson、ServiceOffering和统一Metadata
- 当前禁止操作：正式签名、生成最终VP-JWT

## 2. 暂定统一值

| 项目 | 暂定值 | 状态 |
|---|---|---|
| Provider名称 | Energy Data Provider Ltd. | 暂时固定 |
| Provider DID | did:web:mp-operations.org | 暂时固定 |
| LegalPerson主体ID | did:web:mp-operations.org | 暂时固定 |
| ServiceOffering ID | urn:dssc:service-offering:building-energy-hourly-v1 | 等待组长确认 |
| Dataset ID | building-energy-hourly-v1 | 暂时固定 |
| Dataset canonical URI | urn:dssc:dataset:building-energy-hourly-v1 | 建议采用 |
| Endpoint | https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001 | 采用A组实际部署值 |
| Environment | local-real-cluster | 建议采用 |
| Publicly reachable | false | 建议采用 |
| Serialization family | JSON | 建议采用 |
| Response media type | application/ld+json | 采用A组实际接口格式 |
| Update frequency | hourly | 暂时固定 |
| Unit | kWh | 暂时固定 |
| License | https://creativecommons.org/licenses/by/4.0/  | 建议采用 |
| Metadata主要类型 | dcat:Dataset | 等待确认 |
| Metadata补充类型 | be:DataProductMetadata | 等待确认 |

## 3. 当前未确认内容

1. Gaia-X ontology/schema最终版本；
2. Compliance API准确Endpoint；
3. Compliance API要求的Content-Type；
4. JWT签名算法；
5. 可用DID Document；
6. JWT Header中的kid；
7. 项目正式签名私钥；
8. VP-JWT必须包含哪些VC；
9. ServiceOffering ID是否正式冻结；
10. 修改后的最终Shapes和SHA-256。

## 4. 暂定数据使用原则

1. 真实主体、业务ID和部署Endpoint以A组为基准；
2. Metadata字段和语义结构由C组负责解释；
3. Shapes和验证规则由D组负责修改并重新验证；
4. 未确认签名参数前，不生成最终VC-JWT和VP-JWT；
5. 私钥不得上传GitHub。

## LegalPerson草稿状态

已完成最小未签名草稿：

- Credential ID：`urn:dssc:credential:legal-person:mp-operations:v0.1`
- Credential Subject ID：`did:web:mp-operations.org`
- Issuer：`did:web:mp-operations.org`
- Legal Name：`Energy Data Provider Ltd.`
- Credential类型：`LegalPerson`
- 当前状态：Provisional / Unsigned

当前缺失：

- 最终Gaia-X Schema/ontology版本
- Legal Registration Number Credential
- Legal Address
- Headquarters Address
- validUntil
- DID Document
- kid
- 签名算法
- 私钥
- Trust Anchor材料

在以上内容确认前，不生成最终LegalPerson VC-JWT。