# B 组 — Gaia-X Compliance API Demo

> 文件: `产物/legal-person-minimal.jsonld`
> 凭证类型: **LegalPerson (参与者凭证)**
> 目标: 基于 Gaia-X 官方格式，创建最少必填字段的凭证，供 Compliance API 验证测试。

---

## 一、选型分析：为什么选 LegalPerson 而非 ServiceOffering

| 维度 | LegalPerson | ServiceOffering |
|------|------------|-----------------|
| Ontology 必填字段数 | **3** (registrationNumber, legalAddress, headquartersAddress) | **3+** (providedBy, termsAndConditions, dataAccountExport) |
| 嵌套复杂度 | Address 平面对象 (countryCode + vcard 字段) | 需引用已存在的 LegalPerson 凭证、T&C 需含 hash、dataAccountExport 含多种子字段 |
| 独立可验证性 | 可独立存为凭证 | `providedBy` 必须指向已存在的 participant 凭证 |
| 最小可行原则 | ✅ 适合 | ❌ 依赖链太长 |

**结论**：选 LegalPerson，它是 Gaia-X 信任链的起点。

---

## 二、格式基准与版本差异

本凭证参照 **官方 Gaia-X LegalPerson 示例**（`https://gaia-x.eu/.well-known/legal-person.json`，Loire 25.10 格式），而非项目模板（Tagus 22.04 教学模板）。

### Tagus 22.04 vs Loire 25.10 关键差异

| 项目 | Tagus 22.04 (PDF/模板) | Loire 25.10 (官方) |
|------|----------------------|---------------------|
| VC @context | `2018/credentials/v1` | `ns/credentials/v2` |
| `type` | `LegalParticipant` | `gx:LegalPerson` |
| 日期字段 | `issuanceDate` | `validFrom` + `validUntil` |
| 名称 | `gx:legalName` (内联) | `schema:name` (映射 `sdo:name`) |
| 总部地址 | `gx:headquarterAddress` (仅 `countrySubdivisionCode`) | `gx:headquartersAddress` (完整 vcard) |
| 注册号 | 内联字符串 | 引用对象 `{"id": "..."}` |
| 地址模型 | 仅 `countrySubdivisionCode` | 完整 Address: `countryCode` + `vcard:street-address` + `vcard:locality` + `vcard:postal-code` |

### 来源依据

- **PDF (Gaia-X Trust Framework 22.04)**：第 6-7 页定义 LegalPerson 属性表（3 个必填 + 3 个可选）
- **官方 Ontology**：`https://docs.gaia-x.eu/ontology/development/classes/LegalPerson/` 定义 3 mandatory props
- **官方凭证示例**：`https://gaia-x.eu/.well-known/legal-person.json` 展示当前 Loire 格式

---

## 三、凭证字段清单

### 3.1 VC 层级（所有 Gaia-X Credential 通用必填）

| 字段 | 值 | 状态 |
|------|-----|------|
| `@context` | `ns/credentials/v2` + `gaia-x/development#` + `vcard` + `schema` | ✅ 已填 |
| `id` | `https://energy-provider.example.org/.well-known/legal-person.json` | ✅ 已填 |
| `type` | `["VerifiableCredential", "gx:LegalPerson"]` | ✅ 已填 |
| `issuer` | `did:web:energy-provider.example.org` | ✅ 已填 (占位) |
| `validFrom` | `2026-05-01T00:00:00Z` | ✅ 已填 |
| `credentialSubject` | (见 3.2) | ✅ 已填 |

### 3.2 CredentialSubject 层级（Ontology 必填）

| 字段 | 值 | 状态 |
|------|-----|------|
| `id` | `...#cs` fragment | ✅ 已填 |
| `schema:name` | `"Energy Data Provider Ltd."` | ✅ 建议（非强制） |
| `gx:registrationNumber` | 引用 `registration-number.json#cs` | ✅ **必填** 1..* |
| `gx:headquartersAddress` | Address 对象 (CN, Shenzhen) | ✅ **必填** 1 |
| `gx:legalAddress` | Address 对象 (CN, Shenzhen) | ✅ **必填** 1 |

