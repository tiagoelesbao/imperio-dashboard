"""
FastAPI App Factory - Core System
"""
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from datetime import datetime
import os

def create_app(client_name: str = "imperio") -> FastAPI:
    """
    Aplicação FastAPI dedicada ao sistema Império Prêmios
    Sistema de monitoramento de ROI, vendas e campanhas

    Args:
        client_name: Nome do cliente (sempre "imperio")

    Returns:
        FastAPI: Aplicação configurada
    """
    app = FastAPI(
        title="Império Prêmios - Sistema de ROI",
        description="Sistema de monitoramento de ROI, vendas e campanhas para Império Prêmios",
        version="1.0.0"
    )
    
    # Configurar arquivos estáticos
    app.mount("/static", StaticFiles(directory="static"), name="static")
    
    # Health check básico
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "client": client_name,
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }
    
    # Carregar rotas específicas do Império Prêmios
    if client_name == "imperio":
        from clients.imperio.api.routes import router as imperio_router
        from clients.imperio.api.pages import pages_router as imperio_pages
        from clients.imperio.api.main_action_routes import router as main_action_router

        app.include_router(imperio_router, prefix="/api", tags=["imperio-api"])
        app.include_router(imperio_pages, tags=["imperio-pages"])
        app.include_router(main_action_router, tags=["main-action"])
        
        # Eventos de startup/shutdown para o cliente Imperio
        @app.on_event("startup")
        async def startup_event():
            """Inicializar scheduler e outros serviços"""
            try:
                from core.utils.scheduler import init_scheduler, scheduler, trigger_first_collection_and_capture
                from core.database.base import SessionLocal
                from core.models.base import CollectionLog
                
                print("Iniciando scheduler de coletas automaticas...")
                init_scheduler()
                
                if not scheduler.running:
                    scheduler.start()
                    print("Scheduler iniciado com sucesso - Coletas coordenadas XX:00/30 + capturas XX:01/31")
                else:
                    print("Scheduler ja estava ativo")
                
                # Executar primeira captura se pendente + mostrar status
                try:
                    from core.models.base import CaptureLog
                    db = SessionLocal()
                    collection_count = db.query(CollectionLog).count()
                    capture_count = db.query(CaptureLog).count()
                    db.close()
                    
                    print(f"\n🌅 [SISTEMA ATIVO] {collection_count} coletas, {capture_count} capturas realizadas")
                    
                    # PRIMEIRA CAPTURA DESABILITADA - causa crash do servidor
                    if os.path.exists("data/.first_capture_pending"):
                        print("📸 Removendo flag de primeira captura (desabilitada)")
                        os.remove("data/.first_capture_pending")
                        
                    # Sempre executar trigger_first_collection_and_capture para mostrar status
                    trigger_first_collection_and_capture()
                        
                    # CAPTURA INICIAL DESABILITADA - usava:
                    # import asyncio
                    # async def delayed_first_capture():
                    #     await asyncio.sleep(3)
                    #     from imperio import ImperioSystem
                    #     sistema = ImperioSystem()
                    #     sistema.execute_immediate_capture()
                    # 
                    # asyncio.create_task(delayed_first_capture())
                    
                    # Mostrar próximos horários
                    from core.utils.scheduler import trigger_first_collection_and_capture
                    trigger_first_collection_and_capture()
                        
                except Exception as e:
                    print(f"AVISO: Erro ao verificar status: {e}")
                    
            except Exception as e:
                print(f"AVISO: Erro ao iniciar scheduler: {e}")
        
        @app.on_event("shutdown") 
        async def shutdown_event():
            """Parar scheduler ao encerrar"""
            try:
                from core.utils.scheduler import scheduler
                
                if scheduler.running:
                    scheduler.shutdown()
                    print("Scheduler parado com sucesso")
                    
            except Exception as e:
                print(f"AVISO: Erro ao parar scheduler: {e}")
    
    return app

# Create app instance for uvicorn
app = create_app("imperio")