@echo off
rem =============================================================================
rem run_all.bat — Grid-Arbitrage mit Batteriespeichern CH
rem SC26_Gruppe_2 | CAS Information Engineering — Scripting, ZHAW 2026
rem =============================================================================
rem
rem Ausfuehrung (Doppelklick oder cmd):
rem   run_all.bat              alle Notebooks
rem   run_all.bat pflicht      nur NB01-NB04
rem   run_all.bat kuer         nur Kuer (setzt Pflicht voraus)
rem   run_all.bat nb 03        einzelnes Notebook
rem
rem Voraussetzung: jupyter-env unter C:\Users\patri\jupyter-env
rem
rem =============================================================================

setlocal enabledelayedexpansion

rem ── Umgebung aktivieren ──────────────────────────────────────────────────────
call C:\Users\patri\jupyter-env\Scripts\activate

rem Asyncio ProactorLoop Warning unterdruecken (zmq/tornado, kein Fehler)
set PYTHONASYNCIODEBUG=0

set MODE=%~1
set NB=%~2
if "%MODE%"=="" set MODE=all

set TIMEOUT=1800
set LOG_DIR=logs
if not exist %LOG_DIR% mkdir %LOG_DIR%

for /f "tokens=2 delims==" %%i in ('wmic os get localdatetime /value') do set DT=%%i
set STAMP=%DT:~0,8%_%DT:~8,6%
set LOG_FILE=%LOG_DIR%\run_all_%STAMP%.log

rem ── Pflicht-Reihenfolge ──────────────────────────────────────────────────────
set PFLICHT[0]=01_Daten_Laden
set PFLICHT[1]=02_Daten_Analyse
set PFLICHT[2]=03_Visualisierungen
set PFLICHT[3]=04_Business_Case
set PFLICHT_COUNT=4

rem ── Kuer-Reihenfolge (transfer.json-Abhaengigkeiten) ────────────────────────
set KUER[0]=06_Raeumliche_Analyse
set KUER[1]=07_Cross_Border
set KUER[2]=08_Marktdynamik
set KUER[3]=08a_Animationen
set KUER[4]=09_Revenue_Stacking
set KUER[5]=10_Dispatch_Optimierung
set KUER[6]=11_Technologievergleich
set KUER[7]=12_Alternative_Speicher
set KUER[8]=13_Eigenverbrauch
set KUER[9]=15_Kombinierte_Simulation
set KUER[10]=14_Produkt_Steckbrief
set KUER[11]=05_Business_Strategy
set KUER_COUNT=12

rem ── Helper ───────────────────────────────────────────────────────────────────
set HELPER[0]=00_Project_Overview
set HELPER[1]=00b_Konventionen
set HELPER[2]=99_Datenprovenienz
set HELPER_COUNT=3

rem ── Pruefen ob jupyter verfuegbar ────────────────────────────────────────────
where jupyter >nul 2>&1
if errorlevel 1 (
    echo.
    echo [FEHLER] 'jupyter' nicht gefunden.
    echo          Pruefen ob Pfad korrekt: C:\Users\patri\jupyter-env\Scripts\activate
    echo.
    pause
    exit /b 1
)

rem ── Header ───────────────────────────────────────────────────────────────────
echo.
echo ============================================================
echo   run_all.bat -- Grid-Arbitrage SC26_Gruppe_2
echo   Modus : %MODE%
echo   Log   : %LOG_FILE%
echo ============================================================
echo run_all.bat Modus=%MODE% >> %LOG_FILE%

set TOTAL_OK=0
set TOTAL_FAIL=0

rem ── Ausfuehrung ──────────────────────────────────────────────────────────────
if "%MODE%"=="pflicht" (
    call :run_list PFLICHT %PFLICHT_COUNT%
) else if "%MODE%"=="kuer" (
    echo [INFO] Kuer-Modus: NB01/NB02 muessen bereits ausgefuehrt sein.
    call :run_list KUER %KUER_COUNT%
) else if "%MODE%"=="nb" (
    if "%NB%"=="" (
        echo [FEHLER] Nummer angeben, z.B.:  run_all.bat nb 03
        pause
        exit /b 1
    )
    for /f "tokens=*" %%f in ('dir /b "%NB%_*.ipynb" 2^>nul') do (
        set FOUND=%%f
        goto :run_single
    )
    echo [FEHLER] Kein Notebook mit Nummer %NB% gefunden.
    pause
    exit /b 1
    :run_single
    call :run_nb "%FOUND:.ipynb=%"
) else (
    call :run_list PFLICHT %PFLICHT_COUNT%
    call :run_list KUER %KUER_COUNT%
    call :run_list HELPER %HELPER_COUNT%
)

rem ── Zusammenfassung ──────────────────────────────────────────────────────────
echo.
echo ============================================================
echo   OK    : %TOTAL_OK%
echo   Fehler: %TOTAL_FAIL%
echo   Log   : %LOG_FILE%
echo ============================================================
if %TOTAL_FAIL%==0 (
    echo   [OK] Alle Notebooks erfolgreich ausgefuehrt.
) else (
    echo   [!!] %TOTAL_FAIL% Notebooks fehlgeschlagen -- Log pruefen.
)
echo.
pause
exit /b %TOTAL_FAIL%

rem =============================================================================
:run_list
set _ARR=%~1
set _CNT=%~2
echo.
echo --- %_ARR% ---
for /l %%i in (0,1,%_CNT%) do (
    if %%i lss %_CNT% call :run_nb "!%_ARR%[%%i]!"
)
goto :eof

rem =============================================================================
:run_nb
set _NB=%~1
set _FILE=%_NB%.ipynb
if not exist "%_FILE%" (
    echo   [--] %_FILE% nicht gefunden -- uebersprungen
    goto :eof
)
echo   [^>^>] %_NB%
(echo   [^>^>] %_NB%) >> %LOG_FILE%
jupyter nbconvert --to notebook --execute --inplace ^
    --ExecutePreprocessor.timeout=%TIMEOUT% ^
    --ExecutePreprocessor.kernel_name=python3 ^
    "%_FILE%" >> %LOG_FILE% 2>&1
if errorlevel 1 (
    echo   [!!] FEHLER: %_NB%
    set /a TOTAL_FAIL+=1
) else (
    echo   [OK] %_NB%
    set /a TOTAL_OK+=1
)
goto :eof