### 3.3 可选字段（已省略）

| 字段 | 状态 | 说明 |
|------|------|------|
| `gx:parentOrganizationOf` | ❌ 省略 | 零或多个父组织引用 |
| `gx:subOrganisationOf` | ❌ 省略 | 零或多个子组织引用 |
| `schema:description` | ❌ 省略 | 可选描述 |
| `validUntil` | ❌ 省略 | 凭证过期时间（推荐但非强制） |
| `proof` | ❌ 省略 | 签名块 — 需要真实密钥 |

---

## 四、已知缺失项（真实合规必需）

以下项目是 Gaia-X 正式合规流程的强制要求，本最小凭证**有意忽略**以实现最小字段目标：

| 缺失项 | 说明 | 影响 |
|--------|------|------|
| **Legal Registration Number Credential** | 需从 GXDCH Notary 获取 LEI/VAT/EORI JWT | 无真实注册号凭证则 compliance 必然失败 |
| **Issuer (T&C) Credential** | 需签发并签名 Terms and Conditions 接受凭证 | 参与者身份不完整 |
| **Enveloped VC Signature (proof)** | 所有 VC 需 JWS 签名 (PS256, VC-JWT) | 无签名的裸 JSON-LD 无法通过合规验证 |
| **真实 DID:WEB 文档** | 需部署 `did:web:energy-provider.example.org/.well-known/did.json` | `issuer` 字段为占位值 |
| **Trust Service Provider 证书** | 需从 Gaia-X approved TSP 获取 X.509 证书 | `kid` 和 `x5c` 链缺失 |
| **Verifiable Presentation 封装** | 3 个 VC (LP + LRN + Issuer) 需组合为 VP | 仅提供了一个裸 VC，非完整 VP |

---

## 五、错误凭证变体（用于 Compliance API 报错测试）

为测试 Compliance API 的校验能力和错误信息质量，基于正确版本 (`legal-person-minimal.jsonld`) 构造了 2 个有意错误的变体。

### 5.1 变体 A：缺必填项 (`legal-person-error-missing.jsonld`)

**改动**：删除 Ontology 要求的全部 3 个 mandatory 字段。

| 删除的字段 | 原始值 | 删除原因 |
|-----------|--------|---------|
| `gx:registrationNumber` | 引用 `registration-number.json#cs` | Tagus 22.04 必填 (1..\*) |
| `gx:headquartersAddress` | Address 对象 (CN, Shenzhen) | Tagus 22.04 必填 (1) |
| `gx:legalAddress` | Address 对象 (CN, Shenzhen) | Tagus 22.04 必填 (1) |

credentialSubject 仅保留 `id` 和 `schema:name`。

**预期 SHACL 校验错误**：

| 预期错误 | 约束来源 | 说明 |
|---------|---------|------|
| `sh:minCount` violation × 3 | LegalPerson shape | 三个必填属性 minCount ≥ 1 |
| `sh:class` validation fail | Address shape | `gx:headquartersAddress` 期望 `gx:Address` 类型 |
| `No registration number found` | 合规流程 | 参与者必须提供注册号 |

---

### 5.2 变体 B：格式错误 (`legal-person-error-format.jsonld`)

**改动**：保留所有字段名称，但填入不合法的值。

| 字段 | 正确值 | 错误值 | 违规说明 |
|------|--------|--------|---------|
| `@context[1]` | `https://w3id.org/gaia-x/development#` | `https://w3id.org/gaia-x/TYPO#` | 虚构的 @context URI，无法解析 ontology |
| `validFrom` | `2026-05-01T00:00:00Z` | `2026年5月1日` | 非 ISO 8601 格式，xsd:dateTime 无法解析 |
| `gx:headquartersAddress.gx:countryCode` | `CN` | `China` | 应为 ISO 3166-1 alpha-2 两位码 |
| `gx:legalAddress.gx:countryCode` | `CN` | `China` | 同上 |

