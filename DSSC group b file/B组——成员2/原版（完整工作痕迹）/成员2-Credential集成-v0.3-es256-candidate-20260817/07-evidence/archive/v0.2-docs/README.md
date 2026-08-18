# 成员2 Credential 集成说明

## 1. 项目目的

本目录保存 DSSC Demo 项目中成员2负责的 Credential 集成工作。

成员2当前负责：

* 准备一份 LegalPerson Verifiable Credential；
* 准备一份 ServiceOffering Verifiable Credential；
* 生成一份包含上述两份 Credential 的 Verifiable Presentation；
* 检查各文件之间的 ID、Provider、Dataset 和配置是否一致；
* 生成并在本地验证开发版 JWT；
* 准备有效和无效测试输入；
* 将 Credential、VP-JWT 和验证证据交给成员3执行 Compliance API 测试。

本目录当前状态为：

`v0.2 candidate`

它是候选开发版，不是最终 Compliance 交付版。

## 2. 当前总体状态

| 项目                   | 当前状态                                      |
| -------------------- | ----------------------------------------- |
| 配置版本                 | v0.2 candidate                            |
| VC Data Model        | W3C Verifiable Credentials Data Model 2.0 |
| Gaia-X Context       | development                               |
| Building Energy 语义模型 | v0.4                                      |
| LegalPerson 源文件      | 候选版已更新                                    |
| ServiceOffering 源文件  | 候选版已更新                                    |
| Dataset Metadata     | 候选版已更新                                    |
| 当前 VP 组成             | LegalPerson VC + ServiceOffering VC       |
| 上一版 v0.1 本地开发验签      | PASS                                      |
| v0.2 未签名一致性检查        | TODO                                      |
| v0.2 开发 JWT 重新生成     | TODO                                      |
| v0.2 本地密码学验签         | TODO                                      |
| 公网 DID 解析            | BLOCKED                                   |
| 最终 ES256 签名          | BLOCKED                                   |
| 最终 SHACL 验证          | BLOCKED                                   |
| 最终 Compliance 就绪状态   | BLOCKED                                   |

当前目录中的 JWT 文件是从上一份开发验签通过版本复制过来的。

在重新执行 v0.2 的 JWT 生成和验签脚本前，不能把这些旧 JWT 当作已经更新完成的 v0.2 JWT。

## 3. 当前主要标识符

| 项目                             | 当前值                                                   |
| ------------------------------ | ----------------------------------------------------- |
| 候选 Provider DID                | `did:web:mp-operations.org`                           |
| Provider 名称                    | `Energy Data Provider Ltd.`                           |
| Demo Legal Registration Number | `DEMO-ENERGY-001`                                     |
| ServiceOffering ID             | `urn:dssc:service-offering:building-energy-hourly-v1` |
| Dataset canonical URI          | `urn:dssc:dataset:building-energy-hourly-v1`          |
| 预留 Mock LRN Credential ID      | `urn:dssc:credential:lrn:demo-energy-001`             |
| 最终目标 kid                       | `did:web:mp-operations.org#key-1`                     |

Mock LRN Credential ID 当前只是预留 ID。

这不代表 Mock LRN Credential 已经签发，也不代表它已经加入当前 VP。

## 4. LegalPerson Demo 身份事实

v0.2 候选版目前使用以下 Demo 身份事实：

| 身份事实                                          | 当前值                         |
| --------------------------------------------- | --------------------------- |
| Legal name                                    | `Energy Data Provider Ltd.` |
| Demo Legal Registration Number                | `DEMO-ENERGY-001`           |
| Legal Address country code                    | `CN`                        |
| Legal Address country subdivision code        | `CN-GD`                     |
| Headquarters Address country code             | `CN`                        |
| Headquarters Address country subdivision code | `CN-GD`                     |
| validFrom                                     | `2026-08-16T00:00:00Z`      |
| validUntil                                    | `2027-08-16T00:00:00Z`      |

上述内容是已经确定的 Demo 身份事实。

但是，地址和登记号在最终 JSON-LD 中应该使用哪个准确属性名，仍然必须以最终 LegalPerson 模型或 Shape 为准。

在存在 `headquarterAddress`、`headquartersAddress` 等不同历史写法时，成员2暂时不自行猜测最终字段。

## 5. 语义模型配置

