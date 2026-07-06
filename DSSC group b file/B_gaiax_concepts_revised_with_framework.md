# B Group Notes: Gaia-X Compliance Service and Registry

## 1. Background

This note summarizes the main concepts needed for Group B's work on the Gaia-X Compliance Service and Gaia-X Registry. In the overall data space toolchain, Group B focuses on the trust and compliance layer. The main question is not how data is exchanged, but how a data space can verify that a participant, service, or data offering is described correctly, signed by the right party, and compliant with Gaia-X rules. The Gaia-X Trust Framework 22.04 is treated here as an official baseline reference for understanding the minimum trust and compliance requirements.

In a data space, different organizations need to interact without relying on informal trust. Gaia-X addresses this by using machine-verifiable descriptions and credentials. A participant describes itself and its services through structured metadata. These descriptions are represented as Verifiable Credentials and submitted as Verifiable Presentations. The Compliance Service then validates them using rules, schemas, trust anchors, public keys, and revocation information provided or referenced through the Gaia-X trust infrastructure, including the Registry.

A simplified process is:

```text
Participant / Provider
        ↓
Self-Description of participant, service, or resource
        ↓
Verifiable Credential (VC)
        ↓
Verifiable Presentation (VP)
        ↓
Gaia-X Compliance Service validation
        ↓
Gaia-X Compliance Credential or validation failure
```

According to the Gaia-X Trust Framework 22.04, the Trust Framework defines the compulsory minimum baseline rules for entities that want to be part of the Gaia-X ecosystem. These rules apply to Gaia-X Self-Description files for participants, service offerings, and resources. The document also states that the compliance process is automated and versioned, which explains why Group B should focus not only on the concepts but also on what a validation service checks and why a validation result succeeds or fails.

The same document identifies four major types of trust-framework rules:

- serialization format and syntax;
- cryptographic signature validation and validation of the keypair-associated identity;
- attribute value consistency;
- attribute veracity verification.

This is a useful checklist for the Group B demo: a valid example should not only have the right fields, but also the correct format, valid signatures, trusted key material, consistent values, and verifiable claims.

---

## 2. Self-Description

A Self-Description is a machine-readable description of a Gaia-X participant, service, resource, or data offering. It explains what the entity is, who provides it, what properties it has, and which terms or policies apply to it.

For example, in the project scenario of an energy data space, a provider may publish a data offering for building-level hourly electricity consumption data. Its Self-Description should state information such as:

- the legal identity of the provider;
- the service or data product being offered;
- the type and granularity of the data;
- access conditions and usage policies;
- relevant compliance or terms-and-conditions statements.

The key point is that a Self-Description is not just a natural-language introduction. It is structured metadata intended to be processed by software. The Gaia-X Trust Framework 22.04 describes Gaia-X Self-Description files as machine-readable text files, cryptographically signed to prevent tampering, using linked data to describe attributes, and following the W3C Verifiable Credentials Data Model. In Gaia-X, Self-Descriptions are therefore commonly represented through Verifiable Credentials so that the statements can be signed, verified, and checked against compliance rules.

In short, the Self-Description is the content layer: it says what is being claimed about the participant, service, or resource.

---

## 3. Verifiable Credential (VC)

A Verifiable Credential is a digitally signed, machine-verifiable statement about a subject. It is similar in function to a certificate or proof document, but it is designed for automated verification.

A VC usually contains:

- an `issuer`: the entity that issues the credential;
- a `credentialSubject`: the entity or object being described;
- claims about that subject;
- validity information, such as issue date or expiration date;
- a `proof` or signature;
- optionally, a `credentialStatus` field for revocation checking.

A simplified example is:

```json
{
  "issuer": "did:web:example-provider.eu",
  "credentialSubject": {
    "id": "did:web:example-provider.eu",
    "type": "LegalPerson",
    "name": "Example Energy Data Provider"
  },
  "validFrom": "2026-01-01T00:00:00Z",
  "credentialStatus": "status-list-or-revocation-reference",
  "proof": "digital-signature"
}
```

The role of the VC is to make claims verifiable. A verifier can check whether the credential was issued by the stated issuer, whether the credential content has been modified, and whether the credential is still valid.