**预期校验错误**：

| 预期错误 | 约束来源 | 说明 |
|---------|---------|------|
| `@context dereference failed` | JSON-LD processor | 虚构 URI 无法加载 remote context |
| `xsd:dateTime parse error` | W3C VC Data Model 2.0 | `validFrom` 必须是 `dateTimeStamp` 格式 |
| `sh:pattern` / `sh:in` violation × 2 | Address shape | 国家码必须是 ISO 3166-1 两位字母码 |
| `Unrecognized @context term` | Gaia-X Compliance Service | TYPO URI 对应 ontology 中无 `LegalPerson` 定义 |

---

### 5.3 测试矩阵

| 变体 | 文件 | 错误类型 | 预期通过率 |
|------|------|---------|-----------|
| 正确版 | `legal-person-minimal.jsonld` | 仅缺签名/LRN（非格式错误） | SHACL ✅ / 合规 ❌ |
| 变体 A | `legal-person-error-missing.jsonld` | 结构性缺失 | SHACL ❌ / 合规 ❌ |
| 变体 B | `legal-person-error-format.jsonld` | 格式/枚举错误 | JSON-LD ❌ / SHACL ❌ |

---

## 六、Compliance API 实测结果

> 测试时间: 2026-07-01T19:29 UTC+8
> 原始响应文件: `产物/api-responses/` (共 15 个文件)

### 6.1 已发现的接口

| 端点 | URL | 状态 |
|------|-----|------|
| Gaia-X Lab (development) | `POST https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance?vcid={id}` | ✅ 可用 |
| Gaia-X Lab (main) | `POST https://compliance.lab.gaia-x.eu/main/api/credential-offers/standard-compliance?vcid={id}` | ✅ 可用 |
| Telekom GXDCH | `POST https://gx-compliance.gxdch.dih.telekom.com/v1/api/credential-offers` | ❌ 维护中 |

### 6.2 API 规范（来自 Swagger）

| 项目 | 值 |
|------|-----|
| Content-Type | `application/vp+jwt` |
| 请求体格式 | Raw VP-JWT string（签名后的 Verifiable Presentation） |
| 必填查询参数 | `vcid` (string) |
| 成功响应 | `201` + `Content-Type: application/vc+jwt`，body 为合规凭证 JWT |
| 错误响应 | `400` (请求格式错误) / `503` (服务配置异常) |
| 错误格式 | `{"message","error","statusCode","errors":[]}` |

### 6.3 实测结果矩阵

共提交 3 个凭证 × 3 个端点 × 多种 Content-Type = 15 次请求：

#### 6.3.1 Content-Type: `application/json`（错误用法）

| 凭证 | Lab dev | Lab main | Telekom |
|------|---------|----------|---------|
| 正确版 | **500** | **500** | **500** |
| 缺失版 | — | — | — |
| 格式错误版 | — | — | — |

**响应内容**: `{"statusCode":500,"message":"Internal Server Error","errors":["stream is not readable"]}`

**分析**: Gaia-X Compliance API 不接受 `application/json` Content-Type。服务端尝试从请求流读取时失败，导致内部 500 错误而非预期的 415。这是 API 的边界行为。

#### 6.3.2 Content-Type: `application/vp+jwt`（正确用法，但内容是原始 JSON-LD）

| 凭证 | Lab dev | Lab main | Telekom |
|------|---------|----------|---------|
| 正确版 | **400** | **400** | **500** |
| 缺失版 | **400** | **400** | **500** |
| 格式错误版 | **400** | **400** | **500** |

**响应内容**:
```json
{
  "message": "The payload is not a valid JWT and was not decoded",
  "error": "Invalid verifiable presentation",
  "statusCode": 400,
  "errors": [null]
}
```

