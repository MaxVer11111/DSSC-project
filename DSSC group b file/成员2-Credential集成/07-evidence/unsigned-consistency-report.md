# 未签名凭证一致性检查报告

- 检查时间：2026-08-16 02:35:53
- 配置版本：0.1
- 总体结果：**PASS**

| 检查项目 | 期望值 | 实际值 | 结果 |
|---|---|---|---|
| Provider DID matches LegalPerson subject | did:web:mp-operations.org | did:web:mp-operations.org | PASS |
| Provider name matches LegalPerson name | Energy Data Provider Ltd. | Energy Data Provider Ltd. | PASS |
| ServiceOffering providedBy matches LegalPerson | did:web:mp-operations.org | did:web:mp-operations.org | PASS |
| ServiceOffering subject ID matches config | urn:dssc:service-offering:building-energy-hourly-v1 | urn:dssc:service-offering:building-energy-hourly-v1 | PASS |
| ServiceOffering Dataset reference matches config | urn:dssc:dataset:building-energy-hourly-v1 | urn:dssc:dataset:building-energy-hourly-v1 | PASS |
| Dataset URI matches config | urn:dssc:dataset:building-energy-hourly-v1 | urn:dssc:dataset:building-energy-hourly-v1 | PASS |
| Dataset Endpoint matches config | https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001 | https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001 | PASS |
| Dataset media type matches config | application/ld+json | application/ld+json | PASS |
| Dataset License matches config | https://creativecommons.org/licenses/by/4.0/ | https://creativecommons.org/licenses/by/4.0/ | PASS |

## 说明

本报告只检查未签名文件之间的字段一致性。

它不代表已经完成：

- Gaia-X SHACL验证；
- DID Document验证；
- JWT签名验证；
- Compliance API测试。
