#!/usr/bin/env bash
# run_all.sh — Grid-Arbitrage SC26_Gruppe_2
set -euo pipefail
export PYTHONWARNINGS=ignore::RuntimeWarning
MODE=${1:-all}
TIMEOUT=1800
LOG_DIR=logs
mkdir -p "$LOG_DIR"
STAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$LOG_DIR/run_all_$STAMP.log"
OK=0; FAIL=0

# K_01…K_99 zuerst, K_00 (Synthese/Strategy) zuletzt
PFLICHT=("notebooks/01_Daten_Laden" "notebooks/02_Daten_Bereinigung" "notebooks/03_Daten_Analyse" "notebooks/04_Visualisierungen" "notebooks/00_Business_Case")
KUER=("kuer/K_01_Raeumliche_Analyse" "kuer/K_02_Cross_Border" "kuer/K_03_Marktdynamik" "kuer/K_04_Animationen" "kuer/K_05_Revenue_Stacking" "kuer/K_06_Dispatch_Optimierung" "kuer/K_07_Technologievergleich" "kuer/K_08_Alternative_Speicher" "kuer/K_09_Eigenverbrauch" "kuer/K_10_Produkt_Steckbrief" "kuer/K_99_Kombinierte_Simulation" "kuer/K_00_Business_Strategy")
ORG=("organisation/O_01_Project_Overview" "organisation/O_99_Datenprovenienz")

run_nb() {
    local nb="$1"
    if [ ! -f "${nb}.ipynb" ]; then echo "  [--] ${nb}.ipynb nicht gefunden"; return; fi
    echo "  [>>] $nb" | tee -a "$LOG_FILE"
    if jupyter nbconvert --to notebook --execute --inplace \
        --ExecutePreprocessor.timeout=$TIMEOUT \
        --ExecutePreprocessor.kernel_name=python3 \
        "${nb}.ipynb" >> "$LOG_FILE" 2>&1; then
        echo "  [OK] $nb"; ((OK+=1))
    else
        echo "  [!!] FEHLER: $nb"; ((FAIL+=1))
    fi
}

run_list() { for nb in "$@"; do run_nb "$nb"; done; }

case "$MODE" in
  pflicht) run_list "${PFLICHT[@]}" ;;
  kuer)    run_list "${KUER[@]}" ;;
  nb)      run_nb "${2:-}" ;;
  *)       run_list "${PFLICHT[@]}"; run_list "${KUER[@]}"; run_list "${ORG[@]}" ;;
esac

echo
echo "OK: $OK | Fehler: $FAIL | Log: $LOG_FILE"
exit $FAIL
