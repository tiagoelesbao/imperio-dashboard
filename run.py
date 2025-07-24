#!/usr/bin/env python3
"""
Script principal para executar o Dashboard ROI
"""

import asyncio
import threading
import uvicorn
import logging
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

from app.main import app
from app.scheduler import start_scheduler

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[
        logging.FileHandler("dashboard_roi.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

def run_scheduler_in_thread():
    """Executa o agendador em thread separada"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(start_scheduler())

def main():
    """Função principal"""
    logger.info("Iniciando Dashboard ROI...")
    
    # Verificar variáveis de ambiente essenciais
    required_vars = [
        "API_USERNAME", "API_PASSWORD", "FACEBOOK_ACCESS_TOKEN",
        "AFFILIADO_CODE_INSTAGRAM", "AFFILIADO_CODE_GRUPO_1", "AFFILIADO_CODE_GRUPO_2"
    ]
    
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"Variáveis de ambiente não encontradas: {', '.join(missing_vars)}")
        logger.error("Por favor, configure o arquivo .env baseado no .env.example")
        return
    
    # Iniciar agendador em thread separada
    scheduler_thread = threading.Thread(target=run_scheduler_in_thread, daemon=True)
    scheduler_thread.start()
    logger.info("Agendador iniciado em thread separada")
    
    # Configurações do servidor
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", "8000"))
    debug = os.getenv("DEBUG", "False").lower() == "true"
    
    logger.info(f"Iniciando servidor web em {host}:{port}")
    
    # Iniciar servidor web
    uvicorn.run(
        "app.main:app",
        host=host,
        port=port,
        reload=debug,
        log_level="info"
    )

if __name__ == "__main__":
    main()