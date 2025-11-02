@echo off
REM ================================================================
REM TESTE COLETA COMPLETA - Sistema Principal + Hora do Pix
REM ================================================================
REM Script para testar a nova coleta unificada
REM ================================================================

title Teste Coleta Completa

cd /d "%~dp0"

cls
echo ================================================================
echo       TESTE COLETA COMPLETA - SISTEMA IMPERIO
echo ================================================================
echo.
echo Este script vai testar a nova funcao de coleta unificada que
echo executa em SEQUENCIA:
echo   1. Sistema Principal (Imperio + Facebook)
echo   2. Hora do Pix (sorteios + taxa 3%%)
echo.
echo Isso evita conflitos no banco de dados.
echo.
echo ================================================================
pause

cls
echo.
echo [1/2] EXECUTANDO COLETA COMPLETA...
echo ========================================
.\venv\Scripts\python.exe -c "import asyncio; from core.utils.scheduler import scheduled_full_collection; asyncio.run(scheduled_full_collection())"
echo.

timeout /t 2 /nobreak >nul

echo [2/2] VERIFICANDO DADOS NO BANCO...
echo ========================================
.\venv\Scripts\python.exe -c "from core.database.base import SessionLocal; from core.models.base import CollectionLog; from clients.imperio.models.horapix import HoraPix; db = SessionLocal(); last_coleta = db.query(CollectionLog).order_by(CollectionLog.collection_time.desc()).first(); horapix_count = db.query(HoraPix).count(); db.close(); print(f'  Sistema Principal:'); print(f'    Ultima coleta: {last_coleta.collection_time if last_coleta else \"Nenhuma\"}'); print(f'    ROI: {last_coleta.general_roi if last_coleta else 0:.2f}'); print(f'    Vendas: R$ {last_coleta.total_sales if last_coleta else 0:,.2f}'); print(f''); print(f'  Hora do Pix:'); print(f'    Total sorteios: {horapix_count}'); print('')"
echo.

echo ================================================================
echo                   TESTE CONCLUIDO!
echo ================================================================
echo.
echo Proximo passo:
echo   1. Reinicie o servidor: imperio_daily_reset.bat
echo   2. Aguarde a proxima coleta em XX:00 ou XX:30
echo   3. Verifique se ambos os sistemas estao atualizando
echo.
echo ================================================================
pause
