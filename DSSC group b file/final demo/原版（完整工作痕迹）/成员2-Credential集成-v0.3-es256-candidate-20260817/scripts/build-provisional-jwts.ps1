[CmdletBinding()]
param(
    [string]$PrivateJwkPath,
    [ValidateRange(1, 365)]
    [int]$ValidDays = 30
)

$ErrorActionPreference = 'Stop'

$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$configPath = Join-Path $projectRoot '02-config\demo-config.json'
$legalPersonPath = Join-Path $projectRoot '04-credential-source\legal-person.jsonld'
$serviceOfferingPath = Join-Path $projectRoot '04-credential-source\service-offering.jsonld'
$outputDirectory = Join-Path $projectRoot '05-signed\provisional'
$inspectionDirectory = Join-Path $projectRoot '07-evidence\provisional-jwt-inspection'

if ([string]::IsNullOrWhiteSpace($PrivateJwkPath)) {
    if ([string]::IsNullOrWhiteSpace($env:LOCALAPPDATA)) {
        throw 'LOCALAPPDATA is unavailable. Pass -PrivateJwkPath explicitly.'
    }

    $PrivateJwkPath = Join-Path $env:LOCALAPPDATA 'DSSC-Credential-Dev\dev-rsa-private.jwk'
}

foreach ($requiredPath in @($configPath, $legalPersonPath, $serviceOfferingPath, $PrivateJwkPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}

New-Item -ItemType Directory -Force -Path $outputDirectory | Out-Null
New-Item -ItemType Directory -Force -Path $inspectionDirectory | Out-Null

function ConvertTo-Base64Url {
    param([Parameter(Mandatory)][byte[]]$Bytes)

    [Convert]::ToBase64String($Bytes).TrimEnd('=').Replace('+', '-').Replace('/', '_')
}

function ConvertFrom-Base64Url {
    param([Parameter(Mandatory)][string]$Value)

    $base64 = $Value.Replace('-', '+').Replace('_', '/')
    switch ($base64.Length % 4) {
        2 { $base64 += '==' }
        3 { $base64 += '=' }
    }
    [Convert]::FromBase64String($base64)
}

function ConvertTextTo-Base64Url {
    param([Parameter(Mandatory)][string]$Value)

    ConvertTo-Base64Url ([Text.Encoding]::UTF8.GetBytes($Value))
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

function New-RsaFromPrivateJwk {
    param([Parameter(Mandatory)]$Jwk)

    $parameters = New-Object Security.Cryptography.RSAParameters
    $parameters.Modulus = ConvertFrom-Base64Url $Jwk.n
    $parameters.Exponent = ConvertFrom-Base64Url $Jwk.e
    $parameters.D = ConvertFrom-Base64Url $Jwk.d
    $parameters.P = ConvertFrom-Base64Url $Jwk.p
    $parameters.Q = ConvertFrom-Base64Url $Jwk.q
    $parameters.DP = ConvertFrom-Base64Url $Jwk.dp
    $parameters.DQ = ConvertFrom-Base64Url $Jwk.dq
    $parameters.InverseQ = ConvertFrom-Base64Url $Jwk.qi

    $rsa = [Security.Cryptography.RSA]::Create()
    $rsa.ImportParameters($parameters)
    $rsa
}

function New-SignedJwt {
    param(
        [Parameter(Mandatory)]$Header,
        [Parameter(Mandatory)]$Payload,
        [Parameter(Mandatory)][Security.Cryptography.RSA]$Rsa
    )

    $headerJson = $Header | ConvertTo-Json -Compress -Depth 20
    $payloadJson = $Payload | ConvertTo-Json -Compress -Depth 40
    $encodedHeader = ConvertTextTo-Base64Url $headerJson
    $encodedPayload = ConvertTextTo-Base64Url $payloadJson
    $signingInput = "$encodedHeader.$encodedPayload"
    $signingBytes = [Text.Encoding]::ASCII.GetBytes($signingInput)
    $signature = $Rsa.SignData(
        $signingBytes,
        [Security.Cryptography.HashAlgorithmName]::SHA256,
        [Security.Cryptography.RSASignaturePadding]::Pkcs1
    )

    "$signingInput.$(ConvertTo-Base64Url $signature)"
}

function Set-CredentialValidity {
    param(
        [Parameter(Mandatory)]$Credential,
        [Parameter(Mandatory)][string]$IssuerDid,
        [Parameter(Mandatory)][string]$ValidFrom,
        [Parameter(Mandatory)][string]$ValidUntil
    )

    $Credential | Add-Member -NotePropertyName issuer -NotePropertyValue $IssuerDid -Force
    $Credential | Add-Member -NotePropertyName validFrom -NotePropertyValue $ValidFrom -Force
    $Credential | Add-Member -NotePropertyName validUntil -NotePropertyValue $ValidUntil -Force
    $Credential
}

$config = Get-Content -Raw -Encoding UTF8 -LiteralPath $configPath | ConvertFrom-Json
$development = $config.developmentSigning

if (-not $development.enabled) {
    throw 'developmentSigning.enabled is not true in demo-config.json.'
}

$issuerDid = [string]$development.issuerDid
$holderDid = [string]$development.holderDid
$kid = [string]$development.kid

if ([string]::IsNullOrWhiteSpace($issuerDid) -or
    [string]::IsNullOrWhiteSpace($holderDid) -or
    [string]::IsNullOrWhiteSpace($kid)) {
    throw 'Development issuerDid, holderDid and kid must be present in demo-config.json.'
}

$privateJwk = Get-Content -Raw -Encoding UTF8 -LiteralPath $PrivateJwkPath | ConvertFrom-Json

if ($privateJwk.kid -ne $kid) {
    throw "Private JWK kid '$($privateJwk.kid)' does not match config kid '$kid'."
}

$rsa = New-RsaFromPrivateJwk $privateJwk

try {
    $now = [DateTimeOffset]::UtcNow
    $validFrom = $now.ToString('o')
    $validUntil = $now.AddDays($ValidDays).ToString('o')

    $vcHeader = [ordered]@{
        alg = 'RS256'
        typ = 'vc+jwt'
        cty = 'vc'
        iss = $issuerDid
        kid = $kid
    }

    $legalPerson = Get-Content -Raw -Encoding UTF8 -LiteralPath $legalPersonPath | ConvertFrom-Json
    $serviceOffering = Get-Content -Raw -Encoding UTF8 -LiteralPath $serviceOfferingPath | ConvertFrom-Json

    $legalPerson = Set-CredentialValidity $legalPerson $issuerDid $validFrom $validUntil
    $serviceOffering = Set-CredentialValidity $serviceOffering $issuerDid $validFrom $validUntil

    $legalPersonJwt = New-SignedJwt $vcHeader $legalPerson $rsa
    $serviceOfferingJwt = New-SignedJwt $vcHeader $serviceOffering $rsa

    $vpPayload = [ordered]@{
        '@context' = @('https://www.w3.org/ns/credentials/v2')
        type = 'VerifiablePresentation'
        verifiableCredential = @(
            [ordered]@{
                '@context' = 'https://www.w3.org/ns/credentials/v2'
                id = "data:application/vc+jwt,$legalPersonJwt"
                type = 'EnvelopedVerifiableCredential'
            },
            [ordered]@{
                '@context' = 'https://www.w3.org/ns/credentials/v2'
                id = "data:application/vc+jwt,$serviceOfferingJwt"
                type = 'EnvelopedVerifiableCredential'
            }
        )
        issuer = $holderDid
        validFrom = $validFrom
        validUntil = $validUntil
    }

    $vpHeader = [ordered]@{
        alg = 'RS256'
        typ = 'vp+jwt'
        cty = 'vp'
        iss = $holderDid
        kid = $kid
    }

    $vpJwt = New-SignedJwt $vpHeader $vpPayload $rsa

    $legalOutput = Join-Path $outputDirectory 'legal-person.provisional.vc.jwt'
    $serviceOutput = Join-Path $outputDirectory 'service-offering.provisional.vc.jwt'
    $vpOutput = Join-Path $outputDirectory 'presentation.provisional.vp.jwt'

    Write-Utf8NoBom $legalOutput $legalPersonJwt
    Write-Utf8NoBom $serviceOutput $serviceOfferingJwt
    Write-Utf8NoBom $vpOutput $vpJwt

    Write-Utf8NoBom (Join-Path $inspectionDirectory 'legal-person.header.json') (
        $vcHeader | ConvertTo-Json -Depth 10
    )
    Write-Utf8NoBom (Join-Path $inspectionDirectory 'legal-person.payload.json') (
        $legalPerson | ConvertTo-Json -Depth 40
    )
    Write-Utf8NoBom (Join-Path $inspectionDirectory 'service-offering.header.json') (
        $vcHeader | ConvertTo-Json -Depth 10
    )
    Write-Utf8NoBom (Join-Path $inspectionDirectory 'service-offering.payload.json') (
        $serviceOffering | ConvertTo-Json -Depth 40
    )
    Write-Utf8NoBom (Join-Path $inspectionDirectory 'presentation.header.json') (
        $vpHeader | ConvertTo-Json -Depth 10
    )
    Write-Utf8NoBom (Join-Path $inspectionDirectory 'presentation.payload.json') (
        $vpPayload | ConvertTo-Json -Depth 40
    )
}
finally {
    $rsa.Dispose()
}

Write-Host 'Provisional development JWTs generated.' -ForegroundColor Green
Write-Host "Output directory: $outputDirectory"
Write-Host "Inspection directory: $inspectionDirectory"
Write-Warning 'These JWTs use an unresolvable placeholder DID and are NOT compliance-valid.'
Write-Warning 'Reissue every JWT after the official DID, kid and key material arrive.'

