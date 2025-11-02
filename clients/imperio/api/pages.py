"""
Rotas HTML para páginas do cliente Império
"""
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse

# Router para páginas HTML
pages_router = APIRouter()

# Templates específicos do Império
templates = Jinja2Templates(directory="clients/imperio/templates")

@pages_router.get("/", response_class=HTMLResponse)
async def root_redirect():
    """Redirect root to imperio (migração completa)"""
    return RedirectResponse(url="/imperio", status_code=302)

@pages_router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_redirect():
    """Redirect /dashboard to /imperio (migração completa conforme solicitado)"""
    return RedirectResponse(url="/imperio", status_code=301)

@pages_router.get("/imperio", response_class=HTMLResponse)
async def imperio_page(request: Request):
    """Painel personalizado do Império Prêmios"""
    return templates.TemplateResponse("imperio.html", {
        "request": request,
        "title": "Painel Imperio - Dashboard Personalizado",
        "company": "Imperio Premios"
    })

@pages_router.get("/config", response_class=HTMLResponse)
async def config_page(request: Request):
    """Página de configurações"""
    return templates.TemplateResponse("config.html", {
        "request": request,
        "title": "Configurações - ROI Império"
    })