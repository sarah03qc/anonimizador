param([switch]$SkipZip)
$ErrorActionPreference = 'Stop'
$env:HF_HUB_OFFLINE = '1'
$env:TRANSFORMERS_OFFLINE = '1'
$env:HF_HUB_DISABLE_TELEMETRY = '1'
$projectRoot = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$pythonBuild = Join-Path $projectRoot '.venv\Scripts\python.exe'
if (-not (Test-Path -LiteralPath $pythonBuild)) { throw 'Primero prepare el entorno de build indicado en WINDOWS_DISTRIBUTION.md.' }
$buildRoot = Join-Path $projectRoot 'build\windows'
$distRoot = Join-Path $projectRoot 'dist'
$bundleRoot = Join-Path $distRoot 'Anonimizador_CEN-CINAI'
# Validate exact cleanup targets before deleting only generated build outputs.
foreach ($targetPath in @($buildRoot, $bundleRoot)) {
    $resolvedTarget = [IO.Path]::GetFullPath($targetPath)
    if (-not $resolvedTarget.StartsWith($projectRoot + [IO.Path]::DirectorySeparatorChar,[StringComparison]::OrdinalIgnoreCase)) { throw 'Ruta de limpieza no autorizada.' }
    if (Test-Path -LiteralPath $resolvedTarget) { Remove-Item -LiteralPath $resolvedTarget -Recurse -Force }
}
Push-Location $projectRoot
try {
    & $pythonBuild scripts\prepare_windows_resources.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la preparación de recursos.' }
    & $pythonBuild -m PyInstaller --noconfirm --clean --workpath $buildRoot --distpath $distRoot windows\Anonimizador.spec
    if ($LASTEXITCODE -ne 0) { throw 'Falló PyInstaller.' }
    Copy-Item -LiteralPath 'windows\LEAME.txt' -Destination $bundleRoot
    Copy-Item -LiteralPath 'build\windows\resources\THIRD_PARTY_LICENSES.txt' -Destination $bundleRoot
    Copy-Item -LiteralPath 'build\windows\resources\LICENSES' -Destination $bundleRoot -Recurse
    & $pythonBuild scripts\prune_windows_payload.py
    if ($LASTEXITCODE -ne 0) { throw 'Falló la exclusión de fixtures de dependencias.' }
    & $pythonBuild scripts\validate_windows_bundle.py $bundleRoot
    if ($LASTEXITCODE -ne 0) { throw 'Falló la validación de recursos.' }
    if (-not $SkipZip) {
        New-Item -ItemType Directory -Path 'release' -Force | Out-Null
        & $pythonBuild scripts\zip_windows_bundle.py
        if ($LASTEXITCODE -ne 0) { throw 'Falló la creación del ZIP.' }
    }
} finally { Pop-Location }
