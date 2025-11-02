@echo off
REM ================================================================
REM SISTEMA IMPERIO - INICIALIZACAO NORMAL (SEM RESET)
REM ================================================================
REM Inicia servidor, coleta dados (mantendo historico), captura e WhatsApp
REM Ideal para reinicios ou continuacao do servico
REM ================================================================

title Sistema Imperio - Inicializacao Normal

cd /d "%~dp0"

REM Log do inicio
echo [%date% %time%] INICIO INICIALIZACAO NORMAL >> "data\logs\imperio_start.log"

cls
echo ================================================================
echo       SISTEMA IMPERIO - INICIALIZACAO NORMAL
echo ================================================================
echo.
echo [%date% %time%] Iniciando sistema (mantendo historico)...
echo.

REM ================================================================
REM FASE 1: LIMPEZA BASICA
REM ================================================================
echo [FASE 1] LIMPEZA BASICA
echo ========================================
echo.

REM Finalizar APENAS processos Python e drivers - NAO mata navegadores do usuario
echo [LIMPEZA] Finalizando processos de automacao anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM chromedriver.exe >nul 2>&1
timeout /t 2 /nobreak >nul

REM Limpar screenshots antigos (opcional - comentado para manter historico)
REM echo [LIMPEZA] Removendo screenshots antigos...
REM if exist "screenshots\*.png" del /Q "screenshots\*.png" >nul 2>&1

REM Limpar perfis temporarios
echo [LIMPEZA] Removendo perfis temporarios...
for /d %%i in (C:\temp_chrome_*) do rd /s /q "%%i" 2>nul

REM Criar diretorios necessarios
echo [LIMPEZA] Verificando estrutura de pastas...
if not exist "data\logs" mkdir "data\logs"
if not exist "screenshots" mkdir "screenshots"
if not exist "temp_upload" mkdir "temp_upload"
if not exist "data\whatsapp_session" mkdir "data\whatsapp_session"

echo [LIMPEZA] Limpeza basica finalizada!
echo.

REM ================================================================
REM FASE 2: INICIAR SERVIDOR
REM ================================================================
echo [FASE 2] INICIANDO SERVIDOR IMPERIO
echo ========================================
echo.

echo [SERVIDOR] Iniciando servidor FastAPI com scheduler integrado...
start /B /MIN "Imperio Server Core" .\venv\Scripts\python.exe -m uvicorn core.app:app --host 0.0.0.0 --port 8002 --log-level info

echo [SERVIDOR] Aguardando servidor iniciar (10 segundos)...
timeout /t 10 /nobreak >nul

REM Verificar se servidor esta respondendo
.\venv\Scripts\python.exe -c "import requests; r = requests.get('http://localhost:8002/health', timeout=5); print('[SERVIDOR] Status: OK' if r.status_code == 200 else '[SERVIDOR] ERRO: Servidor nao respondeu'); exit(0 if r.status_code == 200 else 1)" 2>nul

if errorlevel 1 (
    echo [SERVIDOR] ERRO: Servidor nao iniciou corretamente
    echo [SERVIDOR] Tentando iniciar novamente...
    start /B /MIN "Imperio Server Core" .\venv\Scripts\python.exe -m uvicorn core.app:app --host 0.0.0.0 --port 8002 --log-level info
    timeout /t 10 /nobreak >nul
)

echo [SERVIDOR] Servidor iniciado com scheduler integrado!
echo [SERVIDOR] Coletas automaticas: XX:00 e XX:30
echo.

REM ================================================================
REM FASE 3: COLETA DE DADOS INICIAL
REM ================================================================
echo [FASE 3] EXECUTANDO COLETA INICIAL
echo ========================================
echo.

echo [COLETA] Coletando dados do sistema principal...
.\venv\Scripts\python.exe -c "from core.services.data_collector import imperio_collector; from core.database.base import SessionLocal; from core.services.data_manager import imperio_data_manager; result = imperio_collector.execute_full_collection(); db = SessionLocal(); saved = imperio_data_manager.save_collection_data(db, result) if result else False; db.close(); print(f'[COLETA] ROI: {result.get(\"totals\", {}).get(\"roi\", 0):.2f}%%' if result else '[COLETA] Erro na coleta'); print(f'[COLETA] Vendas: R$ {result.get(\"totals\", {}).get(\"sales\", 0):,.2f}' if result else ''); print(f'[COLETA] Dados salvos: {saved}')" 2>>data\logs\imperio_start.log

echo [COLETA] Coleta do sistema principal concluida!
echo.

timeout /t 2 /nobreak >nul

REM ================================================================
REM FASE 3.5: COLETA HORA DO PIX INICIAL
REM ================================================================
echo [FASE 3.5] EXECUTANDO COLETA HORA DO PIX
echo ========================================
echo.

echo [HORAPIX] Coletando dados dos sorteios Hora do Pix...
.\venv\Scripts\python.exe scripts\collect_horapix_initial.py 2>>data\logs\imperio_start.log

