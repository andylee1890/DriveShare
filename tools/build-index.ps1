[CmdletBinding()]
param(
    [string]$Root = (Join-Path $PSScriptRoot "..")
)

$ErrorActionPreference = "Stop"
$rootPath = (Resolve-Path $Root).Path
$setDir = Join-Path $rootPath "data\sets"
$statusPath = Join-Path $rootPath "data\link-status.json"
$indexPath = Join-Path $rootPath "data\index.json"

$sets = @(
    Get-ChildItem -LiteralPath $setDir -Filter "*.json" -File |
        Sort-Object Name |
        ForEach-Object { Get-Content -Raw -LiteralPath $_.FullName | ConvertFrom-Json }
)

$setIds = @{}
$linkIds = @{}
foreach ($set in $sets) {
    if ($setIds.ContainsKey($set.id)) { throw "Duplicate set id: $($set.id)" }
    $setIds[$set.id] = $true
    $positions = @($set.links | ForEach-Object { $_.position } | Sort-Object)
    $expected = 1..$positions.Count
    if ((-join $positions) -ne (-join $expected)) { throw "Positions for set $($set.id) must be continuous from 1" }
    foreach ($link in $set.links) {
        if ($linkIds.ContainsKey($link.id)) { throw "Duplicate link id: $($link.id)" }
        $linkIds[$link.id] = $true
    }
}

$status = @{ links = @{} }
if (Test-Path -LiteralPath $statusPath) {
    $status = Get-Content -Raw -LiteralPath $statusPath | ConvertFrom-Json -AsHashtable
}

$index = [ordered]@{
    schemaVersion = 1
    generatedAt = [DateTime]::UtcNow.ToString("o")
    repository = "andylee1890/DriveShare"
    repositoryUrl = "https://github.com/andylee1890/DriveShare"
    website = "https://englishanchor.online"
    purpose = "English Anchor 网盘分享套索引，供网站展示和检索。"
    indexPath = "/DriveShare/data/index.json"
    statusValues = [ordered]@{
        published = "公开展示中的分享套。"
        archived = "历史记录，不作为默认推荐。"
        draft = "尚未完成核验，不应作为稳定资源推荐。"
    }
    linkHealthValues = [ordered]@{
        unchecked = "尚未检查。"
        online = "HTTP 请求可达；不代表网盘内容完整。"
        redirected = "发生跳转，需要人工确认最终页面。"
        requires_manual_check = "需要登录、Cookie、口令或反爬验证。"
        offline = "请求失败或明确不可达。"
        unknown = "无法可靠判断。"
    }
    providers = @($sets | ForEach-Object { $_.provider } | Sort-Object -Unique)
    setCount = $sets.Count
    sets = @()
}

foreach ($set in $sets) {
    $copy = [ordered]@{}
    foreach ($property in $set.PSObject.Properties) { $copy[$property.Name] = $property.Value }
    $copy.links = @($set.links | Sort-Object position | ForEach-Object {
        $link = [ordered]@{}
        foreach ($property in $_.PSObject.Properties) { $link[$property.Name] = $property.Value }
        $health = $null
        if ($status.links -and $status.links.ContainsKey($_.id)) {
            $health = $status.links[$_.id]
        }
        if ($null -ne $health) { $link.health = $health }
        [pscustomobject]$link
    })
    $index.sets += [pscustomobject]$copy
}

$json = $index | ConvertTo-Json -Depth 20
Set-Content -LiteralPath $indexPath -Value $json -Encoding utf8NoBOM
Write-Host "Generated $indexPath ($($sets.Count) sets, $($linkIds.Count) links)"
