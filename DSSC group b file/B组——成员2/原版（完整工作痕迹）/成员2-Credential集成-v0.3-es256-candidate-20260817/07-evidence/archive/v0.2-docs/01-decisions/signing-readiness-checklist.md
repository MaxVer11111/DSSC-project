# 签名就绪检查表

当前状态：`v0.2 candidate`
更新日期：`2026-08-17`

## 1. 状态说明

| 状态               | 含义               |
| ---------------- | ---------------- |
| PASS             | 已完成，并且已有当前证据支持   |
| TODO             | 成员2目前可以在本地继续完成   |
| WAITING          | 等待其他组确认或决定       |
| BLOCKED          | 依赖该项目的最终步骤暂时不能继续 |
| OUT OF SCOPE     | 不属于当前交付范围        |
| DEVELOPMENT ONLY | 仅适用于本地开发流程       |

## 2. Credential 模型和内容

| 检查项目                          | 状态           | 证据或下一步                                                |
| ----------------------------- | ------------ | ----------------------------------------------------- |
| 选择 W3C VC Data Model 2.0      | PASS         | `https://www.w3.org/ns/credentials/v2`                |
| 选择 Gaia-X development Context | PASS         | `https://w3id.org/gaia-x/development#`                |
| 选择 Building Energy v0.4 候选模型  | PASS         | v0.2 配置                                               |
| Provider 名称已记录                | PASS         | `Energy Data Provider Ltd.`                           |
| Demo 登记号已记录                   | PASS         | `DEMO-ENERGY-001`                                     |
| Legal Address 身份事实已记录         | PASS         | `CN / CN-GD`                                          |
| Headquarters Address 身份事实已记录  | PASS         | `CN / CN-GD`                                          |
| validFrom 已记录                 | PASS         | `2026-08-16T00:00:00Z`                                |
| validUntil 已记录                | PASS         | `2027-08-16T00:00:00Z`                                |
| 最终地址字段映射                      | WAITING      | 遵循最终 LegalPerson 模型或 Shape                            |
| 最终登记号字段映射                     | WAITING      | 遵循最终 LegalPerson 模型或 Shape                            |
| ServiceOffering ID 已记录        | PASS         | `urn:dssc:service-offering:building-energy-hourly-v1` |
| Dataset canonical URI 已记录     | PASS         | `urn:dssc:dataset:building-energy-hourly-v1`          |
| 当前 VP 组成已固定                   | PASS         | LegalPerson VC + ServiceOffering VC                   |
| T&C Credential 已加入            | OUT OF SCOPE | 仅在明确要求时加入                                             |
| Mock LRN Credential 已加入       | OUT OF SCOPE | 当前只预留 ID                                              |

## 3. Metadata 与 Endpoint

| 检查项目                                               | 状态   | 证据或下一步                 |
| -------------------------------------------------- | ---- | ---------------------- |
| Dataset Metadata format 为 `application/json`       | PASS | v0.2 候选 Metadata       |
| Endpoint responseMediaType 为 `application/ld+json` | PASS | 与 Metadata format 分开保存 |
| Dataset URI 与配置一致                                  | TODO | 运行 v0.2 一致性检查          |
| Dataset endpoint 与配置一致                             | TODO | 运行 v0.2 一致性检查          |
| Dataset license 与配置一致                              | TODO | 运行 v0.2 一致性检查          |
| 各文件中的 Provider 引用一致                                | TODO | 运行 v0.2 一致性检查          |
| ServiceOffering 的 Dataset 引用一致                     | TODO | 运行 v0.2 一致性检查          |

Metadata format 和 endpoint responseMediaType 不能作为同一个字段直接比较。

## 4. Shape 与语义验证

