# Official VP Local Validation

## Validation source

- Repository: `https://github.com/MaxVer11111/DSSC-project`
- Branch: `main`
- Reviewed commit: `f1992e3`
- Script: `DSSC group b file/任务结果/run-compliance-demo.ps1`

## Execution mode

Local validation only. The `-Submit` option was not used, so no Compliance API
network request was sent.

## Actual result

| Item | Observed value |
|---|---|
| VP algorithm | `RS256` |
| VP token type | `vp+jwt` |
| VP issuer | `did:web:vc-jwt.io` |
| VP valid from | `2026-08-09T09:13:02.034+00:00` |
| VP valid until | `2026-11-07T09:13:02.035+00:00` |
| Embedded credential count | `3` |
| Local validation | `PASS` |

The embedded credentials were:

1. `LegalPerson.jwt` — `VerifiableCredential, gx:LegalPerson`;
2. `Issuer.jwt` — `VerifiableCredential, gx:Issuer`;
3. `LegalRegistrationNumber.jwt` — `VerifiableCredential, gx:VatID`.

PowerShell ended with:

```text
Local validation passed.
No network request was sent.
Run the script again with -Submit to call the Compliance API.
```

## Conclusion

The official sample VP passed local structural validation. This proves that the
downloaded official sample has the expected VP-JWT structure; it does not prove
that the project identity `Energy Data Provider Ltd.` is compliant.

The official DID, `kid`, registration number and signed JWTs must not be reused
as the project identity.

