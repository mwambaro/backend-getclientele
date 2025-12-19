$venvPython = "$PSScriptRoot\venv\Scripts\python.exe"
if (-not (Test-Path $venvPython)) {
    Write-Host "No local venv found at $venvPython. Using system python in PATH."
    $py = "python"
} else {
    $py = $venvPython
}
& $py -m pip install -r dev-requirements.txt
& $py -m pytest -q
