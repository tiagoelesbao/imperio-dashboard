import asyncio
import requests
from datetime import datetime, timedelta
import pytz
import logging
from typing import Dict, List, Optional
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import ROIData, SalesData, AffiliateData
from .facebook_service import collect_facebook_data
import os
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class DataCollector:
    """Coletor principal de dados com otimizações e rate limiting"""
    
    def __init__(self):
        # Configurações da API
        self.api_username = os.getenv("API_USERNAME")
        self.api_password = os.getenv("API_PASSWORD")
        self.urls = {
            "login": os.getenv("URL_LOGIN_API"),
            "orders": os.getenv("URL_API_ORDERS_BY_DAY"),
            "affiliates": os.getenv("URL_API_AFFILIATES")
        }
        
        # Códigos dos afiliados
        self.affiliate_codes = {
            "instagram": os.getenv("AFFILIADO_CODE_INSTAGRAM"),
            "grupo_1": os.getenv("AFFILIADO_CODE_GRUPO_1"),
            "grupo_2": os.getenv("AFFILIADO_CODE_GRUPO_2")
        }
        
        # Cache de token
        self._token = None
        self._token_expiry = None
    
    def get_token(self) -> str:
        """Obtém token de acesso com cache"""
        if self._token and self._token_expiry and datetime.now() < self._token_expiry:
            return self._token
        
        logger.info("Obtendo novo token de acesso...")
        
        payload = {
            "email": self.api_username,
            "password": self.api_password
        }
        headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        
        try:
            response = requests.post(self.urls["login"], json=payload, headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                if "accessToken" in data:
                    self._token = data["accessToken"]
                    # Token válido por 1 hora (estimativa conservadora)
                    self._token_expiry = datetime.now() + timedelta(hours=1)
                    logger.info("Token obtido com sucesso")
                    return self._token
                else:
                    raise Exception("'accessToken' não encontrado na resposta")
            else:
                raise Exception(f"Falha na autenticação: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao obter token: {e}")
            raise
    
    def get_sales_data(self) -> List[Dict]:
        """Coleta dados de vendas"""
        token = self.get_token()
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        try:
            response = requests.get(self.urls["orders"], headers=headers, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Dados de vendas obtidos com sucesso")
                return self.process_sales_data(data)
            else:
                raise Exception(f"Falha ao obter vendas: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao obter dados de vendas: {e}")
            raise
    
    def process_sales_data(self, raw_data: Dict) -> List[Dict]:
        """Processa dados de vendas"""
        processed_data = []
        
        for item in raw_data.get("somasPorDia", []):
            date_str = item["_id"]  # "YYYY-MM-DD"
            dt = datetime.strptime(date_str, '%Y-%m-%d')
            formatted_date = dt.strftime('%d/%m/%Y')
            
            processed_data.append({
                "date": formatted_date,
                "total_orders": item["totalOrdensPorDia"],
                "total_numbers": item["totalNumerosPorDia"],
                "total_value": item["totalPorDia"]
            })
        
        return processed_data
    
    def get_affiliates_data(self) -> Dict:
        """Coleta dados de afiliados"""
        token = self.get_token()
        
        # Configurar período (hoje)
        tz_brasilia = pytz.timezone('America/Sao_Paulo')
        now_local = datetime.now(tz_brasilia)
        start_of_day_local = now_local.replace(hour=0, minute=1, second=0, microsecond=0)
        
        now_utc = now_local.astimezone(pytz.UTC)
        start_of_day_utc = start_of_day_local.astimezone(pytz.UTC)
        
        init = start_of_day_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        end = now_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
        
        params = {
            "init": init,
            "end": end,
            "name": "",
            "affiliateCode": ""
        }
        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/json"
        }
        
        try:
            response = requests.get(self.urls["affiliates"], headers=headers, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Dados de afiliados obtidos com sucesso")
                return self.process_affiliates_data(data)
            else:
                raise Exception(f"Falha ao obter afiliados: {response.status_code} - {response.text}")
                
        except Exception as e:
            logger.error(f"Erro ao obter dados de afiliados: {e}")
            raise
    
    def process_affiliates_data(self, raw_data: List) -> Dict:
        """Processa dados de afiliados"""
        processed_data = {}
        
        for item in raw_data:
            code = item["user"].get("affiliateCode", "")
            paid_orders = item.get("totalPaidOrders", 0)
            order_count = item.get("orderCount", 0)
            average_ticket = paid_orders / order_count if order_count > 0 else 0
            
            processed_data[code] = {
                "total_paid_orders": paid_orders,
                "order_count": order_count,
                "average_ticket": average_ticket
            }
        
        return processed_data
    
    def save_sales_data(self, sales_data: List[Dict]):
        """Salva dados de vendas no banco"""
        db = SessionLocal()
        try:
            for item in sales_data:
                sales_record = SalesData(
                    date=item["date"],
                    total_orders=item["total_orders"],
                    total_numbers=item["total_numbers"],
                    total_value=item["total_value"],
                    timestamp=datetime.now()
                )
                db.add(sales_record)
            
            db.commit()
            logger.info(f"Dados de vendas salvos: {len(sales_data)} registros")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de vendas: {e}")
            db.rollback()
        finally:
            db.close()
    
    def save_affiliates_data(self, affiliates_data: Dict):
        """Salva dados de afiliados no banco"""
        db = SessionLocal()
        try:
            # Mapear códigos para nomes
            code_to_name = {
                self.affiliate_codes["instagram"]: "Instagram",
                self.affiliate_codes["grupo_1"]: "Grupo 1",
                self.affiliate_codes["grupo_2"]: "Grupo 2"
            }
            
            for code, data in affiliates_data.items():
                if code in code_to_name:
                    affiliate_record = AffiliateData(
                        affiliate_code=code,
                        affiliate_name=code_to_name[code],
                        total_paid_orders=data["total_paid_orders"],
                        order_count=data["order_count"],
                        average_ticket=data["average_ticket"],
                        timestamp=datetime.now()
                    )
                    db.add(affiliate_record)
            
            db.commit()
            logger.info(f"Dados de afiliados salvos: {len(affiliates_data)} registros")
            
        except Exception as e:
            logger.error(f"Erro ao salvar dados de afiliados: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def calculate_and_save_roi(self, sales_data: List[Dict], facebook_spends: Dict[str, float]):
        """Calcula e salva dados de ROI"""
        db = SessionLocal()
        try:
            # Obter vendas mais recentes por canal
            latest_sales = sales_data[-1] if sales_data else {"total_value": 0}
            
            # Obter dados de afiliados
            affiliates_data = self.get_affiliates_data()
            
            # Configurar gastos por canal
            channel_spends = {
                "geral": sum(facebook_spends.values()),
                "instagram": facebook_spends.get("instagram_accounts", 0),
                "grupo": facebook_spends.get("grupo_accounts", 0)
            }
            
            # Calcular ROI por canal
            channels = {
                "geral": latest_sales["total_value"],
                "instagram": affiliates_data.get(self.affiliate_codes["instagram"], {}).get("total_paid_orders", 0),
                "grupo": (
                    affiliates_data.get(self.affiliate_codes["grupo_1"], {}).get("total_paid_orders", 0) +
                    affiliates_data.get(self.affiliate_codes["grupo_2"], {}).get("total_paid_orders", 0)
                )
            }
            
            for channel, sales_value in channels.items():
                spend = channel_spends.get(channel, 0)
                roi = sales_value / spend if spend > 0 else 0
                
                roi_record = ROIData(
                    page_type=channel,
                    spend=spend,
                    sales=sales_value,
                    roi=roi,
                    period="hourly",
                    timestamp=datetime.now()
                )
                db.add(roi_record)
            
            db.commit()
            logger.info("Dados de ROI calculados e salvos")
            
        except Exception as e:
            logger.error(f"Erro ao calcular ROI: {e}")
            db.rollback()
        finally:
            db.close()
    
    async def collect_all_data(self):
        """Coleta todos os dados de forma otimizada"""
        try:
            logger.info("Iniciando coleta completa de dados...")
            
            # Coletar dados de vendas e afiliados
            sales_data = self.get_sales_data()
            affiliates_data = self.get_affiliates_data()
            
            # Coletar dados do Facebook de forma assíncrona
            facebook_spends = await collect_facebook_data()
            
            # Salvar dados no banco
            self.save_sales_data(sales_data)
            self.save_affiliates_data(affiliates_data)
            
            # Calcular e salvar ROI
            await self.calculate_and_save_roi(sales_data, facebook_spends)
            
            logger.info("Coleta completa de dados finalizada com sucesso")
            
        except Exception as e:
            logger.error(f"Erro na coleta completa de dados: {e}")
            raise

# Instância global do coletor
data_collector = DataCollector()

async def run_data_collection():
    """Função principal para executar coleta de dados"""
    await data_collector.collect_all_data()