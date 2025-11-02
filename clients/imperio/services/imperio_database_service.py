"""
Serviço de dados baseado em banco de dados (substitui Google Sheets)
"""
from datetime import datetime, date, timedelta
import pytz
from typing import Dict, List, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc
from core.database.base import get_db
from core.models.base import ChannelData, DailySnapshot, CollectionLog

class ImperioDatabaseService:
    """Serviço para obter dados do banco de dados (substitui Google Sheets)"""
    
    def __init__(self):
        self.tz_brasilia = pytz.timezone('America/Sao_Paulo')
        
    def get_looker_geral_data(self) -> Dict[str, Any]:
        """Obtém dados para visualização Looker Geral baseado no banco"""
        try:
            db = next(get_db())
            
            # Data atual no Brasil
            today_brazil = datetime.now(self.tz_brasilia).date()
            
            # CORRIGIDO: Usar DailySnapshot que contém os dados REAIS
            snapshots = db.query(DailySnapshot).filter(
                DailySnapshot.date >= today_brazil,
                DailySnapshot.product_id == "68ff78f80d0e097d617d472b"
            ).order_by(DailySnapshot.collected_at.asc()).all()
            
            # Processar dados cumulativos REAIS
            cumulative_data = []
            for snapshot in snapshots:
                cumulative_data.append({
                    "dateTime": snapshot.collected_at.strftime('%d/%m/%Y %H:%M:%S'),
                    "valorUsado": snapshot.total_spend,
                    "vendas": snapshot.total_sales,
                    "roi": snapshot.general_roi
                })
            
            # Calcular intervalos baseado nos snapshots REAIS
            interval_data = []
            previous_sales = 0
            previous_spend = 0
            
            for i, snapshot in enumerate(snapshots):
                if i > 0:  # Calcular diferença da coleta anterior
                    interval_sales = snapshot.total_sales - previous_sales
                    interval_spend = snapshot.total_spend - previous_spend
                    interval_roi = interval_sales / interval_spend if interval_spend > 0 else 0
                    
                    # Criar formato de intervalo de tempo
                    previous_snapshot = snapshots[i-1]
                    start_time = previous_snapshot.collected_at.strftime('%H:%M:%S')
                    end_time = snapshot.collected_at.strftime('%H:%M:%S')
                    date_str = snapshot.collected_at.strftime('%d/%m/%Y')
                    
                    interval_data.append({
                        "dateTime": f"{date_str} {start_time} às {end_time}",
                        "valorUsado": interval_spend,
                        "vendas": interval_sales,
                        "roi": interval_roi
                    })
                
                previous_sales = snapshot.total_sales
                previous_spend = snapshot.total_spend
            
            db.close()
            
            return {
                "dateRange": f"Dados ROI Geral - {datetime.now(self.tz_brasilia).strftime('%d/%m/%Y %H:%M')}",
                "cumulativeData": cumulative_data,
                "intervalData": interval_data
            }
            
        except Exception as e:
            print(f"Erro ao obter dados looker geral do banco: {e}")
            return {
                "dateRange": "Erro ao carregar dados do banco",
                "cumulativeData": [],
                "intervalData": []
            }
    
    def get_looker_perfil_data(self) -> Dict[str, Any]:
        """Obtém dados para visualização Looker Perfil (Instagram) baseado no banco"""
        try:
            db = next(get_db())
            
            # Data atual no Brasil
            today_brazil = datetime.now(self.tz_brasilia).date()
            
            # Buscar dados específicos do Instagram - todos os registros
            instagram_data = db.query(ChannelData).filter(
                ChannelData.date >= today_brazil - timedelta(days=1),
                ChannelData.channel_name == "instagram",
                ChannelData.product_id == "68ff78f80d0e097d617d472b"
            ).order_by(ChannelData.collected_at.asc()).all()
            
            # Processar dados cumulativos do Instagram
            cumulative_data = []
            for data in instagram_data:
                cumulative_data.append({
                    "dateTime": data.collected_at.strftime('%d/%m/%Y %H:%M:%S'),
                    "valorUsado": data.spend,
                    "vendas": data.sales,
                    "roi": data.roi
                })
            
            # Processar dados de intervalo (diferença entre coletas)
            interval_data = []
            previous_sales = 0
            previous_spend = 0
            
            for i, data in enumerate(instagram_data):
                if i > 0:
                    interval_sales = data.sales - previous_sales
                    interval_spend = data.spend - previous_spend
                    interval_roi = interval_sales / interval_spend if interval_spend > 0 else 0
                    
                    # Criar formato de intervalo
                    previous_data = instagram_data[i-1]
                    start_time = previous_data.collected_at.strftime('%H:%M:%S')
                    end_time = data.collected_at.strftime('%H:%M:%S')
                    date_str = data.collected_at.strftime('%d/%m/%Y')
                    
                    interval_data.append({
                        "dateTime": f"{date_str} {start_time} às {end_time}",
                        "valorUsado": interval_spend,
                        "vendas": interval_sales,
                        "roi": interval_roi
                    })
                
                previous_sales = data.sales
                previous_spend = data.spend
            
            db.close()
            
            return {
                "dateRange": f"Instagram ROI - {datetime.now(self.tz_brasilia).strftime('%d/%m/%Y %H:%M')}",
                "cumulativeData": cumulative_data,
                "intervalData": interval_data
            }
            
        except Exception as e:
            print(f"Erro ao obter dados looker perfil do banco: {e}")
            return {
                "dateRange": "Erro ao carregar Instagram",
                "cumulativeData": [],
                "intervalData": []
            }
    
    def get_looker_grupos_data(self) -> Dict[str, Any]:
        """Obtém dados para visualização Looker Grupos baseado no banco"""
        try:
            db = next(get_db())
            
            # Data atual no Brasil
            today_brazil = datetime.now(self.tz_brasilia).date()
            
            # Buscar dados específicos dos Grupos
            grupos_data = db.query(ChannelData).filter(
                ChannelData.date >= today_brazil - timedelta(days=1),
                ChannelData.channel_name == "grupos",
                ChannelData.product_id == "68ff78f80d0e097d617d472b"
            ).order_by(ChannelData.collected_at.asc()).all()
            
            # Processar dados cumulativos dos Grupos
            cumulative_data = []
            for data in grupos_data:
                cumulative_data.append({
                    "dateTime": data.collected_at.strftime('%d/%m/%Y %H:%M:%S'),
                    "valorUsado": data.spend,
                    "vendas": data.sales,
                    "roi": data.roi
                })
            
            # Processar dados de intervalo (diferença entre coletas)
            interval_data = []
            previous_sales = 0
            previous_spend = 0
            
            for i, data in enumerate(grupos_data):
                if i > 0:
                    interval_sales = data.sales - previous_sales
                    interval_spend = data.spend - previous_spend
                    interval_roi = interval_sales / interval_spend if interval_spend > 0 else 0
                    
                    # Criar formato de intervalo
                    previous_data = grupos_data[i-1]
                    start_time = previous_data.collected_at.strftime('%H:%M:%S')
                    end_time = data.collected_at.strftime('%H:%M:%S')
                    date_str = data.collected_at.strftime('%d/%m/%Y')
                    
                    interval_data.append({
                        "dateTime": f"{date_str} {start_time} às {end_time}",
                        "valorUsado": interval_spend,
                        "vendas": interval_sales,
                        "roi": interval_roi
                    })
                
                previous_sales = data.sales
                previous_spend = data.spend
            
            db.close()
            
            return {
                "dateRange": f"Grupos ROI (WhatsApp + Telegram) - {datetime.now(self.tz_brasilia).strftime('%d/%m/%Y %H:%M')}",
                "cumulativeData": cumulative_data,
                "intervalData": interval_data
            }
            
        except Exception as e:
            print(f"Erro ao obter dados looker grupos do banco: {e}")
            return {
                "dateRange": "Erro ao carregar Grupos",
                "cumulativeData": [],
                "intervalData": []
            }

    def get_dashboard_orcamento_data(self) -> Dict[str, Any]:
        """Obtém dados para o dashboard de orçamento (formato da screenshot)"""
        try:
            db = next(get_db())
            
            # Data atual no Brasil
            today_brazil = datetime.now(self.tz_brasilia).date()
            
            # Buscar último snapshot do dia (dados mais recentes)
            latest_snapshot = db.query(DailySnapshot).filter(
                DailySnapshot.date == today_brazil,
                DailySnapshot.product_id == "68ff78f80d0e097d617d472b"
            ).order_by(DailySnapshot.collected_at.desc()).first()

            if not latest_snapshot:
                # Se não tem dados de hoje, buscar de ontem
                yesterday = today_brazil - timedelta(days=1)
                latest_snapshot = db.query(DailySnapshot).filter(
                    DailySnapshot.date == yesterday,
                    DailySnapshot.product_id == "68ff78f80d0e097d617d472b"
                ).order_by(DailySnapshot.collected_at.desc()).first()

            # Buscar dados por canal (mais recentes de hoje)
            channels_data = {}
            for channel in ['geral', 'instagram', 'grupos']:
                channel_record = db.query(ChannelData).filter(
                    ChannelData.date == today_brazil,
                    ChannelData.channel_name == channel,
                    ChannelData.product_id == "68ff78f80d0e097d617d472b"
                ).order_by(ChannelData.collected_at.desc()).first()
                
                if channel_record:
                    channels_data[channel] = {
                        "roi": channel_record.roi,
                        "sales": channel_record.sales,
                        "spend": channel_record.spend,
                        "profit": channel_record.profit,
                        "budget": channel_record.budget
                    }
            
            # Buscar histórico de coletas (últimas 10) - filtrar registros válidos
            collection_history_raw = db.query(CollectionLog).filter(
                CollectionLog.date >= today_brazil - timedelta(days=1),
                CollectionLog.total_sales > 0,  # Filtrar registros com dados válidos
                CollectionLog.total_spend > 0
            ).order_by(CollectionLog.collection_time.asc()).limit(10).all()
            
            # Reverter para mostrar mais recente primeiro no frontend
            collection_history = list(reversed(collection_history_raw))
            
            db.close()
            
            # Preparar dados de retorno
            if latest_snapshot:
                # Métricas principais
                main_metrics = {
                    "roi_atual": latest_snapshot.general_roi,
                    "vendas_hoje": latest_snapshot.total_sales,
                    "gastos_hoje": latest_snapshot.total_spend,
                    "lucro_hoje": latest_snapshot.profit,
                    
                    # Metas REAIS baseadas na operação atual da empresa
                    "meta_vendas": 45000.0,   # Meta diária realista
                    "meta_gastos": 12000.0,   # Meta de gastos diária realista
                    "margem_atual": latest_snapshot.margin_percent
                }
                
                # Dados dos canais
                canal_data = {
                    "geral": channels_data.get("geral", {"roi": 0, "sales": 0, "spend": 0}),
                    "instagram": channels_data.get("instagram", {"roi": 0, "sales": 0, "spend": 0}),
                    "grupos": channels_data.get("grupos", {"roi": 0, "sales": 0, "spend": 0})
                }
                
                # Histórico formatado com cálculo de variações
                # Processar em ordem cronológica para calcular variações corretas
                history_chronological = []
                previous_log = None
                
                for i, log in enumerate(collection_history_raw):  # Usar ordem cronológica para variações
                    # Calcular variações baseado no período anterior
                    vendas_change = 0
                    lucro_change = 0
                    
                    if previous_log and previous_log.total_sales > 0:
                        # Variação percentual das vendas
                        vendas_change = ((log.total_sales - previous_log.total_sales) / previous_log.total_sales) * 100
                        
                        # Variação percentual do lucro
                        previous_lucro = previous_log.total_sales - previous_log.total_spend
                        current_lucro = log.total_sales - log.total_spend
                        
                        if previous_lucro > 0:
                            lucro_change = ((current_lucro - previous_lucro) / previous_lucro) * 100
                    
                    # Limitar variações a valores razoáveis (-100% a +500%)
                    vendas_change = max(-100, min(500, vendas_change))
                    lucro_change = max(-100, min(500, lucro_change))
                    
                    history_chronological.append({
                        "timestamp": log.collection_time.strftime('%d/%m/%Y %H:%M:%S'),
                        "status": log.status,
                        "roi": round(log.general_roi, 2),
                        "vendas": round(log.total_sales, 2),
                        "gastos": round(log.total_spend, 2),
                        "lucro": round(log.total_sales - log.total_spend, 2),
                        "vendas_change": round(vendas_change, 1),
                        "lucro_change": round(lucro_change, 1)
                    })
                    
                    previous_log = log
                
                # Reverter para mostrar mais recente primeiro
                history_formatted = list(reversed(history_chronological))
                
                return {
                    "status": "success",
                    "data_atual": today_brazil.strftime('%d/%m/%Y'),
                    "ultima_atualizacao": latest_snapshot.collected_at.strftime('%d/%m/%Y %H:%M:%S'),
                    "metricas_principais": main_metrics,
                    "canais": canal_data,
                    "historico_coletas": history_formatted
                }
            
            else:
                return {
                    "status": "no_data",
                    "message": "Nenhum dado disponível para hoje",
                    "data_atual": today_brazil.strftime('%d/%m/%Y')
                }
                
        except Exception as e:
            print(f"Erro ao obter dados do dashboard orçamento: {e}")
            return {
                "status": "error",
                "message": f"Erro ao carregar dados: {str(e)}"
            }

# Instância global do serviço baseado em banco
imperio_db_service = ImperioDatabaseService()