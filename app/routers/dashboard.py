from fastapi import APIRouter, Request, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from ..database import get_db

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/", response_class=HTMLResponse)
async def dashboard_home(request: Request, db: Session = Depends(get_db)):
    """Página principal do dashboard"""
    return templates.TemplateResponse("dashboard/index.html", {"request": request})

@router.get("/roi", response_class=HTMLResponse)
async def roi_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard de ROI detalhado"""
    return templates.TemplateResponse("dashboard/roi.html", {"request": request})

@router.get("/sales", response_class=HTMLResponse)
async def sales_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard de vendas"""
    return templates.TemplateResponse("dashboard/sales.html", {"request": request})

@router.get("/affiliates", response_class=HTMLResponse)
async def affiliates_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard de afiliados"""
    return templates.TemplateResponse("dashboard/affiliates.html", {"request": request})

@router.get("/facebook", response_class=HTMLResponse)
async def facebook_dashboard(request: Request, db: Session = Depends(get_db)):
    """Dashboard do Facebook Ads"""
    return templates.TemplateResponse("dashboard/facebook.html", {"request": request})