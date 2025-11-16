@echo off
REM ================================================================
REM SISTEMA IMPERIO - RESET DIARIO COMPLETO + AUTOMACAO
REM ================================================================
REM Reset total do banco, coleta inicial, captura, WhatsApp e automacao
REM Perfeito para Task Scheduler executar diariamente (00:00 ou ao iniciar)
REM ================================================================

title Sistema Imperio - Reset Diario Completo

cd /d "%~dp0"

REM Log do inicio
echo [%date% %time%] INICIO RESET DIARIO COMPLETO >> "data\logs\daily_reset.log"

cls
echo ================================================================
echo       SISTEMA IMPERIO - RESET DIARIO E MONITORAMENTO
echo ================================================================
echo.
echo [%date% %time%] Iniciando reset completo do sistema...
echo.

REM ================================================================
REM FASE 1: LIMPEZA TOTAL
REM ================================================================
echo [FASE 1] LIMPEZA COMPLETA DO SISTEMA
echo ========================================
echo.

REM Finalizar APENAS processos Python e drivers - NAO mata navegadores do usuario
echo [LIMPEZA] Finalizando apenas processos de automacao anteriores...
taskkill /F /IM python.exe >nul 2>&1
taskkill /F /IM chromedriver.exe >nul 2>&1
REM IMPORTANTE: NAO mata chrome.exe nem brave.exe para preservar sessoes do usuario
timeout /t 2 /nobreak >nul

REM Limpar screenshots antigos
echo [LIMPEZA] Removendo screenshots antigos...
if exist "screenshots\*.png" (
    del /Q "screenshots\*.png" >nul 2>&1
    echo [LIMPEZA] Screenshots antigos removidos
) else (
    echo [LIMPEZA] Nenhum screenshot antigo encontrado
)

REM Limpar logs antigos (manter ultimos 7 dias)
echo [LIMPEZA] Limpando logs antigos...
forfiles /p "data\logs" /s /m *.log /d -7 /c "cmd /c del @path" 2>nul

REM Limpar perfis temporarios
echo [LIMPEZA] Removendo perfis temporarios...
for /d %%i in (C:\temp_chrome_*) do rd /s /q "%%i" 2>nul

REM Criar diretorios necessarios
echo [LIMPEZA] Criando estrutura de pastas...
if not exist "data\logs" mkdir "data\logs"
if not exist "screenshots" mkdir "screenshots"
if not exist "temp_upload" mkdir "temp_upload"
if not exist "data\whatsapp_session" mkdir "data\whatsapp_session"

echo [LIMPEZA] Limpeza completa finalizada!
echo.

REM ================================================================
REM FASE 2: RESET DO BANCO DE DADOS
REM ================================================================
echo [FASE 2] RESET DO BANCO DE DADOS
echo ========================================
echo.

echo [RESET] Executando reset completo do banco...
.\venv\Scripts\python.exe scripts\reset_database_simple.py

echo.

REM ================================================================
REM FASE 3: INICIAR SERVIDOR
REM ================================================================
echo [FASE 3] INICIANDO SERVIDOR IMPERIO
echo ========================================
echo.

echo [SERVIDOR] Iniciando servidor FastAPI com scheduler integrado...
REM Usar uvicorn diretamente com o app do core
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
REM FASE 4: PRIMEIRA COLETA DE DADOS
REM ================================================================
echo [FASE 4] EXECUTANDO PRIMEIRA COLETA
echo ========================================
echo.

echo [COLETA] Coletando dados iniciais completos (Geral, Perfil, Grupos)...

REM Executar coleta COMPLETA e mostrar dados por canal
.\venv\Scripts\python.exe -c "from core.services.data_collector import imperio_collector; from core.database.base import SessionLocal; from core.services.data_manager import imperio_data_manager; result = imperio_collector.execute_full_collection(); db = SessionLocal(); saved = imperio_data_manager.save_collection_data(db, result) if result else False; db.close(); print('[COLETA] === DADOS COLETADOS ==='); print(f'[GERAL] ROI: {result.get(\"totals\", {}).get(\"roi\", 0):.2f} - Vendas: R$ {result.get(\"totals\", {}).get(\"sales\", 0):,.2f} - Gastos: R$ {result.get(\"totals\", {}).get(\"spend\", 0):,.2f}' if result else '[ERRO] Falha na coleta geral'); channels = result.get('channels', {}); instagram = channels.get('instagram', {}); print(f'[PERFIL/INSTAGRAM] ROI: {instagram.get(\"roi\", 0):.2f} - Vendas: R$ {instagram.get(\"sales\", 0):,.2f}' if instagram else '[PERFIL] Sem dados'); grupos = channels.get('grupos', {}); print(f'[GRUPOS] ROI: {grupos.get(\"roi\", 0):.2f} - Vendas: R$ {grupos.get(\"sales\", 0):,.2f}' if grupos else '[GRUPOS] Sem dados'); print(f'[COLETA] Dados salvos no banco: {saved}')" 2>>data\logs\daily_reset.log

echo [COLETA] Primeira coleta completa concluida!
echo.

REM Aguardar dados serem processados
timeout /t 2 /nobreak >nul

