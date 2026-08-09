[CmdletBinding()]
param(
    [switch]$Submit,

    [string]$CredentialDirectory,

    [string]$Endpoint = 'https://compliance.lab.gaia-x.eu/development/api/credential-offers/standard-compliance',

    [string]$Vcid = 'https://gaia-x.eu/.well-known/compliance-credential.jwt'
)

$ErrorActionPreference = 'Stop'

if ([string]::IsNullOrWhiteSpace($CredentialDirectory)) {
    $CredentialDirectory = Join-Path $PSScriptRoot 'wizard-output'
}

function ConvertFrom-Base64Url {
    param(
        [Parameter(Mandatory)]
        [string]$Value
    )

    $base64 = $Value.Replace('-', '+').Replace('_', '/')

    switch ($base64.Length % 4) {
        2 { $base64 += '==' }
        3 { $base64 += '=' }
    }

    [Text.Encoding]::UTF8.GetString(
        [Convert]::FromBase64String($base64)
    )
}

function ConvertFrom-Jwt {
    param(
        [Parameter(Mandatory)]
        [string]$Token
    )

    $trimmedToken = $Token.Trim()
    $parts = $trimmedToken.Split('.')

    if ($parts.Count -ne 3) {
        throw "JWT must contain exactly 3 segments; found $($parts.Count)."
    }

    [PSCustomObject]@{
        Token   = $trimmedToken
        Header  = ConvertFrom-Base64Url $parts[0] | ConvertFrom-Json
        Payload = ConvertFrom-Base64Url $parts[1] | ConvertFrom-Json
    }
}

function Read-JwtFile {
    param(
        [Parameter(Mandatory)]
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        throw "JWT file not found: $Path"
    }

    $rawToken = Get-Content -Raw -Encoding UTF8 -LiteralPath $Path

    if ($rawToken.Trim() -match '\s') {
        throw "JWT contains whitespace: $Path"
    }

    ConvertFrom-Jwt $rawToken
}

function Write-Section {
    param([string]$Title)

    Write-Host "`n=== $Title ===" -ForegroundColor Cyan
}

$credentialDirectoryPath = (
    Resolve-Path -LiteralPath $CredentialDirectory
).Path

$vpPath = Join-Path $credentialDirectoryPath 'Signed Verifiable Presentation.jwt'
$vp = Read-JwtFile $vpPath
$vpCredentials = @($vp.Payload.verifiableCredential)

Write-Section 'Local VP validation'

[PSCustomObject]@{
    File             = $vpPath
    Algorithm        = $vp.Header.alg
    TokenType        = $vp.Header.typ
    Issuer           = $vp.Payload.issuer
    ValidFrom        = $vp.Payload.validFrom
    ValidUntil       = $vp.Payload.validUntil
    CredentialCount  = $vpCredentials.Count
} | Format-List

if ($vp.Header.typ -ne 'vp+jwt') {
    throw "Expected VP header typ 'vp+jwt'; found '$($vp.Header.typ)'."
}

if ($vpCredentials.Count -ne 3) {
    throw "Expected 3 embedded credentials; found $($vpCredentials.Count)."
}

$expectedCredentialFiles = @(
    'LegalPerson.jwt',
    'Issuer.jwt',
    'LegalRegistrationNumber.jwt'
)

$downloadedTokens = @{}

foreach ($fileName in $expectedCredentialFiles) {
    $credentialPath = Join-Path $credentialDirectoryPath $fileName
    $credential = Read-JwtFile $credentialPath
    $downloadedTokens[$credential.Token] = $fileName
}

Write-Section 'Embedded credential validation'

$embeddedSummaries = for ($index = 0; $index -lt $vpCredentials.Count; $index++) {
    $envelope = $vpCredentials[$index]
    $idParts = ([string]$envelope.id).Split(',', 2)

    if ($idParts.Count -ne 2 -or -not $idParts[1]) {
        throw "Embedded credential $($index + 1) is not a JWT data URL."
    }

    $embedded = ConvertFrom-Jwt $idParts[1]
    $matchingFile = $downloadedTokens[$embedded.Token]

    if (-not $matchingFile) {
        throw "Embedded credential $($index + 1) does not match a downloaded VC file."
    }

    [PSCustomObject]@{
        Index        = $index + 1
        File         = $matchingFile
        Type         = $embedded.Payload.type -join ', '
        Issuer       = $embedded.Payload.issuer
        CredentialId = $embedded.Payload.id
        ExactMatch   = $true
    }
}

$embeddedSummaries | Format-Table -AutoSize

Write-Host "`nLocal validation passed." -ForegroundColor Green

if (-not $Submit) {
    Write-Host 'No network request was sent.' -ForegroundColor Yellow
    Write-Host 'Run the script again with -Submit to call the Compliance API.'
    return
}

$curlCommand = Get-Command curl.exe -ErrorAction SilentlyContinue

if (-not $curlCommand) {
    throw 'curl.exe was not found on PATH.'
}

$outputDirectory = Join-Path $credentialDirectoryPath 'cli-output'

if (-not (Test-Path -LiteralPath $outputDirectory)) {
    New-Item -ItemType Directory -Path $outputDirectory | Out-Null
}

$timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
$responsePath = Join-Path $outputDirectory "compliance-response-$timestamp.jwt"
$headersPath = Join-Path $outputDirectory "response-headers-$timestamp.txt"
$decodedPath = Join-Path $outputDirectory "compliance-response-$timestamp.json"
$requestUrl = '{0}?vcid={1}' -f $Endpoint, [Uri]::EscapeDataString($Vcid)

Write-Section 'Compliance API submission'
Write-Host "POST $requestUrl"

$curlArguments = @(
    '--silent',
    '--show-error',
    '--request', 'POST',
    $requestUrl,
    '--header', 'Content-Type: application/vp+jwt',
    '--data-binary', "@$vpPath",
    '--dump-header', $headersPath,
    '--output', $responsePath,
    '--write-out', '%{http_code}'
)

$httpCode = (& curl.exe @curlArguments).Trim()

if ($LASTEXITCODE -ne 0) {
    throw "curl.exe failed with exit code $LASTEXITCODE."
}

Write-Host "HTTP status: $httpCode"

if ($httpCode -ne '201') {
    $errorBody = Get-Content -Raw -Encoding UTF8 -LiteralPath $responsePath
    Write-Host "`nResponse body:" -ForegroundColor Yellow
    Write-Host $errorBody
    throw "Compliance API returned HTTP $httpCode instead of 201."
}

$response = Read-JwtFile $responsePath
$response.Payload | ConvertTo-Json -Depth 30 |
    Set-Content -Encoding UTF8 -LiteralPath $decodedPath

$subject = $response.Payload.credentialSubject

Write-Section 'Compliance result'

[PSCustomObject]@{
    Issuer                    = $response.Payload.issuer
    Type                      = $response.Payload.type -join ', '
    LabelLevel                = $subject.'gx:labelLevel'
    EngineVersion             = $subject.'gx:engineVersion'
    RulesVersion              = $subject.'gx:rulesVersion'
    CompliantCredentialCount  = @($subject.'gx:compliantCredentials').Count
    ValidFrom                 = $response.Payload.validFrom
    ValidUntil                = $response.Payload.validUntil
} | Format-List

Write-Host 'Compliance submission passed.' -ForegroundColor Green
Write-Host "Response JWT: $responsePath"
Write-Host "Response headers: $headersPath"
Write-Host "Decoded payload: $decodedPath"
