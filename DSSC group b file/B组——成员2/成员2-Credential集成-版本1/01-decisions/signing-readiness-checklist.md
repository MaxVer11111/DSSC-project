# Credential签名前准备检查表

## 1. 当前工作状态

- 未签名LegalPerson基础结构：已完成
- LegalPerson合规字段：未完成
- 未签名ServiceOffering基础结构：已完成
- ServiceOffering合规字段：未完成
- Dataset Metadata：已完成
- 未签名文件一致性检查：PASS
- 检查报告：`07-evidence/unsigned-consistency-report.md`
- 当前是否允许正式签名：否
- 原因：Schema、API、DID、kid、算法和必要VC尚未全部确认

---

## 2. 已经完成的数据准备

| 检查项目 | 当前值 | 状态 |
|---|---|---|
| Provider名称 | `Energy Data Provider Ltd.` | READY |
| Provider DID | `did:web:mp-operations.org` | PROVISIONAL，实际DNS解析失败，不可用于正式签名 |
| LegalPerson主体ID | `did:web:mp-operations.org` | PROVISIONAL |
| LegalPerson Credential ID | `urn:dssc:credential:legal-person:mp-operations:v0.1` | READY |
| ServiceOffering主体ID | `urn:dssc:service-offering:building-energy-hourly-v1` | PROVISIONAL |
| ServiceOffering Credential ID | `urn:dssc:credential:service-offering:building-energy-hourly-v1:v0.1` | READY |
| Dataset canonical URI | `urn:dssc:dataset:building-energy-hourly-v1` | PROVISIONAL |
| Dataset Endpoint | A组Scorpio实际Endpoint | READY FOR LOCAL DEMO |
| Response Media Type | `application/ld+json` | READY，等待D组Shapes适配 |
| LegalPerson与providedBy关系 | 完全一致 | PASS |
| ServiceOffering与Dataset关系 | 完全一致 | PASS |
| 未签名一致性报告 | 已生成 | PASS |

状态说明：

- `READY`：当前已经可以使用；
- `PROVISIONAL`：当前暂定使用，但仍需负责人正式确认；
- `BLOCKED`：缺少必要材料，不能继续；
- `NOT REQUIRED`：项目明确不需要。

---

## 3. Schema和验证规则

| 必须确认的内容 | 当前值 | 当前状态 | 需要谁确认 |
|---|---|---|---|
| Gaia-X ontology/schema版本 | 未确认 | BLOCKED | 组长/项目负责人 |
| VC Data Model版本 | 当前草稿使用v2 | PROVISIONAL | 组长/成员3 |
| Gaia-X Context | 当前使用`https://w3id.org/gaia-x/development#` | PROVISIONAL | 组长/成员3 |
| LegalPerson Shapes版本 | 未确认 | BLOCKED | 组长/成员3 |
| ServiceOffering Shapes版本 | 未确认 | BLOCKED | 组长/成员3 |
| Dataset Shapes | D组最新版本 | PROVISIONAL | D组 |
| 当前D Shapes SHA-256 | `17DACE38CB949796D3BDEF0D5BA3002763A5FAC84FF56650F886CDCF8E6AE53D` | PROVISIONAL | D组 |
| Format冲突 | A为`application/ld+json`，D要求`application/json` | BLOCKED | D组/组长 |
| 修改后Shapes SHA-256 | 尚未生成 | BLOCKED | D组 |

---

## 4. Compliance API信息

| 必须确认的内容 | 当前值 | 状态 | 作用 |
|---|---|---|---|
| Compliance API环境 | `development` | READY | 与仓库成功Demo保持一致 |
| Compliance API Endpoint | `https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance` | READY | VP-JWT提交地址 |
| HTTP Method | `POST` | READY | API请求方法 |
| Request Content-Type | `application/vp+jwt` | READY | 声明请求体是VP-JWT |
| Request Body | 原始VP-JWT字符串 | READY | 不使用JSON包装 |
| 必需查询参数 | `vcid` | READY | 指定Compliance Credential ID |
| 默认vcid | `https://gaia-x.eu/.well-known/compliance-credential.jwt` | READY FOR DEMO | 仓库Demo使用值 |
| JWT Header `typ` | VP使用`vp+jwt` | READY FOR DEMO | 声明JWT为VP |
| JWT Header `cty` | VP使用`vp` | READY FOR DEMO | 声明内部内容为VP |
| Bearer Token | 仓库Demo未使用 | READY FOR DEMO | 当前测试脚本不添加Authorization |
| 成功HTTP状态码 | `201` | READY | 表示成功签发Compliance Credential |
| 成功响应类型 | `application/vc+jwt` | READY | 返回Compliance VC-JWT |
| 成员3测试环境 | 尚未确认 | BLOCKED | 确定由谁、在哪里正式执行测试 |

