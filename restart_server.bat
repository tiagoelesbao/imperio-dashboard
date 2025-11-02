@echo off
echo ============================================================
echo REINICIANDO SERVIDOR IMPERIO COM CORREÇÕES
echo ============================================================

echo.
echo [1] Finalizando processos Python antigos...
taskkill /F /IM python.exe 2>nul
taskkill /F /IM pythonw.exe 2>nul
timeout /t 2 >nul

echo.
echo [2] Iniciando servidor com código atualizado...
cd /d "C:\Users\Pichau\Desktop\Sistemas\OracleSys\Clientes\Imperio\REGISTRO_VENDAS_SCHENDULE"
call venv\Scripts\activate

echo.
echo [3] Iniciando FastAPI com as correções aplicadas...
start cmd /k "venv\Scripts\python.exe -m uvicorn core.app:app --host 0.0.0.0 --port 8002"

timeout /t 5 >nul

echo.
echo [4] Testando se o servidor está respondendo...
curl -s http://localhost:8002/health >nul 2>&1
if %ERRORLEVEL% == 0 (
    echo [OK] Servidor iniciado com sucesso!
) else (
    echo [!] Aguardando servidor iniciar...
    timeout /t 5 >nul
)

echo.
echo ============================================================
echo SERVIDOR REINICIADO COM CORREÇÕES
echo ============================================================
echo.
echo Dashboard: http://localhost:8002/imperio
echo.
echo As correções aplicadas:
echo - Product ID atualizado de 6904ea540d0e097d618827fc
echo - Para o ID correto: 68ff78f80d0e097d617d472b
echo.
echo Os dados agora devem aparecer nas abas:
echo - Geral
echo - Perfil (Instagram)
echo - Grupos
echo.
echo ============================================================
pause