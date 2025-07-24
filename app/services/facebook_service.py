import asyncio
import aiohttp
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import logging
from sqlalchemy.orm import Session
from ..database import SessionLocal
from ..models import FacebookAdsData
import os

logger = logging.getLogger(__name__)

class FacebookRateLimiter:
    """Rate limiter para API do Facebook com controle inteligente"""
    
    def __init__(self, max_calls_per_hour: int = 200):
        self.max_calls_per_hour = max_calls_per_hour
        self.calls_history = []
        self.last_reset = time.time()
        
    async def wait_if_needed(self):
        """Espera se necessário para respeitar rate limit"""
        now = time.time()
        
        # Remove chamadas antigas (mais de 1 hora)
        self.calls_history = [call_time for call_time in self.calls_history 
                             if now - call_time < 3600]
        
        # Se atingiu o limite, espera
        if len(self.calls_history) >= self.max_calls_per_hour:
            wait_time = 3600 - (now - self.calls_history[0])
            if wait_time > 0:
                logger.info(f"Rate limit atingido. Aguardando {wait_time:.2f} segundos...")
                await asyncio.sleep(wait_time)
                return await self.wait_if_needed()
        
        # Registra a chamada atual
        self.calls_history.append(now)

class FacebookAdsService:
    """Serviço otimizado para Facebook Ads com rate limiting"""
    
    def __init__(self, access_token: str):
        self.access_token = access_token
        self.rate_limiter = FacebookRateLimiter()
        self.base_url = "https://graph.facebook.com"
        self.api_versions = ["v18.0", "v17.0", "v16.0"]
        
    async def verify_token(self) -> bool:
        """Verifica se o token está válido"""
        try:
            await self.rate_limiter.wait_if_needed()
            
            async with aiohttp.ClientSession() as session:
                url = f"{self.base_url}/v18.0/me?access_token={self.access_token}"
                async with session.get(url) as response:
                    return response.status == 200
                    
        except Exception as e:
            logger.error(f"Erro ao verificar token: {e}")
            return False
    
    async def get_account_spend(self, account_id: str, session: aiohttp.ClientSession) -> float:
        """Obtém gasto de uma conta específica com fallback de versões da API"""
        
        if not account_id or account_id == 'act_':
            logger.warning(f"ID de conta inválido: {account_id}")
            return 0.0
            
        await self.rate_limiter.wait_if_needed()
        
        for api_version in self.api_versions:
            try:
                url = f"{self.base_url}/{api_version}/{account_id}/insights"
                params = {
                    "fields": "spend",
                    "date_preset": "today",
                    "access_token": self.access_token
                }
                
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        if "data" in data and len(data["data"]) > 0:
                            spend = float(data["data"][0].get("spend", 0))
                            logger.info(f"Gasto obtido para {account_id}: R$ {spend:.2f}")
                            return spend
                        else:
                            logger.info(f"Sem dados de gasto para {account_id}")
                            return 0.0
                            
                    elif response.status == 429:  # Rate limit
                        logger.warning("Rate limit atingido, aguardando...")
                        await asyncio.sleep(60)
                        continue
                        
                    elif "OAuthException" in await response.text():
                        logger.warning(f"Erro de autenticação na API {api_version}")
                        continue
                        
                    else:
                        error_text = await response.text()
                        logger.error(f"Erro na API {api_version}: {response.status} - {error_text[:100]}")
                        
            except Exception as e:
                logger.error(f"Erro ao buscar dados da conta {account_id} (API {api_version}): {e}")
                continue
        
        logger.warning(f"Todas as tentativas falharam para {account_id}, usando valor 0")
        return 0.0
    
    async def get_multiple_accounts_spend(self, account_ids: List[str]) -> Dict[str, float]:
        """Obtém gastos de múltiplas contas de forma assíncrona"""
        
        if not await self.verify_token():
            logger.error("Token inválido, retornando valores zero")
            return {account_id: 0.0 for account_id in account_ids}
        
        results = {}
        
        async with aiohttp.ClientSession() as session:
            # Criar tasks para todas as contas
            tasks = []
            for account_id in account_ids:
                if account_id and account_id != 'act_':
                    task = self.get_account_spend(account_id, session)
                    tasks.append((account_id, task))
            
            # Executar com controle de concorrência (máximo 5 simultâneas)
            semaphore = asyncio.Semaphore(5)
            
            async def controlled_request(account_id, task):
                async with semaphore:
                    return account_id, await task
            
            # Executar todas as requisições
            controlled_tasks = [controlled_request(account_id, task) 
                              for account_id, task in tasks]
            
            completed_tasks = await asyncio.gather(*controlled_tasks, return_exceptions=True)
            
            # Processar resultados
            for result in completed_tasks:
                if isinstance(result, Exception):
                    logger.error(f"Erro em task: {result}")
                else:
                    account_id, spend = result
                    results[account_id] = spend
        
        return results
    
    def save_to_database(self, account_spends: Dict[str, float]):
        """Salva dados no banco de dados"""
        db = SessionLocal()
        try:
            for account_id, spend in account_spends.items():
                fb_data = FacebookAdsData(
                    account_id=account_id,
                    spend=spend,
                    timestamp=datetime.now()
                )
                db.add(fb_data)
            
            db.commit()
            logger.info(f"Dados salvos no banco: {len(account_spends)} contas")
            
        except Exception as e:
            logger.error(f"Erro ao salvar no banco: {e}")
            db.rollback()
        finally:
            db.close()

