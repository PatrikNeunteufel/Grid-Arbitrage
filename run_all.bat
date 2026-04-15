@echo off
setlocal EnableDelayedExpansion

rem =========================================================================
rem run_all.bat  -- SC26_Gruppe_2  Grid-Arbitrage Batteriespeicher
rem Verwendung:  run_all.bat [all|pflicht|kuer|org]
rem =========================================================================

set MODE=%1
if "%MODE%"=="" set MODE=all

set OK_COUNT=0
set FAIL_COUNT=0
set FAIL_LIST=

rem -- Timestamp fuer Logdatei -----------------------------------------------
set CUR_DATE=%DATE:~6,4%%DATE:~3,2%%DATE:~0,2%
set CUR_TIME=%TIME:~0,2%%TIME:~3,2%%TIME:~6,2%
set CUR_TIME=%CUR_TIME: =0%
set TIMESTAMP=%CUR_DATE%_%CUR_TIME%
if not exist logs mkdir logs
set LOGFILE=logs\run_all_%TIMESTAMP%.log
echo run_all.bat Modus=%MODE% > "%LOGFILE%"

rem -- venv aktivieren -------------------------------------------------------
rem Pfad aus jupyter-env (C:\Users\patri\jupyter-env\Scripts\...)
set VENV_ROOT=C:\Users\patri\jupyter-env
set NBCONVERT_EXE=%VENV_ROOT%\Scripts\jupyter-nbconvert.EXE

if exist "%NBCONVERT_EXE%" (
    set NBCMD="%NBCONVERT_EXE%"
    echo [venv] Verwende %NBCONVERT_EXE%
) else (
    rem Fallback 1: venv aktivieren und python -m nbconvert
    if exist "%VENV_ROOT%\Scripts\activate.bat" (
        call "%VENV_ROOT%\Scripts\activate.bat"
        set NBCMD=python -m nbconvert
        echo [venv] Aktiviert: %VENV_ROOT%
    ) else (
        rem Fallback 2: System-python
        set NBCMD=python -m nbconvert
        echo [warn] venv nicht gefunden - System-python wird verwendet
    )
)

echo ================================================================
echo  run_all.bat  Modus=%MODE%
echo  Befehl: %NBCMD%
echo ================================================================

rem -- Pflicht ---------------------------------------------------------------
if "%MODE%"=="kuer" goto :kuer
if "%MODE%"=="org"  goto :org

call :run_nb "notebooks/01_Daten_Laden"
call :run_nb "notebooks/02_Daten_Bereinigung"
call :run_nb "notebooks/03_Daten_Analyse"
call :run_nb "notebooks/04_Visualisierungen"
call :run_nb "notebooks/00_Business_Case"

if "%MODE%"=="pflicht" goto :summary

rem -- Kuer ------------------------------------------------------------------
:kuer
call :run_nb "kuer/K_01_Raeumliche_Analyse"
call :run_nb "kuer/K_02_Cross_Border"
call :run_nb "kuer/K_03_Marktdynamik"
call :run_nb "kuer/K_04_Animationen"
call :run_nb "kuer/K_05_Revenue_Stacking"
call :run_nb "kuer/K_06_Dispatch_Optimierung"
call :run_nb "kuer/K_07_Technologievergleich"
call :run_nb "kuer/K_08_Alternative_Speicher"
call :run_nb "kuer/K_09_Eigenverbrauch"
call :run_nb "kuer/K_10_Produkt_Steckbrief"
call :run_nb "kuer/K_99_Kombinierte_Simulation"
call :run_nb "kuer/K_00_Business_Strategy"

if "%MODE%"=="kuer" goto :summary

rem -- Organisation ----------------------------------------------------------
:org
call :run_nb "organisation/O_01_Project_Overview"
call :run_nb "organisation/O_99_Datenprovenienz"

goto :summary

rem =========================================================================
:run_nb
set NB_PATH=%~1
set NB_FILE=%NB_PATH%.ipynb

echo [>>] %NB_PATH%

%NBCMD% --execute --to notebook --inplace "%NB_FILE%" >> "%LOGFILE%" 2>&1

if !ERRORLEVEL! NEQ 0 (
    echo [FAIL] %NB_PATH%
    set /a FAIL_COUNT=FAIL_COUNT+1
    set FAIL_LIST=!FAIL_LIST! %NB_PATH%
) else (
    echo [OK]   %NB_PATH%
    set /a OK_COUNT=OK_COUNT+1
)
goto :eof

rem =========================================================================
:summary
echo ================================================================
echo OK     : %OK_COUNT%
echo Fehler : %FAIL_COUNT%
if not "%FAIL_LIST%"=="" (
    echo.
    echo Fehlgeschlagene Notebooks:
    for %%F in (%FAIL_LIST%) do echo   [FAIL] %%F
)
echo ================================================================
if %FAIL_COUNT% GTR 0 (
    echo [!] %FAIL_COUNT% Fehler.
) else (
    echo [OK] Alle Notebooks erfolgreich ausgefuehrt.
)
echo Log: %LOGFILE%
echo.
pause
