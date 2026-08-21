$ErrorActionPreference = "Stop"
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$Python = Get-Command python3 -ErrorAction SilentlyContinue
if (-not $Python) {
  $Python = Get-Command python -ErrorAction Stop
}
& $Python.Source (Join-Path $ScriptDir "uninstall-kilo-qwen38-policy.py") @args
exit $LASTEXITCODE
