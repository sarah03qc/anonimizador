param([switch]$FromZip,[switch]$ProbeOnly)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Split-Path $PSScriptRoot -Parent))
$validationRoot = Join-Path ([IO.Path]::GetTempPath()) ('CENCINAI Portable QA ' + [guid]::NewGuid().ToString('N'))
New-Item -ItemType Directory -Path $validationRoot | Out-Null
if ($FromZip) {
    $zipFile = Join-Path $projectRoot 'release\Anonimizador_CEN-CINAI_v1.0_Windows.zip'
    Expand-Archive -LiteralPath $zipFile -DestinationPath $validationRoot
} else {
    Copy-Item -LiteralPath (Join-Path $projectRoot 'dist\Anonimizador_CEN-CINAI') -Destination $validationRoot -Recurse
}
$bundle = Join-Path $validationRoot 'Anonimizador_CEN-CINAI'
$exe = Join-Path $bundle 'Anonimizador CEN-CINAI.exe'
$probe = Join-Path $validationRoot 'probe.json'
$diagnostic = Join-Path $validationRoot 'diagnostic.txt'
$status = Join-Path $validationRoot 'startup.json'
$savedEnv = @{}
foreach ($key in @('PATH','PYTHONPATH','PYTHONHOME','HF_HOME','HF_HUB_CACHE')) { $savedEnv[$key] = [Environment]::GetEnvironmentVariable($key,'Process') }
try {
    $env:PATH = (Join-Path $env:SystemRoot 'System32') + ';' + $env:SystemRoot
    Remove-Item Env:PYTHONPATH -ErrorAction SilentlyContinue
    Remove-Item Env:PYTHONHOME -ErrorAction SilentlyContinue
    $env:HF_HOME = Join-Path $validationRoot 'empty-external-cache'
    $env:HF_HUB_CACHE = Join-Path $validationRoot 'empty-external-cache\hub'
    $probeProcess = Start-Process -FilePath $exe -WorkingDirectory $validationRoot -ArgumentList @('--qa-probe',('"' + $probe + '"'),'--diagnostics-log',('"' + $diagnostic + '"')) -WindowStyle Hidden -PassThru
    if (-not $probeProcess.WaitForExit(300000)) { Stop-Process -Id $probeProcess.Id; throw 'El diagnóstico del bundle excedió el tiempo esperado.' }
    if ($probeProcess.ExitCode -ne 0 -or -not (Test-Path -LiteralPath $probe)) { throw ('Falló el diagnóstico: ' + $diagnostic) }
    if (-not $ProbeOnly) {
        # This is the actual user-facing GUI, intentionally visible; its server is windowless.
        $app = Start-Process -FilePath $exe -WorkingDirectory $validationRoot -ArgumentList @('--qa-status',('"' + $status + '"'),'--diagnostics-log',('"' + $diagnostic + '"')) -WindowStyle Normal -PassThru
        $deadline = [DateTime]::UtcNow.AddSeconds(200)
        while (-not (Test-Path -LiteralPath $status)) {
            if ($app.HasExited -or [DateTime]::UtcNow -gt $deadline) { throw ('No arrancó el bundle. Diagnóstico: ' + $diagnostic) }
            Start-Sleep -Milliseconds 500
        }
    }
} finally {
    foreach ($key in $savedEnv.Keys) { [Environment]::SetEnvironmentVariable($key,$savedEnv[$key],'Process') }
}
$report = @{validation_root=$validationRoot;bundle=$bundle;probe=(Get-Content -LiteralPath $probe -Raw | ConvertFrom-Json);from_zip=[bool]$FromZip;path_without_python=$true;external_cache_initially_empty=$true}
if (-not $ProbeOnly) { $report.startup=Get-Content -LiteralPath $status -Raw | ConvertFrom-Json }
$outputName = if ($FromZip) { 'windows_zip_validation.json' } else { 'windows_clean_validation.json' }
$report | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $projectRoot ('reports\' + $outputName)) -Encoding UTF8
$report | ConvertTo-Json -Depth 8