In Gaia-X, VCs may be used to represent legal person information, terms-and-conditions acceptance, service offering descriptions, registration number information, or compliance results.

---

## 4. Verifiable Presentation (VP)

A Verifiable Presentation is a package of one or more Verifiable Credentials submitted to a verifier. If a VC is one signed statement, a VP is the set of signed statements presented together for a specific verification purpose.

For a Gaia-X compliance check, a provider may need to submit several credentials at the same time, such as:

- a Legal Person Credential;
- a Legal Registration Number Credential;
- a Terms and Conditions Credential;
- a Service Offering Credential;
- a Data Product or Resource Description Credential.

These credentials can be combined into a VP and submitted to the Gaia-X Compliance Service. The Compliance Service then validates both the individual credentials and the consistency of the submitted package.

The distinction is:

| Concept | Meaning | Function |
|---|---|---|
| Verifiable Credential | One signed claim or set of claims | Proves something about a subject |
| Verifiable Presentation | A package of one or more VCs | Presents credentials to a verifier |

---

## 5. SHACL Shape

SHACL stands for Shapes Constraint Language. It is used to define validation rules for RDF or JSON-LD data. Since Gaia-X descriptions are intended to be machine-readable and semantically structured, SHACL shapes can be used to check whether a description follows the expected structure.

A SHACL shape can specify rules such as:

- a required property must be present;
- a property must have a certain datatype;
- a property must appear at least or at most a certain number of times;
- a value must belong to a defined class or controlled vocabulary;
- a service offering must be linked to a provider or policy.

For example, a simplified rule for a service offering could be:

```text
A ServiceOffering must have:
- a provider;
- a service title or name;
- terms and conditions;
- access or usage policy information.
```

If a submitted Self-Description lacks a required field, the SHACL validation fails. This is important because Gaia-X compliance is not only about whether a credential is signed. It also checks whether the submitted content follows the required semantic model and policy structure.

In the Group B context, SHACL shapes can be understood as the structural validation rules used by the compliance process.

---

## 6. Trust Anchor

A Trust Anchor is a trusted starting point in a trust chain. It represents an entity, registry, key source, or authority that the system already recognizes as trustworthy.

Digital signatures alone are not enough. A signature can prove that a credential was signed by a certain key, but it does not automatically prove that the signer is trusted in the Gaia-X ecosystem. Trust anchors provide the basis for deciding whether an issuer or key source should be accepted.

For example:

```text
Signature validation answers:
Was this credential signed by the corresponding private key?

Trust validation answers:
Is the signer or issuer recognized as trustworthy under the governance framework?
```

In Gaia-X, trust anchors and related trust information are part of the trust infrastructure. The Gaia-X Trust Framework 22.04 defines trust anchors as Gaia-X-endorsed entities responsible for managing certificates used to sign claims. It also states that all keypairs used to sign claims must have at least one Trust Anchor in their certificate chain, and that the current list of valid Trust Anchors is stored in the Gaia-X Registry. The Registry is therefore relevant because it provides or references trusted governance artefacts, trust anchor information, schemas, and validation materials used by compliance components.

---

## 7. Public Key

A public key is used to verify a digital signature. It is paired with a private key:

- the private key is kept secret and used to sign credentials;
- the public key is shared and used by others to verify signatures.

When an issuer signs a Verifiable Credential, it uses its private key. A verifier uses the corresponding public key to check whether the credential was really signed by that issuer and whether the content has been changed after signing.

In a Gaia-X compliance process, public keys are needed to verify:

- the signature of each submitted VC;
- the signature of the VP, if applicable;
- the signature of the Gaia-X Compliance Credential returned by the Compliance Service.

The public key only solves the cryptographic verification problem. It does not by itself prove that the issuer is trusted. That requires trust anchor and governance checks.

---

## 8. Revocation

Revocation means that a credential, key, or trust status is invalidated before its normal expiration time. This is necessary because a credential that was valid when issued may become invalid later.

Possible reasons for revocation include:

- the credential was issued incorrectly;
- the legal status of a participant changed;
- a service is no longer compliant;
- the issuer's private key was compromised;
- the issuer or participant is no longer trusted;
- the credential subject no longer satisfies the original claim.

