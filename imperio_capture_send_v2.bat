@echo off
setlocal enabledelayedexpansion
REM ================================================================
REM SISTEMA IMPERIO - CAPTURAS CONTINUAS V2
REM ================================================================

title Imperio Capture Send V2

cd /d "%~dp0"

REM Criar pastas necessarias
if not exist "data\logs" mkdir "data\logs"
if not exist "screenshots" mkdir "screenshots"

echo ================================================================
echo    SISTEMA IMPERIO - CAPTURA CONTINUA V2
echo ================================================================
echo.

REM ================================================================
REM AGUARDAR SERVIDOR (LOOP INFINITO ATE ENCONTRAR)
REM ================================================================
:wait_server
echo [%time:~0,8%] Verificando servidor...

.\venv\Scripts\python.exe -c "import requests; requests.get('http://localhost:8002/health', timeout=3)" 2>nul
if !errorlevel! neq 0 (
    echo [%time:~0,8%] Servidor nao encontrado, aguardando 10s...
    timeout /t 10 /nobreak >nul
    goto wait_server
)

echo [%time:~0,8%] Servidor ATIVO!
echo.

REM ================================================================
REM LOOP PRINCIPAL SIMPLIFICADO
REM ================================================================
echo [%time:~0,8%] Monitoramento iniciado
echo Capturas programadas: XX:01 e XX:31
echo.

:main_loop

REM Pegar apenas o minuto atual
for /f "tokens=2 delims=:." %%a in ("%time%") do set min=%%a

REM Remover zero a esquerda se houver
set min=!min: =!
if "!min:~0,1!"=="0" set min=!min:~1!

REM Verificar se e minuto 1 ou 31
if "!min!"=="1" (
    call :do_capture
    call :wait_next_minute
)
if "!min!"=="31" (
    call :do_capture
    call :wait_next_minute
)

REM Aguardar 10 segundos antes de verificar novamente
timeout /t 10 /nobreak >nul
goto main_loop

REM ================================================================
REM FUNCAO: EXECUTAR CAPTURA
REM ================================================================
:do_capture
echo.
echo ================================================================
echo [%time:~0,8%] EXECUTANDO CAPTURA
echo ================================================================

REM Verificar servidor
.\venv\Scripts\python.exe -c "import requests; r=requests.get('http://localhost:8002/health',timeout=3); exit(0 if r.status_code==200 else 1)" 2>nul
if !errorlevel! neq 0 (
    echo [%time:~0,8%] Servidor offline - captura cancelada
    goto :eof
)

REM Verificar se há outra captura em execução (LOCK)
if exist "data\capture.lock" (
    echo [%time:~0,8%] Outra captura em execucao - pulando
    goto :eof
)

REM Criar arquivo de lock
echo %time% > "data\capture.lock"

REM Executar captura
echo [%time:~0,8%] Capturando screenshots...
.\venv\Scripts\python.exe execute_capture.py 2>nul
set capture_result=!errorlevel!

REM Remover lock
del "data\capture.lock" >nul 2>&1

if !capture_result! equ 0 (
    echo [%time:~0,8%] Captura concluida!
) else (
    echo [%time:~0,8%] Captura falhou
)

echo ================================================================
echo.
goto :eof

REM ================================================================
REM FUNCAO: AGUARDAR PROXIMO MINUTO
REM ================================================================
:wait_next_minute
echo [%time:~0,8%] Aguardando proximo ciclo...
timeout /t 60 /nobreak >nul
goto :eof