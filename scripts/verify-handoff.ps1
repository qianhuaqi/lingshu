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

function Assert-CurrentBranch {
    param([Parameter(Mandatory = $true)][string]$ExpectedBranch)

    $actualBranch = (Invoke-Git @("branch", "--show-current") | Select-Object -First 1).Trim()
    if ($actualBranch -ne $ExpectedBranch) {
        throw "Current branch is '$actualBranch', expected '$ExpectedBranch'. Switch to the phase branch first."
    }
}

function Assert-CleanWorktree {
    $status = Invoke-Git @("status", "--porcelain")
    if ($status) {
        throw "Worktree is dirty. Commit and push intended changes before handoff."
    }
}

function Assert-GithubRemote {
    $remotes = Invoke-Git @("remote")
    if ($remotes -notcontains "github") {
        throw "Remote 'github' is missing. Add the correct remote before handoff."
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
        throw "Local HEAD $localHead does not match github/$BranchName $remoteHead. Push or fast-forward before handoff."
    }
}

function Read-HandoffFields {
    param([Parameter(Mandatory = $true)][string]$Path)

    if (-not (Test-Path $Path)) {
        throw "docs/codex/HANDOFF.md is missing. Create it before handoff."
    }

    $fields = @{}
    Get-Content $Path | ForEach-Object {
        if ($_ -match "^([^:#][^:]+):\s*(.*)$") {
            $fields[$Matches[1].Trim()] = $Matches[2].Trim()
        }
    }
    return $fields
}

function Assert-HandoffMatchesRepository {
    param(
        [Parameter(Mandatory = $true)][hashtable]$Fields,
        [Parameter(Mandatory = $true)][string]$BranchName,
        [Parameter(Mandatory = $true)][string]$LocalHead,
        [Parameter(Mandatory = $true)][string]$RemoteHead
    )

    if ($Fields["Branch"] -ne $BranchName) {
        throw "HANDOFF Branch is '$($Fields["Branch"])', expected '$BranchName'. Update docs/codex/HANDOFF.md."
    }
    if ($Fields["Local HEAD"] -ne $LocalHead) {
        throw "HANDOFF Local HEAD does not match actual HEAD. Update docs/codex/HANDOFF.md."
    }
    if ($Fields["Remote HEAD"] -ne $RemoteHead) {
        throw "HANDOFF Remote HEAD does not match github/$BranchName. Update docs/codex/HANDOFF.md."
    }
    if ($Fields["Worktree"] -ne "clean") {
        throw "HANDOFF Worktree must be clean. Update docs/codex/HANDOFF.md after committing."
    }
}

function Assert-NoGeneratedUntrackedArtifacts {
    param([Parameter(Mandatory = $true)][string]$RepositoryRoot)

    $untracked = Invoke-Git @("ls-files", "--others", "--exclude-standard")
    $blocked = @()

    foreach ($path in $untracked) {
        $normalized = $path -replace "\\", "/"
        if (
            $normalized -eq "dist" -or
            $normalized -like "dist/*" -or
            $normalized -eq "build" -or
            $normalized -like "build/*" -or
            $normalized -like "*.egg-info/*" -or
            $normalized -like "*.egg-info" -or
            $normalized -like "*/__pycache__/*" -or
            $normalized -like "__pycache__/*" -or
            $normalized -eq ".pytest_cache" -or
            $normalized -like ".pytest_cache/*" -or
            $normalized -like ".venv/*" -or
            $normalized -like "venv/*" -or
            $normalized -like "env/*" -or
            $normalized -like ".tmp-*/*"
        ) {
            $blocked += $normalized
        }
    }

    if ($blocked.Count -gt 0) {
        throw "Generated or temporary untracked artifacts remain: $($blocked -join ', '). Remove them intentionally before handoff."
    }
}

try {
    $repoRoot = Get-RepositoryRoot
    Set-Location $repoRoot

    Assert-CurrentBranch $Branch
    Assert-CleanWorktree
    Assert-GithubRemote
    Invoke-Git @("fetch", "github") | Out-Null
    Assert-HeadMatchesRemote $Branch

    $localHead = Get-FullSha "HEAD"
    $remoteHead = Get-FullSha "github/$Branch"
    $handoffPath = Join-Path $repoRoot "docs/codex/HANDOFF.md"
    $fields = Read-HandoffFields $handoffPath

    Assert-HandoffMatchesRepository $fields $Branch $localHead $remoteHead
    Assert-NoGeneratedUntrackedArtifacts $repoRoot

    Write-Host "Handoff verification passed"
    exit 0
}
catch {
    Write-Error $_.Exception.Message
    exit 1
}
