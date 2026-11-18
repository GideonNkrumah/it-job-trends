#Requires -Version 5.1
<#
.SYNOPSIS
    One-shot setup: authenticate, create the repo, push, set secrets, trigger a run.

.DESCRIPTION
    Run this in your OWN terminal (not inside the DSH sandbox - the sandbox blocks
    git's MSYS helper processes and cannot reach github.com).

    powershell -ExecutionPolicy Bypass -File .\setup.ps1

    The only manual step is the browser sign-in that `gh auth login` opens.

.NOTES
    git and gh write to stderr for entirely normal reasons ("not logged in", hints,
    progress). Windows PowerShell 5.1 promotes ANY native stderr output to a
    terminating error when $ErrorActionPreference is 'Stop', which makes a naive
    script abort on expected conditions. This script keeps the preference at
    'Continue' and checks $LASTEXITCODE after every native call instead.
#>
[CmdletBinding()]
param(
    [string]$Owner = 'GideonNkrumah',
    [string]$RepoName = 'it-job-trends'
)

$ErrorActionPreference = 'Continue'
$repoDir = Split-Path -Parent $PSCommandPath
Set-Location $repoDir
$script:GhPath = $null

function Step([int]$n, [string]$msg) { Write-Host "`n[$n] $msg" -ForegroundColor Cyan }
function Ok([string]$msg) { Write-Host "    OK   $msg" -ForegroundColor Green }
function Warn([string]$msg) { Write-Host "    !!   $msg" -ForegroundColor Yellow }
function Die([string]$msg) { Write-Host "`nFAILED: $msg" -ForegroundColor Red; exit 1 }

# Run gh with output visible to the console; return its exit code.
function Invoke-Gh([string[]]$GhArgs) {
    & $script:GhPath @GhArgs 2>&1 | Out-Host
    return $LASTEXITCODE
}

# Run gh silently; return its exit code.
function Test-Gh([string[]]$GhArgs) {
    $null = & $script:GhPath @GhArgs 2>&1
    return $LASTEXITCODE
}

# Pushing files under .github/workflows requires the `workflow` token scope,
# which `gh auth login` does NOT request by default.
function Test-WorkflowScope {
    $text = & $script:GhPath auth status 2>&1 | Out-String
    return ($text -match "'workflow'")
}

# ---------------------------------------------------------------- 0. sanity ---
Step 0 'Checking the working folder'
if (-not (Test-Path (Join-Path $repoDir '.git'))) {
    Die "No .git in $repoDir - run this script from the it-job-trends folder."
}
if (-not (Get-Command git -ErrorAction SilentlyContinue)) { Die 'git is not on PATH.' }
Ok "repo at $repoDir"

# ------------------------------------------------------------------ 1. gh -----
Step 1 'Checking for the GitHub CLI'
$candidate = Get-Command gh -ErrorAction SilentlyContinue
if ($candidate) { $script:GhPath = $candidate.Source }

if (-not $script:GhPath) {
    Warn 'gh not found - installing via winget'
    winget install --id GitHub.cli -e --source winget --accept-package-agreements --accept-source-agreements 2>&1 | Out-Host
    $env:Path = [Environment]::GetEnvironmentVariable('Path', 'Machine') + ';' + [Environment]::GetEnvironmentVariable('Path', 'User')
    $candidate = Get-Command gh -ErrorAction SilentlyContinue
    if ($candidate) { $script:GhPath = $candidate.Source }
}
if (-not $script:GhPath) {
    Die 'gh is still not on PATH. Open a NEW terminal and re-run this script.'
}
& $script:GhPath --version 2>&1 | Select-Object -First 1 | Out-Host
Ok 'gh ready'

# ---------------------------------------------------------------- 2. auth -----
Step 2 'Authenticating with GitHub (a browser window will open)'
if ((Test-Gh @('auth', 'status')) -ne 0) {
    Warn 'not signed in - starting the browser login'
    if ((Invoke-Gh @('auth', 'login', '--hostname', 'github.com', '--git-protocol', 'https', '--web', '--scopes', 'workflow')) -ne 0) {
        Die 'gh auth login failed or was cancelled. Re-run the script to try again.'
    }
    $null = Invoke-Gh @('auth', 'setup-git')
} else {
    Ok 'already authenticated'
}

if (-not (Test-WorkflowScope)) {
    Warn 'token is missing the workflow scope - approving it now (browser again, briefly)'
    if ((Invoke-Gh @('auth', 'refresh', '--hostname', 'github.com', '--scopes', 'workflow')) -ne 0) {
        Die 'could not add the workflow scope. Run: gh auth refresh -h github.com -s workflow'
    }
}
Ok 'token may push workflows'

# ---------------------------------------------------------------- 3. repo -----
Step 3 "Ensuring $Owner/$RepoName exists on GitHub"
if ((Test-Gh @('repo', 'view', "$Owner/$RepoName")) -ne 0) {
    if ((Invoke-Gh @('repo', 'create', "$Owner/$RepoName", '--public', '--description', 'Daily IT job market tracker (Adzuna Canada, HN, BLS)')) -ne 0) {
        Die "gh repo create failed. Check that the account is $Owner and the name is free."
    }
    Ok 'repository created'
} else {
    Ok 'repository already exists'
}

# ---------------------------------------------------------------- 4. push -----
Step 4 'Pushing main'
$origin = git remote get-url origin 2>$null
if ($LASTEXITCODE -ne 0 -or -not $origin) {
    git remote add origin "https://github.com/$Owner/$RepoName.git"
    if ($LASTEXITCODE -ne 0) { Die 'could not add the origin remote.' }
    Ok 'origin remote added'
}
$pushOutput = git push -u origin main 2>&1 | Out-String
Write-Host $pushOutput
if ($LASTEXITCODE -ne 0) {
    if ($pushOutput -match 'workflow') {
        Warn 'GitHub refused the push for a missing workflow scope - refreshing the token, then retrying once'
        $null = Invoke-Gh @('auth', 'refresh', '--hostname', 'github.com', '--scopes', 'workflow')
        $pushOutput = git push -u origin main 2>&1 | Out-String
        Write-Host $pushOutput
    }
    if ($LASTEXITCODE -ne 0) {
        Die 'push failed. If git says "fetch first", the remote already has commits - use the fallback steps in SETUP.md.'
    }
}
Ok 'pushed'

# ------------------------------------------------------------- 5. secrets -----
Step 5 'Setting Actions secrets from .env'
$envPath = Join-Path $repoDir '.env'
$pairs = @{}
if (Test-Path $envPath) {
    foreach ($line in Get-Content $envPath) {
        if ($line -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)$') {
            $pairs[$Matches[1]] = $Matches[2].Trim()
        }
    }
}
foreach ($name in @('ADZUNA_APP_ID', 'ADZUNA_APP_KEY')) {
    if ($pairs.ContainsKey($name) -and $pairs[$name]) {
        if ((Test-Gh @('secret', 'set', $name, '--repo', "$Owner/$RepoName", '--body', $pairs[$name])) -eq 0) {
            Ok "$name set"
        } else {
            Warn "could not set $name - add it under Settings > Secrets and variables > Actions"
        }
    } else {
        Warn "$name not found in .env - add it later under Settings > Secrets and variables > Actions"
    }
}

# ------------------------------------------------------------- 6. trigger -----
Step 6 'Triggering the first snapshot'
if ((Test-Gh @('workflow', 'run', 'daily.yml', '--repo', "$Owner/$RepoName")) -ne 0) {
    Warn 'could not trigger the workflow; run it from the Actions tab instead.'
} else {
    Ok 'workflow queued - waiting for it to appear'
    Start-Sleep -Seconds 12
    Invoke-Gh @('run', 'list', '--workflow', 'daily.yml', '--limit', '1', '--repo', "$Owner/$RepoName")
}

# ------------------------------------------------------------- 7. summary -----
Step 7 'Done'
Write-Host "    Repo    : https://github.com/$Owner/$RepoName"
Write-Host "    Actions : https://github.com/$Owner/$RepoName/actions"
Write-Host "    Profile : https://github.com/$Owner"
Write-Host ''
Write-Host '    Watch the run finish, then reload the repo to see the populated README.' -ForegroundColor Gray
