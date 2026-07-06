# Failure in Registry — Gaia-X Compliance 失败原因分析

> **目标**：查明 Gaia-X Registry 中哪些 SHACL shapes 和 Trust Anchors 导致了验证失败
> **关联文档**：`B_compliance_api_demo.md` — 完整合规 API 测试报告
> **日期**：2026-07-01

---

## 一、Registry 架构总览

Gaia-X Registry (`https://registry.gaia-x.eu`，Lab 实例：`https://registry.lab.gaia-x.eu/development/`) 是公开、分布式、不可篡改的数据库，Compliance Service 从中读取校验规则。存储四类核心条目：

```
registry.gaia-x.eu
├── ① Trust Anchors Keyring
│     ├── eiDAS issuers
│     ├── EV SSL issuers (Mozilla CA 列表)
│     ├── registrationNumberIssuer (Gaia-X Notary)
│     └── revoked anchors
├── ② Credential Schemas (SHACL Shapes)
│     ├── LegalPerson shape
│     ├── ServiceOffering shape
│     ├── Address shape
│     ├── RegistrationNumber shape
│     └── GaiaXTermsAndCondition shape
├── ③ T&C Hashes
│     └── Gaia-X Ecosystem T&C SHA-256
└── ④ Notary & Trusted Data Sources
      ├── OpenCorporates API (local registration)
      ├── GLEIF API (LEI)
      ├── VIES API (VAT)
      └── EU EOS API (EORI)
```

---

## 二、校验链与失败映射

Gaia-X Compliance Service 按以下**7 层**逐层校验，前一层失败则后续层无法执行：

| 层 | 校验内容 | Registry 数据来源 | 我们各凭证的失败情况 |
|----|---------|------------------|---------------------|
| ① | JWT 解码 | API 入口规范 (Content-Type: vp+jwt) | ❌ 正确版/变体A/变体B 均为裸 JSON-LD |
| ② | JWT Header (alg, typ, iss, kid) | DID Document (verificationMethod) | ❌ 伪 JWT 缺 iss |
| ③ | 签名验证 + DID Resolution | DID Document + Trust Anchors keyring | ╳ |
| ④ | VP 结构校验 | VP SHACL shape | ╳ |
| ⑤ | VC 内容 SHACL 校验 | LegalPerson/Address shape | ╳ (变体A 理论失败) |
| ⑥ | T&C Acceptance | GaiaXTermsAndCondition shape + T&C hash | ╳ |
| ⑦ | Registration 真实性 (Notary) | registrationNumberIssuer + Trusted Data Sources | ╳ |

---

## 三、Layer 1 — JWT 解码层失败

### 3.1 涉及的 Registry 条目

**API 入口规范**（并非 Registry 数据库条目，而是 Compliance Service 的硬编码接口约束）：

| 参数 | 要求 | 我们的实际值 | 是否满足 |
|------|------|------------|---------|
| Content-Type | `application/vp+jwt` | `application/vp+jwt` ✅ | ✅ |
| Body format | 三段式 JWT (`header.payload.signature`) | 裸 JSON-LD / 裸 伪 JWT | ❌ |
| Body encoding | Base64URL | — | ❌ |

### 3.2 失败原因

```json
{
  "message": "The payload is not a valid JWT and was not decoded",
  "error": "Invalid verifiable presentation",
  "statusCode": 400
}
```

**根因**：我们传入的是原始 JSON-LD 字符串，Compliance Service 的 JWT parser 期望接收到 `eyJ...` 开头的 Base64URL 编码三段式 JWT。这是 API 层面的格式约束，不涉及 Registry 中任何条目。

### 3.3 如何绕过

