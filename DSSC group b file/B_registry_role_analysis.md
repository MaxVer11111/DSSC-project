# B 组 — Gaia-X Registry Role Analysis
 
> 分析文件：  
> - `B_compliance_api_demo.md`
> - `failure_in_registry.md`
> - `legal-person-minimal.jsonld`

---

## 1. 任务范围和关键分析

本文件分析 Gaia-X Registry 在 Compliance 验证过程中的作用，重点回答：

1. Registry 在验证过程中提供什么；
2. shapes、schemas、trust anchors、valid / revoked keys 分别负责什么；
3. Task 2 的 Compliance API 测试实际失败在哪一层；
4. 哪些错误是 API 实际返回的，哪些只是后续 Registry 层的理论推断。

**说明：Task 2 当前实测主要失败在 JWT decode / JWT header 层，并未真正进入 SHACL shapes 或 Trust Anchor validation。因此，本文会区分 actual API errors 和 inferred Registry errors，避免把 Registry 前置层错误误写成 Registry shape 或 trust anchor 导致的错误。**

---

## 2. Demo Results Used in This Analysis

Demo 提供了一个最小 LegalPerson credential payload：`legal-person-minimal.jsonld`，并基于它设计了两个错误变体：

| Credential | Purpose |
|---|---|
| `legal-person-minimal.jsonld` | 最小 LegalPerson VC payload，模拟 Gaia-X participant identity |
| missing-field variant | 删除 mandatory fields，用于理论测试 LegalPerson SHACL shape |
| format-error variant | 修改 context、date、countryCode 等格式，用于理论测试 JSON-LD / Address shape |

Demo 使用 Compliance API 进行测试，得到以下实际结果：

| Test | Actual API Result | Meaning |
|---|---|---|
| `application/json` + raw JSON-LD | `500 stream is not readable` | API 不接受普通 JSON 提交 |
| `application/vp+jwt` + raw JSON-LD | `400 not a valid JWT` | API 要求 VP-JWT，不接受裸 JSON-LD |
| pseudo JWT | `400 iss header ... missing` | 伪 JWT 通过 decode，但缺少 issuer DID |

Demo 的核心发现是：

**Gaia-X Compliance API 不是一个直接接收 JSON-LD 的 SHACL validator。它要求输入为签名后的 VP-JWT。当前测试只实际到达 JWT decode / JWT header 层，尚未进入 SHACL、Trust Anchor、T&C 或 Notary validation。**

---

## 3. What Registry Provides During Compliance Validation

Gaia-X Registry 可以理解为 Compliance Service 的规则来源和信任来源。它主要提供以下内容：

| Registry Component | What It Provides | Role in Compliance Validation |
|---|---|---|
| SHACL shapes | LegalPerson shape、Address shape、ServiceOffering shape、T&C shape | 检查 credential 字段是否齐全、格式是否正确、cardinality 是否满足要求 |
| schemas / ontology | `gx:LegalPerson`、`gx:Address`、`gx:registrationNumber` 等语义定义 | 解释 JSON-LD 中的字段和类型是什么意思 |
| trust anchors | accepted CA / TSP / Notary / registrationNumberIssuer roots | 判断 issuer、certificate chain 或 registration number source 是否可信 |
| valid public keys | 当前仍被接受的 signing keys / certificates | 用于验证 VP-JWT / VC-JWT 的签名是否可信 |
| revoked keys / anchors | 被撤销的 keys、certificates、trust anchors | 防止曾经可信但已失效的 key 或 anchor 继续被使用 |
| T&C rules / hash | Gaia-X Terms and Conditions 相关规则 | 判断 issuer 是否接受 Gaia-X 条款 |
| Notary / trusted data sources | registrationNumberIssuer、Notary、LEI / VAT / EORI 等来源 | 验证 LegalPerson registration number 是否真实可信 |