---

## 5. DID和签名材料


| 必须确认的内容 | 当前值 | 状态 | 作用 |
|---|---|---|---|
| Issuer DID | `did:web:mp-operations.org` | BLOCKED | 当前域名无法解析，只能作为暂定标识 |
| Holder DID | 未提供 | BLOCKED | 标识VP持有者和提交者 |
| DID Document URL | `https://mp-operations.org/.well-known/did.json` | FAIL | DNS无法解析 |
| DID Document | 无法取得 | BLOCKED | 无法获得公开验证密钥 |
| DID解析实际测试 | `DNS_RESOLUTION_FAILED` | FAIL | 已保存实际测试证据 |
| `kid` | 无法确认 | BLOCKED | 没有DID Document可供查找 |
| 签名算法`alg` | 未提供 | BLOCKED | 不能从示例擅自选择 |
| 公钥 | 未提供 | BLOCKED | 无法验证签名 |
| 私钥保管人 | 未确认 | BLOCKED | 尚未确定谁执行签名 |
| DID、公钥、私钥是否匹配 | 无法验证 | BLOCKED | 缺少真实签名材料 |
| 私钥是否上传GitHub | 否 | READY | 私钥禁止进入仓库 |

安全要求：

1. 私钥不得写入本检查表；
2. 私钥不得通过微信群或普通聊天发送；
3. 私钥不得提交到GitHub；
4. 检查表只记录“谁保管私钥”，不记录私钥内容；
5. `kid`、DID Document、公钥和私钥必须属于同一套密钥材料。

---

## 6. LegalPerson缺失材料

| 内容 | 当前状态 | 是否阻塞最终合规 |
|---|---|---|
| Legal Name | 已有 | 否 |
| Legal Registration Number | 缺失 | 是 |
| LRN Credential | 缺失 | 是 |
| Legal Address | 缺失 | 可能阻塞 |
| Headquarters Address | 缺失 | 可能阻塞 |
| `validUntil` | 缺失 | 待确认 |
| 正式Issuer | 暂定 | 是 |
| 正式签名 | 尚未完成 | 是 |

---

## 7. ServiceOffering缺失材料

| 内容 | 当前状态 | 是否阻塞最终合规 |
|---|---|---|
| ServiceOffering ID | 暂定完成 | 需要正式确认 |
| Service名称 | 已有 | 否 |
| Service描述 | 已有 | 否 |
| `gx:providedBy` | 已有并通过一致性检查 | 否 |
| `gx:aggregationOf` | 已有并通过一致性检查 | 否 |
| `gx:dataAccountExport.requestType` | 候选值为`API` | 等待Shapes确认 |
| `gx:dataAccountExport.accessType` | 候选值为`digital` | 等待Shapes确认 |
| `gx:dataAccountExport.formatType` | 候选值为`application/ld+json` | 等待D组解决Format冲突 |
| `gx:termsAndConditions.URL` | 缺失 | 是 |
| `gx:termsAndConditions.hash` | 缺失 | 是 |
| `gx:policy` | 未确认 | 可能阻塞 |
| `validUntil` | 未确认 | 待确认 |
| ServiceOffering提交方式 | 未确认 | 是 |
| 正式签名 | 尚未完成 | 是 |

---

## 8. VP必须包含哪些VC

| Credential类型 | 当前是否已有 | 是否进入仓库成功VP | 项目当前状态 |
|---|---|---|---|
| LegalPerson | 有未签名基础草稿 | 是 | 缺注册号和地址等合规字段 |
| Issuer / Terms and Conditions | 项目主体没有 | 是 | BLOCKED |
| LegalRegistrationNumber | 项目主体没有 | 是 | BLOCKED |
| ServiceOffering | 有未签名基础草稿 | 不在仓库的参与者成功VP中 | 是否单独提交或加入其他VP待确认 |
| Dataset Metadata | 已有未签名Metadata | 不在仓库的参与者成功VP中 | 是否签发为VC待确认 |
| Compliance Credential | 仓库有官方样例 | 这是API成功后返回的结果 | 不是请求前自己生成 |

