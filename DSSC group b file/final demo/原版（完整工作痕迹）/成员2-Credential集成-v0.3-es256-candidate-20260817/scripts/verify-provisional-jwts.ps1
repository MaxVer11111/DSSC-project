[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'

$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..'))
$configPath = Join-Path $projectRoot '02-config\demo-config.json'
$didDocumentPath = Join-Path $projectRoot '07-evidence\development-did-document.unpublished.json'
$jwtDirectory = Join-Path $projectRoot '05-signed\provisional'
$reportPath = Join-Path $projectRoot '07-evidence\provisional-jwt-verification.md'

function ConvertFrom-Base64Url {
    param([Parameter(Mandatory)][string]$Value)

    $base64 = $Value.Replace('-', '+').Replace('_', '/')
    switch ($base64.Length % 4) {
        2 { $base64 += '==' }
        3 { $base64 += '=' }
    }
    [Convert]::FromBase64String($base64)
}

function ConvertFrom-Base64UrlText {
    param([Parameter(Mandatory)][string]$Value)

    [Text.Encoding]::UTF8.GetString((ConvertFrom-Base64Url $Value))
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

foreach ($requiredPath in @($configPath, $didDocumentPath)) {
    if (-not (Test-Path -LiteralPath $requiredPath -PathType Leaf)) {
        throw "Required file not found: $requiredPath"
    }
}

$config = Get-Content -Raw -Encoding UTF8 -LiteralPath $configPath | ConvertFrom-Json
$didDocument = Get-Content -Raw -Encoding UTF8 -LiteralPath $didDocumentPath | ConvertFrom-Json
$kid = [string]$config.developmentSigning.kid
$method = @($didDocument.verificationMethod | Where-Object { $_.id -eq $kid })

if ($method.Count -ne 1) {
    throw "Expected exactly one verificationMethod for kid '$kid'; found $($method.Count)."
}

$publicJwk = $method[0].publicKeyJwk
$parameters = New-Object Security.Cryptography.RSAParameters
$parameters.Modulus = ConvertFrom-Base64Url $publicJwk.n
$parameters.Exponent = ConvertFrom-Base64Url $publicJwk.e
$rsa = [Security.Cryptography.RSA]::Create()
$rsa.ImportParameters($parameters)

$cases = @(
    [ordered]@{
        File = 'legal-person.provisional.vc.jwt'
        ExpectedType = 'vc+jwt'
    },
    [ordered]@{
        File = 'service-offering.provisional.vc.jwt'
        ExpectedType = 'vc+jwt'
    },
    [ordered]@{
        File = 'presentation.provisional.vp.jwt'
        ExpectedType = 'vp+jwt'
    }
)

$results = @()

try {
    foreach ($case in $cases) {
        $path = Join-Path $jwtDirectory $case.File

        if (-not (Test-Path -LiteralPath $path -PathType Leaf)) {
            throw "JWT file not found: $path"
        }

        $token = (Get-Content -Raw -Encoding UTF8 -LiteralPath $path).Trim()
        $parts = $token.Split('.')

        if ($parts.Count -ne 3) {
            throw "JWT '$($case.File)' does not contain exactly 3 segments."
        }

        $header = ConvertFrom-Base64UrlText $parts[0] | ConvertFrom-Json
        $null = ConvertFrom-Base64UrlText $parts[1] | ConvertFrom-Json
        $signature = ConvertFrom-Base64Url $parts[2]
        $signingInput = [Text.Encoding]::ASCII.GetBytes("$($parts[0]).$($parts[1])")
        $signatureValid = $rsa.VerifyData(
            $signingInput,
            $signature,
            [Security.Cryptography.HashAlgorithmName]::SHA256,
            [Security.Cryptography.RSASignaturePadding]::Pkcs1
        )

        $resultValue = if (
            $parts.Count -eq 3 -and
            $header.alg -eq 'RS256' -and
            $header.typ -eq $case.ExpectedType -and
            $header.kid -eq $kid -and
            $signatureValid
        ) { 'PASS' } else { 'FAIL' }

        $results += [PSCustomObject]@{
            File = $case.File
            Segments = $parts.Count
            Algorithm = $header.alg
            Type = $header.typ
            KidMatches = ($header.kid -eq $kid)
            SignatureValid = $signatureValid
            Result = $resultValue
        }
    }
}
finally {
    $rsa.Dispose()
}

$results | Format-Table -AutoSize

$overall = if (@($results | Where-Object { $_.Result -ne 'PASS' }).Count -eq 0) {
    'PASS'
}
else {
    'FAIL'
}

$lines = @(
    '# Provisional JWT Verification',
    '',
    '> Development-only result. This does not establish Gaia-X compliance.',
    '',
    '| File | Segments | Algorithm | Type | kid matches | Signature valid | Result |',
    '|---|---:|---|---|---|---|---|'
)

foreach ($result in $results) {
    $lines += "| ``$($result.File)`` | $($result.Segments) | ``$($result.Algorithm)`` | ``$($result.Type)`` | $($result.KidMatches) | $($result.SignatureValid) | $($result.Result) |"
}

$lines += @(
    '',
    "Overall local cryptographic verification: **$overall**",
    '',
    'The placeholder DID is not publicly resolvable. These JWTs must be',
    'reissued with the official DID, kid and key material before API testing.'
)

Write-Utf8NoBom $reportPath ($lines -join [Environment]::NewLine)

if ($overall -ne 'PASS') {
    throw 'One or more provisional JWT checks failed.'
}

Write-Host "Overall local cryptographic verification: $overall" -ForegroundColor Green
Write-Host "Report saved to: $reportPath"

