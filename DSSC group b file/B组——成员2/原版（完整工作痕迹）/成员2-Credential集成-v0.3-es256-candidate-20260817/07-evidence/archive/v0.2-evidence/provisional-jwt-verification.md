# Provisional JWT Verification

> Development-only result. This does not establish Gaia-X compliance.

| File | Segments | Algorithm | Type | kid matches | Signature valid | Result |
|---|---:|---|---|---|---|---|
| `legal-person.provisional.vc.jwt` | 3 | `RS256` | `vc+jwt` | True | True | PASS |
| `service-offering.provisional.vc.jwt` | 3 | `RS256` | `vc+jwt` | True | True | PASS |
| `presentation.provisional.vp.jwt` | 3 | `RS256` | `vp+jwt` | True | True | PASS |

Overall local cryptographic verification: **PASS**

The placeholder DID is not publicly resolvable. These JWTs must be
reissued with the official DID, kid and key material before API testing.