v0.2 候选版当前使用：

| 项目                         | 当前值                                                                |
| -------------------------- | ------------------------------------------------------------------ |
| VC Context                 | `https://www.w3.org/ns/credentials/v2`                             |
| Gaia-X Context             | `https://w3id.org/gaia-x/development#`                             |
| Building Energy 模型版本       | v0.4                                                               |
| Model IRI                  | `https://w3id.org/dssc-demo/building-energy/v0.4`                  |
| Profile                    | `dssc-building-energy-metadata-v0.4`                               |
| Context SHA-256            | `F46D3056239CC1CB7D678707E749B33E336564E5FCE23FFCCCD528EAE6CBE391` |
| Canonical example SHA-256  | `9ACC287AE274E549BECD15852231B325C43E1DBDDC14E9F2459F4C490420F239` |
| Dataset Metadata format    | `application/json`                                                 |
| Endpoint responseMediaType | `application/ld+json`                                              |

Dataset Metadata 的 `format` 和 A 组 endpoint 的 `responseMediaType` 描述的是两个不同对象：

* `application/json` 是当前 C/D 语义验证契约中的 Dataset Metadata 格式；
* `application/ld+json` 是 A 组 Scorpio endpoint 返回数据的格式。

这两个字段必须分别保存和检查，不能再强制要求它们相同。

## 6. Shape 当前状态

当前记录了三组不同来源的 Shape hash：

| 来源                 | SHA-256                                                            | 状态          |
| ------------------ | ------------------------------------------------------------------ | ----------- |
| C 组当前 v0.4 Shape   | `A556039C0EC3030A9C4273C62A787E448B8869F7648E948663E10D3FE007CBDA` | CANDIDATE   |
| D 组当前 main 分支文件    | `E5F150D7DBE338FCBB7B020585CC83713DE1FDB6B1A4BE393BE1BEF47895411E` | CANDIDATE   |
| D 组 README 记录值     | `17DACE38CB949796D3BDEF0D5BA3002763A5FAC84FF56650F886CDCF8E6AE53D` | RECORD ONLY |
| 最终权威 Shape         | 尚未选定                                                               | WAITING     |
| 最终权威 Shape SHA-256 | 尚未提供                                                               | WAITING     |

当前不能把上述任意一个 hash 写成最终权威 Shape hash。

C、D 组仍然需要共同确认：

* 唯一权威 Shape 文件；
* 权威仓库路径；
* 原始文件字节的 SHA-256；
* 计算原始文件 hash 时采用的换行格式；
* 多余属性最终采用 `sh:Warning` 还是 `sh:Violation`；
* 多余属性最终导致 INAPPLICABLE 还是直接拒绝。

## 7. 开发签名与最终签名

### 7.1 当前开发签名

当前 provisional 开发 JWT 使用：

| 项目           | 当前值                                   |
| ------------ | ------------------------------------- |
| 签名算法         | RS256                                 |
| 密钥类型         | 本地 RSA 开发密钥                           |
| 开发 kid       | `did:web:mp-operations.org#dev-key-1` |
| 私钥位置         | 仓库外部                                  |
| DID Document | 本地未发布的开发 DID Document                 |
| 使用目的         | 验证 JWT 结构和本地密码学签名流程                   |

当前 RS256 JWT 只是开发产物。

不能将它描述成最终 A 组 ES256 Demo Credential。

### 7.2 最终 Demo 签名目标

最终 Demo 目标为：

| 项目               | 目标值                                              |
| ---------------- | ------------------------------------------------ |
| 签名算法             | ES256                                            |
| 密钥类型             | EC                                               |
| 曲线               | P-256                                            |
| 候选 Provider DID  | `did:web:mp-operations.org`                      |
| 目标 kid           | `did:web:mp-operations.org#key-1`                |
| DID Document URL | `https://mp-operations.org/.well-known/did.json` |

只有满足以下条件后，才能执行最终 ES256 签名：

1. A 组确认最终 Provider DID；
2. 公网 DID Document 可以正常解析；
3. DID Document 中存在最终 `kid`；
4. DID Document 中的 EC P-256 公钥与 A 组 Demo 私钥匹配；
5. 最终 Credential 内容和验证契约已经冻结。

不能只把 JWT Header 中的 `RS256` 改成 `ES256`。

