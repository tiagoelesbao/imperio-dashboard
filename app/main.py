from fastapi import FastAPI, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from sqlalchemy.orm import Session
import uvicorn
import os
import asyncio
from datetime import datetime
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from .api import router as api_router
from .database import engine, get_db
from .models import Base

# Criar aplicação
app = FastAPI(
    title="Sistema ROI Império - Sorteio 200mil",
    description="Sistema de monitoramento ROI para ação 684c73283d75820c0a77a42f",
    version="1.0.0"
)

# Criar tabelas
Base.metadata.create_all(bind=engine)

# Configurar templates
templates = Jinja2Templates(directory="app/templates")

# Configurar arquivos estáticos
static_dir = "app/static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir, exist_ok=True)
    os.makedirs(os.path.join(static_dir, "css"), exist_ok=True)
    os.makedirs(os.path.join(static_dir, "js"), exist_ok=True)

app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Incluir routers da API
app.include_router(api_router, prefix="/api", tags=["api"])

# Rota de health check
@app.get("/health")
async def health_check():
    """Health check para monitoramento do Railway"""
    return {
        "status": "healthy",
        "service": "Sistema ROI Império",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

# Rota catch-all para webhooks não mapeados (evitar 404s)
@app.post("/api/webhook/{webhook_path:path}")
async def catch_all_webhook(webhook_path: str):
    """Capturar todos os webhooks não mapeados para evitar 404s"""
    return {"status": "ok", "message": f"Webhook {webhook_path} recebido", "timestamp": datetime.now().isoformat()}

@app.on_event("startup")
async def startup_event():
    """Executar na inicialização"""
    print("=" * 70)
    print("SISTEMA ROI IMPERIO - INICIANDO")
    print("=" * 70)
    print(f"Produto ID: 684c73283d75820c0a77a42f")
    print(f"Campanha: Sorteio 200mil")
    print(f"Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
    print("=" * 70)
    
    # Executar primeira coleta
    await execute_initial_collection()
    
    # Inicializar scheduler para coletas automáticas
    from .scheduler import scheduler, init_scheduler
    init_scheduler()
    scheduler.start()

async def execute_initial_collection():
    """Executar coleta inicial"""
    try:
        from .database import get_db
        from .core.data_collector import imperio_collector
        from .core.data_manager import imperio_data_manager
        
        print("Executando coleta inicial...")
        
        # Executar coleta
        result = imperio_collector.execute_full_collection()
        
        if "error" not in result:
            # Salvar no banco
            db = next(get_db())
            saved = imperio_data_manager.save_collection_data(db, result)
            db.close()
            
            if saved:
                print("Coleta inicial realizada e dados salvos!")
                print(f"ROI: {result['totals']['roi']:.2f}")
                print(f"Vendas: R$ {result['totals']['sales']:,.2f}")
                print(f"Gastos: R$ {result['totals']['spend']:,.2f}")
            else:
                print("Coleta realizada mas erro ao salvar")
        else:
            print(f"Erro na coleta inicial: {result['error']}")
            
    except Exception as e:
        print(f"Erro na coleta inicial: {e}")

@app.get("/")
async def root():
    """Página inicial - redirecionar para dashboard"""
    return RedirectResponse(url="/dashboard", status_code=302)

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    """Página principal do dashboard"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Dashboard ROI - Sorteio 200mil",
        "product_id": "684c73283d75820c0a77a42f"
    })

@app.get("/config", response_class=HTMLResponse)
async def config_page(request: Request, db: Session = Depends(get_db)):
    """Página de configurações"""
    from .models import Campaign, FacebookAccountMapping
    
    # Buscar campanha ativa
    campaign = db.query(Campaign).filter(Campaign.is_active == True).first()
    
    # Buscar mapeamentos de canal
    mappings = db.query(FacebookAccountMapping).filter(
        FacebookAccountMapping.is_active == True
    ).all()
    
    # Organizar mapeamentos por canal
    channel_mapping = {}
    for mapping in mappings:
        if mapping.channel not in channel_mapping:
            channel_mapping[mapping.channel] = []
        channel_mapping[mapping.channel].append(mapping.account_id)
    
    return templates.TemplateResponse("config.html", {
        "request": request,
        "title": "Configurações - ROI Império",
        "product_id": campaign.product_id if campaign else "684c73283d75820c0a77a42f",
        "campaign_name": campaign.name if campaign else "Sorteio 200mil",
        "roi_goal": campaign.roi_goal if campaign else 2.0,
        "daily_budget": campaign.daily_budget if campaign else 10000.0,
        "facebook_accounts": [
            "act_2067257390316380",
            "act_1391112848236399",
            "act_406219475582745",
            "act_790223756353632",
            "act_772777644802886",
            "act_303402486183447"
        ],
        "channel_mapping": channel_mapping,
        "affiliate_instagram": "L8UTEDVTI0",
        "affiliate_grupo1": "17QB25AKRL",
        "affiliate_grupo2": "30CS8W9DP1"
    })

@app.get("/campaigns", response_class=HTMLResponse)
async def campaigns_page(request: Request):
    """Página de campanhas ativas com ranking por lucro"""
    return templates.TemplateResponse("campaigns.html", {
        "request": request,
        "title": "Campanhas - ROI Império"
    })

@app.get("/affiliates", response_class=HTMLResponse)
async def affiliates_page(request: Request):
    """Página de afiliados por canal"""
    return templates.TemplateResponse("affiliates.html", {
        "request": request,
        "title": "Afiliados - ROI Império"
    })

@app.get("/facebook", response_class=HTMLResponse)
async def facebook_page(request: Request):
    """Página de Facebook Ads por canal"""
    return templates.TemplateResponse("facebook.html", {
        "request": request,
        "title": "Facebook Ads - ROI Império"
    })

@app.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    """Página de histórico com dados cumulativos"""
    return templates.TemplateResponse("history.html", {
        "request": request,
        "title": "Histórico - ROI Império"
    })

@app.get("/hourly-monitor", response_class=HTMLResponse)
async def hourly_monitor_page(request: Request):
    """Página de monitoramento horário cumulativo"""
    return templates.TemplateResponse("hourly_monitor.html", {
        "request": request,
        "title": "Monitoramento Horário - ROI Império"
    })

@app.get("/analytics", response_class=HTMLResponse)
async def analytics_page(request: Request):
    """Página de análises (placeholder)"""
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "title": "Análises - ROI Império",
        "product_id": "684c73283d75820c0a77a42f"
    })

@app.get("/health")
async def health_check():
    """Verificação de saúde do sistema"""
    return {
        "status": "healthy",
        "system": "Sistema ROI Império",
        "product_id": "684c73283d75820c0a77a42f",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)