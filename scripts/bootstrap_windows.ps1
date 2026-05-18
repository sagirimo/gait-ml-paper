param(
    [string]$Proxy = $env:HTTPS_PROXY
)

$ErrorActionPreference = "Stop"

if (-not (Get-Command py -ErrorAction SilentlyContinue)) {
    throw "Python launcher 'py' was not found. Install Python 3 first."
}

function Invoke-Checked {
    param(
        [Parameter(Mandatory = $true)]
        [string]$FilePath,
        [string[]]$Arguments = @()
    )

    & $FilePath @Arguments
    if ($LASTEXITCODE -ne 0) {
        throw "Command failed with exit code ${LASTEXITCODE}: $FilePath $($Arguments -join ' ')"
    }
}

Invoke-Checked "py" @("-3", "-m", "venv", ".venv")
Invoke-Checked ".\.venv\Scripts\python.exe" @("-m", "pip", "install", "--upgrade", "pip")
Invoke-Checked ".\.venv\Scripts\python.exe" @("-m", "pip", "install", "-r", "requirements.txt")
if ($Proxy) {
    Invoke-Checked ".\.venv\Scripts\python.exe" @("src\download_gaitpdb.py", "--proxy", $Proxy)
} else {
    Invoke-Checked ".\.venv\Scripts\python.exe" @("src\download_gaitpdb.py")
}
Invoke-Checked ".\.venv\Scripts\python.exe" @("src\run_rf_baseline.py")
Invoke-Checked ".\.venv\Scripts\python.exe" @("src\run_model_comparison.py")

Write-Host "Windows bootstrap complete. Check results/ for baseline outputs."