---

## 9. 正式签名前的放行条件

只有下面项目全部完成，才允许生成正式VC-JWT：

- [ ] 组长确认Provider DID
- [ ] 组长确认ServiceOffering ID
- [ ] 组长确认Dataset canonical URI
- [ ] 确认Gaia-X ontology/schema版本
- [ ] 确认LegalPerson Shapes
- [ ] 确认ServiceOffering Shapes
- [ ] D组解决`application/ld+json`与`application/json`冲突
- [ ] D组提供修改后的Shapes SHA-256
- [ ] 确认Compliance API Endpoint
- [ ] 确认Compliance API Content-Type
- [ ] 确认VP中必须包含哪些VC
- [ ] 获得或确认LRN Credential
- [ ] 获得或确认Terms and Conditions Credential
- [ ] 确认Issuer DID
- [ ] 确认Holder DID
- [ ] 获得可用DID Document
- [ ] 确认kid
- [ ] 确认签名算法alg
- [ ] 确认私钥保管人
- [ ] 验证私钥与DID Document公钥匹配
- [ ] 重新运行未签名一致性检查并得到PASS

当前结论：

`NOT READY TO SIGN`

---

## 10. 开发阶段本地签名通道

为了在等待 A 组正式 DID 材料期间继续推进，允许使用以下开发配置：

| 项目 | 开发值 | 限制 |
|---|---|---|
| Issuer / Holder DID | `did:web:mp-operations.org` | DNS不可解析，仅作占位 |
| `kid` | `did:web:mp-operations.org#dev-key-1` | 只对应本地临时公钥 |
| `alg` | `RS256` | 用于复现仓库成功样例的签名流程 |
| 私钥位置 | `%LOCALAPPDATA%\DSSC-Credential-Dev\dev-rsa-private.jwk` | 仓库外保存，禁止上传 |
| 输出目录 | `05-signed/provisional/` | 不得移动到`valid/` |
| Compliance预期 | `FAIL / NOT SUBMITTED` | 占位DID不可公开解析 |

开发通道只证明本地签名、VP组装和公钥验签流程能够运行，不解除上面的
正式签名放行条件。正式 DID、`kid` 和密钥到位后，必须重新签发全部 JWT。




## 11. 开发签名流程

| 检查项目                      | 结果      | 证据                                                          |
| ------------------------- | ------- | ----------------------------------------------------------- |
| 已生成开发用RSA密钥对              | PASS    | 私钥保存在仓库外部                                                   |
| 已生成公开开发用DID Document      | PASS    | `07-evidence/development-did-document.unpublished.json`     |
| 已生成LegalPerson VC-JWT     | PASS    | `05-signed/provisional/legal-person.provisional.vc.jwt`     |
| 已生成ServiceOffering VC-JWT | PASS    | `05-signed/provisional/service-offering.provisional.vc.jwt` |
| 已生成VP-JWT                 | PASS    | `05-signed/provisional/presentation.provisional.vp.jwt`     |
| JWT分段检查                   | PASS    | 所有JWT均包含三个分段                                                |
| 签名算法检查                    | PASS    | `RS256`                                                     |
| 本地`kid`匹配检查               | PASS    | `did:web:mp-operations.org#dev-key-1`                       |
| 本地签名验证                    | PASS    | 三个JWT的签名均已通过验证                                              |
| 公共DID解析                   | FAIL    | 占位域名无法解析                                                    |
| 最终Compliance准备状态          | BLOCKED | 正在等待正式身份材料                                                  |

## 结论

本地开发签名流程已经完成。

生成的JWT在结构和密码学签名方面均有效，并且能够通过尚未公开发布的本地开发DID Document完成验证。

但是，这些JWT目前还不是最终满足Compliance要求的有效凭证。原因是当前DID无法通过公共网络解析，并且正式的LegalPerson、LegalRegistrationNumber以及Terms and Conditions材料尚未提供。
