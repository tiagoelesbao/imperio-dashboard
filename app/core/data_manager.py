#!/usr/bin/env python3
"""
Data Manager - Gerencia persistência de dados cumulativos
Garante que os dados do dia sejam cumulativos desde 00:00
"""

import logging
from datetime import datetime, date, timedelta
from typing import Dict, Optional, List
from sqlalchemy.orm import Session
from ..models import (
    DailySnapshot, ChannelData, FacebookAccount, 
    AffiliateSnapshot, CollectionLog, Campaign
)

logger = logging.getLogger(__name__)

class ImperioDataManager:
    """Gerenciador de dados para o sistema Império ROI"""
    
    def __init__(self, product_id: str = "684c73283d75820c0a77a42f"):
        self.product_id = product_id

    def save_collection_data(self, db: Session, collection_result: Dict) -> bool:
        """Salvar dados da coleta no banco"""
        try:
            today = date.today()
            collection_time = datetime.now()
            
            # Verificar se coleta foi bem-sucedida
            if "error" in collection_result:
                self._log_collection(db, today, "error", collection_result.get("error"))
                return False
            
            # Extrair dados
            totals = collection_result.get("totals", {})
            channels = collection_result.get("channels", {})
            
            # 1. Salvar snapshot diário (dados cumulativos)
            self._save_daily_snapshot(db, today, totals)
            
            # 2. Salvar dados por canal
            self._save_channel_data(db, today, channels)
            
            # 3. Log da coleta
            self._log_collection(db, today, "success", f"ROI: {totals.get('roi', 0):.2f}")
            
            db.commit()
            logger.info("Dados salvos no banco com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados: {e}")
            db.rollback()
            return False

    def _save_daily_snapshot(self, db: Session, today: date, totals: Dict):
        """Criar novo snapshot a cada coleta (histórico completo)"""
        # SEMPRE criar novo snapshot - não sobrescrever
        # Isso permite histórico completo de todas as coletas
        snapshot = DailySnapshot(
            date=today,
            product_id=self.product_id,
            total_sales=totals.get("sales", 0.0),
            total_orders=totals.get("orders", 0),
            total_numbers=totals.get("numbers", 0),
            total_spend=totals.get("spend", 0.0),
            total_budget=totals.get("budget", 0.0),
            general_roi=totals.get("roi", 0.0),
            profit=totals.get("profit", 0.0),
            margin_percent=totals.get("margin", 0.0),
            collected_at=datetime.now()
        )
        db.add(snapshot)
        logger.info(f"📝 Novo snapshot criado: Vendas=R$ {totals.get('sales', 0.0):,.2f}, ROI={totals.get('roi', 0.0):.2f}")

    def _save_channel_data(self, db: Session, today: date, channels: Dict):
        """Salvar/atualizar dados por canal"""
        logger.info(f"Salvando dados de {len(channels)} canais: {list(channels.keys())}")
        for channel_name, channel_data in channels.items():
            logger.info(f"Canal {channel_name}: vendas={channel_data.get('sales', 0):.2f}, gastos={channel_data.get('spend', 0):.2f}, roi={channel_data.get('roi', 0):.2f}")
            # Buscar dados existentes para hoje
            existing = db.query(ChannelData).filter(
                ChannelData.date == today,
                ChannelData.product_id == self.product_id,
                ChannelData.channel_name == channel_name
            ).first()
            
            if existing:
                # Atualizar
                existing.sales = channel_data.get("sales", 0.0)
                existing.spend = channel_data.get("spend", 0.0)
                existing.budget = channel_data.get("budget", 0.0)
                existing.roi = channel_data.get("roi", 0.0)
                existing.profit = channel_data.get("profit", 0.0)
                existing.margin_percent = channel_data.get("margin", 0.0)
                existing.collected_at = datetime.now()
            else:
                # Criar novo
                channel_record = ChannelData(
                    date=today,
                    product_id=self.product_id,
                    channel_name=channel_name,
                    sales=channel_data.get("sales", 0.0),
                    spend=channel_data.get("spend", 0.0),
                    budget=channel_data.get("budget", 0.0),
                    roi=channel_data.get("roi", 0.0),
                    profit=channel_data.get("profit", 0.0),
                    margin_percent=channel_data.get("margin", 0.0),
                    collected_at=datetime.now()
                )
                db.add(channel_record)

    def _log_collection(self, db: Session, today: date, status: str, message: str):
        """Registrar log da coleta"""
        log = CollectionLog(
            date=today,
            collection_time=datetime.now(),
            status=status,
            message=message,
            sales_collected=True,
            affiliates_collected=True,
            facebook_collected=True
        )
        db.add(log)

    def get_today_data(self, db: Session) -> Optional[Dict]:
        """Obter dados de hoje"""
        try:
            today = date.today()
            
            # Buscar snapshot mais recente do dia
            snapshot = db.query(DailySnapshot).filter(
                DailySnapshot.date == today,
                DailySnapshot.product_id == self.product_id
            ).order_by(DailySnapshot.collected_at.desc()).first()
            
            # Buscar dados por canal mais recentes
            channels = db.query(ChannelData).filter(
                ChannelData.date == today,
                ChannelData.product_id == self.product_id
            ).order_by(ChannelData.collected_at.desc()).all()
            
            logger.info(f"Encontrados {len(channels)} registros de canal para hoje")
            
            if not snapshot:
                return None
            
            # Montar resultado - pegar apenas o mais recente de cada canal
            channels_data = {}
            seen_channels = set()
            for channel in channels:
                if channel.channel_name not in seen_channels:
                    channels_data[channel.channel_name] = {
                        "sales": channel.sales,
                        "spend": channel.spend,
                        "budget": channel.budget,
                        "roi": channel.roi,
                        "profit": channel.profit,
                        "margin": channel.margin_percent
                    }
                    seen_channels.add(channel.channel_name)
                    logger.info(f"Canal {channel.channel_name}: ROI={channel.roi:.2f}, Vendas=R${channel.sales:.2f}, Gastos=R${channel.spend:.2f}")
            
            if not channels_data:
                logger.warning("Nenhum dado de canal encontrado - retornando canais vazios")
                channels_data = {
                    "geral": {"sales": 0.0, "spend": 0.0, "roi": 0.0, "profit": 0.0, "margin": 0.0},
                    "instagram": {"sales": 0.0, "spend": 0.0, "roi": 0.0, "profit": 0.0, "margin": 0.0},
                    "grupos": {"sales": 0.0, "spend": 0.0, "roi": 0.0, "profit": 0.0, "margin": 0.0}
                }
            
            return {
                "date": today.strftime("%d/%m/%Y"),
                "totals": {
                    "sales": snapshot.total_sales,
                    "spend": snapshot.total_spend,
                    "budget": snapshot.total_budget,
                    "roi": snapshot.general_roi,
                    "orders": snapshot.total_orders,
                    "numbers": snapshot.total_numbers,
                    "profit": snapshot.profit,
                    "margin": snapshot.margin_percent
                },
                "channels": channels_data,
                "last_update": snapshot.collected_at.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter dados de hoje: {e}")
            return None

    def get_collection_history(self, db: Session, days: int = 7) -> List[Dict]:
        """Obter histórico de coletas com dados de snapshot e cálculo de diferenças"""
        try:
            # Buscar logs com os snapshots correspondentes
            from sqlalchemy import and_
            
            # Buscar snapshots dos últimos dias - ordenar por tempo ASC para cálculos corretos
            snapshots = db.query(DailySnapshot).filter(
                and_(
                    DailySnapshot.date >= date.today() - timedelta(days=days),
                    DailySnapshot.product_id == self.product_id
                )
            ).order_by(DailySnapshot.collected_at.asc()).all()
            
            result = []
            
            # Calcular diferenças processando em ordem cronológica
            for i, snapshot in enumerate(snapshots):
                # Buscar log correspondente
                log = db.query(CollectionLog).filter(
                    CollectionLog.date == snapshot.date
                ).order_by(CollectionLog.collection_time.desc()).first()
                
                # Inicializar diferenças
                sales_diff = 0.0
                sales_percent_change = 0.0
                roi_percent_change = 0.0
                profit_diff = 0.0
                profit_percent_change = 0.0
                has_data_to_compare = False
                
                # Comparar com coleta anterior (se existe)
                if i > 0:
                    prev_snapshot = snapshots[i-1]
                    has_data_to_compare = True
                    
                    # Calcular diferenças
                    sales_diff = snapshot.total_sales - prev_snapshot.total_sales
                    if prev_snapshot.total_sales > 0:
                        sales_percent_change = ((snapshot.total_sales - prev_snapshot.total_sales) / prev_snapshot.total_sales) * 100

                    if prev_snapshot.general_roi > 0:
                        roi_percent_change = ((snapshot.general_roi - prev_snapshot.general_roi) / prev_snapshot.general_roi) * 100
                    
                    profit_diff = snapshot.profit - prev_snapshot.profit
                    if prev_snapshot.profit > 0:
                        profit_percent_change = ((snapshot.profit - prev_snapshot.profit) / prev_snapshot.profit) * 100
                
                result.append({
                    "date": snapshot.date.strftime("%d/%m/%Y"),
                    "time": snapshot.collected_at.strftime("%H:%M:%S"),
                    "status": log.status if log else "success",
                    "message": f"ROI: {snapshot.general_roi:.2f} | Vendas: R$ {snapshot.total_sales:,.2f}",
                    "roi": snapshot.general_roi,
                    "sales": snapshot.total_sales,
                    "spend": snapshot.total_spend,
                    "profit": snapshot.profit,
                    "sales_diff": sales_diff,
                    "sales_percent_change": sales_percent_change,
                    "roi_percent_change": roi_percent_change,
                    "profit_diff": profit_diff,
                    "profit_percent_change": profit_percent_change,
                    "has_growth": sales_diff > 0,
                    "has_data_to_compare": has_data_to_compare
                })
                
            # Retornar em ordem decrescente (mais recente primeiro) para exibição
            return list(reversed(result))
            
        except Exception as e:
            logger.error(f"Erro ao obter histórico: {e}")
            return []

    def get_collection_status(self, db: Session) -> Dict:
        """Obter status da coleta"""
        try:
            today = date.today()
            
            # Última coleta
            last_log = db.query(CollectionLog).filter(
                CollectionLog.date == today
            ).order_by(CollectionLog.collection_time.desc()).first()
            
            # Contar coletas de hoje
            today_count = db.query(CollectionLog).filter(
                CollectionLog.date == today
            ).count()
            
            return {
                "last_collection": last_log.collection_time.isoformat() if last_log else None,
                "last_status": last_log.status if last_log else "none",
                "today_collections": today_count,
                "is_active": today_count > 0,
                "next_collection": "A cada 30 minutos"
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter status: {e}")
            return {"error": str(e)}

# Instância global
imperio_data_manager = ImperioDataManager()