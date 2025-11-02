#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Modelos para Ação Principal - Monitoramento de sorteios específicos
"""
from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from core.database.base import Base


class MainAction(Base):
    """Ação Principal - Sorteio específico monitorado"""
    __tablename__ = "main_actions"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String(100), unique=True, nullable=False, index=True)
    name = Column(String(500), nullable=False)
    prize_value = Column(Float, default=0.0)  # Valor da premiação extraído do nome
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    is_active = Column(Boolean, default=True, index=True)
    is_current = Column(Boolean, default=False, index=True)  # Ação sendo monitorada atualmente

    # Totais acumulados
    total_revenue = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    total_tickets = Column(Integer, default=0)
    total_fb_cost = Column(Float, default=0.0)
    total_platform_fee = Column(Float, default=0.0)  # Taxa 3%
    total_profit = Column(Float, default=0.0)
    total_roi = Column(Float, default=0.0)

    # Metadados
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    raw_data = Column(JSON, nullable=True)

    # Relacionamento com registros diários
    daily_records = relationship("MainActionDaily", back_populates="action", cascade="all, delete-orphan")


class MainActionDaily(Base):
    """Registro diário de uma Ação Principal"""
    __tablename__ = "main_action_daily"

    id = Column(Integer, primary_key=True, index=True)
    action_id = Column(Integer, ForeignKey("main_actions.id"), nullable=False, index=True)
    date = Column(Date, nullable=False, index=True)

    # Vendas do dia
    daily_revenue = Column(Float, default=0.0)
    daily_orders = Column(Integer, default=0)
    daily_tickets = Column(Integer, default=0)

    # Custos do dia
    daily_fb_cost = Column(Float, default=0.0)
    daily_platform_fee = Column(Float, default=0.0)  # Taxa 3%

    # Resultados do dia
    daily_profit = Column(Float, default=0.0)
    daily_roi = Column(Float, default=0.0)
    daily_margin = Column(Float, default=0.0)

    # Acumulados até esta data
    accumulated_revenue = Column(Float, default=0.0)
    accumulated_orders = Column(Integer, default=0)
    accumulated_tickets = Column(Integer, default=0)
    accumulated_fb_cost = Column(Float, default=0.0)
    accumulated_platform_fee = Column(Float, default=0.0)
    accumulated_profit = Column(Float, default=0.0)
    accumulated_roi = Column(Float, default=0.0)

    # Metadados
    created_at = Column(DateTime, default=datetime.now)
    raw_data = Column(JSON, nullable=True)

    # Relacionamento
    action = relationship("MainAction", back_populates="daily_records")
