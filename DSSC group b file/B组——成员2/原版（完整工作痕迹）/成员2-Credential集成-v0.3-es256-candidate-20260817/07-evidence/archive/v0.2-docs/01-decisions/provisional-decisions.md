# 候选决定记录

当前状态：`v0.2 candidate`
更新日期：`2026-08-17`

## 1. 文件目的

本文件记录成员2当前采用的项目决定。

标记为“候选版已确认”的决定，可以用于准备和本地测试 v0.2 开发产物。

如果某项内容仍然等待其他组确认，就不能将它写成最终跨组决定。

## 2. Credential 与 Context 决定

| 决定项目                           | 当前值                                       | 状态                      |
| ------------------------------ | ----------------------------------------- | ----------------------- |
| VC Data Model                  | W3C Verifiable Credentials Data Model 2.0 | CONFIRMED FOR CANDIDATE |
| VC Context                     | `https://www.w3.org/ns/credentials/v2`    | CONFIRMED FOR CANDIDATE |
| Gaia-X Context                 | `https://w3id.org/gaia-x/development#`    | CONFIRMED FOR CANDIDATE |
| 当前 VP 组成                       | LegalPerson VC + ServiceOffering VC       | CONFIRMED CURRENT SCOPE |
| 当前 VP 是否包含 T&C Credential      | 否                                         | OUT OF SCOPE            |
| 当前 VP 是否包含 Mock LRN Credential | 否                                         | OUT OF SCOPE            |

只有最终 Compliance API 契约或项目负责人明确要求时，才增加 T&C Credential 和 Mock LRN Credential。

## 3. LegalPerson Demo 身份事实

| 身份事实                                          | 当前值                                       | 状态                  |
| --------------------------------------------- | ----------------------------------------- | ------------------- |
| Legal name                                    | `Energy Data Provider Ltd.`               | CONFIRMED DEMO FACT |
| Demo Legal Registration Number                | `DEMO-ENERGY-001`                         | CONFIRMED DEMO FACT |
| Legal Address country code                    | `CN`                                      | CONFIRMED DEMO FACT |
| Legal Address country subdivision code        | `CN-GD`                                   | CONFIRMED DEMO FACT |
| Headquarters Address country code             | `CN`                                      | CONFIRMED DEMO FACT |
| Headquarters Address country subdivision code | `CN-GD`                                   | CONFIRMED DEMO FACT |
| validFrom                                     | `2026-08-16T00:00:00Z`                    | CONFIRMED DEMO FACT |
| validUntil                                    | `2027-08-16T00:00:00Z`                    | CONFIRMED DEMO FACT |
| 预留 Mock LRN Credential ID                     | `urn:dssc:credential:lrn:demo-energy-001` | RESERVED ONLY       |

LegalPerson 身份事实与最终 JSON-LD 属性映射分开记录。

地址和登记号最后使用哪个字段，必须遵循最终 LegalPerson 模型或 Shape。

在历史文件出现 `headquarterAddress`、`headquartersAddress` 等不同写法时，成员2不自行猜测最终字段。

## 4. 主要 ID 决定

| 项目                    | 当前值                                                   | 状态                                     |
| --------------------- | ----------------------------------------------------- | -------------------------------------- |
| 候选 Provider DID       | `did:web:mp-operations.org`                           | WAITING FOR FINAL A-GROUP CONFIRMATION |
| Provider name         | `Energy Data Provider Ltd.`                           | CONFIRMED DEMO FACT                    |
| ServiceOffering ID    | `urn:dssc:service-offering:building-energy-hourly-v1` | CONFIRMED FOR CANDIDATE                |
| Dataset canonical URI | `urn:dssc:dataset:building-energy-hourly-v1`          | CONFIRMED FOR CANDIDATE                |
| 最终目标 kid              | `did:web:mp-operations.org#key-1`                     | CONFIRMED TARGET PARAMETER             |

如果最终 Provider DID 改变，必须统一修改：

* LegalPerson subject；
* ServiceOffering `providedBy`；
* Credential issuer；
* VP issuer 或 holder；
* JWT `iss`；
* JWT `kid`；
* DID Document URL；
* 一致性检查报告；
* 签名验证报告。

## 5. Building Energy 语义模型决定

| 项目                         | 当前值                                                                | 状态                      |
| -------------------------- | ------------------------------------------------------------------ | ----------------------- |
| 模型版本                       | v0.4                                                               | CONFIRMED FOR CANDIDATE |
| Model IRI                  | `https://w3id.org/dssc-demo/building-energy/v0.4`                  | CONFIRMED FOR CANDIDATE |
| Profile                    | `dssc-building-energy-metadata-v0.4`                               | CONFIRMED FOR CANDIDATE |
| Context SHA-256            | `F46D3056239CC1CB7D678707E749B33E336564E5FCE23FFCCCD528EAE6CBE391` | RECORDED                |
| Canonical example SHA-256  | `9ACC287AE274E549BECD15852231B325C43E1DBDDC14E9F2459F4C490420F239` | RECORDED                |
| Dataset Metadata format    | `application/json`                                                 | CONFIRMED FOR CANDIDATE |
| Endpoint responseMediaType | `application/ld+json`                                              | CONFIRMED FOR CANDIDATE |

Dataset Metadata format 和 endpoint responseMediaType 属于不同层级，不能要求两者必须相同。

## 6. Shape 候选状态

