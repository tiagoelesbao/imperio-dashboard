"""
Modelos de banco de dados para Hora do Pix
"""
from sqlalchemy import Column, String, Float, Integer, DateTime, Text, JSON
from sqlalchemy.sql import func
from core.database.base import Base


class HoraPixCollection(Base):
    """Registro de cada coleta de dados Hora do Pix"""
    __tablename__ = "horapix_collections"

    id = Column(Integer, primary_key=True, index=True)
    collection_time = Column(DateTime(timezone=True), server_default=func.now())

    # Totais gerais
    total_draws = Column(Integer, default=0)
    active_draws = Column(Integer, default=0)
    finished_draws = Column(Integer, default=0)
    total_prize_value = Column(Float, default=0.0)
    total_revenue = Column(Float, default=0.0)
    total_platform_fee = Column(Float, default=0.0)  # Taxa de 3% da plataforma
    total_profit = Column(Float, default=0.0)
    total_roi = Column(Float, default=0.0)

    # Dados completos em JSON
    raw_data = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<HoraPixCollection(id={self.id}, time={self.collection_time}, draws={self.total_draws})>"


class HoraPixDraw(Base):
    """Registro individual de cada sorteio"""
    __tablename__ = "horapix_draws"

    id = Column(Integer, primary_key=True, index=True)
    draw_id = Column(String(100), unique=True, index=True)  # ID do sorteio na API
    collection_time = Column(DateTime(timezone=True), server_default=func.now())

    # Dados do sorteio
    title = Column(String(500))
    status = Column(String(50))  # active, done, etc
    prize_value = Column(Float, default=0.0)
    price = Column(Float, default=0.0)

    # Quantidades
    qty_paid = Column(Integer, default=0)
    qty_free = Column(Integer, default=0)
    qty_total = Column(Integer, default=0)

    # Métricas
    revenue = Column(Float, default=0.0)
    platform_fee = Column(Float, default=0.0)  # Taxa de 3% da plataforma
    profit = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    participants = Column(Integer, default=0)
    ticket_medio = Column(Float, default=0.0)

    # Datas
    created_at = Column(String(100))
    draw_date = Column(String(100))

    # Detalhes adicionais em JSON
    top_buyers = Column(JSON, nullable=True)
    top_regions = Column(JSON, nullable=True)

    def __repr__(self):
        return f"<HoraPixDraw(id={self.draw_id}, title={self.title[:30]}, status={self.status})>"