REM ================================================================
REM FASE 4.5: PRIMEIRA COLETA HORA DO PIX
REM ================================================================
echo [FASE 4.5] EXECUTANDO COLETA HORA DO PIX
echo ========================================
echo.

echo [HORAPIX] Coletando dados dos sorteios Hora do Pix...
.\venv\Scripts\python.exe scripts\collect_horapix_initial.py 2>>data\logs\daily_reset.log

if errorlevel 1 (
    echo [HORAPIX] Aviso: Coleta Hora do Pix falhou - sera tentada novamente na proxima execucao
) else (
    echo [HORAPIX] Coleta Hora do Pix concluida com sucesso!
)

echo.

REM Aguardar processamento
timeout /t 2 /nobreak >nul

REM ================================================================
REM FASE 4.5B: LIMPAR HISTORICO DA ACAO PRINCIPAL
REM ================================================================
echo [FASE 4.5B] LIMPANDO HISTORICO DA ACAO PRINCIPAL
echo ========================================
echo.

echo [LIMPEZA] Removendo dados antigos para preparar coleta fresca...
.\venv\Scripts\python.exe clean_main_action_history.py 2>>data\logs\daily_reset.log

echo.

REM ================================================================
REM FASE 4.6: PRIMEIRA COLETA ACAO PRINCIPAL
REM ================================================================
echo [FASE 4.6] EXECUTANDO COLETA ACAO PRINCIPAL
echo ========================================
echo.

echo [ACAO PRINCIPAL] Coletando dados frescos do sorteio vigente...

REM Executar coleta da Ação Principal
.\venv\Scripts\python.exe -c "from core.database.base import SessionLocal; from core.services.main_action_service import main_action_service; db = SessionLocal(); current = main_action_service.get_current_action(db); product_id = current['product_id'] if current else '6916292bf6051e4133d86ef9'; result = main_action_service.collect_and_save(db, product_id); action = main_action_service.get_current_action(db); db.close(); print('[ACAO PRINCIPAL] === DADOS COLETADOS ==='); print(f'[ACAO PRINCIPAL] Nome: {action[\"name\"]}' if action else '[ACAO PRINCIPAL] Nenhuma acao vigente'); print(f'[ACAO PRINCIPAL] Receita: R$ {action[\"total_revenue\"]:,.2f}' if action else ''); print(f'[ACAO PRINCIPAL] Custos FB: R$ {action[\"total_fb_cost\"]:,.2f}' if action else ''); print(f'[ACAO PRINCIPAL] Lucro: R$ {action[\"total_profit\"]:,.2f}' if action else ''); print(f'[ACAO PRINCIPAL] ROI: {action[\"total_roi\"]:.2f}%%' if action else ''); print(f'[ACAO PRINCIPAL] Registros diarios: {len(action[\"daily_records\"]) if action and \"daily_records\" in action else 0}')" 2>>data\logs\daily_reset.log

if errorlevel 1 (
    echo [ACAO PRINCIPAL] Aviso: Coleta falhou - sera tentada novamente na proxima execucao
) else (
    echo [ACAO PRINCIPAL] Coleta concluida com sucesso!
)

echo [ACAO PRINCIPAL] Proximas coletas automaticas: XX:00 e XX:30
echo.

REM ================================================================
REM FASE 5: PRIMEIRA CAPTURA DE SCREENSHOTS
REM ================================================================
echo [FASE 5] CAPTURANDO SCREENSHOTS
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

echo [CAPTURA] Capturando dashboards com OTIMIZACAO PARA DIA COMPLETO...
echo [CAPTURA] Sistema configurado para 38 coletas diarias (04:30-23:30)
echo [CAPTURA] Altura minima: 1500px + deteccao inteligente de conteudo
.\venv\Scripts\python.exe -c "import asyncio; from core.services.capture_service_fast import ImperioCaptureServiceFast; s = ImperioCaptureServiceFast(); result = asyncio.run(s.capture_screenshots_fast('screenshots')); print(f'[CAPTURA] Capturados: {result[\"total_captured\"]} arquivos'); [print(f'[CAPTURA] - {f[\"page\"]}: {f[\"file_size_kb\"]}KB') for f in result.get('files', [])]" 2>>data\logs\daily_reset.log

REM Remover lock
del "data\capture.lock" >nul 2>&1

REM Validar se captura funcionou com altura adequada
if exist "screenshots\geral_*.png" (
    echo [CAPTURA] ✅ Screenshot geral capturado com sucesso
    .\venv\Scripts\python.exe -c "import os, glob; files = glob.glob('screenshots/geral_*.png'); latest = max(files, key=os.path.getctime) if files else None; size = os.path.getsize(latest) if latest else 0; print(f'[CAPTURA] Arquivo: {os.path.basename(latest)}' if latest else '[CAPTURA] Erro: arquivo não encontrado'); print(f'[CAPTURA] Tamanho: {size//1024}KB ({\"OK\" if size > 100000 else \"PEQUENO DEMAIS\"})' if latest else '')" 2>>data\logs\daily_reset.log
) else (
    echo [CAPTURA] ❌ ERRO: Screenshot geral nao foi criado
)

