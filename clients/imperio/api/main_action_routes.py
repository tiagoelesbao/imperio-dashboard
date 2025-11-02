#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rotas da API para Ação Principal
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel

from core.database.base import get_db
from core.services.main_action_service import main_action_service

router = APIRouter(prefix="/api/main-action", tags=["main-action"])


class CollectRequest(BaseModel):
    product_id: str


class SetCurrentRequest(BaseModel):
    product_id: str


@router.post("/collect")
async def collect_action_data(request: CollectRequest, db: Session = Depends(get_db)):
    """Coletar dados de uma ação"""
    result = main_action_service.collect_and_save(db, request.product_id)
    if result.get('success'):
        return {"status": "success", "data": result}
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))


@router.get("/all")
async def get_all_actions(year: int = None, db: Session = Depends(get_db)):
    """Buscar todas as ações com resumo anual"""
    actions = main_action_service.get_all_actions(db, year)

    # Calcular resumo anual
    yearly_summary = {
        'total_revenue': sum(a['total_revenue'] for a in actions),
        'total_fb_cost': sum(a['total_fb_cost'] for a in actions),
        'total_platform_fee': sum(a['total_platform_fee'] for a in actions),
        'total_profit': sum(a['total_profit'] for a in actions),
        'avg_roi': sum(a['total_roi'] for a in actions) / len(actions) if actions else 0
    }

    return {
        "status": "success",
        "data": {
            "actions": actions,
            "yearly_summary": yearly_summary
        }
    }


@router.get("/current")
async def get_current_action(db: Session = Depends(get_db)):
    """Buscar ação atual"""
    action = main_action_service.get_current_action(db)
    if action:
        return {"status": "success", "data": action}
    else:
        return {"status": "no_data", "message": "Nenhuma ação atual configurada"}


@router.get("/{action_id}/details")
async def get_action_details(action_id: int, db: Session = Depends(get_db)):
    """Buscar detalhes completos de uma ação"""
    details = main_action_service.get_action_details(db, action_id)
    if details:
        return {"status": "success", "data": details}
    else:
        raise HTTPException(status_code=404, detail="Ação não encontrada")


@router.post("/set-current")
async def set_current_action(request: SetCurrentRequest, db: Session = Depends(get_db)):
    """Definir ação atual"""
    result = main_action_service.set_current_action(db, request.product_id)
    if result.get('success'):
        return {"status": "success"}
    else:
        raise HTTPException(status_code=500, detail=result.get('error'))