| 检查项目                        | 状态      | 证据或下一步                                                             |
| --------------------------- | ------- | ------------------------------------------------------------------ |
| C 当前 v0.4 Shape hash 已记录    | PASS    | `A556039C0EC3030A9C4273C62A787E448B8869F7648E948663E10D3FE007CBDA` |
| D 当前 main 文件 hash 已记录       | PASS    | `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E` |
| D README hash 已单独记录         | PASS    | `17DACE38CB949796D3BDEF0D5BA3002763A5FAC84FF56650F886CDCF8E6AE53D` |
| 唯一权威 Shape 已确定              | BLOCKED | 等待 C/D                                                             |
| 最终原始文件 SHA-256 已确认          | BLOCKED | 等待 C/D                                                             |
| Extra-property severity 已确认 | BLOCKED | 等待 C/D                                                             |
| 有效候选内容通过最终 Shape            | BLOCKED | 需要权威 Shape                                                         |
| 无效测试内容通过最终规则测试              | BLOCKED | 需要权威 Shape                                                         |
| 最终 SHACL 报告已生成              | BLOCKED | 需要权威 Shape                                                         |

当前不能把任何候选 hash 标记成最终权威 Shape hash。

## 5. 最终签名身份

| 检查项目                                | 状态      | 证据或下一步                                           |
| ----------------------------------- | ------- | ------------------------------------------------ |
| 最终目标算法确定为 ES256                     | PASS    | A 组 Demo 目标                                      |
| 最终目标密钥类型确定为 EC                      | PASS    | A 组 Demo 目标                                      |
| 最终目标曲线确定为 P-256                     | PASS    | A 组 Demo 目标                                      |
| 最终目标 kid 已记录                        | PASS    | `did:web:mp-operations.org#key-1`                |
| 候选 Provider DID 已记录                 | PASS    | `did:web:mp-operations.org`                      |
| 最终 Provider DID 已确认                 | WAITING | 等待 A 组                                           |
| 公网 DID Document 可以解析                | BLOCKED | `https://mp-operations.org/.well-known/did.json` |
| DID Document 包含最终 kid               | BLOCKED | 发布后检查                                            |
| 公网密钥为 EC P-256                      | BLOCKED | 发布后检查                                            |
| 公网密钥与 Demo 私钥匹配                     | BLOCKED | 必须进行密钥匹配验证                                       |
| 私钥未进入仓库                             | PASS    | 强制安全要求                                           |
| 最终 ES256 LegalPerson VC-JWT 已生成     | BLOCKED | 需要最终签名身份                                         |
| 最终 ES256 ServiceOffering VC-JWT 已生成 | BLOCKED | 需要最终签名身份                                         |
| 最终 ES256 VP-JWT 已生成                 | BLOCKED | 需要最终两份 VC-JWT                                    |
| 通过公网 DID 完成最终验签                     | BLOCKED | 需要公网 DID                                         |

## 6. 开发签名流程

| 检查项目                                         | 状态      | 证据或下一步                     |
| -------------------------------------------- | ------- | -------------------------- |
| 开发 RSA 密钥已生成                                 | PASS    | 私钥保存在仓库外                   |
| 开发公钥 DID Document 已生成                        | PASS    | 本地未发布文档                    |
| 上一版 v0.1 LegalPerson VC-JWT 已生成              | PASS    | 上一开发检查点                    |
| 上一版 v0.1 ServiceOffering VC-JWT 已生成          | PASS    | 上一开发检查点                    |
| 上一版 v0.1 VP-JWT 已生成                          | PASS    | 上一开发检查点                    |
| 上一版 v0.1 JWT 三段式检查                           | PASS    | 每份 JWT 都是三个分段              |
| 上一版 v0.1 RS256 本地验签                          | PASS    | 上一版验证证据                    |
| v0.2 JSON 语法检查                               | TODO    | 在一致性检查前运行                  |
| v0.2 未签名一致性检查                                | TODO    | 运行 `check-consistency.ps1` |
| v0.2 LegalPerson provisional VC-JWT 重新生成     | TODO    | 一致性 PASS 后运行生成脚本           |
| v0.2 ServiceOffering provisional VC-JWT 重新生成 | TODO    | 一致性 PASS 后运行生成脚本           |
| v0.2 provisional VP-JWT 重新生成                 | TODO    | 一致性 PASS 后运行生成脚本           |
| v0.2 JWT 三段式检查                               | TODO    | 检查全部新 JWT                  |
| v0.2 本地密码学验签                                 | TODO    | 运行验签脚本                     |
| 公网 DID 验签                                    | BLOCKED | 当前只有本地开发 DID               |
| 最终 Compliance 就绪                             | BLOCKED | 仍缺少外部输入                    |

本地 RS256 开发流程和最终 ES256 Demo 流程必须分开描述。

