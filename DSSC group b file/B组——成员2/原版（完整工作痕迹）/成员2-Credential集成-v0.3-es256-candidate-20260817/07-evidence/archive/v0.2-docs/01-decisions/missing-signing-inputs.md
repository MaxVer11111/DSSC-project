# 最终签名仍缺少的输入

当前状态：`BLOCKED`
更新日期：`2026-08-17`

## 1. 文件目的

本文件记录成员2在生成和验证最终 ES256 Demo Credential 前，仍然缺少的输入。

本文件区分：

* 缺失的密码学签名输入；
* 最终内容验证的前置条件；
* API 集成阻塞项；
* 当前交付范围以外的内容。

## 2. 已知的最终签名目标

以下签名参数已经可以确定：

| 项目               | 目标值                                              | 是否仍然缺失     |
| ---------------- | ------------------------------------------------ | ---------- |
| 签名算法             | ES256                                            | 否          |
| 密钥类型             | EC                                               | 否          |
| 曲线               | P-256                                            | 否          |
| 候选 Provider DID  | `did:web:mp-operations.org`                      | 仍需 A 组最终确认 |
| 目标 kid           | `did:web:mp-operations.org#key-1`                | 否          |
| DID Document URL | `https://mp-operations.org/.well-known/did.json` | 需要发布或恢复解析  |

因此，算法、密钥类型、曲线和目标 `kid` 不能再写成“未知”。

## 3. 仍然缺少的密码学输入

### 3.1 最终 Provider DID 确认

A 组必须确认最终 Provider DID 是否继续采用：

`did:web:mp-operations.org`

如果最终选择其他 DID，所有 Credential、VP、JWT 和 DID 引用都必须统一更新后，才能执行最终签名。

当前状态：`WAITING`

### 3.2 公网可解析的 DID Document

如果继续使用候选 DID，则以下地址必须能够从公网解析：

`https://mp-operations.org/.well-known/did.json`

DID Document 必须是有效 JSON，并且其 `id` 必须与最终 Provider DID 一致。

当前状态：`BLOCKED`

### 3.3 最终 Verification Method

最终 DID Document 必须包含与以下值一致的 verification method：

`did:web:mp-operations.org#key-1`

该 verification method 必须提供可用于 ES256 验签的 EC P-256 公钥。

当前状态：`BLOCKED`

### 3.4 公钥与私钥匹配

DID Document 中发布的公钥必须与成员2最终使用的 A 组 Demo 私钥相匹配。

只知道：

* ES256；
* EC；
* P-256；
* `#key-1`

仍然不够。

还必须验证这确实是同一对公私钥。

当前状态：`BLOCKED`

### 3.5 安全使用 Demo 私钥

最终签名必须通过安全的本地方式使用 A 组 Demo 私钥。

私钥必须：

* 保存在 Git 仓库外；
* 保存在交付 ZIP 外；
* 不打印到日志；
* 不粘贴进 Markdown 报告；
* 不进入任何 Git 历史记录。

当前状态：`MUST BE CONFIRMED BEFORE FINAL SIGNING`

## 4. 已经不再缺少的决定

以下内容不再是完全未知的设计决定：

* VC Data Model：W3C VC Data Model 2.0；
* VC Context：`https://www.w3.org/ns/credentials/v2`；
* Gaia-X Context：`https://w3id.org/gaia-x/development#`；
* Building Energy 候选模型：v0.4；
* 最终目标算法：ES256；
* 最终目标密钥类型：EC；
* 最终目标曲线：P-256；
* 最终目标 kid：`did:web:mp-operations.org#key-1`；
* 当前 VP 组成：LegalPerson VC + ServiceOffering VC。

这些值仍可能作为完整跨组配置的一部分被再次确认，但不能再把它们写成“尚未提供”。

## 5. 最终内容验证的前置条件

以下内容不是密码学签名参数，但最终 Credential 内容不能在缺少这些信息时正式冻结。

### 5.1 唯一权威 Shape

C、D 组必须共同确定一份唯一权威 Shape 文件。

当前状态：`BLOCKED`

### 5.2 权威 Shape 原始文件 SHA-256

C、D 组必须提供或确认该权威 Shape 原始文件字节的 SHA-256。

当前状态：`BLOCKED`

### 5.3 Extra-property Severity

C、D 组必须确认多余属性最终采用：

* `sh:Warning` 并映射为 INAPPLICABLE；或
* `sh:Violation` 并直接拒绝。

当前状态：`BLOCKED`

### 5.4 LegalPerson 最终字段映射

当历史示例存在不同属性名时，必须由最终 LegalPerson 模型或 Shape 决定权威字段。

当前状态：`WAITING`

## 6. 不属于签名输入的集成阻塞项

当前记录的 A 组 endpoint 为：

`https://scorpio-provider.127.0.0.1.nip.io/ngsi-ld/v1/entities/urn:ngsi-ld:Building:BLD-001`

该域名解析到调用者自己的 `127.0.0.1`，因此成员3还需要 A 组提供访问或复现方法。

它会阻塞跨电脑 API 测试，但不会决定 ES256 签名的密码学内容。

当前状态：`BLOCKED FOR INTEGRATION`

## 7. 当前交付范围以外的内容

以下内容不是当前缺失的签名输入：

* T&C Credential；
* Mock LRN Credential。

成员2当前开发 VP 只包含：

* LegalPerson VC；
* ServiceOffering VC。

只有最终 Compliance API 契约或项目负责人明确要求时，才重新考虑加入 T&C 和 Mock LRN。

预留 Mock LRN Credential ID 为：

`urn:dssc:credential:lrn:demo-energy-001`

预留 ID 不代表该 Credential 已经签发。

## 8. 开发签名与最终签名分离

本地开发流程使用 RSA 开发密钥和 RS256。

它可以继续用于：

* 测试 JWT 结构；
* 测试 JWT 生成脚本；
* 测试验签脚本；
* 生成 provisional 本地证据。

本地 RS256 验签成功，不代表最终 ES256 所需输入已经齐全。

## 9. 开始最终签名的条件

只有以下条件全部满足后，才能开始最终 ES256 签名：

* [ ] A 组确认最终 Provider DID；
* [ ] 最终公网 DID Document 可以正常解析；
* [ ] DID Document 中存在最终 `kid`；
* [ ] 公网密钥确认为 EC P-256；
* [ ] 公网密钥与最终 Demo 私钥匹配；
* [ ] 最终 Credential 源内容已经冻结；
* [ ] C/D 权威验证契约已经确定；
* [ ] 有效候选内容通过所需验证；
* [ ] 私钥仍然保存在 Git 仓库外。

在这些条件全部满足前，新生成的 JWT 必须继续标记为 `provisional` 或 `candidate`，不能标记为 `final`。
