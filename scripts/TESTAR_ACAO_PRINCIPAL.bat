@echo off
REM ================================================================
REM TESTE RAPIDO - ACAO PRINCIPAL
REM ================================================================
REM Script para testar a implementacao da Acao Principal
REM ================================================================

title Teste Acao Principal

cd /d "%~dp0"

cls
echo ================================================================
echo       TESTE ACAO PRINCIPAL - SISTEMA IMPERIO
echo ================================================================
echo.
echo Este script vai:
echo   1. Criar tabelas no banco
echo   2. Coletar dados da acao vigente
echo   3. Exibir resumo
echo   4. Verificar se esta tudo OK
echo.
echo ================================================================
pause

cls
echo.
echo [1/4] CRIANDO TABELAS...
echo ========================================
.\venv\Scripts\python.exe scripts\maintenance\create_main_action_tables.py
echo.

timeout /t 2 /nobreak >nul

echo [2/4] COLETANDO DADOS...
echo ========================================
.\venv\Scripts\python.exe scripts\collect_main_action.py
echo.

timeout /t 2 /nobreak >nul

echo [3/4] VERIFICANDO DADOS NO BANCO...
echo ========================================
.\venv\Scripts\python.exe -c "from core.database.base import SessionLocal; from core.models.main_action import MainAction, MainActionDaily; db = SessionLocal(); actions = db.query(MainAction).all(); daily_count = db.query(MainActionDaily).count(); db.close(); print(f'  Acoes cadastradas: {len(actions)}'); print(f'  Registros diarios: {daily_count}'); print(''); [print(f'  - {a.name} (ROI: {a.total_roi:.2f}%%)') for a in actions]"
echo.

timeout /t 2 /nobreak >nul

echo [4/4] TESTE DE API (requer servidor rodando)...
echo ========================================
echo Pulando teste de API (requer servidor ativo)
echo Para testar API, inicie o servidor e acesse:
echo   http://localhost:8002/api/main-action/current
echo.

echo ================================================================
echo                   TESTE CONCLUIDO!
echo ================================================================
echo.
echo Proximo passo:
echo   1. Reinicie o servidor: imperio_daily_reset.bat
echo   2. Acesse: http://localhost:8002/imperio
echo   3. Clique em "Acao Principal" no menu
echo.
echo ================================================================
pause