## 7. 无效测试准备

| 检查项目                  | 状态      | 证据或下一步                |
| --------------------- | ------- | --------------------- |
| 无效测试目录已创建             | TODO    | 创建 `06-invalid-tests` |
| 缺少 LegalPerson 名称的源文件 | TODO    | INV-01                |
| 已过期 LegalPerson 源文件   | TODO    | INV-02                |
| Provider 不一致源文件       | TODO    | INV-03                |
| Dataset 引用不一致源文件      | TODO    | INV-04                |
| Metadata format 错误源文件 | TODO    | INV-05                |
| 时间范围倒序源文件             | TODO    | INV-06                |
| 无效源文件仍然是合法 JSON       | TODO    | 运行 JSON 语法检查          |
| 签名有效但内容无效的 JWT        | BLOCKED | 需要最终签名身份              |
| Payload 被篡改的签名无效 JWT  | BLOCKED | 最终有效 JWT 生成后再制作       |
| 无效测试执行报告              | BLOCKED | 需要最终 Shape 和 API 测试   |

## 8. API 集成与交付

| 检查项目                      | 状态      | 证据或下一步              |
| ------------------------- | ------- | ------------------- |
| A 组 endpoint 已记录          | PASS    | 本地 Scorpio endpoint |
| 成员3可以访问 endpoint          | BLOCKED | 等待 A 组提供方法          |
| v0.2 有效 Credential 候选包已准备 | TODO    | 完成本地步骤              |
| 最终有效 ES256 包已准备           | BLOCKED | 需要最终签名              |
| 最终无效 JWT 包已准备             | BLOCKED | 需要最终签名              |
| 候选包不包含私钥                  | TODO    | ZIP 前运行安全扫描         |
| 候选文件 hash 已生成             | TODO    | ZIP 前生成             |
| v0.2 ZIP 已生成              | TODO    | 所有本地检查通过后压缩         |
| v0.2 已提交到 `member2` 分支    | TODO    | 安全检查后提交             |
| Compliance API 测试已执行      | BLOCKED | 成员3负责               |
| Compliance API 响应已保存      | BLOCKED | 成员3负责               |
| API 失败层级已分析               | BLOCKED | 需要 API 响应           |
| 修正后已经复测                   | BLOCKED | 需要第一次 API 测试        |

## 9. 当前可以继续执行的步骤

在不等待 A、C、D 回复的情况下，成员2现在可以：

1. 保存四份更新后的说明文档；
2. 检查所有候选 JSON 和 JSON-LD 的语法；
3. 运行未签名一致性检查；
4. 准备无效测试源文件；
5. 确认开发私钥仍然保存在仓库外；
6. 重新生成 v0.2 provisional RS256 JWT；
7. 在本地验证 v0.2 provisional JWT；
8. 根据真实运行结果更新本检查表；
9. 扫描候选目录是否包含私钥；
10. 生成候选文件 SHA-256；
11. 创建候选 ZIP；
12. 将候选文件提交到 `member2` 分支。

## 10. 必须停止的情况

出现以下情况时，不得继续压缩或提交：

* 任意候选 JSON 文件无法解析；
* 未签名一致性检查不是 PASS；
* 任意 JWT 不是三段式；
* 任意 JWT 本地验签失败；
* 候选目录中发现私钥；
* 文档把 provisional RS256 写成最终 ES256。

出现以下情况时，不得开始最终 ES256 签名：

* 最终 Provider DID 尚未确认；
* 公网 DID Document 无法解析；
* 公网公钥与私钥的匹配尚未验证；
* C/D 权威 Shape 和验证契约仍未确定。

## 11. 当前结论

上一版本地开发签名流程已经使用 RS256 通过验证。

v0.2 源文件和配置候选版现在可以继续执行：

* 本地语法检查；
* 一致性检查；
* 无效测试准备；
* provisional JWT 重新生成；
* 本地验签。

最终 ES256 签名和最终 Compliance 就绪状态仍然受到以下事项阻塞：

* A 组最终公网 Provider DID；
* 公网公钥和 Demo 私钥匹配；
* C/D 权威 Shape 和 SHA-256；
* 最终 extra-property severity；
* A 组 endpoint 访问方法。