| 来源                         | 已记录 SHA-256                                                        | 状态          |
| -------------------------- | ------------------------------------------------------------------ | ----------- |
| C 组当前 v0.4 Shape           | `A556039C0EC3030A9C4273C62A787E448B8869F7648E948663E10D3FE007CBDA` | CANDIDATE   |
| D 组当前 main 分支文件            | `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E` | CANDIDATE   |
| D 组 README 记录值             | `17DACE38CB949796D3BDEF0D5BA3002763A5FAC84FF56650F886CDCF8E6AE53D` | RECORD ONLY |
| 最终权威 Shape                 | 尚未选定                                                               | WAITING     |
| 最终权威 SHA-256               | 尚未提供                                                               | WAITING     |
| 最终 extra-property severity | 尚未统一                                                               | WAITING     |

`17DACE...` 只因为出现在 D 组 README 中而被记录。

不能将它描述成 D 组当前 main 分支文件的实际 SHA-256。

`E5F150...` 是当前检查到的 D 组文件 SHA-256。

在 D 组正式确认前，也不能把它描述成最终权威 SHA-256。

C、D 当前还存在真实规则差异：

* C 当前将相关多余属性判为 `sh:Warning`，并映射为 INAPPLICABLE；
* D 当前将其判为 `sh:Violation`，并拒绝提交。

最终处理方式尚未确定。

## 7. 开发签名决定

当前本地 provisional 签名流程使用：

| 项目           | 开发值                                   | 状态               |
| ------------ | ------------------------------------- | ---------------- |
| 签名算法         | RS256                                 | DEVELOPMENT ONLY |
| 密钥类型         | RSA                                   | DEVELOPMENT ONLY |
| 开发 kid       | `did:web:mp-operations.org#dev-key-1` | DEVELOPMENT ONLY |
| 私钥位置         | Git 仓库外部                              | REQUIRED         |
| DID Document | 本地未发布的开发 DID Document                 | DEVELOPMENT ONLY |
| 使用目的         | 本地生成 JWT 和完成密码学验签                     | DEVELOPMENT ONLY |

当前 provisional JWT 不是最终 A 组 Demo JWT。

## 8. 最终 Demo 签名目标

| 项目               | 目标值                                              | 状态                             |
| ---------------- | ------------------------------------------------ | ------------------------------ |
| 签名算法             | ES256                                            | TARGET KNOWN                   |
| 密钥类型             | EC                                               | TARGET KNOWN                   |
| 曲线               | P-256                                            | TARGET KNOWN                   |
| 候选 Provider DID  | `did:web:mp-operations.org`                      | WAITING FOR FINAL CONFIRMATION |
| kid              | `did:web:mp-operations.org#key-1`                | TARGET KNOWN                   |
| DID Document URL | `https://mp-operations.org/.well-known/did.json` | CURRENTLY NOT RESOLVABLE       |

最终 ES256 签名必须等待：

1. A 组确认最终 Provider DID；
2. 公网 DID Document 可以解析；
3. DID Document 中存在最终 verification method；
4. 公网 EC P-256 公钥与 Demo 私钥匹配；
5. 最终 Credential 内容通过选定的验证契约。

## 9. A 组 Endpoint 决定

当前 endpoint 为：

`https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001`

该域名解析到调用者自己的本机回环地址。

候选配置暂时保留该 endpoint，用于标识 A 组本地 Scorpio 资源。

成员3仍需要以下任意一种方法：

* 本地复现步骤；
* 远程访问 A 组环境；
* 共享测试部署；
* 公网可访问的新 endpoint。

Endpoint 访问方式仍然是外部集成阻塞项。

## 10. 当前交付范围

成员2当前交付包括：

* LegalPerson VC 源文件；
* ServiceOffering VC 源文件；
* 包含上述两份 VC 的开发 VP；
* 本地开发签名证据；
* 文件一致性证据；
* 无效测试源文件。

当前交付不包括：

* T&C Credential；
* Mock LRN Credential；
* Compliance Credential；
* 最终 ES256 Credential 集；
* 公网 DID 解析成功报告；
* 最终 C/D SHACL 验证报告；
* 最终 Compliance API 响应。

## 11. 仍需外部确认的决定

以下事项仍然需要其他组确认：

* 最终 Provider DID；
* 公网 DID 发布；
* 公网公钥与 Demo 私钥是否匹配；
* C/D 唯一权威 Shape；
* 最终原始文件 SHA-256；
* 最终 extra-property severity；
* 存在冲突时的 LegalPerson 最终字段；
* 成员3访问 endpoint 的方法。

## 12. 变更规则

不能把候选值直接改名为最终值。

收到外部最终决定后，必须：

1. 保存对方回复或仓库证据；
2. 记录权威来源；
3. 更新候选配置；
4. 重新运行一致性检查；
5. 重新运行适用的 Shape 验证；
6. 重新生成 JWT；
7. 重新生成证据报告；
8. 更新签名就绪检查表。



## 2026-08-17 C/D Shapes交付更新

D组已提供新的B组交付包，并将GitHub中当前权威Shape统一为LF换行版本。

- D组最终Shape SHA-256：
  `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E`
- 旧传输TTL原始SHA-256：
  `17DACE38CB949796D3BDEF0D5BA3002763A5FAC84FF56650F886CDCF8E6AE53D`
- 旧传输TTL统一为LF后的SHA-256：
  `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E`
- D组当前extra-property处理：
  `sh:Violation`，提交将被拒绝。
- Dataset metadata format：
  `application/json`。
- A组Endpoint responseMediaType：
  `application/ld+json`。

D组GitHub及本次交付包已经统一为E5F版本。C组GitHub当前仍保留
A556版本，其Closed Shape对多余字段使用sh:Warning，因此C/D仓库
尚未完全字节统一。该差异不阻塞当前两VC开发签名，但在最终跨组
文档中仍应标记为等待C组同步。

D组交付包中的PDF报告验证的是D组提供的示例metadata，不直接证明
本项目实际metadata已经通过验证。本项目metadata仍需使用E5F Shape
单独执行验证。