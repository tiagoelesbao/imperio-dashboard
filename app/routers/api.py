from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import List, Optional
import pytz
from ..database import get_db
from ..models import ROIData, SalesData, AffiliateData, FacebookAdsData

router = APIRouter()

@router.get("/roi/geral")
async def get_roi_geral(db: Session = Depends(get_db), hours: int = 24):
    """Obter dados de ROI geral das últimas N horas"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    roi_data = db.query(ROIData).filter(
        ROIData.page_type == "geral",
        ROIData.timestamp >= cutoff_time
    ).order_by(desc(ROIData.timestamp)).all()
    
    return {
        "data": [
            {
                "timestamp": item.timestamp.isoformat(),
                "spend": item.spend,
                "sales": item.sales,
                "roi": item.roi,
                "period": item.period
            }
            for item in roi_data
        ]
    }

@router.get("/roi/instagram")
async def get_roi_instagram(db: Session = Depends(get_db), hours: int = 24):
    """Obter dados de ROI do Instagram das últimas N horas"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    roi_data = db.query(ROIData).filter(
        ROIData.page_type == "instagram",
        ROIData.timestamp >= cutoff_time
    ).order_by(desc(ROIData.timestamp)).all()
    
    return {
        "data": [
            {
                "timestamp": item.timestamp.isoformat(),
                "spend": item.spend,
                "sales": item.sales,
                "roi": item.roi,
                "period": item.period
            }
            for item in roi_data
        ]
    }

@router.get("/roi/grupo")
async def get_roi_grupo(db: Session = Depends(get_db), hours: int = 24):
    """Obter dados de ROI dos grupos das últimas N horas"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    roi_data = db.query(ROIData).filter(
        ROIData.page_type == "grupo",
        ROIData.timestamp >= cutoff_time
    ).order_by(desc(ROIData.timestamp)).all()
    
    return {
        "data": [
            {
                "timestamp": item.timestamp.isoformat(),
                "spend": item.spend,
                "sales": item.sales,
                "roi": item.roi,
                "period": item.period
            }
            for item in roi_data
        ]
    }

@router.get("/sales/latest")
async def get_latest_sales(db: Session = Depends(get_db), limit: int = 50):
    """Obter dados de vendas mais recentes"""
    sales_data = db.query(SalesData).order_by(
        desc(SalesData.timestamp)
    ).limit(limit).all()
    
    return {
        "data": [
            {
                "timestamp": item.timestamp.isoformat(),
                "date": item.date,
                "total_orders": item.total_orders,
                "total_numbers": item.total_numbers,
                "total_value": item.total_value
            }
            for item in sales_data
        ]
    }

@router.get("/affiliates/performance")
async def get_affiliates_performance(db: Session = Depends(get_db), days: int = 7):
    """Obter performance dos afiliados dos últimos N dias"""
    cutoff_time = datetime.now() - timedelta(days=days)
    
    affiliate_data = db.query(AffiliateData).filter(
        AffiliateData.timestamp >= cutoff_time
    ).order_by(desc(AffiliateData.timestamp)).all()
    
    return {
        "data": [
            {
                "timestamp": item.timestamp.isoformat(),
                "affiliate_code": item.affiliate_code,
                "affiliate_name": item.affiliate_name,
                "total_paid_orders": item.total_paid_orders,
                "order_count": item.order_count,
                "average_ticket": item.average_ticket
            }
            for item in affiliate_data
        ]
    }

@router.get("/facebook/spend")
async def get_facebook_spend(db: Session = Depends(get_db), hours: int = 24):
    """Obter gastos do Facebook Ads das últimas N horas"""
    cutoff_time = datetime.now() - timedelta(hours=hours)
    
    fb_data = db.query(FacebookAdsData).filter(
        FacebookAdsData.timestamp >= cutoff_time
    ).order_by(desc(FacebookAdsData.timestamp)).all()
    
    # Agrupar por timestamp para somar gastos de todas as contas
    spend_by_time = {}
    for item in fb_data:
        time_key = item.timestamp.strftime("%Y-%m-%d %H:%M")
        if time_key not in spend_by_time:
            spend_by_time[time_key] = {
                "timestamp": item.timestamp.isoformat(),
                "total_spend": 0,
                "accounts": []
            }
        spend_by_time[time_key]["total_spend"] += item.spend
        spend_by_time[time_key]["accounts"].append({
            "account_id": item.account_id,
            "spend": item.spend
        })
    
    return {
        "data": list(spend_by_time.values())
    }

@router.get("/dashboard/summary")
async def get_dashboard_summary(db: Session = Depends(get_db)):
    """Obter resumo do dashboard com métricas principais"""
    
    # ROI atual (última hora)
    latest_roi = db.query(ROIData).filter(
        ROIData.page_type == "geral"
    ).order_by(desc(ROIData.timestamp)).first()
    
    # Total de vendas hoje
    today = datetime.now().strftime("%d/%m/%Y")
    today_sales = db.query(SalesData).filter(
        SalesData.date == today
    ).order_by(desc(SalesData.timestamp)).first()
    
    # Gasto total do Facebook hoje
    today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    today_fb_spend = db.query(func.sum(FacebookAdsData.spend)).filter(
        FacebookAdsData.timestamp >= today_start
    ).scalar() or 0
    
    return {
        "current_roi": latest_roi.roi if latest_roi else 0,
        "today_sales": today_sales.total_value if today_sales else 0,
        "today_spend": today_fb_spend,
        "last_update": datetime.now().isoformat()
    }