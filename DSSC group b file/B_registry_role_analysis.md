# B 组 — Gaia-X Registry Role Analysis

> 任务：Task 3 — 研究 Registry 在 Gaia-X Compliance 验证过程中提供什么  
> 分析文件：  
> - `B_compliance_api_demo.md`
> - `failure_in_registry.md`
> - `legal-person-minimal.jsonld`

---

## 1. Task 3 Scope and Key Clarification

本文件分析 Gaia-X Registry 在 Compliance 验证过程中的作用，重点回答：

1. Registry 在验证过程中提供什么；
2. shapes、schemas、trust anchors、valid / revoked keys 分别负责什么；
3. Task 2 的 Compliance API 测试实际失败在哪一层；
4. 哪些错误是 API 实际返回的，哪些只是后续 Registry 层的理论推断。

**说明：Task 2 当前实测主要失败在 JWT decode / JWT header 层，并未真正进入 SHACL shapes 或 Trust Anchor validation。因此，本文会区分 actual API errors 和 inferred Registry errors，避免把 Registry 前置层错误误写成 Registry shape 或 trust anchor 导致的错误。**

---

## 2. Task 2 Results Used in This Analysis

Task 2 提供了一个最小 LegalPerson credential payload：`legal-person-minimal.jsonld`，并基于它设计了两个错误变体：

| Credential | Purpose |
|---|---|
| `legal-person-minimal.jsonld` | 最小 LegalPerson VC payload，模拟 Gaia-X participant identity |
| missing-field variant | 删除 mandatory fields，用于理论测试 LegalPerson SHACL shape |
| format-error variant | 修改 context、date、countryCode 等格式，用于理论测试 JSON-LD / Address shape |

Task 2 使用 Compliance API 进行测试，得到以下实际结果：

| Test | Actual API Result | Meaning |
|---|---|---|
| `application/json` + raw JSON-LD | `500 stream is not readable` | API 不接受普通 JSON 提交 |
| `application/vp+jwt` + raw JSON-LD | `400 not a valid JWT` | API 要求 VP-JWT，不接受裸 JSON-LD |
| pseudo JWT | `400 iss header ... missing` | 伪 JWT 通过 decode，但缺少 issuer DID |

Task 2 的核心发现是：

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

结合 Task 2 的测试结果，可以将 Gaia-X Compliance 验证链理解为：

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

Task 2 当前实际到达的层级如下：

| Layer | Reached in Task 2? | Explanation |
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

**Therefore, Task 2 actual failures occur before Registry SHACL shapes and Trust Anchor validation are reached. Registry-level errors are mainly inferred future errors.**

---

## 5. Actual API Errors vs Inferred Registry Errors

To avoid overclaiming, this report separates:

- **Actual API errors**: errors actually returned by the Compliance API in Task 2;
- **Inferred Registry errors**: errors that would likely occur if the credential passed JWT / DID / signature layers and reached Registry-based validation.

| Error / Issue | Actual or Inferred | Validation Layer | Registry Relation | Explanation |
|---|---|---|---|---|
| `not a valid JWT` | Actual | JWT decode | No direct Registry involvement | The submitted body is raw JSON-LD, not VP-JWT |
| `iss header referencing the issuer's DID is missing` | Actual | JWT header | Indirect | Missing issuer DID, so DID / key resolution cannot start |
| DID cannot resolve | Inferred | DID resolution | Indirect | Example DID `did:web:energy-provider.example.org` is a placeholder |
| no signature / invalid signature | Inferred | Signature validation | Related to public key / trust anchor | Current payload is not a signed VP-JWT |
| no trusted certificate chain | Inferred | Trust Anchor validation | Trust anchors / valid keys | No X.509 / TSP chain is provided |
| public key revoked | Inferred | Key status validation | Revoked keys | A revoked key should not be trusted even if signature is mathematically valid |
| trust anchor revoked | Inferred | Trust Anchor validation | Revoked anchors | A revoked anchor invalidates the trust chain |
| missing `gx:registrationNumber` | Inferred | SHACL validation | LegalPerson shape | Missing-field variant would trigger this if SHACL is reached |
| missing `gx:headquartersAddress` | Inferred | SHACL validation | LegalPerson / Address shape | Missing-field variant would trigger this if SHACL is reached |
| missing `gx:legalAddress` | Inferred | SHACL validation | LegalPerson / Address shape | Missing-field variant would trigger this if SHACL is reached |
| invalid `countryCode = "China"` | Inferred | SHACL validation | Address shape | Format-error variant may violate Address shape |
| invalid `@context` | Inferred | JSON-LD processing / schema | Ontology / context | Wrong context may prevent RDF graph construction |
| missing T&C VC | Inferred | T&C validation | T&C shape / hash | Minimal LegalPerson payload does not include Issuer T&C Credential |
| registration number not verifiable | Inferred | Notary validation | registrationNumberIssuer / trusted data sources | Example registration number is not verified by a real Notary / LRN credential |

**Conclusion of this section：`not a valid JWT` and `missing iss` are actual API errors, but they are pre-Registry errors. LegalPerson shape、Address shape、Trust Anchor、T&C、Notary、valid / revoked key errors are currently inferred future errors.**

---

## 5.1 Direct Answer to the Question：whether we can identify which Registry shapes or trust anchors caused the API failure.

Based on the current Task 2 results, the answer is:

**No Registry SHACL shape or Trust Anchor actually caused the observed API failures, because the current tests did not reach Registry-level validation.**

The actual observed errors were:

