[CmdletBinding()]
param(
    [string]$IssuerDid = 'did:web:mp-operations.org',
    [string]$Kid,
    [string]$PrivateJwkPath
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($Kid)) {
    $Kid = "$IssuerDid#dev-key-1"
}

if ([string]::IsNullOrWhiteSpace($PrivateJwkPath)) {
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        throw 'LOCALAPPDATA is unavailable. Pass -PrivateJwkPath explicitly.'
    }

    $secretDirectory = Join-Path $env:LOCALAPPDATA 'DSSC-Credential-Dev'
    $PrivateJwkPath = Join-Path $secretDirectory 'dev-rsa-private.jwk'
}
else {
    $secretDirectory = Split-Path -Parent $PrivateJwkPath
}

if (-not (Test-Path -LiteralPath $secretDirectory)) {
    New-Item -ItemType Directory -Path $secretDirectory -Force | Out-Null
}

if (Test-Path -LiteralPath $PrivateJwkPath) {
    throw "Refusing to overwrite an existing private key: $PrivateJwkPath"
}

function ConvertTo-Base64Url {
    param([Parameter(Mandatory)][byte[]]$Bytes)

    [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function Write-Utf8NoBom {
    param(
        [Parameter(Mandatory)][string]$Path,
        [Parameter(Mandatory)][string]$Value
    )

    [IO.File]::WriteAllText(
        $Path,
        $Value,
        (New-Object Text.UTF8Encoding($false))
    )
}

$rsa = New-Object Security.Cryptography.RSACryptoServiceProvider -ArgumentList 2048

try {
    $parameters = $rsa.ExportParameters($true)

    $privateJwk = [ordered]@{
        kty = 'RSA'
        use = 'sig'
        alg = 'RS256'
        kid = $Kid
        n   = ConvertTo-Base64Url $parameters.Modulus
        e   = ConvertTo-Base64Url $parameters.Exponent
        d   = ConvertTo-Base64Url $parameters.D
        p   = ConvertTo-Base64Url $parameters.P
        q   = ConvertTo-Base64Url $parameters.Q
        dp  = ConvertTo-Base64Url $parameters.DP
        dq  = ConvertTo-Base64Url $parameters.DQ
        qi  = ConvertTo-Base64Url $parameters.InverseQ
    }

    Write-Utf8NoBom -Path $PrivateJwkPath -Value (
        $privateJwk | ConvertTo-Json -Depth 5
    )

    $publicJwk = [ordered]@{
        kty = 'RSA'
        use = 'sig'
        alg = 'RS256'
        kid = $Kid
        n   = $privateJwk.n
        e   = $privateJwk.e
    }

    $didDocument = [ordered]@{
        '@context' = @(
            'https://www.w3.org/ns/did/v1',
            'https://w3id.org/security/suites/jws-2020/v1'
        )
        id = $IssuerDid
        verificationMethod = @(
            [ordered]@{
                id = $Kid
                type = 'JsonWebKey2020'
                controller = $IssuerDid
                publicKeyJwk = $publicJwk
            }
        )
        assertionMethod = @($Kid)
        authentication = @($Kid)
    }

    $publicOutputPath = [IO.Path]::GetFullPath(
        (Join-Path $PSScriptRoot '..\07-evidence\development-did-document.unpublished.json')
    )

    Write-Utf8NoBom -Path $publicOutputPath -Value (
        $didDocument | ConvertTo-Json -Depth 10
    )
}
finally {
    $rsa.Dispose()
}

Write-Host 'Development RSA key pair generated.' -ForegroundColor Green
Write-Host "Private JWK (outside repository): $PrivateJwkPath"
Write-Host "Public DID Document (UNPUBLISHED): $publicOutputPath"
Write-Host "Development kid: $Kid"
Write-Warning 'This key and DID are for local pipeline testing only.'
Write-Warning 'Never upload the private JWK to GitHub, chat, email, or the project ZIP.'

