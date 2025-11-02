from sqlalchemy import Column, Integer, Float, String, DateTime, Boolean, Text, Date
from sqlalchemy.sql import func
from core.database.base import Base

class Campaign(Base):
    """Campanha ativa - Sorteio 200mil"""
    __tablename__ = "campaigns"

    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(String, nullable=False, default="68ff78f80d0e097d617d472b")
    name = Column(String, nullable=False)
    description = Column(Text)
    roi_goal = Column(Float, default=2.0)
    daily_budget = Column(Float, default=10000.0)
    target_sales = Column(Float, default=30000.0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())

class DailySnapshot(Base):
    """Snapshot de dados do dia - dados cumulativos desde 00:00"""
    __tablename__ = "daily_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    product_id = Column(String, nullable=False)
    
    # Dados de vendas (cumulativo do dia)
    total_sales = Column(Float, default=0.0)
    total_orders = Column(Integer, default=0)
    total_numbers = Column(Integer, default=0)
    
    # Dados de gastos (cumulativo do dia)
    total_spend = Column(Float, default=0.0)
    total_budget = Column(Float, default=0.0)
    
    # ROI geral do dia
    general_roi = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    margin_percent = Column(Float, default=0.0)
    
    # Timestamp da coleta
    collected_at = Column(DateTime, default=func.now())

class ChannelData(Base):
    """Dados por canal (Geral, Instagram, Grupos)"""
    __tablename__ = "channel_data"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    product_id = Column(String, nullable=False)
    channel_name = Column(String, nullable=False)  # 'geral', 'instagram', 'grupos'
    
    # Dados do canal
    sales = Column(Float, default=0.0)
    spend = Column(Float, default=0.0)
    budget = Column(Float, default=0.0)
    roi = Column(Float, default=0.0)
    profit = Column(Float, default=0.0)
    margin_percent = Column(Float, default=0.0)
    
    # Timestamp da coleta
    collected_at = Column(DateTime, default=func.now())

class FacebookAccount(Base):
    """Dados das contas do Facebook Ads"""
    __tablename__ = "facebook_accounts"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    account_id = Column(String, nullable=False)
    spend = Column(Float, default=0.0)
    api_version = Column(String)
    channel = Column(String, default="geral")  # geral, instagram, grupos
    collected_at = Column(DateTime, default=func.now())

class AffiliateSnapshot(Base):
    """Snapshot de dados de afiliados"""
    __tablename__ = "affiliate_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    product_id = Column(String, nullable=False)
    affiliate_code = Column(String, nullable=False)
    affiliate_name = Column(String)
    
    # Dados do afiliado
    total_paid_orders = Column(Float, default=0.0)
    order_count = Column(Integer, default=0)
    average_ticket = Column(Float, default=0.0)
    
    # Classificação por canal
    channel = Column(String)  # 'geral', 'instagram', 'grupos'
    
    collected_at = Column(DateTime, default=func.now())

class CollectionLog(Base):
    """Log de coletas realizadas"""
    __tablename__ = "collection_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False)
    collection_time = Column(DateTime, default=func.now())
    
    # Status da coleta
    status = Column(String, default="success")  # success, error, partial
    
    # Dados coletados
    sales_collected = Column(Boolean, default=False)
    affiliates_collected = Column(Boolean, default=False)
    facebook_collected = Column(Boolean, default=False)
    
    # Resumo dos dados
    total_sales = Column(Float, default=0.0)
    total_spend = Column(Float, default=0.0)
    general_roi = Column(Float, default=0.0)
    
    # Mensagens/erros
    message = Column(Text)
    error_details = Column(Text)

class FacebookAccountMapping(Base):
    """Mapeamento de contas Facebook por canal"""
    __tablename__ = "facebook_account_mapping"
    
    id = Column(Integer, primary_key=True, index=True)
    account_id = Column(String, nullable=False)
    channel = Column(String, nullable=False)  # geral, instagram, grupos
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CaptureConfig(Base):
    """Configurações do sistema de captura"""
    __tablename__ = "capture_config"
    
    id = Column(Integer, primary_key=True, index=True)
    output_folder = Column(String, nullable=False)
    capture_enabled = Column(Boolean, default=True)
    whatsapp_enabled = Column(Boolean, default=True)
    whatsapp_group = Column(String, default="OracleSys - Império Prêmios [ROI DIÁRIO]")
    schedule_times = Column(Text, default="01,31")  # minutos: 01 e 31
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

class CaptureLog(Base):
    """Log de capturas realizadas"""
    __tablename__ = "capture_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    capture_time = Column(DateTime, default=func.now())
    capture_type = Column(String, nullable=False)  # 'geral', 'perfil', 'grupos'
    status = Column(String, default="success")  # success, error, partial
    file_path = Column(String)
    whatsapp_sent = Column(Boolean, default=False)
    error_message = Column(Text)
    execution_time_seconds = Column(Float, default=0.0)
    screenshot_size_kb = Column(Integer, default=0)