if errorlevel 1 (
    echo [HORAPIX] Aviso: Coleta Hora do Pix falhou - sera tentada novamente na proxima execucao
) else (
    echo [HORAPIX] Coleta Hora do Pix concluida com sucesso!
)

echo.
timeout /t 2 /nobreak >nul

REM ================================================================
REM FASE 4: CAPTURA DE SCREENSHOTS
REM ================================================================
echo [FASE 4] CAPTURANDO SCREENSHOTS
echo ========================================
echo.

REM Verificar se há outra captura em execução
if exist "data\capture.lock" (
    echo [CAPTURA] AVISO: Outra captura em execucao - aguardando...
    timeout /t 30 /nobreak >nul
    if exist "data\capture.lock" (
        echo [CAPTURA] Timeout - removendo lock antigo
        del "data\capture.lock" >nul 2>&1
    )
)

REM Criar arquivo de lock
echo %time% > "data\capture.lock"

REM Limpar screenshots antigos para evitar duplicatas
echo [CAPTURA] Limpando screenshots antigos para evitar duplicatas...
if exist "screenshots\*.png" del /Q "screenshots\*.png" >nul 2>&1

echo [CAPTURA] Capturando dashboards (geral, perfil, grupos, horapix)...
.\venv\Scripts\python.exe -c "import asyncio; from core.services.capture_service_fast import ImperioCaptureServiceFast; s = ImperioCaptureServiceFast(); result = asyncio.run(s.capture_screenshots_fast('screenshots')); print(f'[CAPTURA] Capturados: {result[\"total_captured\"]} arquivos'); [print(f'[CAPTURA] - {f[\"page\"]}: {f[\"file_size_kb\"]}KB') for f in result.get('files', [])]" 2>>data\logs\imperio_start.log

REM Remover lock
del "data\capture.lock" >nul 2>&1

if exist "screenshots\geral_*.png" (
    echo [CAPTURA] Screenshots capturados com sucesso!
) else (
    echo [CAPTURA] Aviso: Alguns screenshots podem ter falhado
)

echo.

REM ================================================================
REM FASE 5: ENVIAR VIA WHATSAPP
REM ================================================================
echo [FASE 5] ENVIANDO VIA WHATSAPP
echo ========================================
echo.

if exist "screenshots\*.png" (
    echo [WHATSAPP] Screenshots encontrados - separando por grupo...
    timeout /t 3 /nobreak >nul

    REM Usar script Python dedicado para evitar problemas de encoding
    .\venv\Scripts\python.exe scripts\send_whatsapp_screenshots.py 2>>data\logs\imperio_start.log

    if errorlevel 1 (
        echo [WHATSAPP] Primeiro envio requer QR Code - execute enviar_whatsapp_brave.bat manualmente
    ) else (
        echo [WHATSAPP] Envio concluido com sucesso!
    )
) else (
    echo [WHATSAPP] Nenhum screenshot encontrado para envio
)

echo.

REM ================================================================
REM FASE 6: SISTEMA ATIVO
REM ================================================================
echo [FASE 6] SISTEMA CONFIGURADO
echo ========================================
echo.

echo [AUTOMACAO] Sistema configurado para:
echo   - Coleta sistema principal: XX:00 e XX:30
echo   - Coleta Hora do Pix: XX:00 e XX:30 (integrado)
echo   - Captura + WhatsApp: XX:01 e XX:31
echo   - Dashboard: http://localhost:8002/imperio
echo.

REM Log de sucesso
echo [%date% %time%] INICIALIZACAO NORMAL CONCLUIDA >> "data\logs\imperio_start.log"

REM ================================================================
REM SISTEMA INICIADO
REM ================================================================
echo ================================================================
echo         SISTEMA IMPERIO INICIADO COM SUCESSO!
echo ================================================================
echo.
echo Dashboard: http://localhost:8002/imperio
echo.
echo Sistema configurado:
echo   [OK] Banco de dados mantido (historico preservado)
echo   [OK] Coleta do sistema principal executada
echo   [OK] Coleta Hora do Pix executada
echo   [OK] Screenshots capturados (4 abas: geral, perfil, grupos, horapix)
echo   [OK] WhatsApp configurado
echo   [OK] Servidor rodando com scheduler integrado
echo.
echo Proximas execucoes automaticas:
echo   - Coletas: XX:00 e XX:30 (sistema principal + Hora do Pix)
echo   - Capturas: XX:01 e XX:31 (4 abas)
echo.
echo O servidor mantem o sistema rodando 24/7 com coletas automaticas.
echo.
echo ================================================================
echo.

REM Log final
echo [%date% %time%] SISTEMA ATIVO - SERVIDOR RODANDO >> "data\logs\imperio_start.log"

echo [AUTO] Sistema em execucao continua
echo [AUTO] Dashboard: http://localhost:8002/imperio
echo [AUTO] Logs: data\logs\imperio_start.log
echo.

REM Script termina - servidor continua rodando
exit /b 0
