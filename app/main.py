from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import uvicorn
import os
from .routers import dashboard, api
from .database import engine
from .models import Base

app = FastAPI(title="Dashboard ROI - Sistema de Monitoramento", version="1.0.0")

# Criar tabelas do banco de dados
Base.metadata.create_all(bind=engine)

# Configurar templates e arquivos estáticos
templates = Jinja2Templates(directory="app/templates")

# Verificar se diretório static existe, se não, criar
static_dir = "app/static"
if not os.path.exists(static_dir):
    os.makedirs(static_dir)
    os.makedirs(os.path.join(static_dir, "css"))
    os.makedirs(os.path.join(static_dir, "js"))

app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Incluir routers
app.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
app.include_router(api.router, prefix="/api", tags=["api"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "Dashboard ROI está funcionando"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)