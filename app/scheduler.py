#!/usr/bin/env python3
"""
Scheduler para coletas automáticas a cada 30 minutos
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# Criar scheduler global
scheduler = AsyncIOScheduler()

async def scheduled_collection():
    """Executar coleta agendada"""
    try:
        from .database import get_db
        from .core.data_collector import imperio_collector
        from .core.data_manager import imperio_data_manager
        
        print(f"\n{'='*60}")
        print(f"COLETA AUTOMATICA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")
        
        # Log início da coleta
        logger.info("INICIANDO COLETA AUTOMATICA AGENDADA")
        
        # Executar coleta
        result = imperio_collector.execute_full_collection()
        
        if "error" not in result:
            # Salvar no banco
            db = next(get_db())
            saved = imperio_data_manager.save_collection_data(db, result)
            db.close()
            
            if saved:
                print("SUCESSO: Coleta automatica realizada com sucesso!")
                print(f"   ROI: {result['totals']['roi']:.2f}")
                print(f"   Vendas: R$ {result['totals']['sales']:,.2f}")
                print(f"   Gastos: R$ {result['totals']['spend']:,.2f}")
                print(f"   Orcamento: R$ {result['totals']['budget']:,.2f}")
                logger.info(f"COLETA AUTOMATICA CONCLUIDA - ROI: {result['totals']['roi']:.2f}")
            else:
                print("ERRO: Coleta realizada mas erro ao salvar")
                logger.error("Erro ao salvar dados da coleta automatica")
        else:
            print(f"ERRO: Erro na coleta automatica: {result['error']}")
            logger.error(f"Erro na coleta automatica: {result['error']}")
        
        print(f"Proxima coleta: {(datetime.now() + timedelta(minutes=30)).strftime('%H:%M:%S')}")
        print(f"{'='*60}")
            
    except Exception as e:
        logger.error(f"ERRO CRITICO na coleta agendada: {e}")
        print(f"ERRO CRITICO na coleta automatica: {e}")
        # Não deixar o scheduler quebrar por um erro
        try:
            # Tentar reagendar se houve erro
            print("Tentando manter scheduler ativo...")
        except:
            pass

def init_scheduler():
    """Inicializar scheduler com coleta a cada 30 minutos"""
    try:
        # Agendar coleta a cada 30 minutos
        scheduler.add_job(
            scheduled_collection,
            IntervalTrigger(minutes=30),
            id='coleta_30min',
            name='Coleta automática a cada 30 minutos',
            replace_existing=True,
            next_run_time=datetime.now() + timedelta(minutes=30)  # Primeira execução em 30 min
        )
        
        logger.info("Scheduler configurado: coleta a cada 30 minutos")
        print("Coleta automatica configurada: a cada 30 minutos")
        
        # Mostrar próxima execução
        job = scheduler.get_job('coleta_30min')
        if job:
            print(f"Proxima coleta agendada: {job.next_run_time.strftime('%d/%m/%Y %H:%M:%S')}")
        
        return True
        
    except Exception as e:
        logger.error(f"Erro ao configurar scheduler: {e}")
        print(f"Erro ao configurar coleta automatica: {e}")
        return False

def get_scheduler_info():
    """Obter informações do scheduler"""
    try:
        job = scheduler.get_job('coleta_30min')
        if job:
            return {
                "active": True,
                "interval_minutes": 30,
                "next_run": job.next_run_time.isoformat() if job.next_run_time else None,
                "job_name": job.name
            }
        else:
            return {
                "active": False,
                "interval_minutes": 30,
                "next_run": None,
                "job_name": None
            }
    except Exception as e:
        logger.error(f"Erro ao obter info do scheduler: {e}")
        return {
            "active": False,
            "error": str(e)
        }