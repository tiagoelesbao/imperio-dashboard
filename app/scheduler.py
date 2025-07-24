import asyncio
import schedule
import time
import logging
from datetime import datetime, timedelta
from typing import Optional
import os
from .services.data_collector import run_data_collection

logger = logging.getLogger(__name__)

class DataScheduler:
    """Agendador otimizado para coleta de dados"""
    
    def __init__(self):
        self.collection_interval = int(os.getenv("COLLECTION_INTERVAL_MINUTES", "30"))
        self.max_retries = int(os.getenv("MAX_RETRIES", "3"))
        self.retry_delay = int(os.getenv("RETRY_DELAY_SECONDS", "60"))
        self.is_running = False
        self.last_successful_run: Optional[datetime] = None
        self.consecutive_failures = 0
    
    async def run_collection_with_retry(self):
        """Executa coleta de dados com retry automático"""
        attempt = 0
        
        while attempt < self.max_retries:
            try:
                logger.info(f"Iniciando coleta de dados (tentativa {attempt + 1}/{self.max_retries})")
                
                await run_data_collection()
                
                # Sucesso
                self.last_successful_run = datetime.now()
                self.consecutive_failures = 0
                logger.info("Coleta de dados concluída com sucesso")
                return
                
            except Exception as e:
                attempt += 1
                self.consecutive_failures += 1
                
                logger.error(f"Erro na coleta (tentativa {attempt}/{self.max_retries}): {e}")
                
                if attempt < self.max_retries:
                    logger.info(f"Aguardando {self.retry_delay} segundos para nova tentativa...")
                    await asyncio.sleep(self.retry_delay)
                else:
                    logger.error("Todas as tentativas de coleta falharam")
                    
                    # Se muitas falhas consecutivas, aumentar intervalo
                    if self.consecutive_failures >= 3:
                        logger.warning("Muitas falhas consecutivas, aumentando intervalo temporariamente")
    
    def schedule_collection(self):
        """Agenda coleta de dados a cada N minutos"""
        logger.info(f"Agendando coleta de dados a cada {self.collection_interval} minutos")
        
        # Agendar para minutos específicos (0 e 30)
        if self.collection_interval == 30:
            schedule.every().hour.at(":00").do(self._run_async_job)
            schedule.every().hour.at(":30").do(self._run_async_job)
        else:
            # Para outros intervalos, usar every N minutes
            schedule.every(self.collection_interval).minutes.do(self._run_async_job)
    
    def _run_async_job(self):
        """Wrapper para executar job assíncrono"""
        if self.is_running:
            logger.warning("Coleta anterior ainda em execução, pulando...")
            return
        
        self.is_running = True
        try:
            asyncio.run(self.run_collection_with_retry())
        finally:
            self.is_running = False
    
    async def run_scheduler(self):
        """Executa o agendador principal"""
        logger.info("Iniciando agendador de coleta de dados")
        
        # Executar coleta inicial
        await self.run_collection_with_retry()
        
        # Configurar agendamento
        self.schedule_collection()
        
        # Loop principal
        while True:
            schedule.run_pending()
            await asyncio.sleep(10)  # Verificar a cada 10 segundos
    
    def get_status(self) -> dict:
        """Retorna status do agendador"""
        return {
            "is_running": self.is_running,
            "last_successful_run": self.last_successful_run.isoformat() if self.last_successful_run else None,
            "consecutive_failures": self.consecutive_failures,
            "collection_interval_minutes": self.collection_interval,
            "next_scheduled_run": self._get_next_run_time()
        }
    
    def _get_next_run_time(self) -> Optional[str]:
        """Calcula próximo horário de execução"""
        now = datetime.now()
        
        if self.collection_interval == 30:
            # Próximo horário: xx:00 ou xx:30
            minutes = now.minute
            if minutes < 30:
                next_run = now.replace(minute=30, second=0, microsecond=0)
            else:
                next_run = now.replace(hour=now.hour + 1, minute=0, second=0, microsecond=0)
        else:
            # Calcular baseado no intervalo
            minutes_to_add = self.collection_interval - (now.minute % self.collection_interval)
            next_run = now.replace(second=0, microsecond=0) + timedelta(minutes=minutes_to_add)
        
        return next_run.isoformat()

# Instância global do agendador
scheduler = DataScheduler()

async def start_scheduler():
    """Inicia o agendador"""
    await scheduler.run_scheduler()

def get_scheduler_status():
    """Obtém status do agendador"""
    return scheduler.get_status()