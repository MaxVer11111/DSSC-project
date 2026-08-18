# 遇到错误时立即停止
$ErrorActionPreference = "Stop"

# 找到项目根目录
# 当前脚本在 scripts 文件夹中，所以它的上一级就是项目根目录
$projectRoot = Split-Path -Parent $PSScriptRoot

# 定义需要读取的四个文件
$configPath = Join-Path $projectRoot "02-config/demo-config.json"

$datasetPath = Join-Path `
    $projectRoot `
    "03-normalized-metadata/dataset-metadata.jsonld"

$legalPersonPath = Join-Path `
    $projectRoot `
    "04-credential-source/legal-person.jsonld"

$serviceOfferingPath = Join-Path `
    $projectRoot `
    "04-credential-source/service-offering.jsonld"

# 定义检查报告的输出位置
$reportPath = Join-Path `
    $projectRoot `
    "07-evidence/unsigned-consistency-report.md"

# 读取JSON和JSON-LD文件
$config = Get-Content `
    $configPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$dataset = Get-Content `
    $datasetPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$legalPerson = Get-Content `
    $legalPersonPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

$serviceOffering = Get-Content `
    $serviceOfferingPath `
    -Raw `
    -Encoding UTF8 |
    ConvertFrom-Json

# 保存所有检查结果
$reportRows = @()

# 记录是否出现失败
$hasFailure = $false

# 定义一个自动比较两个值的功能
function Test-SameValue {
    param(
        [string]$CheckName,
        [object]$Expected,
        [object]$Actual
    )

    $expectedText = [string]$Expected
    $actualText = [string]$Actual

    if ($expectedText -ceq $actualText) {
        $status = "PASS"
    }
    else {
        $status = "FAIL"
        $script:hasFailure = $true
    }

    $script:reportRows += `
        "| $CheckName | $expectedText | $actualText | $status |"

    Write-Host "$status - $CheckName"
}

# 检查一：配置中的Provider DID
# 是否等于LegalPerson描述的主体ID
Test-SameValue `
    "Provider DID matches LegalPerson subject" `
    $config.provider.did `
    $legalPerson.credentialSubject.id

# 检查二：Provider名称
# 是否等于LegalPerson中的法定名称
Test-SameValue `
    "Provider name matches LegalPerson name" `
    $config.provider.name `
    $legalPerson.credentialSubject.'gx:legalName'

# 检查三：ServiceOffering中的providedBy
# 是否等于LegalPerson主体ID
Test-SameValue `
    "ServiceOffering providedBy matches LegalPerson" `
    $legalPerson.credentialSubject.id `
    $serviceOffering.credentialSubject.'gx:providedBy'.id

# 检查四：ServiceOffering主体ID
# 是否等于配置中的ServiceOffering ID
Test-SameValue `
    "ServiceOffering subject ID matches config" `
    $config.serviceOffering.id `
    $serviceOffering.credentialSubject.id

# 检查五：ServiceOffering引用的Dataset
# 是否等于配置中的Dataset canonical URI
Test-SameValue `
    "ServiceOffering Dataset reference matches config" `
    $config.dataset.canonicalUri `
    $serviceOffering.credentialSubject.'gx:aggregationOf'[0].id

# 检查六：Dataset Metadata的@id
# 是否等于配置中的Dataset canonical URI
Test-SameValue `
    "Dataset URI matches config" `
    $config.dataset.canonicalUri `
    $dataset.'@id'

# 检查七：Dataset Endpoint
# 是否等于配置中的A组真实Endpoint
Test-SameValue `
    "Dataset Endpoint matches config" `
    $config.distribution.endpoint `
    $dataset.endpointUrl

# 检查八：Dataset响应格式
# 是否等于配置中的Response Media Type
Test-SameValue `
    "Dataset metadata format matches semantic contract" `
    $config.metadata.format `
    $dataset.format

# 检查九：Dataset License
# 是否等于配置中的License
Test-SameValue `
    "Dataset License matches config" `
    $config.dataset.license `
    $dataset.license

# 确保报告输出文件夹存在
$reportFolder = Split-Path -Parent $reportPath

New-Item `
    -ItemType Directory `
    -Force `
    -Path $reportFolder |
    Out-Null

# 根据检查结果确定总体结果
if ($hasFailure) {
    $overallResult = "FAIL"
}
else {
    $overallResult = "PASS"
}

# 组成Markdown报告
$reportContent = @(
    "# 未签名凭证一致性检查报告",
    "",
    "- 检查时间：$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')",
    "- 配置版本：$($config.configVersion)",
    "- 总体结果：**$overallResult**",
    "",
    "| 检查项目 | 期望值 | 实际值 | 结果 |",
    "|---|---|---|---|"
)

$reportContent += $reportRows

$reportContent += @(
    "",
    "## 说明",
    "",
    "本报告只检查未签名文件之间的字段一致性。",
    "",
    "它不代表已经完成：",
    "",
    "- Gaia-X SHACL验证；",
    "- DID Document验证；",
    "- JWT签名验证；",
    "- Compliance API测试。"
)

# 将结果写入Markdown文件
$reportContent |
    Set-Content `
        -Path $reportPath `
        -Encoding UTF8

Write-Host ""
Write-Host "Overall result: $overallResult"
Write-Host "Report saved to:"
Write-Host $reportPath

# 如果有失败项，以错误状态结束
if ($hasFailure) {
    exit 1
}

exit 0