A VC may contain a `credentialStatus` field that allows a verifier to check whether the credential has been revoked. Therefore, validation should not only check the signature and expiration date. It should also check the current status of the credential.

The basic validation logic is:

```text
1. Is the credential format valid?
2. Is the signature valid?
3. Is the issuer trusted?
4. Is the credential expired?
5. Has the credential been revoked?
6. Does the content satisfy the required shapes and policy rules?
```

Revocation is important because trust is time-dependent. A statement can be valid in the past but no longer acceptable in the present.

---

## 9. Gaia-X Registry

The Gaia-X Registry is a trust-related component that provides or references governance and validation artefacts needed by Gaia-X services. It is not a repository for business data. Instead, it supports compliance and trust verification.

The Registry may include or reference materials such as:

- schemas;
- SHACL shapes;
- trust anchor information;
- terms and conditions;
- governance documents;
- information relevant to credential and trust validation.

For Group B, the Registry can be understood as the place where the Compliance Service obtains part of the trusted reference material used during validation. It supports the question: what rules and trusted sources should the validator rely on?

---

## 10. Gaia-X Compliance Service

The Gaia-X Compliance Service validates submitted Verifiable Presentations against Gaia-X requirements. It checks whether the credentials are structurally correct, signed, trustworthy, and compliant with the relevant rules.

Typical checks include:

- whether the VP is in the expected format;
- whether each VC has a valid signature;
- whether the issuer can be trusted;
- whether the relevant public keys are valid;
- whether credentials are expired or revoked;
- whether the Self-Description satisfies SHACL shapes;
- whether the submitted claims satisfy Gaia-X policy rules.

If validation succeeds, the Compliance Service issues a Gaia-X Compliance Credential. This new credential acts as machine-verifiable evidence that the submitted material passed the compliance check.

If validation fails, the result should indicate the reason, such as a missing required field, invalid signature, untrusted issuer, revoked credential, or SHACL validation error.

---

## 11. How the Concepts Work Together

The concepts can be connected as follows:

```text
Trust Anchor
   ↓ establishes trusted issuers / key sources
Issuer
   ↓ signs claims using a private key
Verifiable Credential
   ↓ contains signed claims about a participant, service, or resource
Holder / Provider
   ↓ packages multiple credentials
Verifiable Presentation
   ↓ submitted for compliance validation
Gaia-X Compliance Service
   ↓ checks signatures, trust, revocation, SHACL shapes, and policy rules
Compliance Credential or Validation Failure
```

In this process:

- Self-Description provides the structured claims.
- VC provides a signed and verifiable format for those claims.
- VP provides a package for submitting multiple credentials.
- SHACL shapes provide structural validation rules.
- Trust anchors define the trusted starting points.
- Public keys enable signature verification.
- Revocation prevents outdated or compromised credentials from being accepted.
- The Registry provides trusted reference materials for the compliance process.
- The Compliance Service performs the validation and returns the result.

---

## 12. Minimal Scenario for the Project

The project scenario is an energy data space. A provider wants to publish building-level hourly electricity consumption data as a data product or service.

A minimal Group B example could use the following materials:

1. **Provider Legal Person Credential**  
   States that the provider is a legal entity.

2. **Terms and Conditions Credential**  
   States that the provider accepts Gaia-X terms and conditions.

3. **Service Offering Self-Description / Credential**  
   Describes the service that provides access to the electricity consumption data. At minimum, the Trust Framework example suggests that a service offering should include a `providedBy` link to the participant Self-Description and `termsAndConditions` information. It may also include `aggregationOf` links to related resources and `policies`, for example expressed in ODRL or Rego.

4. **Data Product / Resource Description**  
   Describes the offered data, such as hourly electricity consumption, building scope, format, access method, and usage policy. In the Gaia-X model, a dataset can be treated as a virtual resource. Relevant resource-level information can include copyright ownership, licence information, related physical or virtual resources, and endpoint information if the resource is exposed through a running API.

5. **Verifiable Presentation**  
   Packages the above credentials and descriptions for submission to the Compliance Service.

The expected validation results can be recorded in two categories.

Successful validation may indicate:

- required fields are present;
- credential signatures are valid;
- issuers are trusted;
- credentials are not expired or revoked;
- submitted descriptions satisfy SHACL shapes;
- Gaia-X policy rules are satisfied.