RS256 和 ES256 使用不同的密钥与签名算法，最终 JWT 必须使用正确的 EC P-256 私钥重新签名。

## 8. 当前 VP 交付范围

当前开发 VP 只包含：

1. 一份 LegalPerson VC；
2. 一份 ServiceOffering VC。

T&C Credential 和 Mock LRN Credential 不属于成员2当前两份 VC 开发 VP 的交付范围。

它们当前不作为阻塞项。

只有出现以下情况时才另行增加：

* 最终 Compliance API 契约明确要求；
* 项目负责人明确扩大成员2的交付范围。

## 9. A 组 Endpoint

当前记录的 A 组 endpoint 为：

`https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001`

该域名会解析到调用者自己电脑的 `127.0.0.1`。

因此，成员3不能直接从另一台电脑访问 A 组本地 Scorpio 服务，除非 A 组提供以下任意一种方式：

* 完整的本地部署和复现步骤；
* A 组环境的远程访问方法；
* 共享测试环境；
* 公网可访问的新 endpoint。

成员3的 endpoint 访问方法仍然是集成阻塞项。

## 10. 目录结构

```text
00-original/
01-decisions/
02-config/
03-normalized-metadata/
04-credential-source/
05-signed/
06-invalid-tests/
07-evidence/
08-logs/
scripts/
README.md
```

各目录用途：

* `01-decisions`：保存身份事实、候选决定和就绪状态；
* `02-config`：保存机器可读取的候选配置；
* `03-normalized-metadata`：保存规范化 Dataset Metadata；
* `04-credential-source`：保存有效的未签名 Credential 源文件；
* `05-signed`：保存 provisional 开发 JWT；
* `06-invalid-tests`：保存故意构造的无效测试源文件和后续无效 JWT；
* `07-evidence`：保存一致性检查、文件 hash 和验签证据；
* `08-logs`：保存开发执行日志；
* `scripts`：保存一致性、JWT 生成和验签脚本。

## 11. 开发命令

运行未签名一致性检查：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\check-consistency.ps1"
```

重新生成 provisional 开发 JWT：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\build-provisional-jwts.ps1"
```

验证 provisional 开发 JWT：

```powershell
powershell -NoProfile -ExecutionPolicy Bypass `
  -File ".\scripts\verify-provisional-jwts.ps1"
```

本地 RS256 验签成功只能证明：

* JWT 结构正确；
* 本地开发密钥能够完成签名；
* 本地公钥能够验证对应签名。

它不能证明：

* 公网 DID 能够解析；
* 最终 ES256 签名有效；
* 最终 SHACL 验证通过；
* 最终 Compliance API 接受该 VP。

## 12. 当前外部阻塞项

最终交付仍然被以下事项阻塞：

1. A 组确认最终 Provider DID；
2. 发布公网可解析的 `did.json`；
3. 确认公网公钥与 Demo 私钥匹配；
4. C/D 确认唯一权威 Shape；
5. C/D 确认权威 Shape 原始字节 SHA-256；
6. C/D 确认 extra-property severity；
7. 使用最终 Shape 完成验证；
8. A 组提供成员3访问 endpoint 的方法；
9. 成员3完成最终 Compliance API 测试。

## 13. 安全要求

* 绝对不能把私钥提交到 GitHub。
* 绝对不能把开发 RSA 私钥放入 ZIP。
* 绝对不能把最终 A 组 EC 私钥放入 ZIP。
* 公共 DID Document 和公钥 JWK 可以提交。
* 提交 Demo JWT 前，应确认其中不包含不应该公开的内容。
* 压缩和 Git 提交前必须检查所有文件。

## 14. 当前结论

成员2上一版 v0.1 本地开发签名流程已经通过验证。

目前已经准备 v0.2 Credential 和 Metadata 候选内容，但仍然需要依次完成：

1. JSON 和 JSON-LD 语法检查；
2. 未签名一致性检查；
3. 无效测试源文件准备；
4. v0.2 provisional RS256 JWT 重新生成；
5. v0.2 本地密码学验签。

上述本地步骤全部通过后，可以将 v0.2 候选版作为开发检查点提交到 `member2` 分支。

最终 ES256 签名和最终 Compliance 就绪状态，仍然需要等待 A 组公网 DID 以及 C/D 最终验证契约。
