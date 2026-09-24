[CmdletBinding()]
param(
    [string]$Root = (Join-Path $PSScriptRoot ".."),
    [int]$TimeoutSec = 20
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path $Root).Path
$setDir = Join-Path $rootPath "data\sets"
$statusPath = Join-Path $rootPath "data\link-status.json"
$reportDir = Join-Path $rootPath "reports"
New-Item -ItemType Directory -Force -Path $reportDir | Out-Null

$results = [ordered]@{}
foreach ($file in Get-ChildItem -LiteralPath $setDir -Filter "*.json" -File | Sort-Object Name) {
    $set = Get-Content -Raw -LiteralPath $file.FullName | ConvertFrom-Json
    foreach ($link in @($set.links | Sort-Object position)) {
        $checkedAt = [DateTime]::UtcNow.ToString("o")
        $state = "unknown"
        $httpStatus = $null
        $finalUrl = $null
        $requestError = $null
        try {
            $response = Invoke-WebRequest -Uri $link.url -Method Head -MaximumRedirection 5 -TimeoutSec $TimeoutSec -UseBasicParsing
            $httpStatus = [int]$response.StatusCode
            $finalUrl = $response.BaseResponse.ResponseUri.AbsoluteUri
            if ($httpStatus -ge 200 -and $httpStatus -lt 300) { $state = "online" }
            elseif ($httpStatus -ge 300 -and $httpStatus -lt 400) { $state = "redirected" }
            elseif ($httpStatus -in @(401, 403, 429)) { $state = "requires_manual_check" }
            elseif ($httpStatus -ge 400) { $state = "offline" }
        } catch {
            $requestError = $_.Exception.Message
            if ($requestError -match "401|403|429|login|captcha|forbidden|Unauthorized") { $state = "requires_manual_check" }
            else { $state = "unknown" }
        }
        $results[$link.id] = [ordered]@{
            state = $state
            checkedAt = $checkedAt
            httpStatus = $httpStatus
            finalUrl = $finalUrl
            error = $requestError
        }
        Write-Host "$state`t$($link.id)" 
    }
}

$payload = [ordered]@{
    schemaVersion = 1
    checkedAt = [DateTime]::UtcNow.ToString("o")
    links = $results
}
Set-Content -LiteralPath $statusPath -Value ($payload | ConvertTo-Json -Depth 10) -Encoding utf8NoBOM
$reportPath = Join-Path $reportDir ("link-check-{0}.json" -f (Get-Date -Format "yyyyMMdd-HHmmss"))
Set-Content -LiteralPath $reportPath -Value ($payload | ConvertTo-Json -Depth 10) -Encoding utf8NoBOM
Write-Host "Saved $statusPath"
Write-Host "Saved $reportPath"