需使用 VC-JWT 签名工具将 JSON-LD 凭证封装为 JWT：
- 推荐工具：[vc-jwt.io](https://gitlab.com/gaia-x/gaia-x-community/vc-jwt.io)（Gaia-X 官方）
- 或：`walt.id SSI Kit`、`Spruce DIDKit`

---

## 四、Layer 2 — JWT Header 层失败

### 4.1 涉及的 Registry 条目

| Registry 条目 | 校验内容 | 存储位置 |
|--------------|---------|---------|
| **DID Document** | JWT `iss` header 必须引用可解析的 DID | `did:web:{domain}/.well-known/did.json` |
| **verificationMethod** | JWT `kid` header 必须对应 DID 中的 key | DID Document 中 `verificationMethod` 数组 |

### 4.2 伪 JWT 的失败信息

```json
{
  "message": "Invalid request",
  "error": "Invalid verifiable presentation",
  "statusCode": 400,
  "errors": ["The iss header referencing the issuer's DID is missing"]
}
```

### 4.3 失败原因分析

伪 JWT header 为 `{"alg":"none","typ":"JWT"}` — 缺少 `iss` claim。Compliance Service 要求 JWT header 包含以下字段：

| JWT Header | 必须 | 对应 Registry 条目 | 示例 |
|-----------|------|-------------------|------|
| `alg` | ✅ | — | `PS256` |
| `typ` | ✅ | — | `JWT` |
| `iss` | ✅ | DID Document | `did:web:energy-provider.example.org` |
| `kid` | ✅ | verificationMethod | `did:web:...org#key-1` |
| `x5c` | ✅ (EV SSL) | Trust Anchor keyring | X.509 证书链 |

**我们的 `iss` 是 `did:web:energy-provider.example.org`** — 这是一个虚构 DID，Compliance Service 会尝试 `GET https://energy-provider.example.org/.well-known/did.json` — DNS 不可解析，DID Resolution 必然失败。

---

## 五、Layer 5 — SHACL Shapes 层分析（理论预测）

> 因 Layer 1-2 已失败，以下为基于 Trust Framework §5.2 的 SHACL 规则推导。

### 5.1 LegalPerson SHACL Shape

**Registry 位置**：`registry.gaia-x.eu` → shapes → LegalPerson

基于 Trust Framework §5.2 的属性表，Registry 中 LegalPerson shape 应包含以下 SHACL 属性约束：

```turtle
@prefix sh: <http://www.w3.org/ns/shacl#> .
@prefix gx: <https://w3id.org/gaia-x/development#> .

gx:LegalPersonShape
    a sh:NodeShape ;
    sh:targetClass gx:LegalPerson ;

    # 1. registrationNumber — mandatory (1..*)
    sh:property [
        sh:path gx:registrationNumber ;
        sh:minCount 1 ;
        sh:node gx:RegistrationNumberShape ;
        sh:message "LegalPerson must have at least one registrationNumber" ;
    ] ;

    # 2. headquartersAddress.countryCode — mandatory (1)
    sh:property [
        sh:path ( gx:headquartersAddress gx:countryCode ) ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[A-Z]{2}$" ;
        sh:message "headquartersAddress.countryCode must be ISO 3166-1 alpha-2" ;
    ] ;

    # 3. legalAddress.countryCode — mandatory (1)
    sh:property [
        sh:path ( gx:legalAddress gx:countryCode ) ;
        sh:minCount 1 ;
        sh:datatype xsd:string ;
        sh:pattern "^[A-Z]{2}$" ;
        sh:message "legalAddress.countryCode must be ISO 3166-1 alpha-2" ;
    ] ;

    # 4. parentOrganization — optional (0..*)
    sh:property [
        sh:path gx:parentOrganization ;
        sh:minCount 0 ;
    ] ;

    # 5. subOrganization — optional (0..*)
    sh:property [
        sh:path gx:subOrganization ;
        sh:minCount 0 ;
    ] .
```

### 5.2 变体 A（缺必填项）的 SHACL 判定

若穿透 JWT 层进入 SHACL，变体 A 的 credentialSubject 为：

```json
{
  "id": "https://energy-provider.example.org/.well-known/legal-person.json#cs",
  "schema:name": "Energy Data Provider Ltd."
}
```

**Shader 检验结果**：

| SHACL Constraint | credentialSubject 实际值 | 判定 |
|-----------------|------------------------|------|
| `sh:path gx:registrationNumber; sh:minCount 1` | **缺失** | ❌ Violation: "Less than 1 values" |
| `sh:path (gx:headquartersAddress gx:countryCode); sh:minCount 1` | **缺失** | ❌ Violation: "Less than 1 values" |
| `sh:path (gx:legalAddress gx:countryCode); sh:minCount 1` | **缺失** | ❌ Violation: "Less than 1 values" |

**3 个 SHACL Violation，全部属于 `sh:MinCountConstraintComponent`**。

### 5.3 变体 B（格式错误）的 SHACL 判定

**在 SHACL 之前先失败的部分**：

`@context` 中 `"https://w3id.org/gaia-x/TYPO#"` 是虚构 URI。JSON-LD processor 在展开 terms（如 `gx:LegalPerson` → `https://w3id.org/gaia-x/TYPO#LegalPerson`）时会尝试 dereference 该 context，失败则无法构造 data graph → SHACL engine 收到空图或报错。

**若 @context 修复后进入 SHACL**：

| SHACL Constraint | credentialSubject 实际值 | 判定 |
|-----------------|------------------------|------|
| `sh:pattern "^[A-Z]{2}$"` on countryCode | `"China"` (5 字符，非两位) | ❌ Violation × 2 |

---

## 六、Trust Anchors 失败分析

> 来源：Gaia-X Trust Framework §4 "Trust Anchors"

### 6.1 四个 Trust Anchor 及对我们的适用性

| Trust Anchor | 触发条件 | 是否适用于我们的凭证 | 若适用则失败原因 |
|-------------|---------|-------------------|----------------|
| **eiDAS** | `legalAddress.countryCode` ∈ EEA | ❌ `"CN"` 不在 EEA → 不适用 | N/A |
| **EV SSL** | 过渡期 TSP | ✅ 适用（中国 entity 需 EV SSL 密钥链） | 我们没有 X.509 证书 |
| **registrationNumberIssuer** | 任何 LegalPerson | ✅ 适用 | LRN URL 虚构，Notary 无法验证 |
| **State** | `legalAddress.countryCode` 在 EEA 时强制 eiDAS | ❌ 不触发（CN 不在 EEA） | N/A |

### 6.2 EV SSL Trust Anchor 失败根因

Trust Framework §4 规定："all keypairs used to sign claims must have at least one of the Trust Anchors in their certificate chain"。

我们的凭证**没有任何签名**（无 `proof` 块 → 无 keypair → 无证书链）。这是一个结构性缺失，不是 Registry 条目缺失。

### 6.3 registrationNumberIssuer Trust Anchor 失败根因

Trust Framework §4.1 定义：
> "registrationNumberIssuer: During the pilot phase, the Gaia-X Association nominated itself as a valid Trust Anchor under https://notary.gaia-x.eu"

我们的 `gx:registrationNumber` 引用 `https://energy-provider.example.org/.well-known/registration-number.json#cs` — 这是一个虚构 URL。

流程应为：
1. 获取真实商业注册号（如 LEI、VAT、本地工商号）
2. 调用 Gaia-X Notary API 验证
3. Notary 返回已签名的 LRN JWT
4. 在 VP 中引用该 LRN JWT

---

## 七、逐一错误 → Registry 条目映射表

下表是 **Task 3 需要查明的核心结论**：

| # | 错误信息 / 现象 | Registry 条目 | 条目类型 | 当前状态 | 修复需要 |
|---|---------------|-------------|---------|---------|---------|
| 1 | `"not a valid JWT"` | API 接口规范 | 硬编码 | — | 生成 VC-JWT |
| 2 | `"iss header ... missing"` | DID Document | DID:WEB (需自主部署) | ❌ 虚构 | 部署 `.well-known/did.json` |
| 3 | (预测) JWT 签名无效 | Trust Anchors keyring | Trust Anchor 列表 | ❌ 无签名 | 从 EV SSL CA 获取 X.509 证书 |
| 4 | (预测) kid 不匹配 | DID Document → verificationMethod | DID 文档字段 | ❌ DID 不可解析 | DID Document 中声明 verificationMethod |
| 5 | (预测) SHACL minCount violation × 3 | LegalPerson SHACL shape | Schema (shapes graph) | ⚠️ 变体 A 会触发 | 填写 3 个必填字段 |
| 6 | (预测) countryCode pattern violation × 2 | Address SHACL shape | Schema | ⚠️ 变体 B 会触发 | 填两位 ISO 3166-1 码 |
| 7 | (预测) @context dereference failed | @context URI | ontology term definition | ⚠️ 变体 B 会触发 (TYPO) | 使用正确的 `gaia-x/development#` |
| 8 | (预测) T&C not accepted | GaiaXTermsAndCondition | T&C hash + shape | ❌ 未签发 | 签名 T&C VC |
| 9 | (预测) Registration not verifiable | registrationNumberIssuer | Trust Anchor + Notary API | ❌ 虚构号码 | 获取 Notary-verified LRN JWT |

---

## 八、Registry 如何影响验证结果 — 机制详解

### 8.1 Compliance Engine 的工作流程

```
┌────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Participant   │────▶│ Compliance Engine │────▶│ Gaia-X Registry  │
│  submits VP-JWT│     │                  │     │                 │
└────────────────┘     │  ① 解析 JWT      │     │ ① Trust Anchors │
                       │  ② 校验 header   │     │    (keyring)    │
                       │  ③ 验证签名      │◀───│ ② SHACL shapes  │
                       │  ④ 校验 VP       │     │ ③ T&C hash      │
                       │  ⑤ 校验 VC       │     │ ④ Notary list   │
                       │  ⑥ 校验 T&C      │     └─────────────────┘
                       │  ⑦ 校验 Notary   │
                       │  ⑧ 签发 GC       │
                       └──────────────────┘
```

### 8.2 Registry Shapes 的动态加载

Compliance Service **不硬编码** SHACL shapes —— 它在运行时从 Registry 中加载：

1. 根据凭证 `type`（如 `gx:LegalPerson`）查询 Registry 中对应的 SHACL shape
2. 将 shape 作为 shapes graph，凭证 credentialSubject 作为 data graph
3. 执行 SHACL validation
4. 返回 `sh:conforms true/false` + 违规详情

这解释了为什么 Registry 中的 shapes **是活的而非静态的** — 如果 Governance Authority 在 Registry 中更新了 shape（如新增必填字段），所有后续验证自动生效。

### 8.3 Trust Anchors 的链式验证

每个参与者的 JWT 签名密钥必须链到至少一个 Trust Anchor：

```
JWT signature key
    ↓ signed by
Intermediate CA (EV SSL issuer)
    ↓ rooted at
Root CA (in Mozilla CA list)
    ↓ listed in
Registry → Trust Anchors keyring
```

如果中间 CA 被 Registry 标记为 revoked（存储在 `revoked anchors` 列表），之前已通过的凭证也会失效 —— Registry 支持动态撤销。

---

## 九、结论与 Task 3 建议

### 9.1 核心发现

1. **Registry 是 Compliance 的单一真相源**：所有校验规则（SHACL shapes、Trust Anchors、T&C hash、Notary 列表）都存储在 Registry 中
2. **7 层校验链**：JWT 解码 → Header 校验 → 签名 & DID → VP 结构 → SHACL → T&C → Notary
3. **我们的凭证卡在第 1 层**：缺少 JWT 签名，后续 6 层无法触发
4. **SHACL 层（Layer 5）是不同的"边界"**：变体 A/B 在 SHACL 层会产生不同错误，但被前置的 JWT 解码层统一屏蔽了
5. **Trust Anchors 是硬门槛**：中国 entity 需 EV SSL（而非 eiDAS），但 EV SSL 只是过渡方案

### 9.2 三个凭证的 Registry 级归因

| 凭证 | 实际失败层 | Registry 条目 | 若穿透至 SHACL 层的额外失败条目 |
|------|-----------|-------------|---------------------------|
| 正确版 | ① JWT 解码 | 无 Registry 条目参与 | LegalPerson shape: ✅ (通过) |
| | ③ 签名/DID | DID Document + Trust Anchors | GaiaXTermsAndCondition: ❌ |
| | | | registrationNumberIssuer: ❌ |
| 变体 A | ① JWT 解码 | 同正确版 | LegalPerson shape: ❌ sh:minCount × 3 |
| 变体 B | ① JWT 解码 | 同正确版 | @context dereference: ❌ |
| | | | Address shape: ❌ sh:pattern × 2 |

### 9.3 给后续研究的建议

如需**真正触发 SHACL 层和 Trust Anchor 层的失败**（而非卡在 JWT 解码），建议：

1. 使用 Gaia-X [vc-jwt.io](https://gitlab.com/gaia-x/gaia-x-community/vc-jwt.io) 或 [walt.id SSI Kit](https://github.com/walt-id/waltid-ssikit) 对三个凭证分别签名
2. 使用自签密钥（即使签名不链到 Trust Anchor），至少穿透 Layer 1-2
3. 观察 Layer 3（签名/Trust Anchor）的失败信息
4. 若需到 SHACL 层，需暂时禁用 Trust Anchor 校验（或在 Lab 环境用测试配置）

---

## 十、参考资料

- Gaia-X Trust Framework §4 — [Trust Anchors](https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/trust_anchors/)
- Gaia-X Trust Framework §5 — [Participant](https://gaia-x.gitlab.io/policy-rules-committee/trust-framework/participant/)
- Gaia-X Architecture Document §6 — [Trust Framework Components](https://docs.gaia-x.eu/technical-committee/architecture-document/23.10/gx_services/)
- Gaia-X Registry — [Lab Instance](https://registry.lab.gaia-x.eu/development/)
- Gaia-X Compliance Service — [Lab Swagger](https://compliance.lab.gaia-x.eu/development/docs)
- 项目场景文档 — `DSSC_Toolbox_Scenario.md` B 组任务
- 本报告关联文件 — `产物/B_compliance_api_demo.md`
