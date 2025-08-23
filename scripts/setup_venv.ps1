Param()

if (-Not (Test-Path "venv")) {
  python -m venv venv
}

& ./venv/Scripts/Activate.ps1
python -m pip install --upgrade pip
Write-Output "Python: $(python --version)"
Write-Output "Pip: $(pip --version)"
Write-Output "Venv ready at .\venv"

