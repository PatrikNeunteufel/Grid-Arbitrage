# run_all.ps1 — Grid-Arbitrage SC26_Gruppe_2
param([string]$Mode='all', [string]$Nb='')
$ErrorActionPreference='Stop'
$env:PYTHONWARNINGS='ignore::RuntimeWarning'
$timeout=1800; $ok=0; $fail=0
$logDir='logs'; New-Item -ItemType Directory -Force $logDir | Out-Null
$stamp=(Get-Date -Format 'yyyyMMdd_HHmmss')
$log="$logDir/run_all_$stamp.log"

$pflicht = @("notebooks/01_Daten_Laden", "notebooks/02_Daten_Bereinigung", "notebooks/03_Daten_Analyse", "notebooks/04_Visualisierungen", "notebooks/00_Business_Case")
# K_01…K_99 zuerst, K_00 (Synthese/Strategy) zuletzt
$kuer = @("kuer/K_01_Raeumliche_Analyse", "kuer/K_02_Cross_Border", "kuer/K_03_Marktdynamik", "kuer/K_04_Animationen", "kuer/K_05_Revenue_Stacking", "kuer/K_06_Dispatch_Optimierung", "kuer/K_07_Technologievergleich", "kuer/K_08_Alternative_Speicher", "kuer/K_09_Eigenverbrauch", "kuer/K_10_Produkt_Steckbrief", "kuer/K_99_Kombinierte_Simulation", "kuer/K_00_Business_Strategy")
$org = @("organisation/O_01_Project_Overview", "organisation/O_99_Datenprovenienz")

function Run-NB($nb) {
    if (-not (Test-Path "$nb.ipynb")) { Write-Host "  [--] $nb.ipynb nicht gefunden"; return }
    Write-Host "  [>>] $nb"
    $res = jupyter nbconvert --to notebook --execute --inplace `
        --ExecutePreprocessor.timeout=$timeout `
        --ExecutePreprocessor.kernel_name=python3 "$nb.ipynb" 2>&1
    $res | Add-Content $log
    if ($LASTEXITCODE -eq 0) { Write-Host "  [OK] $nb"; $script:ok++ }
    else { Write-Host "  [!!] FEHLER: $nb"; $script:fail++ }
}

switch ($Mode) {
    'pflicht' { $pflicht | ForEach-Object { Run-NB $_ } }
    'kuer'    { $kuer    | ForEach-Object { Run-NB $_ } }
    'nb'      { Run-NB $Nb }
    default   { $pflicht+$kuer+$org | ForEach-Object { Run-NB $_ } }
}

Write-Host ""
Write-Host "OK: $ok | Fehler: $fail | Log: $log"
exit $fail
