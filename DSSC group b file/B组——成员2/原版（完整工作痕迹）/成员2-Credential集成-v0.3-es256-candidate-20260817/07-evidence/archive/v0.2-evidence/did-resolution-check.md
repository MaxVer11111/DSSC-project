# DID Resolution Check

## Tested DID

`did:web:mp-operations.org`

## Expected DID Document URL

`https://mp-operations.org/.well-known/did.json`

## Test command

```powershell
Invoke-WebRequest `
  -Uri "https://mp-operations.org/.well-known/did.json" `
  -UseBasicParsing
```

## Actual result

```text
Invoke-WebRequest : 未能解析此远程名称: 'mp-operations.org'
FullyQualifiedErrorId:
WebCmdletWebResponseException,
Microsoft.PowerShell.Commands.InvokeWebRequestCommand
```

## Result

`FAIL — DNS_RESOLUTION_FAILED`

## Meaning

The domain `mp-operations.org` could not be resolved. Therefore, the
corresponding DID Document could not be downloaded.

The DID is internally consistent across the current project files, but it is
not currently usable as a publicly resolvable signing identity.

## Impact

The following formal signing steps are blocked:

- DID Document retrieval;
- verification method lookup;
- `kid` confirmation;
- public key retrieval;
- externally verifiable VC-JWT and VP-JWT signatures.

## Current decision

Keep `did:web:mp-operations.org` as a provisional cross-file identifier. It may
be used only to exercise the local development signing pipeline. Do not call
development output a valid compliance credential, and reissue every JWT after
the project leader provides the real DID and matching key material.

