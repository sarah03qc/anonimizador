$ErrorActionPreference = 'Stop'
Set-Location -LiteralPath $PSScriptRoot
try {
    Remove-Item -LiteralPath '.installation_ok' -ErrorAction SilentlyContinue
    $pythonCommand = Get-Command python -ErrorAction SilentlyContinue
    if (-not $pythonCommand) { throw 'Instale Python 3.12 x64 desde python.org y vuelva a ejecutar este instalador.' }
    & $pythonCommand.Source -c "import sys,struct; sys.exit(0 if sys.version_info[:2]==(3,12) and struct.calcsize('P')==8 else 1)"
    if ($LASTEXITCODE -ne 0) { throw 'Se necesita Python 3.12 de 64 bits.' }
    if (-not (Test-Path -LiteralPath '.venv\Scripts\python.exe')) {
        & $pythonCommand.Source -m venv .venv
        if ($LASTEXITCODE -ne 0) { throw 'No fue posible crear el entorno local.' }
    }
    $projectPython = Join-Path $PSScriptRoot '.venv\Scripts\python.exe'
    & $projectPython -m pip install --disable-pip-version-check --cache-dir .pip-cache pip==26.2.2
    if ($LASTEXITCODE -ne 0) { throw 'No fue posible actualizar el instalador de paquetes local.' }
    & $projectPython -m pip install --disable-pip-version-check --cache-dir .pip-cache -r requirements-lock.txt
    if ($LASTEXITCODE -ne 0) { throw 'No fue posible instalar las dependencias. Compruebe Internet y espacio disponible.' }
    & $projectPython scripts\install_model.py
    if ($LASTEXITCODE -ne 0) { throw 'No fue posible descargar el modelo.' }
    & $projectPython -m pip check
    if ($LASTEXITCODE -ne 0) { throw 'La comprobacion de dependencias encontro incompatibilidades.' }
    & $projectPython scripts\smoke_check.py
    if ($LASTEXITCODE -ne 0) { throw 'La prueba local no termino correctamente. La herramienta no se marcara como instalada.' }
    Set-Content -LiteralPath '.installation_ok' -Value 'Instalacion verificada localmente' -Encoding UTF8
    Write-Host 'INSTALACION COMPLETADA. Abra run_windows.bat con doble clic.' -ForegroundColor Green
} catch {
    Write-Host ('INSTALACION INCOMPLETA: ' + $_.Exception.Message) -ForegroundColor Red
    exit 1
}
