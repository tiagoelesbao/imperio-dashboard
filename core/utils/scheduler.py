#!/usr/bin/env python3
"""
Scheduler para coletas automáticas a cada 30 minutos
"""

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
import logging
from datetime import datetime, timedelta
import asyncio

logger = logging.getLogger(__name__)

# Criar scheduler global
scheduler = AsyncIOScheduler()

async def immediate_post_collection_capture():
    """Executar captura IMEDIATA após a coleta (sem delay)"""
    try:
        print("\n" + "="*60)
        print(f"CAPTURA IMEDIATA PÓS-COLETA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print("="*60)
        
        # Executar captura com WhatsApp IMEDIATAMENTE
        from core.services.capture_service import ImperioCaptureService
        capture_service = ImperioCaptureService()
        
        result = await capture_service.execute_capture(
            capture_type="all",
            send_whatsapp=True
        )
        
        if result.get("status") == "success":
            capture_result = result.get("capture_result", {})
            whatsapp_result = result.get("whatsapp_result", {})
            
            print("SUCESSO: Captura pós-coleta realizada!")
            print(f"   Screenshots: {capture_result.get('total_captured', 0)}")
            print(f"   WhatsApp: {'Enviado' if whatsapp_result and whatsapp_result.get('success') else 'Não enviado'}")
        else:
            print("ERRO: Captura pós-coleta falhou")
            if "capture_result" in result:
                for error in result["capture_result"].get("errors", []):
                    print(f"   {error}")
        
        print("="*60)
        
    except Exception as e:
        logger.error(f"Erro na captura pós-coleta: {e}")
        print(f"ERRO na captura pós-coleta: {e}")

async def scheduled_collection():
    """Executar coleta REAL agendada"""
    try:
        from core.services.data_collector import imperio_collector
        from core.services.data_manager import imperio_data_manager
        from core.database.base import get_db

        print(f"\n{'='*60}")
        print(f"COLETA AUTOMATICA REAL - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")

        # Log início da coleta
        logger.info("INICIANDO COLETA AUTOMATICA REAL")

        # Executar coleta REAL das APIs Facebook + Imperio
        result = imperio_collector.execute_full_collection()

        if "error" not in result:
            # Salvar dados reais no banco
            db = next(get_db())
            saved = imperio_data_manager.save_collection_data(db, result)
            db.close()

            if saved:
                print("SUCESSO: Coleta automatica REAL realizada com sucesso!")
                print(f"   ROI REAL: {result['totals']['roi']:.2f}")
                print(f"   Vendas REAIS: R$ {result['totals']['sales']:,.2f}")
                print(f"   Gastos REAIS: R$ {result['totals']['spend']:,.2f}")
                print(f"   Lucro REAL: R$ {result['totals']['profit']:,.2f}")
                print(f"   Orçamento: R$ {result['totals']['budget']:,.2f}")
                logger.info(f"COLETA AUTOMATICA REAL CONCLUIDA - ROI: {result['totals']['roi']:.2f}")

                # NÃO executar captura nas coletas agendadas - apenas nas coordenadas XX:01/31

            else:
                print("ERRO: Coleta real realizada mas erro ao salvar")
                logger.error("Erro ao salvar dados reais da coleta automatica")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            print(f"ERRO: Erro na coleta automatica real: {error_msg}")
            logger.error(f"Erro na coleta automatica real: {error_msg}")

        # Calcular próxima coleta (próximo XX:00 ou XX:30)
        now = datetime.now()
        if now.minute < 30:
            next_coleta = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_coleta = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

        print(f"Próxima coleta: {next_coleta.strftime('%d/%m/%Y %H:%M:%S')}")
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

async def scheduled_horapix_collection():
    """Executar coleta HORA DO PIX agendada"""
    try:
        from clients.imperio.services.horapix_service import horapix_service
        from core.database.base import get_db

        print(f"\n{'='*60}")
        print(f"COLETA HORA DO PIX - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")

        # Log início da coleta
        logger.info("INICIANDO COLETA HORA DO PIX")

        # Executar coleta Hora do Pix
        db = next(get_db())
        result = horapix_service.collect_and_save(db, fetch_details=False)
        db.close()

        if result.get('success'):
            data = result.get('data', {})
            totals = data.get('totals', {})

            print("SUCESSO: Coleta Hora do Pix realizada com sucesso!")
            print(f"   Total Sorteios: {totals.get('total_draws', 0)}")
            print(f"   Sorteios Ativos: {totals.get('active_draws', 0)}")
            print(f"   Receita: R$ {totals.get('total_revenue', 0):,.2f}")
            print(f"   Taxa (3%): R$ {totals.get('total_platform_fee', 0):,.2f}")
            print(f"   Lucro: R$ {totals.get('total_profit', 0):,.2f}")
            print(f"   ROI: {totals.get('total_roi', 0):.2f}%")
            logger.info(f"COLETA HORA DO PIX CONCLUIDA - {totals.get('total_draws', 0)} sorteios")
        else:
            error_msg = result.get('error', 'Erro desconhecido')
            print(f"ERRO: Erro na coleta Hora do Pix: {error_msg}")
            logger.error(f"Erro na coleta Hora do Pix: {error_msg}")

        # Calcular próxima coleta (próximo XX:00 ou XX:30)
        now = datetime.now()
        if now.minute < 30:
            next_coleta = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_coleta = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

        print(f"Próxima coleta Hora do Pix: {next_coleta.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")

    except Exception as e:
        logger.error(f"ERRO CRITICO na coleta Hora do Pix agendada: {e}")
        print(f"ERRO CRITICO na coleta Hora do Pix: {e}")
        # Não deixar o scheduler quebrar por um erro
        try:
            print("Tentando manter scheduler ativo...")
        except:
            pass

async def scheduled_full_collection():
    """Executar coleta COMPLETA: Sistema Principal + Hora do Pix + Acao Principal em SEQUENCIA"""
    try:
        print(f"\n{'='*70}")
        print(f"COLETA COMPLETA AUTOMATICA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"3 SISTEMAS: Imperio + Hora do Pix + Acao Principal")
        print(f"{'='*70}")

        # ==================================================
        # ETAPA 1: COLETA SISTEMA PRINCIPAL (Imperio + FB)
        # ==================================================
        from core.services.data_collector import imperio_collector
        from core.services.data_manager import imperio_data_manager
        from core.database.base import get_db

        print(f"\n[1/2] COLETANDO SISTEMA PRINCIPAL...")
        print("-" * 70)
        logger.info("INICIANDO COLETA SISTEMA PRINCIPAL")

        # Executar coleta REAL das APIs Facebook + Imperio
        result_imperio = imperio_collector.execute_full_collection()

        if "error" not in result_imperio:
            # Salvar dados reais no banco
            db = next(get_db())
            saved = imperio_data_manager.save_collection_data(db, result_imperio)
            db.close()

            if saved:
                print("[OK] SISTEMA PRINCIPAL: Coleta realizada com sucesso!")
                print(f"   ROI: {result_imperio['totals']['roi']:.2f}")
                print(f"   Vendas: R$ {result_imperio['totals']['sales']:,.2f}")
                print(f"   Gastos: R$ {result_imperio['totals']['spend']:,.2f}")
                print(f"   Lucro: R$ {result_imperio['totals']['profit']:,.2f}")
                logger.info(f"SISTEMA PRINCIPAL CONCLUIDO - ROI: {result_imperio['totals']['roi']:.2f}")
            else:
                print("[AVISO] SISTEMA PRINCIPAL: Erro ao salvar dados")
                logger.error("Erro ao salvar dados sistema principal")
        else:
            error_msg = result_imperio.get('error', 'Erro desconhecido')
            print(f"[ERRO] SISTEMA PRINCIPAL: {error_msg}")
            logger.error(f"Erro sistema principal: {error_msg}")

        # ==================================================
        # ETAPA 2: COLETA HORA DO PIX
        # ==================================================
        from clients.imperio.services.horapix_service import horapix_service

        print(f"\n[2/2] COLETANDO HORA DO PIX...")
        print("-" * 70)
        logger.info("INICIANDO COLETA HORA DO PIX")

        # Executar coleta Hora do Pix
        db = next(get_db())
        result_horapix = horapix_service.collect_and_save(db, fetch_details=False)
        db.close()

        if result_horapix.get('success'):
            data = result_horapix.get('data', {})
            totals = data.get('totals', {})

            print("[OK] HORA DO PIX: Coleta realizada com sucesso!")
            print(f"   Total Sorteios: {totals.get('total_draws', 0)}")
            print(f"   Sorteios Ativos: {totals.get('active_draws', 0)}")
            print(f"   Receita: R$ {totals.get('total_revenue', 0):,.2f}")
            print(f"   Taxa (3%): R$ {totals.get('total_platform_fee', 0):,.2f}")
            print(f"   Lucro: R$ {totals.get('total_profit', 0):,.2f}")
            print(f"   ROI: {totals.get('total_roi', 0):.2f}%")
            logger.info(f"HORA DO PIX CONCLUIDO - {totals.get('total_draws', 0)} sorteios")
        else:
            error_msg = result_horapix.get('error', 'Erro desconhecido')
            print(f"[ERRO] HORA DO PIX: {error_msg}")
            logger.error(f"Erro Hora do Pix: {error_msg}")

        # ==================================================
        # ETAPA 3: COLETA ACAO PRINCIPAL
        # ==================================================
        from core.services.main_action_service import main_action_service

        print(f"\n[3/3] COLETANDO ACAO PRINCIPAL...")
        print("-" * 70)
        logger.info("INICIANDO COLETA ACAO PRINCIPAL")

        # Buscar ação atual ou usar ID padrão
        db = next(get_db())
        current_action = main_action_service.get_current_action(db)
        product_id = current_action['product_id'] if current_action else '68efdf010d0e097d616d7121'

        # Executar coleta Ação Principal
        result_action = main_action_service.collect_and_save(db, product_id)
        db.close()

        if result_action.get('success'):
            # Buscar dados atualizados
            db = next(get_db())
            updated_action = main_action_service.get_current_action(db)
            db.close()

            if updated_action:
                print("[OK] ACAO PRINCIPAL: Coleta realizada com sucesso!")
                print(f"   Nome: {updated_action['name']}")
                print(f"   Receita: R$ {updated_action['total_revenue']:,.2f}")
                print(f"   Custos FB: R$ {updated_action['total_fb_cost']:,.2f}")
                print(f"   Lucro: R$ {updated_action['total_profit']:,.2f}")
                print(f"   ROI: {updated_action['total_roi']:.2f}%")
                logger.info(f"ACAO PRINCIPAL CONCLUIDA - ROI: {updated_action['total_roi']:.2f}%")
            else:
                print("[OK] ACAO PRINCIPAL: Dados coletados")
        else:
            error_msg = result_action.get('error', 'Erro desconhecido')
            print(f"[ERRO] ACAO PRINCIPAL: {error_msg}")
            logger.error(f"Erro Acao Principal: {error_msg}")

        # ==================================================
        # RESUMO FINAL
        # ==================================================
        print(f"\n{'='*70}")
        print("COLETA COMPLETA FINALIZADA (3 SISTEMAS)")
        print(f"{'='*70}")

        # Calcular próxima coleta (próximo XX:00 ou XX:30)
        now = datetime.now()
        if now.minute < 30:
            next_coleta = now.replace(minute=30, second=0, microsecond=0)
        else:
            next_coleta = (now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1))

        print(f"Próxima coleta completa: {next_coleta.strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*70}\n")

    except Exception as e:
        logger.error(f"ERRO CRITICO na coleta completa agendada: {e}")
        print(f"[ERRO CRITICO] Falha na coleta completa: {e}")
        # Não deixar o scheduler quebrar por um erro
        try:
            print("Tentando manter scheduler ativo...")
        except:
            pass

async def scheduled_capture():
    """Executar captura agendada SOMENTE após coleta bem-sucedida"""
    try:
        from core.services.capture_service_fast import ImperioCaptureServiceFast
        from core.database.base import SessionLocal
        from core.models.base import CollectionLog

        print(f"\n{'='*60}")
        print(f"CAPTURA AUTOMATICA - {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")

        # VERIFICAR SE HOUVE COLETA RECENTE (últimos 5 minutos)
        db = SessionLocal()
        try:
            last_collection = db.query(CollectionLog).order_by(
                CollectionLog.collection_time.desc()
            ).first()

            if not last_collection:
                print("BLOQUEADO: Nenhuma coleta encontrada - captura cancelada")
                print("   Execute primeiro uma coleta manual ou aguarde XX:00/XX:30")
                db.close()
                return

            # Verificar se coleta foi há menos de 5 minutos
            time_diff = datetime.now() - last_collection.collection_time
            if time_diff.total_seconds() > 300:  # 5 minutos
                print(f"BLOQUEADO: Última coleta há {int(time_diff.total_seconds()/60)} minutos")
                print("   Captura cancelada - dados podem estar desatualizados")
                db.close()
                return

            print(f"OK: Coleta recente encontrada ({int(time_diff.total_seconds())}s atrás)")
            print(f"   ROI: {last_collection.general_roi:.2f}")
            print(f"   Vendas: R$ {last_collection.total_sales:,.2f}")

        except Exception as e:
            print(f"ERRO: Falha ao verificar coleta recente: {e}")
            db.close()
            return
        finally:
            db.close()

        logger.info("INICIANDO CAPTURA AUTOMATICA OTIMIZADA (coleta validada)")

        # Executar captura OTIMIZADA
        service = ImperioCaptureServiceFast()
        result = await service.capture_screenshots_fast('screenshots')

        if result and result.get('success'):
            total_captured = result.get('total_captured', 0)
            print(f"[OK] Captura automatica OTIMIZADA: {total_captured} arquivos")

            # Enviar via WhatsApp
            files = result.get('files', [])
            if files:
                whatsapp_result = await service.send_to_whatsapp_fast(files[:3])
                if whatsapp_result and whatsapp_result.get('success'):
                    sent = whatsapp_result.get('total_sent', 0)
                    print(f"[OK] WhatsApp automatico: {sent} arquivos enviados")
                else:
                    print("[AVISO] WhatsApp automatico: falha no envio")
        else:
            print("[ERRO] Captura automatica falhou")

        print(f"Próxima captura: {(datetime.now().replace(minute=1 if datetime.now().minute < 31 else 31, second=0) + timedelta(hours=1 if datetime.now().minute >= 31 else 0)).strftime('%d/%m/%Y %H:%M:%S')}")
        print(f"{'='*60}")

    except Exception as e:
        logger.error(f"ERRO CRITICO na captura agendada: {e}")
        print(f"ERRO CRITICO na captura automatica: {e}")

def init_scheduler():
    """Inicializar scheduler com coleta COMPLETA (Sistema + Hora do Pix em sequência)"""
    try:
        # Agendar coleta COMPLETA nos minutos 00 e 30 de cada hora
        # Executa 3 sistemas em SEQUÊNCIA para evitar conflitos: Imperio + Hora do Pix + Acao Principal
        scheduler.add_job(
            scheduled_full_collection,
            CronTrigger(minute='0,30'),
            id='coleta_completa_horarios_fixos',
            name='Coleta Completa: 3 Sistemas (XX:00 e XX:30)',
            replace_existing=True
        )

        # CAPTURAS DESABILITADAS - causam crash do servidor
        # scheduler.add_job(
        #     scheduled_capture,
        #     CronTrigger(minute='1,31'),
        #     id='captura_telas',
        #     name='Captura automática de telas (XX:01 e XX:31)',
        #     replace_existing=True
        # )

        logger.info("Scheduler configurado: Coleta COMPLETA (3 Sistemas) XX:00/XX:30")
        print("Automações configuradas:")
        print("- Coleta COMPLETA: XX:00 e XX:30 (3 sistemas em sequência)")
        print("  └─ [1/3] Sistema Principal (Imperio + Facebook)")
        print("  └─ [2/3] Hora do Pix (sorteios + taxa 3%)")
        print("  └─ [3/3] Ação Principal (sorteio vigente)")
        print("- Capturas: DESABILITADAS (usar bat separado)")

        # Mostrar próximas execuções
        try:
            coleta_job = scheduler.get_job('coleta_completa_horarios_fixos')

            if coleta_job and hasattr(coleta_job, 'next_run_time') and coleta_job.next_run_time:
                print(f"\nPróxima coleta completa: {coleta_job.next_run_time.strftime('%d/%m/%Y %H:%M:%S')}")
            else:
                print("\nPróxima coleta completa: Agendada para XX:00 e XX:30")

            print("Capturas: Use imperio_capture_send.bat manualmente")
        except Exception as e:
            logger.warning(f"Erro ao obter próximas execuções: {e}")
            print("Agendamentos configurados - próximas execuções calculadas automaticamente")

        return True

    except Exception as e:
        logger.error(f"Erro ao configurar scheduler: {e}")
        print(f"Erro ao configurar automações: {e}")
        return False

def trigger_first_collection_and_capture():
    """Sistema pronto - primeira captura será feita pelo scheduler automático"""
    from datetime import datetime, timedelta
    
    now = datetime.now()
    if now.minute < 30:
        next_coleta = now.replace(minute=30, second=0, microsecond=0)
        next_captura = now.replace(minute=31, second=0, microsecond=0)
    else:
        next_coleta = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        next_captura = (now + timedelta(hours=1)).replace(minute=1, second=0, microsecond=0)
    
    print(f"\n✅ SERVIDOR IMPERIO PRONTO!")
    print(f"   📊 Coletas automáticas: XX:00 e XX:30")
    print(f"   📸 Capturas: Use imperio_capture_send.bat")
    print(f"   ⏰ Próxima coleta: {next_coleta.strftime('%H:%M')}")
    print(f"   📱 Próxima captura: {next_captura.strftime('%H:%M')}")
    print(f"   🌐 Dashboard: http://localhost:8002/imperio")
    print(f"   🔄 Sistema estável rodando 24/7")
    
    return None

def trigger_first_collection_and_capture_OLD():
    """Executar primeira captura após inicialização do servidor"""
    import asyncio
    import time
    from core.services.capture_service_fast import ImperioCaptureServiceFast
    
    async def execute_first_capture():
        """Executar primeira captura de forma assíncrona"""
        try:
            print("📸 Aguardando servidor estar completamente pronto...")
            # Aguardar 15 segundos para garantir que servidor está respondendo
            await asyncio.sleep(15)
            
            print("📸 Executando primeira captura OTIMIZADA (servidor confirmado ativo)...")
            
            # Usar o serviço OTIMIZADO
            service = ImperioCaptureServiceFast()
            
            # Executar captura OTIMIZADA
            result = await service.capture_screenshots_fast('screenshots')
            
            if result and result.get('success'):
                total_captured = result.get('total_captured', 0)
                print(f"   ✅ Primeira captura OTIMIZADA executada com sucesso!")
                print(f"   ✅ {total_captured} capturas realizadas")
                
                # Tentar enviar via WhatsApp
                files = result.get('files', [])
                if files:
                    print("   📱 Enviando para WhatsApp...")
                    whatsapp_result = await service.send_to_whatsapp_fast(files[:3])
                    if whatsapp_result and whatsapp_result.get('success'):
                        sent = whatsapp_result.get('total_sent', 0)
                        print(f"   ✅ WhatsApp: {sent} arquivos enviados")
                    else:
                        print("   ⚠️ WhatsApp não enviado (QR Code necessário?)")
                else:
                    print("   ⚠️ Nenhum arquivo para enviar")
            else:
                print(f"   ❌ Erro na primeira captura: {result.get('error', 'Erro desconhecido') if result else 'Sem resultado'}")
                
        except Exception as e:
            logger.error(f"Erro na primeira captura: {e}")
            print(f"   ❌ Erro na primeira captura: {e}")
    
    # Executar captura em background
    try:
        asyncio.create_task(execute_first_capture())
    except RuntimeError:
        # Se não há loop de eventos, criar um novo
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(execute_first_capture())
        finally:
            loop.close()
    
    # Calcular próximos horários
    now = datetime.now()
    if now.minute < 1:
        next_coleta = now.replace(minute=0, second=0, microsecond=0) + timedelta(hours=1)
        next_captura = now.replace(minute=1, second=0, microsecond=0)
    elif now.minute < 30:
        next_coleta = now.replace(minute=30, second=0, microsecond=0)
        next_captura = now.replace(minute=31, second=0, microsecond=0)
    elif now.minute < 31:
        next_captura = now.replace(minute=31, second=0, microsecond=0)
        next_coleta = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
    else:
        next_coleta = (now + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)
        next_captura = (now + timedelta(hours=1)).replace(minute=1, second=0, microsecond=0)
    
    print(f"\n✅ SISTEMA PRONTO!")
    print(f"   📊 Primeira coleta: CONCLUÍDA no reset")
    print(f"   📸 Primeira captura: EM EXECUÇÃO...")
    print(f"   ⏰ Próxima coleta: {next_coleta.strftime('%H:%M')}")
    print(f"   📱 Próxima captura: {next_captura.strftime('%H:%M')}")
    print(f"   🔄 Sistema em modo automático")
    
    return None

def get_scheduler_info():
    """Obter informações do scheduler"""
    try:
        coleta_completa_job = scheduler.get_job('coleta_completa_horarios_fixos')
        captura_job = scheduler.get_job('captura_telas')

        if coleta_completa_job:
            # Extrair next_run_time com segurança
            next_coleta_completa = None
            next_captura = None

            try:
                if hasattr(coleta_completa_job, 'next_run_time') and coleta_completa_job.next_run_time:
                    next_coleta_completa = coleta_completa_job.next_run_time.isoformat()
            except:
                pass

            try:
                if captura_job and hasattr(captura_job, 'next_run_time') and captura_job.next_run_time:
                    next_captura = captura_job.next_run_time.isoformat()
            except:
                pass

            return {
                "active": True,
                "schedule_type": "cron",
                "coleta_completa_schedule": "XX:00 e XX:30 (Sistema + Hora do Pix)",
                "captura_schedule": "XX:01 e XX:31",
                "next_coleta_completa": next_coleta_completa,
                "next_captura": next_captura,
                "coleta_completa_job_name": coleta_completa_job.name,
                "captura_job_name": captura_job.name if captura_job else None
            }
        else:
            return {
                "active": False,
                "schedule_type": "cron",
                "next_coleta_completa": None,
                "next_captura": None,
                "job_name": None
            }
    except Exception as e:
        logger.error(f"Erro ao obter info do scheduler: {e}")
        return {
            "active": False,
            "error": str(e)
        }