| Actual API Error | Did it reach Registry shapes / trust anchors? | Explanation |
|---|---|---|
| `not a valid JWT` | No | The payload failed at JWT decode because raw JSON-LD was submitted instead of VP-JWT |
| `iss header referencing the issuer's DID is missing` | No | The pseudo JWT passed decoding but failed at JWT header validation before DID / signature / Trust Anchor validation |

Therefore, for the current tests, there is no actual Registry shape or trust anchor that can be identified as the direct cause of failure.

However, Registry analysis is still meaningful because once a valid signed VP-JWT is submitted, Compliance Service would rely on Registry-provided components in later layers:

| Later Validation Layer | Registry Component That Would Be Used | Possible Failure |
|---|---|---|
| SHACL validation | LegalPerson shape / Address shape | missing mandatory fields, invalid countryCode |
| Trust validation | Trust Anchors / valid keys / revoked keys | no trusted certificate chain, revoked key, revoked anchor |
| T&C validation | T&C shape / hash | missing Issuer T&C Credential |
| Registration validation | registrationNumberIssuer / Notary | registration number not verifiable |

**In short, Task 2 produced pre-Registry failures, not actual Registry-level failures. Task 3 therefore reports this limitation and analyzes which Registry components would become relevant in later validation layers.**

---

## 6. Credential-Level Registry Analysis

The three Task 2 credential cases can be mapped as follows:

| Credential Case | Actual Failure in Task 2 | If Registry Validation Were Reached |
|---|---|---|
| Correct version: `legal-person-minimal.jsonld` | Fails at JWT decode because it is raw JSON-LD, not VP-JWT | Basic LegalPerson SHACL may pass, but Trust Anchor、T&C、Notary validation would still fail due to missing signature, certificate chain, T&C VC and LRN credential |
| Missing-field variant | Also fails at JWT decode | LegalPerson shape would likely report `sh:minCount` violations for missing `gx:registrationNumber`、`gx:headquartersAddress`、`gx:legalAddress` |
| Format-error variant | Also fails at JWT decode | Invalid `@context` may fail during JSON-LD processing; invalid `countryCode = "China"` may fail Address shape validation |

**Key point：All three credentials currently fail at the same pre-Registry JWT layer. Their differences would only become visible after a valid signed VP-JWT is submitted and the validation process reaches JSON-LD / SHACL / Registry layers.**

---

## 7. Focused Explanation of Required Registry Components

This section directly answers the Task 3 requirement.

### 7.1 Shapes

Shapes define the structural rules that credentials must satisfy. For example, a LegalPerson shape may require:

- `gx:registrationNumber`
- `gx:headquartersAddress`
- `gx:legalAddress`

If these fields are missing, SHACL validation may return `sh:minCount` violations.

In Task 2, the missing-field variant is designed to test this layer, but it never actually reached SHACL because JWT decode failed first.

---

### 7.2 Schemas

Schemas / ontology define the meaning of Gaia-X terms.

For example:

| Term | Meaning |
|---|---|
| `gx:LegalPerson` | A legal participant in Gaia-X |
| `gx:Address` | Address object |
| `gx:registrationNumber` | Legal registration number |
| `gx:headquartersAddress` | Headquarters address |
| `gx:legalAddress` | Legal address |

If `@context` is wrong, the JSON-LD processor may not correctly expand Gaia-X terms, and the RDF data graph may not be built correctly. In Task 2, the format-error variant is designed to test this type of problem.

---

### 7.3 Trust Anchors

Trust Anchors are trusted roots used to decide whether a signing key, certificate chain, issuer, or notary source can be trusted.

A credential may have a technically valid signature, but Gaia-X still needs to check whether the signing key or certificate chain can be linked to an accepted Trust Anchor.

In Task 2, Trust Anchor validation was not reached because no signed VP-JWT, public key, or certificate chain was provided.

---

### 7.4 Valid / Revoked Keys

Valid / revoked keys are used to decide whether a public key or certificate is still trusted at validation time.

Even if a signature is mathematically correct, the credential should not be accepted if:

- the public key is revoked;
- the certificate is revoked;
- the trust anchor is revoked;
- the credential status is revoked.

**This means key validation is not only about whether the signature can be verified, but also about whether the key is still trusted now.**

---

## 8. Conclusion and Next Steps

Task 2 shows that the current sample credential cannot be directly validated by Gaia-X Compliance API because the API expects a signed VP-JWT, not raw JSON-LD. The actual observed failures are:

1. `not a valid JWT` at the JWT decode layer;
2. `iss header referencing the issuer's DID is missing` at the JWT header layer.

These actual errors occur before Registry SHACL shapes and Trust Anchor validation are reached.

Registry still plays a central role in the full Gaia-X Compliance process. It provides:

1. SHACL shapes for structural validation;
2. schemas / ontology for semantic interpretation;
3. trust anchors for certificate and issuer trust;
4. valid / revoked key information for dynamic trust decisions;
5. T&C rules / hash for Terms and Conditions acceptance;
6. registrationNumberIssuer / Notary information for legal registration validation.

**Final statement：Task 2’s actual failures are Registry-precondition failures, while Registry shapes、schemas、trust anchors、valid / revoked keys、T&C and Notary would determine later-stage validation results once a valid signed VP-JWT is submitted.**

For future work, the group should generate a real signed VC-JWT / VP-JWT, include required `iss` and `kid` fields, deploy a resolvable DID:WEB document, and then re-test whether the API reaches Trust Anchor, SHACL, T&C or Notary validation.