**分析**: 三个凭证在 Lab 端点均返回**完全相同的 400 错误**。API 在 JWT 解码阶段就失败了——它无法将原始 JSON-LD 解析为三段式 JWT（header.payload.signature）。因此，SHACL 层面（字段缺失/格式错误）的校验**根本没有执行到**。

#### 6.3.3 伪 JWT 提交（Base64 编码三段式）

| 凭证 | Lab dev | Lab main | Telekom |
|------|---------|----------|---------|
| 伪 JWT (alg:none) | **400** | **400** | **500** |

**响应内容**:
```json
{
  "message": "Invalid request",
  "error": "Invalid verifiable presentation",
  "statusCode": 400,
  "errors": ["The iss header referencing the issuer's DID is missing"]
}
```

**分析**: 这是本次测试**最有信息量**的响应。伪 JWT 通过了解码阶段，进入 JWT Claim 校验。API 检查到 JWT header 中缺少 `iss` claim（issuer DID），返回了精确的字段级错误。说明合规 API 的校验链是:

```
1. JWT 解码 (parse JWT three-part)
2. JWT Header 校验 (alg, typ, iss, kid 等)
3. DID 解析 + 签名验证
4. VP 结构校验
5. VC 内容校验（SHACL / Trust Framework rules）
```

我们卡在第 1 层（裸 JSON-LD）和第 2 层（伪 JWT 缺 iss）。

### 6.4 Telekom GXDCH 状态

Telekom Data Intelligence Hub 合规服务当前处于 **Scheduled Maintenance** 状态，所有请求返回 HTML 维护页面，无法用于测试。

```
Scheduled Maintenance
We are currently enhancing the Telekom Data Intelligence Hub
with essential upgrades.
```

### 6.5 关键发现与差距分析

| # | 发现 | 影响 |
|---|------|------|
| 1 | API **必须**是 VP-JWT 格式，不接受裸 JSON-LD | 我们的凭证无法直接验证 |
| 2 | JWT 解码失败时，所有凭证返回**相同**错误 | 无法区分字段缺失 vs 格式错误 |
| 3 | 伪 JWT 可以 bypass 解码层，进入 claim 校验 | 说明签名层之前有逐层校验 |
| 4 | 要看到 SHACL/ontology 层面的错误 | 需要真正的签名 VP-JWT |
| 5 | 正式合规需要 3 个 VC + DID:WEB + X.509 | 完整流程远超"最小凭证"范围 |

### 6.6 若要推进到 SHACL 层校验

需要以下额外工作（已超出本次任务范围，但记录了路径）:

1. **签名工具**: 使用 Gaia-X [VC-JWT Signer](https://gitlab.com/gaia-x/gaia-x-community/vc-jwt.io) 对凭证签名
2. **DID:WEB**: 部署 DID 文档 (使用 [DID:WEB Generator](https://gitlab.com/gaia-x/lab/libraries/did-web-generator))
3. **X.509 证书**: 从 Gaia-X approved TSP 获取
4. **LRN 凭证**: 从 GXDCH Notary 获取 Legal Registration Number JWT
5. **Issuer 凭证**: 签名 Terms & Conditions 接受凭证
6. **VP 组合**: 将 LP + LRN + Issuer 三个 VC 组合为 Verifiable Presentation
7. **签名提交**: 将 VP 签名为 VP-JWT 后 POST

---

## 七、Registry Shapes 与 Trust Anchors 校验链分析

> 本章基于 Gaia-X Trust Framework §4-§5、Architecture Document §6、以及 `registry.gaia-x.eu` 的官方定义。

### 7.1 Registry 的四层结构

Gaia-X Registry（`https://registry.gaia-x.eu`）是治理中枢，存储以下四类关键条目，Compliance Service 按此顺序逐层校验：

```
┌──────────────────────────────────────────────────┐
│  Layer 1 — Trust Anchors (keyring)               │
│  eiDAS / EV SSL / registrationNumberIssuer       │
│  → 校验: 签名密钥链中是否有 Valid Trust Anchor      │
├──────────────────────────────────────────────────┤
│  Layer 2 — Credential Schemas (SHACL Shapes)     │
│  LegalPerson / ServiceOffering / LRN / T&C shapes│
│  → 校验: data graph ⊨ shapes graph (SHACL)       │
├──────────────────────────────────────────────────┤
│  Layer 3 — T&C Acceptance                        │
│  GaiaXTermsAndConditions SHA-256 hash            │
│  → 校验: Issuer 是否已签 T&C VC                   │
├──────────────────────────────────────────────────┤
│  Layer 4 — Notary Validation                     │
│  registrationNumber 真实性验证                     │
│  → 校验: LRN 号码是否经 Notary API 确认             │
└──────────────────────────────────────────────────┘
```

### 7.2 Layer 1：Trust Anchors 详细定义

> 来源：Gaia-X Trust Framework §4 "Trust Anchors"

所有用于签名的密钥必须在其证书链中至少包含一个 Trust Anchor。Registry 中维护有效的 Trust Anchor 列表。

| Trust Anchor | 定义 | 适用范围 |
|-------------|------|---------|
| **eiDAS** | eIDAS Regulation 认可的数字签名证书颁发者 | EEA 国家的 `legalAddress.countryCode` |
| **EV SSL** | Extended Validation SSL 证书颁发者 (Mozilla CA 列表) | 临时过渡期有效 |
| **registrationNumberIssuer** | Gaia-X Notary (`notary.gaia-x.eu`) — 试点阶段 Gaia-X 协会自行担任 | 验证注册号真实性 |
| **State** | 国家验证的身份颁发者 | `legalAddress.countryCode` 在 EEA 时强制 eiDAS |

**对我们凭证的影响**：`gx:legalAddress.gx:countryCode = "CN"` — 中国不在 EEA，因此 eiDAS 不适用。需 EV SSL 或 Gaia-X Association 直接背书。我们的凭证无任何签名密钥，Layer 1 直接失败。

### 7.3 Layer 2：SHACL Shapes 详细约束

> 来源：Gaia-X Trust Framework §5.2 "Legal person"

Compliance Service 从 Registry 加载 LegalPerson SHACL shape，对每个凭证的 credentialSubject 执行以下约束：

| SHACL Property | Cardinality | 对应 Trust Anchor | 校验逻辑 |
|---------------|-------------|-------------------|---------|
| `gx:registrationNumber` | `sh:minCount 1` | registrationNumberIssuer | 必须存在且值为合法类型（local/EUID/EORI/vatID/leiCode 之一） |
| `gx:headquartersAddress.gx:countryCode` | `sh:minCount 1` | State | 必须为 ISO 3166-2 alpha-2/alpha-3/numeric 格式 |
| `gx:legalAddress.gx:countryCode` | `sh:minCount 1` | State | 同上 |
| `gx:parentOrganization` | `sh:minCount 0` (0..\*) | State | 可选，如有则需指向有效 participant |
| `gx:subOrganization` | `sh:minCount 0` (0..\*) | State | 可选，如有则需有合法授权 |

**针对三个凭证的 SHACL 判定（假设已穿透 JWT 层）**：

| 凭证 | SHACL 判定 | 触发的违规 |
|------|-----------|-----------|
| 正确版 | ✅ 通过 | — 3 个必填字段齐全，值合法 |
| 变体 A（缺字段） | ❌ 失败 | `sh:minCount` violation × 3（registrationNumber / headquartersAddress / legalAddress 均缺失） |
| 变体 B（格式错） | ❌ 失败 | `sh:pattern` violation × 2（countryCode = "China" 非 ISO 3166-2 格式）；JSON-LD @context 在 SHACL 之前先失败 |

**变体 A 的 SHACL Validation Report（预测）**：

```turtle
[ a sh:ValidationReport ;
  sh:conforms false ;
  sh:result
    [ sh:focusNode <...credentialSubject> ;
      sh:resultPath gx:registrationNumber ;
      sh:resultSeverity sh:Violation ;
      sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
      sh:message "Less than 1 values" ],
    [ sh:focusNode <...credentialSubject> ;
      sh:resultPath gx:headquartersAddress ;
      sh:resultSeverity sh:Violation ;
      sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
      sh:message "Less than 1 values" ],
    [ sh:focusNode <...credentialSubject> ;
      sh:resultPath gx:legalAddress ;
      sh:resultSeverity sh:Violation ;
      sh:sourceConstraintComponent sh:MinCountConstraintComponent ;
      sh:message "Less than 1 values" ]
] .
```

### 7.4 Layer 3：T&C Acceptance

> 来源：Gaia-X Trust Framework §5.1 "Issuer"

每个 Issuer 必须颁发一个 `GaiaXTermsAndCondition` VC，其 `termsAndConditions` 字段为 Gaia-X Ecosystem T&C 的 SHA-256 hash：

```
SHA-256("The PARTICIPANT signing Gaia-X credentials agrees as follows:
- to update its Gaia-X credentials about any changes...")
→ 0f5ced73... (示例 hash)
```

**对我们凭证的影响**：我们没有任何 Issuer T&C VC。即使穿透 JWT 和 SHACL 层，Layer 3 也会因缺少 `GaiaXTermsAndCondition` VC 而失败。

### 7.5 Layer 4：Notary — registrationNumber 真实性验证

> 来源：Gaia-X Trust Framework §4.2 "Trusted Data Sources"

Trust Anchor `registrationNumberIssuer` 使用可信数据源验证注册号：

| 注册号类型 | 验证 API | 返回附加信息 |
|-----------|---------|-------------|
| `local` | [OpenCorporates API](https://api.opencorporates.com/) | `headquarterAddress.countryCode` |
| `leiCode` | [GLEIF API](https://www.gleif.org/en/lei-data/gleif-api) | — |
| `EORI` | [EU EOS API](https://ec.europa.eu/taxation_customs/dds2/eos/validation/services/validation?wsdl) | — |
| `vatID` | [VIES API](https://ec.europa.eu/taxation_customs/vies/checkVatTestService.wsdl) | `headquarterAddress.countryCode` |

**对我们凭证的影响**：我们的 `gx:registrationNumber` 指向 `https://energy-provider.example.org/.well-known/registration-number.json#cs` — 这是一个虚构 URL，无法被 Notary 解析。即使前 3 层全通过，Layer 4 也会因 "registration number not verifiable against trusted data source" 而失败。

---

## 八、逐凭证错误归因 — 完整校验链视角

### 8.1 校验链与各凭证的穿透深度

```
Compliance API 逐层校验:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Layer                   正确版    变体A(缺字段)  变体B(格式错)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
① JWT 解码              ❌ 裸JSON  ❌ 裸JSON    ❌ 裸JSON
② JWT Header (alg/iss)   ❌        ❌          ❌
③ DID 解析+签名验证      ╳        ╳          ╳
④ VP 结构校验           ╳        ╳          ╳
⑤ SHACL (Layer 2)       ╳        ╳          ╳
⑥ T&C (Layer 3)         ╳        ╳          ╳
⑦ Notary (Layer 4)      ╳        ╳          ╳
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
❌ = 实际失败  ╳ = 无法到达（因前置层失败）
```

### 8.2 正确版（`legal-person-minimal.jsonld`）的错误归因

| 失败层 | 具体失败原因 | Registry 对应条目 |
|--------|------------|------------------|
| **① JWT 解码** | 传入的是裸 JSON-LD，非三段式 JWT | — (API 入口规范要求 VP-JWT) |
| 若穿透 → ② JWT Header | 无 `iss` claim（JWT header 缺 issuer DID） | Registry: DID Document |
| 若穿透 → ③ 签名 | 无 `proof` 块，无 `x5c` 证书链 | Registry: Trust Anchors keyring |
| 若穿透 → ⑤ SHACL | ✅ 通过（3 个必填字段齐全） | Registry: LegalPerson SHACL shape |
| 若穿透 → ⑥ T&C | 缺 `GaiaXTermsAndCondition` VC | Registry: T&C hash |
| 若穿透 → ⑦ Notary | 注册号 URL 虚构，无法验证 | Registry: registrationNumberIssuer |

**根因**：凭证缺少完整的签名链（proof + DID + x5c），在最外层 JWT 解码即被拦截。该凭证在**纯 SHACL 层理论上是正确的**，但 Gaia-X 合规远不止 SHACL。

### 8.3 变体 A（缺必填项）的错误归因

| 失败层 | 具体失败原因 | Registry 对应条目 |
|--------|------------|------------------|
| **① JWT 解码** | 裸 JSON-LD | 同正确版 |
| 若穿透 → ⑤ SHACL | **`sh:minCount` × 3** — 删除的 registrationNumber、headquartersAddress、legalAddress 各触发 Violation | Registry: LegalPerson SHACL shape (§5.2) |

**关键发现**：变体 A 和正确版返回了**完全相同的 HTTP 400 + "not a valid JWT"** — 证明 JWT 解码层对内容不敏感，无论凭证内容如何，只要是裸 JSON-LD 就统一拒收。

### 8.4 变体 B（格式错误）的错误归因

| 失败层 | 具体失败原因 | Registry 对应条目 |
|--------|------------|------------------|
| **① JWT 解码** | 裸 JSON-LD | 同正确版 |
| 若穿透 → JSON-LD 处理 | `@context` 中 `gaia-x/TYPO#` 虚构 URI 无法 dereference | Registry: ontology @context |
| 若穿透 → ⑤ SHACL | `sh:pattern` × 2 — countryCode = "China" 非 ISO 3166-2 两位码 | Registry: LegalPerson SHACL shape (§5.2) |
| 若穿透 → SHACL 日期 | `validFrom = "2026年5月1日"` 非 ISO 8601 / xsd:dateTime | Registry: VC Data Model v2 shape |

**关键发现**：变体 B 的格式错误**比 SHACL 约束更早触发** — @context URI 虚构导致 JSON-LD processor 无法展开 term，SHACL engine 连 data graph 都构造不出来。这验证了 "JSON-LD → SHACL" 的双层保护。

### 8.5 伪 JWT 的错误归因

| 失败层 | 具体失败原因 | Registry 对应条目 |
|--------|------------|------------------|
| **① JWT 解码** | ✅ 通过（三段式 Base64 格式正确） | — |
| **② JWT Header** | ❌ `"The iss header referencing the issuer's DID is missing"` | Registry: issuer DID 必须在 JWT header `iss` 中声明 |

**这是最重要的发现**：伪 JWT 穿透了第 1 层，证明 7 层校验链是真实存在的。`iss` 校验是硬性要求，对应的 Registry 条目是 DID Document 中 `alsoKnownAs` 和 `verificationMethod`。

---

## 九、结论

### 9.1 为什么我们的凭证无法通过 Compliance API

根本原因：**Gaia-X Compliance API 不是单纯的 SHACL 校验器**。它要求完整的信任链：

```
JWT 签名 ← DID Resolution ← X.509 Chain ← Trust Anchor ← T&C ← Notary ← SHACL ✅
```

我们的凭证停在第一步 — 缺少 JWT 签名。即使签名通过，后续还需要：
- **可解析的 DID:WEB 文档**（目前为虚构 `did:web:energy-provider.example.org`）
- **Trust Anchor 背书的 X.509 证书链**（中国的 entity 需要 EV SSL 或 Gaia-X 直接背书）
- **Issuer T&C VC**（需签名 Gaia-X Ecosystem 条款）
- **Legal Registration Number 真实性验证**（需 LRN JWT 经 Notary API 确认）

### 9.2 给 Task 3（Registry 研究）的输入

本报告为 Task 3 "查明 Registry 中哪些 shapes/trust anchors 导致失败" 提供了完整映射：

| Error Message（实际） | 对应 Registry 条目 | 需满足的条件 |
|----------------------|-------------------|-------------|
| "not a valid JWT" | API 入口规范 | 生成 JOSE-signed VP-JWT |
| "iss header ... missing" | DID Document | did:web 可解析，含 verificationMethod |
| (预测) SHACL minCount violation | LegalPerson shape | 3 个必填字段齐全 |
| (预测) ISO 3166 pattern violation | Address shape | countryCode 为两位码 |
| (预测) T&C not accepted | T&C hash | Issuer 签发 T&C VC |
| (预测) Registration not verifiable | registrationNumberIssuer | Notary API 确认 |

### 9.3 最小合规路径

若要将此凭证推进到真正通过 Compliance API，需要以下组件（按先后顺序）：

1. 部署 DID 文档 → 使用 Gaia-X [DID:WEB Generator](https://gitlab.com/gaia-x/lab/libraries/did-web-generator)
2. 获取 X.509 证书 → 从 Gaia-X approved EV SSL CA
3. 签名凭证为 VC-JWT → 使用 [vc-jwt.io](https://gitlab.com/gaia-x/gaia-x-community/vc-jwt.io) 或 [walt.id SSI Kit](https://github.com/walt-id/waltid-ssikit)
4. 获取 LRN JWT → 调用 Gaia-X Notary API 验证真实注册号
5. 签发 T&C VC → 对 Gaia-X Ecosystem T&C 做 SHA-256 后签名
6. 组合 VP → 3 个 VC (LP + LRN + T&C) 打包为 Verifiable Presentation
7. 签名 VP-JWT → 提交到 Compliance API

这已超出"最小凭证"范围，属于正式 Gaia-X 参与者的 onboarding 流程。

---

## 十、Tagus 22.04 格式对照（参考）

为便于对照项目模板中的 Tagus 22.04 格式，以下是等价的最小 LegalPerson 凭证在该版本下的写法：

```json
{
  "@context": [
    "https://www.w3.org/2018/credentials/v1",
    { "gx": "https://w3id.org/gaia-x/development#" }
  ],
  "type": ["VerifiableCredential", "gx:LegalParticipant"],
  "issuer": "did:web:energy-provider.example.org",
  "issuanceDate": "2026-05-01T00:00:00Z",
  "credentialSubject": {
    "id": "did:web:energy-provider.example.org",
    "gx:legalName": "Energy Data Provider Ltd.",
    "gx:legalRegistrationNumber": "DEMO-ENERGY-CN-001",
    "gx:headquarterAddress": { "gx:countrySubdivisionCode": "CN-GD" },
    "gx:legalAddress": { "gx:countrySubdivisionCode": "CN-GD" }
  }
}
```

> ⚠️ 此 Tagus 格式仅作参考。Compliance API 使用 Loire (v2) 规范，应按本凭证主文件（Loire 格式）提交。

---

## 十一、参考资料

- Gaia-X Trust Framework 22.04 PDF — 第 6-7 页 (LegalPerson 属性表)
- Gaia-X ICAM 文档 25.11 — [Credential Format](https://docs.gaia-x.eu/technical-committee/identity-credential-access-management/25.11/gaia-x_credentials/)
- Gaia-X Ontology — [LegalPerson Class](https://docs.gaia-x.eu/ontology/development/classes/LegalPerson/)
- 官方 LegalPerson 示例 — [gaia-x.eu/.well-known/legal-person.json](https://gaia-x.eu/.well-known/legal-person.json)
- Gaia-X Compliance Document — [Process](https://gaia-x.gitlab.io/policy-rules-committee/compliance-document/Process/)
- 项目场景 — `DSSC_Toolbox_Scenario.md` B 组任务