**Registry 不是单纯的文件存储，而是 Compliance Service 判断“结构是否合规”和“信任链是否有效”的依据。**

**但并不是所有 API 错误都直接来自 Registry。JWT decode、Content-Type、body 是否为 VP-JWT 等属于 Registry 前置层；Registry 主要参与后续 SHACL、Trust Anchor、valid / revoked key、T&C 和 Notary 等验证阶段。**

---

## 4. Gaia-X Compliance Validation Chain

结合 Demo 的测试结果，可以将 Gaia-X Compliance 验证链理解为：

```text
[1] JWT decode
        ↓
[2] JWT header check: alg / typ / iss / kid / x5c
        ↓
[3] DID resolution and public key lookup
        ↓
[4] Signature validation
        ↓
[5] Trust Anchor and valid / revoked key validation
        ↓
[6] VP structure validation
        ↓
[7] VC content validation using SHACL shapes
        ↓
[8] T&C validation
        ↓
[9] Registration Number / Notary validation
        ↓
Compliance Credential issued or validation error returned
```

Demo 当前实际到达的层级如下：

| Layer | Reached in Demo? | Explanation |
|---|---|---|
| [1] JWT decode | Yes, failed | Raw JSON-LD is not a three-part VP-JWT |
| [2] JWT header check | Yes, failed for pseudo JWT | Missing `iss`, so issuer DID cannot be identified |
| [3] DID resolution | No | Requires valid `iss` / DID |
| [4] Signature validation | No | Requires signed VP-JWT |
| [5] Trust Anchor / key status validation | No | Requires public key and certificate chain |
| [6] VP structure validation | No | Requires valid Verifiable Presentation |
| [7] SHACL validation | No | Requires previous layers to pass |
| [8] T&C validation | No | Requires Issuer T&C Credential |
| [9] Notary validation | No | Requires Legal Registration Number Credential |

**因此，demo的实际错误发生在Registry SHACL shapes and Trust Anchor validation之前。Registry层级的错误主要警示了未来可能遇到的错误。**

---

## 5. 实际 API 错误与推断的 Registry 错误

为避免过度推断，本报告将错误分为两类：

- **实际 API 错误**：Demo 中 Compliance API 实际返回的错误；
- **推断的 Registry 错误**：如果 credential 通过 JWT / DID / signature 层并进入基于 Registry 的验证，后续可能出现的错误。

| 错误 / 问题 | 实际或推断 | 验证层级 | 与 Registry 的关系 | 说明 |
|---|---|---|---|---|
| `not a valid JWT` | 实际 | JWT decode | Registry 未直接参与 | 提交的 body 是裸 JSON-LD，而不是 VP-JWT |
| `iss header referencing the issuer's DID is missing` | 实际 | JWT header | 间接相关 | 缺少 issuer DID，因此无法开始 DID / key resolution |
| DID 无法解析 | 推断 | DID resolution | 间接相关 | 示例 DID `did:web:energy-provider.example.org` 只是占位符 |
| 缺少签名 / 签名无效 | 推断 | Signature validation | 与 public key / trust anchor 相关 | 当前 payload 不是已签名的 VP-JWT |
| 缺少可信 certificate chain | 推断 | Trust Anchor validation | Trust anchors / valid keys | 未提供 X.509 / TSP chain |
| public key 已撤销 | 推断 | Key status validation | Revoked keys | 即使签名在数学上有效，已撤销的 key 也不应被信任 |
| trust anchor 已撤销 | 推断 | Trust Anchor validation | Revoked anchors | 已撤销的 anchor 会使 trust chain 失效 |
| 缺少 `gx:registrationNumber` | 推断 | SHACL validation | LegalPerson shape | 如果进入 SHACL 验证，missing-field variant 会触发此错误 |
| 缺少 `gx:headquartersAddress` | 推断 | SHACL validation | LegalPerson / Address shape | 如果进入 SHACL 验证，missing-field variant 会触发此错误 |
| 缺少 `gx:legalAddress` | 推断 | SHACL validation | LegalPerson / Address shape | 如果进入 SHACL 验证，missing-field variant 会触发此错误 |
| `countryCode = "China"` 无效 | 推断 | SHACL validation | Address shape | format-error variant 可能违反 Address shape |
| `@context` 无效 | 推断 | JSON-LD processing / schema | Ontology / context | 错误的 context 可能导致 RDF graph 无法构建 |
| 缺少 T&C VC | 推断 | T&C validation | T&C shape / hash | 最小 LegalPerson payload 不包含 Issuer T&C Credential |
| registration number 无法验证 | 推断 | Notary validation | registrationNumberIssuer / trusted data sources | 示例 registration number 未经过真实的 Notary / LRN credential 验证 |