Failed validation may be caused by:

- missing required fields in the Self-Description;
- incorrect JSON-LD or RDF structure;
- invalid or missing signature;
- issuer not connected to a trusted anchor;
- revoked credential;
- expired credential;
- failure to satisfy Gaia-X policy rules.

---

## 13. Notes from Gaia-X Trust Framework 22.04 for the Demo

The Gaia-X Trust Framework 22.04 adds several concrete points that are useful for Group B's project deliverable.

### 13.1 Scope of Validation

The framework applies to Self-Descriptions of three main entity categories:

- **Participant**, including legal persons and natural persons;
- **Service Offering**;
- **Resource**.

For the energy data space scenario, this means the demo should not only describe the data product. It should also show the relation between:

```text
Provider / Participant
        ↓ providedBy
Service Offering
        ↓ aggregationOf
Resource / Dataset / API
```

### 13.2 Participant-Level Fields

For a legal person, the Trust Framework lists fields such as:

- `registrationNumber`;
- `headquarterAddress.country`;
- `legalAddress.country`;
- optional `leiCode`;
- optional parent or subsidiary organization links.

The document also gives consistency rules. For example, if an LEI code is used, the LEI headquarters country should match `headquarterAddress.country`, and the LEI legal country should match `legalAddress.country`.

### 13.3 Service Offering-Level Fields

For a service offering, useful fields include:

- `providedBy`: a resolvable link to the participant Self-Description providing the service;
- `aggregationOf`: links to related resources;
- `termsAndConditions`: links to the applicable terms and conditions;
- `policies`: optional policy expressions, for example in Rego or ODRL.

The Terms and Conditions structure includes:

- `URL`: a resolvable link to the terms document;
- `hash`: a SHA-256 hash of that document.

This gives Group B a concrete validation point: a service may fail if the terms link or hash is missing, invalid, or inconsistent.

### 13.4 Resource-Level Fields

For a virtual resource such as a dataset, the framework lists fields such as:

- `copyrightOwnedBy`;
- `license`.

For an instantiated virtual resource such as a running API, it lists fields such as:

- `maintainedBy`;
- `hostedOn`;
- `tenantOwnedBy`;
- `endpoint`.

This is useful for the project scenario because the building-hourly-electricity data can be described as a dataset, while the API exposing it can be described as an instantiated virtual resource.

### 13.5 Suggested Minimal Failure Cases

Based on the Trust Framework, the demo can include several simple failure cases:

| Failure Case | Expected Reason |
|---|---|
| Missing `providedBy` in Service Offering | Required participant link is absent |
| Missing `termsAndConditions` | Required terms information is absent |
| Incorrect terms hash | Terms document integrity cannot be verified |
| Missing `registrationNumber` for legal person | Required legal identity attribute is absent |
| Country code not in expected ISO format | Attribute value consistency error |
| Signature chain does not connect to a Trust Anchor | Keypair-associated identity is not trusted |
| Dataset has no `license` | Resource-level required attribute is absent |

These examples are simple enough to explain in a presentation while still being directly linked to the official framework.

---

## 14. Relation to Other Groups

In the whole data space onboarding workflow, Group B connects to the other groups as follows:

```text
Group C: defines semantic model and metadata structure
        ↓
Group A: publishes data offering and supports discovery / exchange
        ↓
Group B: verifies participant, service, and credentials for trust and compliance
        ↓
Group D: validates metadata and reports valid / invalid results
```

Group B therefore focuses on whether the provider and service can be trusted and whether their credentials pass Gaia-X compliance checks. It does not primarily focus on API packaging, semantic model design, or general metadata testing, although it depends on those parts in the complete onboarding workflow.

---

## 15. Short Summary

Group B studies the trust and compliance layer of Gaia-X-based data space onboarding. The main task is to understand how Self-Descriptions are represented as Verifiable Credentials, how multiple credentials are submitted as a Verifiable Presentation, and how the Gaia-X Compliance Service validates them using SHACL shapes, public keys, trust anchors, revocation information, policy rules, and Registry-based reference materials. The output of this process is either a Gaia-X Compliance Credential or a validation failure report.

