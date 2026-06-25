param(
    [Parameter(Mandatory = $true)]
    [string]$Branch
)

$ErrorActionPreference = "Stop"

function Invoke-Git {
    param([Parameter(Mandatory = $true)][string[]]$Arguments)

    $output = & git @Arguments 2>&1
    if ($LASTEXITCODE -ne 0) {
        throw "git $($Arguments -join ' ') failed: $output"
    }
    return $output
}

function Get-RepositoryRoot {
    $root = Invoke-Git @("rev-parse", "--show-toplevel")
    return ($root | Select-Object -First 1).Trim()
}

function Assert-GitRepository {
    Invoke-Git @("rev-parse", "--is-inside-work-tree") | Out-Null
}

function Assert-CleanWorktree {
    $status = Invoke-Git @("status", "--porcelain")
    if ($status) {
        throw "Worktree is dirty. Commit or intentionally discard local changes before resuming on another computer."
    }
}

function Assert-GithubRemote {
    $remotes = Invoke-Git @("remote")
    if ($remotes -notcontains "github") {
        throw "Remote 'github' is missing. Add it before resuming work."
    }
}

function Get-FullSha {
    param([Parameter(Mandatory = $true)][string]$Revision)
    return (Invoke-Git @("rev-parse", $Revision) | Select-Object -First 1).Trim()
}

function Assert-HeadMatchesRemote {
    param([Parameter(Mandatory = $true)][string]$BranchName)

    $localHead = Get-FullSha "HEAD"
    $remoteHead = Get-FullSha "github/$BranchName"
    if ($localHead -ne $remoteHead) {
        throw "Local HEAD $localHead does not match github/$BranchName $remoteHead. Stop and reconcile manually."
    }
}

function Get-CurrentPrNumber {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $phaseFile = Join-Path $RepositoryRoot "docs/codex/CURRENT_PHASE.md"
    if (-not (Test-Path $phaseFile)) {
        return "unknown"
    }

    $line = Get-Content $phaseFile | Where-Object { $_ -match "^Current PR:\s*(.+)$" } | Select-Object -First 1
    if ($line -match "^Current PR:\s*(.+)$") {
        return $Matches[1].Trim()
    }
    return "unknown"
}

try {
    Assert-GitRepository
    $repoRoot = Get-RepositoryRoot
    Set-Location $repoRoot

    Assert-CleanWorktree
    Assert-GithubRemote

    Invoke-Git @("fetch", "github") | Out-Null
    Invoke-Git @("switch", $Branch) | Out-Null
    Invoke-Git @("pull", "--ff-only", "github", $Branch) | Out-Null
    Assert-HeadMatchesRemote $Branch

    $currentBranch = (Invoke-Git @("branch", "--show-current") | Select-Object -First 1).Trim()
    $currentHead = Get-FullSha "HEAD"
    $handoffPath = Join-Path $repoRoot "docs/codex/HANDOFF.md"
    $prNumber = Get-CurrentPrNumber $repoRoot

    Write-Host "Current branch: $currentBranch"
    Write-Host "Current HEAD: $currentHead"
    Write-Host ""
    Write-Host "Recent commits:"
    Invoke-Git @("log", "-5", "--oneline") | ForEach-Object { Write-Host $_ }
    Write-Host ""
    Write-Host "HANDOFF.md:"
    if (-not (Test-Path $handoffPath)) {
        throw "docs/codex/HANDOFF.md is missing. Stop before editing code."
    }
    Get-Content $handoffPath | ForEach-Object { Write-Host $_ }
    Write-Host ""
    Write-Host "Current PR: $prNumber"
    Write-Host "Before editing, read the latest GitHub PR comments and confirm there is no active [WORKING] lock."
    exit 0
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