**本节结论：`not a valid JWT` 和 `missing iss` 是实际 API 错误，但它们属于 Registry 前置层错误。LegalPerson shape、Address shape、Trust Anchor、T&C、Notary、valid / revoked key 相关错误目前都只是对后续错误的推断。**

---

## 5.1 对问题的直接回答：能否确定是哪些 Registry shapes 或 trust anchors 导致 API 失败

根据当前 Demo 的结果，答案是：

**已观察到的 API 失败并非由任何 Registry SHACL shape 或 Trust Anchor 实际导致，因为当前测试尚未进入 Registry 层验证。**

实际观察到的错误如下：

| 实际 API 错误 | 是否到达 Registry shapes / trust anchors？ | 说明 |
|---|---|---|
| `not a valid JWT` | 否 | 提交的是裸 JSON-LD 而不是 VP-JWT，因此 payload 在 JWT decode 阶段失败 |
| `iss header referencing the issuer's DID is missing` | 否 | pseudo JWT 虽然通过 decode，但在 DID / signature / Trust Anchor 验证之前的 JWT header validation 阶段失败 |

因此，对于当前测试，无法将任何实际的 Registry shape 或 trust anchor 确定为失败的直接原因。

不过，Registry 分析仍然有意义，因为提交有效且已签名的 VP-JWT 后，Compliance Service 会在后续层级使用 Registry 提供的组件：

| 后续验证层级 | 将使用的 Registry 组件 | 可能出现的错误 |
|---|---|---|
| SHACL validation | LegalPerson shape / Address shape | 缺少 mandatory fields、countryCode 无效 |
| Trust validation | Trust Anchors / valid keys / revoked keys | 缺少可信 certificate chain、key 已撤销、anchor 已撤销 |
| T&C validation | T&C shape / hash | 缺少 Issuer T&C Credential |
| Registration validation | registrationNumberIssuer / Notary | registration number 无法验证 |

**简而言之，Demo 出现的是 Registry 前置层失败，而不是实际的 Registry 层失败。因此，Task 3 会说明这一限制，并分析后续验证层级中哪些 Registry 组件会发挥作用。**

---

## 6. Credential 层面的 Registry 分析

Demo 中的三个 credential case 可以对应如下：

| Credential Case | Demo 中的实际失败 | 如果到达 Registry 验证层 |
|---|---|---|
| 正确版本：`legal-person-minimal.jsonld` | 由于是裸 JSON-LD 而不是 VP-JWT，因此在 JWT decode 阶段失败 | 基础 LegalPerson SHACL 可能通过，但由于缺少 signature、certificate chain、T&C VC 和 LRN credential，Trust Anchor、T&C、Notary validation 仍会失败 |
| Missing-field variant | 同样在 JWT decode 阶段失败 | LegalPerson shape 可能会针对缺少 `gx:registrationNumber`、`gx:headquartersAddress`、`gx:legalAddress` 报告 `sh:minCount` violations |
| Format-error variant | 同样在 JWT decode 阶段失败 | 无效的 `@context` 可能在 JSON-LD processing 阶段失败；无效的 `countryCode = "China"` 可能无法通过 Address shape validation |