class FacebookDataCollector:
    """Coletor principal de dados do Facebook com otimizações"""
    
    def __init__(self):
        self.access_token = os.getenv("FACEBOOK_ACCESS_TOKEN")
        self.facebook_service = FacebookAdsService(self.access_token)
        
        # Configurações de contas por canal
        self.account_configs = {
            "geral": os.getenv("FACEBOOK_ACCOUNT_IDS_GERAL", "").split(","),
            "instagram": os.getenv("FACEBOOK_ACCOUNT_IDS_INSTAGRAM", "").split(","),
            "grupo": os.getenv("FACEBOOK_ACCOUNT_IDS_GRUPO", "").split(",")
        }
        
        # Limpar IDs vazios
        for channel in self.account_configs:
            self.account_configs[channel] = [
                acc_id.strip() for acc_id in self.account_configs[channel] 
                if acc_id.strip() and acc_id.strip() != 'act_'
            ]
    
    async def collect_all_data(self) -> Dict[str, float]:
        """Coleta dados de todas as contas configuradas"""
        all_account_ids = []
        
        # Coletar todos os IDs de conta únicos
        for channel, account_ids in self.account_configs.items():
            all_account_ids.extend(account_ids)
        
        # Remover duplicatas
        unique_account_ids = list(set(all_account_ids))
        
        if not unique_account_ids:
            logger.warning("Nenhuma conta configurada")
            return {}
        
        logger.info(f"Coletando dados de {len(unique_account_ids)} contas...")
        
        # Coletar dados de forma assíncrona
        account_spends = await self.facebook_service.get_multiple_accounts_spend(unique_account_ids)
        
        # Salvar no banco
        self.facebook_service.save_to_database(account_spends)
        
        return account_spends
    
    async def get_channel_spend(self, channel: str) -> float:
        """Obtém gasto total de um canal específico"""
        if channel not in self.account_configs:
            logger.error(f"Canal não encontrado: {channel}")
            return 0.0
        
        account_ids = self.account_configs[channel]
        if not account_ids:
            logger.warning(f"Nenhuma conta configurada para o canal {channel}")
            return 0.0
        
        account_spends = await self.facebook_service.get_multiple_accounts_spend(account_ids)
        total_spend = sum(account_spends.values())
        
        logger.info(f"Gasto total do canal {channel}: R$ {total_spend:.2f}")
        return total_spend

# Instância global do coletor
facebook_collector = FacebookDataCollector()

async def collect_facebook_data():
    """Função principal para coletar dados do Facebook"""
    try:
        return await facebook_collector.collect_all_data()
    except Exception as e:
        logger.error(f"Erro na coleta de dados do Facebook: {e}")
        return {}