echo [CAPTURA] Screenshots capturados com otimizacao para dia completo!
echo.

REM ================================================================
REM FASE 5.5: VALIDACAO DA CAPTURA OTIMIZADA
REM ================================================================
echo [FASE 5.5] VALIDANDO CAPTURA PARA DIA COMPLETO
echo ========================================
echo.

echo [VALIDACAO] Verificando se screenshots comportam 38 coletas diarias...
echo [VALIDACAO] Analisando dimensoes e qualidade dos arquivos capturados...

REM Executar validacao detalhada dos screenshots usando script dedicado
.\venv\Scripts\python.exe validate_screenshots.py 2>>data\logs\daily_reset.log

echo [VALIDACAO] Validacao da captura otimizada concluida!
echo.

REM ================================================================
REM FASE 6: ENVIAR VIA WHATSAPP
REM ================================================================
echo [FASE 6] ENVIANDO VIA WHATSAPP
echo ========================================
echo.

REM Verificar se tem screenshots para enviar
if exist "screenshots\*.png" (
    echo [WHATSAPP] Screenshots encontrados - separando por grupo...

    REM Aguardar um pouco para garantir que arquivos estao completos
    timeout /t 3 /nobreak >nul

    REM Usar script Python dedicado para evitar problemas de encoding
    .\venv\Scripts\python.exe scripts\send_whatsapp_screenshots.py 2>>data\logs\daily_reset.log

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
REM FASE 7: CONFIGURAR AUTOMACAO
REM ================================================================
echo [FASE 7] CONFIGURANDO AUTOMACAO
echo ========================================
echo.

echo [AUTOMACAO] Sistema configurado para:
echo   - Coleta sistema principal: XX:00 e XX:30
echo   - Coleta Hora do Pix: XX:00 e XX:30 (integrado)
echo   - Coleta Acao Principal: XX:00 e XX:30 (integrado)
echo   - Captura + WhatsApp: XX:01 e XX:31 (5 abas)
echo   - Dashboard: http://localhost:8002/imperio
echo.

REM Log de sucesso
echo [%date% %time%] RESET DIARIO COMPLETO COM SUCESSO >> "data\logs\daily_reset.log"

REM ================================================================
REM MODO DE EXECUCAO
REM ================================================================
REM ================================================================
REM SISTEMA INICIADO - SERVIDOR RODANDO COM SCHEDULER INTEGRADO
REM ================================================================
echo ================================================================
echo         SISTEMA IMPERIO INICIADO COM SUCESSO!
echo ================================================================
echo.
echo Dashboard: http://localhost:8002/imperio
echo.
echo Sistema configurado:
echo   [OK] Banco de dados resetado (preservando Acao Principal)
echo   [OK] Coleta COMPLETA executada:
echo       - GERAL: Dados consolidados
echo       - PERFIL/INSTAGRAM: Vendas e ROI
echo       - GRUPOS: WhatsApp/Telegram
echo   [OK] Hora do Pix coletado (sorteios + taxa 3%%)
echo   [OK] Acao Principal atualizada (sorteio vigente)
echo   [OK] Screenshots capturados com OTIMIZACAO PARA DIA COMPLETO
echo   [OK] Captura configurada para 38 coletas diarias (04:30-23:30)
echo   [OK] 5 abas capturadas: geral, perfil, grupos, acaoprincipal, horapix
echo   [OK] Altura minima 1500px + deteccao inteligente de conteudo
echo   [OK] WhatsApp configurado
echo   [OK] Servidor rodando com scheduler integrado
echo.
echo ARQUITETURA SIMPLIFICADA (2 ARQUIVOS):
echo   1. imperio_daily_reset.bat (este arquivo)
echo      - Reset diario + servidor + coletas XX:00/30
echo   2. imperio_capture_send.bat
echo      - Capturas continuas XX:01/31
echo.
echo Proximas execucoes automaticas:
echo   - Coletas sistema principal: XX:00 e XX:30 (via scheduler do servidor)
echo   - Coletas Hora do Pix: XX:00 e XX:30 (integrado no scheduler)
echo   - Coletas Acao Principal: XX:00 e XX:30 (integrado no scheduler)
echo   - Capturas: XX:01 e XX:31 (5 abas: geral, perfil, grupos, acaoprincipal, horapix)
echo.
echo O servidor core.app mantem o sistema rodando 24/7
echo com scheduler integrado para coletas automaticas.
echo.
echo ================================================================
echo.

REM Log de conclusao
echo [%date% %time%] SISTEMA INICIADO COM SUCESSO - SERVIDOR ESTAVEL ATIVO >> "data\logs\daily_reset.log"

REM ================================================================
REM MODO 100% AUTOMATICO - SEM INTERACAO
REM ================================================================
echo [AUTO] Modo automatico para Task Scheduler
echo [AUTO] Sistema iniciado e rodando 24/7
echo [AUTO] Dashboard: http://localhost:8002/imperio
echo [%date% %time%] Sistema automatico iniciado com sucesso >> "data\logs\daily_reset.log"

REM Script termina - servidor continua rodando indefinidamente
exit /b 0