**关键点：三个 credentials 当前都在同一个 Registry 前置 JWT 层失败。只有提交有效且已签名的 VP-JWT，并且验证过程到达 JSON-LD / SHACL / Registry 层后，它们之间的差异才会体现出来。**

---

## 7. Registry 必要组件的重点说明

本节直接回答该任务的要求。

### 7.1 Shapes

Shapes 定义 credentials 必须满足的结构规则。例如，LegalPerson shape 可能要求包含：

- `gx:registrationNumber`
- `gx:headquartersAddress`
- `gx:legalAddress`

如果缺少这些字段，SHACL validation 可能返回 `sh:minCount` violations。

在Demo中，missing-field variant 用于测试这一层，但由于 JWT decode 先失败，因此测试实际上并未到达 SHACL。

---

### 7.2 Schemas

Schemas / ontology 定义 Gaia-X 术语的含义。

例如：

| 术语 | 含义 |
|---|---|
| `gx:LegalPerson` | Gaia-X 中的合法参与者 |
| `gx:Address` | 地址对象 |
| `gx:registrationNumber` | 法定注册号 |
| `gx:headquartersAddress` | 总部地址 |
| `gx:legalAddress` | 法定地址 |

如果 `@context` 错误，JSON-LD processor 可能无法正确展开 Gaia-X 术语，也可能无法正确构建 RDF data graph。在 Task 2 中，format-error variant 用于测试这类问题。

---

### 7.3 Trust Anchors

Trust Anchors 是可信根，用于判断 signing key、certificate chain、issuer 或 notary source 是否可信。

一个 credential 的签名可能在技术上有效，但 Gaia-X 仍需检查 signing key 或 certificate chain 能否链接到 accepted Trust Anchor。

在 Demo 中，由于未提供已签名的 VP-JWT、public key 或 certificate chain，因此未到达 Trust Anchor validation。

---

### 7.4 Valid / Revoked Keys

Valid / revoked keys 用于判断 public key 或 certificate 在验证时是否仍然可信。

即使签名在数学上正确，出现以下情况时也不应接受该 credential：

- public key 已撤销；
- certificate 已撤销；
- trust anchor 已撤销；
- credential status 已撤销。

**这意味着 key validation 不仅要确认签名能否通过验证，还要确认该 key 当前是否仍然可信。**

---

## 8. 结论与后续工作

Demo 表明，当前的 sample credential 无法由 Gaia-X Compliance API 直接验证，因为该 API 要求输入已签名的 VP-JWT，而不是裸 JSON-LD。实际观察到的失败包括：

1. JWT decode 层的 `not a valid JWT`；
2. JWT header 层的 `iss header referencing the issuer's DID is missing`。

这些实际错误都发生在到达 Registry SHACL shapes 和 Trust Anchor validation 之前。

Registry 在完整的 Gaia-X Compliance 流程中仍发挥核心作用。它提供：

1. 用于结构验证的 SHACL shapes；
2. 用于语义解释的 schemas / ontology；
3. 用于判断 certificate 和 issuer 是否可信的 trust anchors；
4. 用于动态信任决策的 valid / revoked key 信息；
5. 用于验证是否接受 Terms and Conditions 的 T&C rules / hash；
6. 用于法定注册验证的 registrationNumberIssuer / Notary 信息。

**最终结论：最小demo 的实际失败属于 Registry 前置条件失败；提交有效且已签名的 VP-JWT 后，Registry shapes、schemas、trust anchors、valid / revoked keys、T&C 和 Notary 才会决定后续阶段的验证结果。**

后续工作中，小组应生成真实且已签名的 VC-JWT / VP-JWT，加入必要的 `iss` 和 `kid` 字段，部署可解析的 DID:WEB document，然后重新测试 API 是否能够到达 Trust Anchor、SHACL、T&C 或 Notary validation。

