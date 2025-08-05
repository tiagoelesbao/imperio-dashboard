#!/usr/bin/env python3
"""
Data Collector LIMPO - Versão final baseada no código original
Focado APENAS na ação 684c73283d75820c0a77a42f
"""

import requests
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Optional, List, Tuple
from sqlalchemy.orm import Session
import pytz

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ImperioDataCollector:
    """Coletor de dados para a ação 684c73283d75820c0a77a42f"""
    
    def __init__(self):
        # Configurações da ação específica
        self.PRODUCT_ID = "684c73283d75820c0a77a42f"
        
        # URLs das APIs (baseado exatamente no código original)
        self.URL_LOGIN = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/auth/login"
        self.URL_ORDERS_BY_DAY = f"https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/{self.PRODUCT_ID}/ordersByDay"
        self.URL_AFFILIATES = f"https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/{self.PRODUCT_ID}/affiliates/data"
        
        # Credenciais (do código original)
        self.USERNAME = "tiago"
        self.PASSWORD = "Tt!1zxcqweqweasd"
        
        # Códigos de afiliados específicos (do código original)
        self.AFFILIATES = {
            "INSTAGRAM": "L8UTEDVTI0",
            "GRUPO_1": "17QB25AKRL"
            # GRUPO_2 removido - não existe mais
        }
        
        # Token Facebook Ads (do código original)
        self.FACEBOOK_TOKEN = 'EAAT6ZBgzXABUBO0zMuZCXBmauERl111KuLZAzkEgVhrkhs2RJT8rZAZCxyZB1YhyicYw3fe9XxmCngjv0BDmZCPeBNFIU5kGBZARZAwzPNMaENwiJia7ilwTzsNWxnzi8L2ly3PV2OQAuRzPXFyxXdNdJxWypZBBWeUvZBWrKYIDUTZBAaWsPHd8KmgfaPH8Mt8eb5U7V36T1ne1'
        
        # Contas Facebook (do código original)
        self.FACEBOOK_ACCOUNTS = [
            'act_2067257390316380',
            'act_1391112848236399',
            'act_406219475582745', 
            'act_790223756353632',
            'act_772777644802886',
            'act_303402486183447'
        ]
        
        self.token_cache = None
        self.token_expires = None

    def _safe_float(self, value) -> float:
        """Converter valor para float de forma segura - API Facebook usa formato americano"""
        if value is None:
            return 0.0
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            # Facebook API retorna valores em formato americano (ponto decimal)
            # Exemplo: "3380.46" deve ser 3380.46, não 338046
            clean_value = value.replace("R$", "").replace(" ", "").strip()
            try:
                return float(clean_value)  # Conversão direta sem alteração de formato
            except ValueError:
                return 0.0
        return 0.0

    def _get_account_budget(self, account_id: str, api_version: str) -> float:
        """Coletar orçamento total da conta (campanhas + ad sets)"""
        try:
            total_budget = 0.0
            
            # 1. Buscar campanhas ativas da conta
            campaigns_url = (f"https://graph.facebook.com/{api_version}/{account_id}/campaigns"
                           f"?fields=name,daily_budget,lifetime_budget,status&effective_status=['ACTIVE']"
                           f"&access_token={self.FACEBOOK_TOKEN}")
            
            campaigns_response = requests.get(campaigns_url)
            
            if campaigns_response.status_code == 200:
                campaigns_data = campaigns_response.json()
                
                for campaign in campaigns_data.get("data", []):
                    campaign_budget = 0.0
                    
                    # Orçamento diário da campanha
                    if campaign.get("daily_budget"):
                        campaign_budget = self._safe_float(campaign["daily_budget"]) / 100  # Facebook retorna em centavos
                    # Orçamento vitalício da campanha (dividido por dias estimados)
                    elif campaign.get("lifetime_budget"):
                        lifetime_budget = self._safe_float(campaign["lifetime_budget"]) / 100
                        # Estimar para 30 dias se for lifetime budget
                        campaign_budget = lifetime_budget / 30
                    
                    if campaign_budget > 0:
                        total_budget += campaign_budget
                        logger.info(f"Campanha {campaign.get('name', 'N/A')}: R$ {campaign_budget:.2f}/dia")
                    else:
                        # Se campanha não tem orçamento, buscar nos ad sets
                        campaign_id = campaign.get("id")
                        adset_budget = self._get_adsets_budget(campaign_id, api_version)
                        total_budget += adset_budget
            
            return total_budget
            
        except Exception as e:
            logger.warning(f"Erro ao coletar orçamento de {account_id}: {e}")
            return 0.0

    def _get_adsets_budget(self, campaign_id: str, api_version: str) -> float:
        """Coletar orçamento dos ad sets de uma campanha"""
        try:
            adsets_url = (f"https://graph.facebook.com/{api_version}/{campaign_id}/adsets"
                         f"?fields=name,daily_budget,lifetime_budget,status&effective_status=['ACTIVE']"
                         f"&access_token={self.FACEBOOK_TOKEN}")
            
            response = requests.get(adsets_url)
            
            if response.status_code == 200:
                adsets_data = response.json()
                adset_budget_total = 0.0
                
                for adset in adsets_data.get("data", []):
                    adset_budget = 0.0
                    
                    # Orçamento diário do ad set
                    if adset.get("daily_budget"):
                        adset_budget = self._safe_float(adset["daily_budget"]) / 100
                    # Orçamento vitalício do ad set
                    elif adset.get("lifetime_budget"):
                        lifetime_budget = self._safe_float(adset["lifetime_budget"]) / 100
                        adset_budget = lifetime_budget / 30
                    
                    if adset_budget > 0:
                        adset_budget_total += adset_budget
                        logger.info(f"  Ad Set {adset.get('name', 'N/A')}: R$ {adset_budget:.2f}/dia")
                
                return adset_budget_total
            
            return 0.0
            
        except Exception as e:
            logger.warning(f"Erro ao coletar orçamento dos ad sets da campanha {campaign_id}: {e}")
            return 0.0

    def _get_account_campaigns_with_period(self, account_id: str, date_preset: str) -> List[Dict]:
        """Buscar campanhas ativas de uma conta específica com período customizado"""
        try:
            # Tentar diferentes versões da API
            api_versions = ["v18.0", "v17.0", "v16.0"]
            
            for version in api_versions:
                try:
                    # Buscar campanhas ativas com período específico
                    campaigns_url = (f"https://graph.facebook.com/{version}/{account_id}/campaigns"
                                   f"?fields=name,status,daily_budget,lifetime_budget,insights.date_preset({date_preset}){{spend,impressions,clicks,conversions,cpm,cpc}}"
                                   f"&effective_status=['ACTIVE']"
                                   f"&access_token={self.FACEBOOK_TOKEN}")
                    
                    response = requests.get(campaigns_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        campaigns = []
                        
                        for campaign in data.get("data", []):
                            # Processar dados da campanha
                            insights = campaign.get("insights", {}).get("data", [{}])[0] if campaign.get("insights") else {}
                            
                            # Calcular orçamento
                            budget = 0.0
                            if campaign.get("daily_budget"):
                                budget = self._safe_float(campaign["daily_budget"]) / 100
                            elif campaign.get("lifetime_budget"):
                                budget = self._safe_float(campaign["lifetime_budget"]) / 100 / 30
                            
                            # DADOS EXATOS DO FACEBOOK - SEM QUALQUER CORREÇÃO OU ESTIMATIVA
                            spend_value = self._safe_float(insights.get("spend", "0"))
                            
                            campaigns.append({
                                "id": campaign.get("id"),
                                "name": campaign.get("name", ""),
                                "status": campaign.get("status", "").upper(),
                                "spend": spend_value,  # Valor corrigido
                                "budget": budget,
                                "impressions": int(insights.get("impressions", 0)),
                                "clicks": int(insights.get("clicks", 0)),
                                "conversions": int(insights.get("conversions", 0)),
                                "cpm": self._safe_float(insights.get("cpm", 0)),
                                "cpc": self._safe_float(insights.get("cpc", 0))
                            })
                        
                        return campaigns
                        
                except Exception as e:
                    logger.warning(f"Erro ao buscar campanhas com {version} e período {date_preset}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar campanhas de {account_id} com período {date_preset}: {e}")
            return []

    def _get_campaign_insights_for_period(self, campaign_id: str, start_date: str, end_date: str) -> Dict:
        """Buscar insights de uma campanha específica para um período customizado"""
        try:
            # Tentar diferentes versões da API
            api_versions = ["v18.0", "v17.0", "v16.0"]
            
            for version in api_versions:
                try:
                    # Buscar insights com data range customizada
                    insights_url = (f"https://graph.facebook.com/{version}/{campaign_id}/insights"
                                  f"?fields=spend,impressions,clicks,conversions,cpm,cpc"
                                  f"&time_range={{'since':'{start_date}','until':'{end_date}'}}"
                                  f"&access_token={self.FACEBOOK_TOKEN}")
                    
                    response = requests.get(insights_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        insights_data = data.get("data", [])
                        
                        if insights_data:
                            insight = insights_data[0]  # Primeiro resultado
                            
                            # DADOS EXATOS DO FACEBOOK - SEM QUALQUER CORREÇÃO OU ESTIMATIVA
                            spend_value = self._safe_float(insight.get("spend", "0"))
                            
                            return {
                                "spend": spend_value,
                                "impressions": int(insight.get("impressions", 0)),
                                "clicks": int(insight.get("clicks", 0)),
                                "conversions": int(insight.get("conversions", 0)),
                                "cpm": self._safe_float(insight.get("cpm", 0)),
                                "cpc": self._safe_float(insight.get("cpc", 0))
                            }
                        
                except Exception as e:
                    logger.warning(f"Erro ao buscar insights da campanha {campaign_id} com {version}: {e}")
                    continue
            
            return {}
            
        except Exception as e:
            logger.error(f"Erro ao buscar insights da campanha {campaign_id} para período {start_date}-{end_date}: {e}")
            return {}

    def _get_account_campaigns(self, account_id: str) -> List[Dict]:
        """Buscar campanhas ativas de uma conta específica"""
        try:
            # Tentar diferentes versões da API
            api_versions = ["v18.0", "v17.0", "v16.0"]
            
            for version in api_versions:
                try:
                    # Buscar campanhas ativas
                    campaigns_url = (f"https://graph.facebook.com/{version}/{account_id}/campaigns"
                                   f"?fields=name,status,daily_budget,lifetime_budget,insights{{spend,impressions,clicks,conversions,cpm,cpc}}"
                                   f"&effective_status=['ACTIVE']"
                                   f"&access_token={self.FACEBOOK_TOKEN}")
                    
                    response = requests.get(campaigns_url)
                    
                    if response.status_code == 200:
                        data = response.json()
                        campaigns = []
                        
                        for campaign in data.get("data", []):
                            # Processar dados da campanha
                            insights = campaign.get("insights", {}).get("data", [{}])[0] if campaign.get("insights") else {}
                            
                            # Calcular orçamento
                            budget = 0.0
                            if campaign.get("daily_budget"):
                                budget = self._safe_float(campaign["daily_budget"]) / 100
                            elif campaign.get("lifetime_budget"):
                                budget = self._safe_float(campaign["lifetime_budget"]) / 100 / 30
                            
                            # DADOS EXATOS DO FACEBOOK - SEM QUALQUER CORREÇÃO OU ESTIMATIVA
                            spend_value = self._safe_float(insights.get("spend", "0"))
                            
                            campaigns.append({
                                "id": campaign.get("id"),
                                "name": campaign.get("name", ""),
                                "status": campaign.get("status", "").upper(),
                                "spend": spend_value,  # Valor corrigido
                                "budget": budget,
                                "impressions": int(insights.get("impressions", 0)),
                                "clicks": int(insights.get("clicks", 0)),
                                "conversions": int(insights.get("conversions", 0)),
                                "cpm": self._safe_float(insights.get("cpm", 0)),
                                "cpc": self._safe_float(insights.get("cpc", 0))
                            })
                        
                        return campaigns
                        
                except Exception as e:
                    logger.warning(f"Erro ao buscar campanhas com {version}: {e}")
                    continue
            
            return []
            
        except Exception as e:
            logger.error(f"Erro ao buscar campanhas de {account_id}: {e}")
            return []

    def _get_auth_token(self) -> Optional[str]:
        """Obter token de autenticação - SEMPRE novo token a cada coleta"""
        logger.info("Obtendo novo token de autenticacao (forcado)...")
        
        try:
            payload = {
                "email": self.USERNAME,
                "password": self.PASSWORD
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
            
            response = requests.post(self.URL_LOGIN, json=payload, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                token = data.get("accessToken")  # Usar accessToken igual ao código original
                logger.info("Token obtido com sucesso")
                return token
            else:
                logger.error(f"Erro ao obter token: {response.status_code} - {response.text}")
                return None
                
        except Exception as e:
            logger.error(f"Erro na autenticacao: {e}")
            return None

    def collect_sales_data(self) -> Dict:
        """Coletar dados de vendas para hoje"""
        token = self._get_auth_token()
        if not token:
            return {"error": "Token não disponível"}
        
        logger.info(f"Coletando dados de vendas para acao {self.PRODUCT_ID}...")
        
        try:
            headers = {
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json"
            }
            
            # Chamar API sem parâmetros, igual ao código original
            response = requests.get(self.URL_ORDERS_BY_DAY, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Dados de vendas coletados com sucesso")
                
                # Processar dados igual ao código original
                today_data = self._extract_today_sales_from_response(data)
                
                return {
                    "success": True,
                    "data": today_data,
                    "raw_response": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Erro ao coletar vendas: {response.status_code} - {response.text}")
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Erro na coleta de vendas: {e}")
            return {"error": str(e)}

    def _extract_today_sales_from_response(self, response_data: Dict) -> Dict:
        """Extrair dados de vendas de hoje da resposta da API"""
        try:
            today_str = datetime.now().strftime('%Y-%m-%d')
            
            # Processar dados igual ao código original (somasPorDia)
            somas_por_dia = response_data.get("somasPorDia", [])
            
            for item in somas_por_dia:
                if item.get("_id") == today_str:
                    return {
                        "total_sales": self._safe_float(item.get("totalPorDia", 0)),
                        "total_orders": item.get("totalOrdensPorDia", 0),
                        "total_numbers": item.get("totalNumerosPorDia", 0),
                        "date": today_str
                    }
            
            # Se não encontrou dados de hoje, retornar zeros
            logger.warning(f"Dados de vendas para hoje ({today_str}) não encontrados")
            return {
                "total_sales": 0.0,
                "total_orders": 0,
                "total_numbers": 0,
                "date": today_str
            }
            
        except Exception as e:
            logger.error(f"Erro ao processar dados de vendas: {e}")
            return {
                "total_sales": 0.0,
                "total_orders": 0,
                "total_numbers": 0,
                "date": datetime.now().strftime('%Y-%m-%d'),
                "error": str(e)
            }

    def collect_affiliates_data(self) -> Dict:
        """Coletar dados de afiliados"""
        token = self._get_auth_token()
        if not token:
            return {"error": "Token não disponível"}
        
        logger.info(f"Coletando dados de afiliados para acao {self.PRODUCT_ID}...")
        
        try:
            # Configurar datas igual ao código original (hoje desde 00:01 até agora em UTC)
            tz_brasilia = pytz.timezone('America/Sao_Paulo')
            now_local = datetime.now(tz_brasilia)
            start_of_day_local = now_local.replace(hour=0, minute=1, second=0, microsecond=0)
            now_utc = now_local.astimezone(pytz.UTC)
            start_of_day_utc = start_of_day_local.astimezone(pytz.UTC)
            
            init = start_of_day_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            end = now_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
            
            logger.info(f"Período: {init} até {end} (UTC)")
            
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }
            
            params = {
                "init": init,
                "end": end,
                "name": "",
                "affiliateCode": ""
            }
            
            response = requests.get(self.URL_AFFILIATES, headers=headers, params=params)
            
            if response.status_code == 200:
                data = response.json()
                logger.info("Dados de afiliados coletados com sucesso")
                return {
                    "success": True,
                    "data": data,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                logger.error(f"Erro ao coletar afiliados: {response.status_code} - {response.text}")
                return {"error": f"API Error: {response.status_code}"}
                
        except Exception as e:
            logger.error(f"Erro na coleta de afiliados: {e}")
            return {"error": str(e)}

    def collect_facebook_data(self) -> Dict:
        """Coletar dados REAIS e ATUAIS do Facebook Ads via API"""
        logger.info("Coletando dados REAIS e ATUAIS do Facebook Ads...")
        
        accounts_data = {}
        total_spend = 0.0
        total_budget = 0.0
        
        for account_id in self.FACEBOOK_ACCOUNTS:
            try:
                # Tentar diferentes versões da API
                api_versions = ["v18.0", "v17.0", "v16.0"]
                
                account_spend = 0.0
                account_budget = 0.0
                success = False
                
                for version in api_versions:
                    try:
                        # Coletar gastos ATUAIS (spend) em tempo real
                        insights_url = (f"https://graph.facebook.com/{version}/{account_id}/insights"
                                      f"?fields=spend&date_preset=today&access_token={self.FACEBOOK_TOKEN}")
                        
                        response = requests.get(insights_url)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if "data" in data and len(data["data"]) > 0:
                                # USAR DADOS EXATOS DO FACEBOOK SEM QUALQUER CORREÇÃO
                                raw_spend = data["data"][0].get("spend", "0")
                                account_spend = self._safe_float(raw_spend)
                                logger.info(f"Gasto ATUAL da API para {account_id}: R$ {account_spend:.2f} (raw: {raw_spend})")
                            else:
                                account_spend = 0.0
                                logger.info(f"Nenhum dado de gasto para {account_id} hoje")
                            
                            # Coletar orçamentos das campanhas ativas
                            account_budget = self._get_account_budget(account_id, version)
                            
                            accounts_data[account_id] = {
                                "spend": account_spend,
                                "budget": account_budget,
                                "api_version": version,
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            total_spend += account_spend
                            total_budget += account_budget
                            success = True
                            logger.info(f"✅ {account_id}: Gasto=R$ {account_spend:.2f}")
                            break
                            
                    except Exception as e:
                        logger.warning(f"Tentativa {version} falhou para {account_id}: {e}")
                        continue
                
                if not success:
                    logger.error(f"Falha em todas as tentativas para {account_id}")
                    accounts_data[account_id] = {
                        "spend": 0.0,
                        "budget": 0.0,
                        "error": "Todas as tentativas falharam",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Erro geral para {account_id}: {e}")
                accounts_data[account_id] = {
                    "spend": 0.0,
                    "budget": 0.0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        logger.info(f"🎯 TOTAL ATUAL REAL: R$ {total_spend:,.2f} (atualizado em tempo real)")
        
        return {
            "success": True,
            "total_spend": total_spend,
            "total_budget": total_budget,
            "accounts": accounts_data,
            "timestamp": datetime.now().isoformat(),
            "data_source": "facebook_api_live"
        }
    
    def _collect_facebook_data_original(self) -> Dict:
        """Método original de coleta do Facebook (fallback)"""
        logger.info("Usando método ORIGINAL de coleta do Facebook (fallback)...")
        
        accounts_data = {}
        total_spend = 0.0
        total_budget = 0.0
        
        for account_id in self.FACEBOOK_ACCOUNTS:
            try:
                # Tentar diferentes versões da API
                api_versions = ["v18.0", "v17.0", "v16.0"]
                
                account_spend = 0.0
                account_budget = 0.0
                success = False
                
                for version in api_versions:
                    try:
                        # Coletar gastos (spend) e orçamentos
                        insights_url = (f"https://graph.facebook.com/{version}/{account_id}/insights"
                                      f"?fields=spend&date_preset=today&access_token={self.FACEBOOK_TOKEN}")
                        
                        response = requests.get(insights_url)
                        
                        if response.status_code == 200:
                            data = response.json()
                            
                            if "data" in data and len(data["data"]) > 0:
                                # USAR DADOS EXATOS DO FACEBOOK SEM QUALQUER ESTIMATIVA
                                account_spend = self._safe_float(data["data"][0].get("spend", 0))
                                logger.info(f"Spend EXATO da API para {account_id}: R$ {account_spend:.2f}")
                            else:
                                account_spend = 0.0
                            
                            # Coletar orçamentos das campanhas ativas
                            account_budget = self._get_account_budget(account_id, version)
                            
                            accounts_data[account_id] = {
                                "spend": account_spend,
                                "budget": account_budget,
                                "raw_spend": raw_spend if 'raw_spend' in locals() else 0,
                                "api_version": version,
                                "timestamp": datetime.now().isoformat()
                            }
                            
                            total_spend += account_spend
                            total_budget += account_budget
                            success = True
                            logger.info(f"{account_id}: Gasto=R$ {account_spend:.2f}, Orçamento=R$ {account_budget:.2f}")
                            break
                            
                    except Exception as e:
                        logger.warning(f"Tentativa {version} falhou para {account_id}: {e}")
                        continue
                
                if not success:
                    logger.error(f"Falha em todas as tentativas para {account_id}")
                    accounts_data[account_id] = {
                        "spend": 0.0,
                        "budget": 0.0,
                        "error": "Todas as tentativas falharam",
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                logger.error(f"Erro geral para {account_id}: {e}")
                accounts_data[account_id] = {
                    "spend": 0.0,
                    "budget": 0.0,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        return {
            "success": True,
            "total_spend": total_spend,
            "total_budget": total_budget,
            "accounts": accounts_data,
            "timestamp": datetime.now().isoformat(),
            "data_source": "facebook_api_original"
        }

    def get_channel_mappings(self):
        """Obter mapeamento de contas Facebook por canal do banco"""
        try:
            from ..database import get_db
            from ..models import FacebookAccountMapping
            
            db = next(get_db())
            mappings = db.query(FacebookAccountMapping).filter(
                FacebookAccountMapping.is_active == True
            ).all()
            
            channel_mapping = {}
            for mapping in mappings:
                if mapping.channel not in channel_mapping:
                    channel_mapping[mapping.channel] = []
                channel_mapping[mapping.channel].append(mapping.account_id)
            
            db.close()
            return channel_mapping
            
        except Exception as e:
            logger.error(f"Erro ao obter mapeamento de canais: {e}")
            # Retornar mapeamento padrão se falhar - todas campanhas para Instagram conforme usuário
            return {
                "geral": [],
                "instagram": ["act_2067257390316380", "act_1391112848236399", "act_406219475582745", "act_790223756353632"],
                "grupos": []
            }

    def process_and_calculate_roi(self, sales_data: Dict, affiliates_data: Dict, facebook_data: Dict) -> Dict:
        """Processar dados e calcular ROI por canal"""
        logger.info("Processando dados e calculando ROI...")
        
        try:
            # Obter mapeamento de canais atual
            channel_mapping = self.get_channel_mappings()
            logger.info(f"Mapeamento de canais: {channel_mapping}")
            
            # Extrair vendas totais (API ordersByDay)
            total_sales_from_api = 0.0
            total_orders = 0
            total_numbers = 0
            
            if sales_data.get("success") and "data" in sales_data:
                sales_info = sales_data["data"]
                total_sales_from_api = self._safe_float(sales_info.get("total_sales", 0))
                total_orders = int(sales_info.get("total_orders", 0))
                total_numbers = int(sales_info.get("total_numbers", 0))
            
            # Processar gastos do Facebook por canal baseado na configuração
            spend_by_channel = {
                "instagram": 0.0, 
                "grupos": 0.0
            }
            
            # Obter total de gastos e orçamentos do Facebook
            total_facebook_spend = 0.0
            total_facebook_budget = 0.0
            if facebook_data.get("success") and "accounts" in facebook_data:
                facebook_accounts = facebook_data["accounts"]
                
                # Verificar se accounts é um dict (formato {account_id: data}) ou lista
                if isinstance(facebook_accounts, dict):
                    for account_id, account_data in facebook_accounts.items():
                        if isinstance(account_data, dict):
                            spend = account_data.get("spend", 0.0)
                            budget = account_data.get("budget", 0.0)
                            total_facebook_spend += spend
                            total_facebook_budget += budget
                            
                            # Determinar canal baseado no mapeamento
                            channel_found = False
                            for channel, accounts in channel_mapping.items():
                                if account_id in accounts:
                                    spend_by_channel[channel] += spend
                                    channel_found = True
                                    logger.info(f"{account_id} -> {channel}: R$ {spend:.2f}")
                                    break
                            
                            # Se não encontrou mapeamento, colocar no Instagram (canal principal)
                            if not channel_found:
                                spend_by_channel["instagram"] += spend
                                logger.warning(f"{account_id} não mapeado, adicionado ao Instagram: R$ {spend:.2f}")
                        else:
                            logger.warning(f"Dados de conta inválidos para {account_id}: {account_data}")
                elif isinstance(facebook_accounts, list):
                    for account_data in facebook_accounts:
                        if isinstance(account_data, dict):
                            account_id = account_data.get("account_id", "")
                            spend = account_data.get("spend", 0.0)
                            budget = account_data.get("budget", 0.0)
                            total_facebook_spend += spend
                            total_facebook_budget += budget
                            
                            # Determinar canal baseado no mapeamento
                            channel_found = False
                            for channel, accounts in channel_mapping.items():
                                if account_id in accounts:
                                    spend_by_channel[channel] += spend
                                    channel_found = True
                                    logger.info(f"{account_id} -> {channel}: R$ {spend:.2f}")
                                    break
                            
                            # Se não encontrou mapeamento, colocar no Instagram (canal principal)
                            if not channel_found:
                                spend_by_channel["instagram"] += spend
                                logger.warning(f"{account_id} não mapeado, adicionado ao Instagram: R$ {spend:.2f}")
                        else:
                            logger.warning(f"Dados de conta inválidos: {account_data}")
                else:
                    logger.warning(f"Formato inesperado para facebook_accounts: {type(facebook_accounts)}")
            
            # Processar afiliados por canal - GERAL não recebe vendas diretas, é soma dos outros
            sales_by_channel = {
                "instagram": 0.0, 
                "grupos": 0.0
            }
            
            if affiliates_data.get("success") and "data" in affiliates_data:
                affiliate_list = affiliates_data["data"]
                # Verificar se é lista direta ou dict com "data"
                if isinstance(affiliate_list, list):
                    affiliates = affiliate_list
                elif isinstance(affiliate_list, dict) and "data" in affiliate_list:
                    affiliates = affiliate_list["data"]
                else:
                    affiliates = []
                
                for affiliate in affiliates:
                    # O código do afiliado está em user.affiliateCode
                    user_info = affiliate.get("user", {})
                    affiliate_code = user_info.get("affiliateCode", "")
                    paid_orders = self._safe_float(affiliate.get("totalPaidOrders", 0))
                    
                    # Classificar por canal - afiliados desconhecidos vão para Instagram (canal principal)
                    if affiliate_code == self.AFFILIATES["INSTAGRAM"]:
                        sales_by_channel["instagram"] += paid_orders
                        logger.info(f"Afiliado Instagram ({affiliate_code}): R$ {paid_orders:,.2f}")
                    elif affiliate_code == self.AFFILIATES["GRUPO_1"]:
                        sales_by_channel["grupos"] += paid_orders
                        logger.info(f"Afiliado Grupos ({affiliate_code}): R$ {paid_orders:,.2f}")
                    else:
                        # Afiliados não identificados vão para Instagram (canal principal de campanhas)
                        sales_by_channel["instagram"] += paid_orders
                        logger.info(f"Afiliado não identificado ({affiliate_code}): R$ {paid_orders:,.2f} -> Instagram")
            
            # Calcular vendas totais: usar API se disponível, senão somar afiliados
            total_sales_from_affiliates = sum(sales_by_channel.values())
            
            if total_sales_from_api > 0:
                total_sales = total_sales_from_api
                logger.info(f"Usando vendas da API ordersByDay: R$ {total_sales:,.2f}")
                
                # Se temos vendas totais mas não temos distribuição por afiliados, distribuir proporcionalmente ao gasto
                if total_sales_from_affiliates == 0 and total_facebook_spend > 0:
                    logger.info("Sem dados de afiliados - distribuindo vendas proporcionalmente aos gastos")
                    for channel in ["instagram", "grupos"]:
                        if spend_by_channel[channel] > 0:
                            proportion = spend_by_channel[channel] / total_facebook_spend
                            sales_by_channel[channel] = total_sales * proportion
                            logger.info(f"{channel}: {proportion:.1%} do gasto = R$ {sales_by_channel[channel]:,.2f} em vendas")
                    
                    # Se não há gasto em grupos (apenas Instagram), todas as vendas vão para Instagram
                    if spend_by_channel["grupos"] == 0 and spend_by_channel["instagram"] > 0:
                        sales_by_channel["instagram"] = total_sales
                        logger.info(f"Todas as vendas atribuídas ao Instagram: R$ {total_sales:,.2f}")
                        
            elif total_sales_from_affiliates > 0:
                total_sales = total_sales_from_affiliates
                logger.info(f"Usando soma dos afiliados: R$ {total_sales:,.2f}")
            else:
                total_sales = 0.0
                logger.warning("Nenhuma venda encontrada")
            
            # Calcular ROI por canal usando gastos reais por canal
            roi_by_channel = {}
            
            # Primeiro calcular Instagram e Grupos separadamente
            for channel in ["instagram", "grupos"]:
                sales = sales_by_channel[channel]
                channel_spend = spend_by_channel[channel]
                
                # Calcular ROI - evitar valores infinitos para compatibilidade JSON
                if channel_spend > 0:
                    roi = 1 + ((sales - channel_spend) / channel_spend)
                else:
                    roi = 999.99 if sales > 0 else 0.0  # ROI muito alto em vez de infinito
                
                roi_by_channel[channel] = {
                    "sales": sales,
                    "spend": channel_spend,
                    "roi": roi,
                    "profit": sales - channel_spend,
                    "margin": ((sales - channel_spend) / sales * 100) if sales > 0 else 0
                }
            
            # Canal GERAL = VENDAS TOTAIS REAIS da plataforma (não soma de afiliados)
            geral_sales = total_sales_from_api if total_sales_from_api > 0 else total_sales
            geral_spend = total_facebook_spend  # Total de gastos do Facebook
            geral_profit = geral_sales - geral_spend
            
            # ROI geral baseado no faturamento real da ação
            if geral_spend > 0:
                geral_roi = 1 + ((geral_sales - geral_spend) / geral_spend)
            else:
                geral_roi = 999.99 if geral_sales > 0 else 0.0  # ROI muito alto em vez de infinito
            
            roi_by_channel["geral"] = {
                "sales": geral_sales,
                "spend": geral_spend,
                "roi": geral_roi,
                "profit": geral_profit,
                "margin": ((geral_profit) / geral_sales * 100) if geral_sales > 0 else 0
            }
            
            logger.info(f"Canal GERAL - Vendas totais da plataforma: R$ {geral_sales:,.2f}, Gastos: R$ {geral_spend:,.2f}, ROI: {geral_roi:.2f}")
            
            # ROI geral
            general_roi = 1 + ((total_sales - total_facebook_spend) / total_facebook_spend) if total_facebook_spend > 0 else 0
            
            result = {
                "timestamp": datetime.now().isoformat(),
                "product_id": self.PRODUCT_ID,
                "totals": {
                    "sales": total_sales,
                    "spend": total_facebook_spend,
                    "budget": total_facebook_budget,
                    "roi": general_roi,
                    "orders": total_orders,
                    "numbers": total_numbers,
                    "profit": total_sales - total_facebook_spend,
                    "margin": ((total_sales - total_facebook_spend) / total_sales * 100) if total_sales > 0 else 0
                },
                "channels": roi_by_channel
            }
            
            logger.info("ROI calculado com sucesso")
            logger.info(f"ROI Geral: {general_roi:.2f}")
            logger.info(f"Vendas: R$ {total_sales:.2f}")
            logger.info(f"Gastos: R$ {total_facebook_spend:.2f}")
            logger.info(f"Orçamento: R$ {total_facebook_budget:.2f}")
            
            return result
            
        except Exception as e:
            logger.error(f"Erro no processamento: {e}")
            return {"error": str(e)}

    def execute_full_collection(self) -> Dict:
        """Executar coleta completa de dados"""
        logger.info("INICIANDO COLETA COMPLETA DE DADOS")
        logger.info(f"Ação: {self.PRODUCT_ID}")
        logger.info("=" * 50)
        
        # 1. Coletar dados de vendas
        sales_data = self.collect_sales_data()
        
        # 2. Coletar dados de afiliados  
        affiliates_data = self.collect_affiliates_data()
        
        # 3. Coletar dados do Facebook
        facebook_data = self.collect_facebook_data()
        
        # 4. Processar e calcular ROI
        result = self.process_and_calculate_roi(sales_data, affiliates_data, facebook_data)
        
        logger.info("=" * 50)
        logger.info("COLETA COMPLETA FINALIZADA")
        
        return result

# Instância global do coletor
imperio_collector = ImperioDataCollector()