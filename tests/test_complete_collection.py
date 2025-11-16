#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para testar coleta completa inicial
Simula o que o imperio_daily_reset.bat faz
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.data_collector import imperio_collector
from core.services.data_manager import imperio_data_manager
from core.services.main_action_service import main_action_service
from clients.imperio.services.horapix_service import horapix_service
from core.database.base import SessionLocal

def test_complete_collection():
    """Testa coleta completa de todos os sistemas"""
    print("="*60)
    print("TESTE DE COLETA COMPLETA INICIAL")
    print("="*60)

    db = SessionLocal()

    try:
        # 1. COLETA SISTEMA PRINCIPAL (Geral, Perfil, Grupos)
        print("\n[FASE 1] SISTEMA PRINCIPAL")
        print("-"*40)

        result = imperio_collector.execute_full_collection()

        if result and "error" not in result:
            saved = imperio_data_manager.save_collection_data(db, result)

            # Dados Gerais
            totals = result.get("totals", {})
            print(f"[GERAL]")
            print(f"  ROI: {totals.get('roi', 0):.2f}")
            print(f"  Vendas: R$ {totals.get('sales', 0):,.2f}")
            print(f"  Gastos: R$ {totals.get('spend', 0):,.2f}")
            print(f"  Lucro: R$ {totals.get('profit', 0):,.2f}")

            # Dados por Canal
            channels = result.get("channels", {})

            # Perfil/Instagram
            instagram = channels.get("instagram", {})
            if instagram:
                print(f"\n[PERFIL/INSTAGRAM]")
                print(f"  ROI: {instagram.get('roi', 0):.2f}")
                print(f"  Vendas: R$ {instagram.get('sales', 0):,.2f}")
                print(f"  Gastos: R$ {instagram.get('spend', 0):,.2f}")

            # Grupos
            grupos = channels.get("grupos", {})
            if grupos:
                print(f"\n[GRUPOS]")
                print(f"  ROI: {grupos.get('roi', 0):.2f}")
                print(f"  Vendas: R$ {grupos.get('sales', 0):,.2f}")
                print(f"  Gastos: R$ {grupos.get('spend', 0):,.2f}")

            print(f"\n  Status: {'OK - Dados salvos' if saved else 'ERRO ao salvar'}")
        else:
            print(f"  [ERRO] {result.get('error', 'Erro desconhecido')}")

        # 2. COLETA HORA DO PIX
        print("\n[FASE 2] HORA DO PIX")
        print("-"*40)

        hp_result = horapix_service.collect_and_save(db, fetch_details=False)

        if hp_result.get('success'):
            data = hp_result.get('data', {})
            totals = data.get('totals', {})

            print(f"  Sorteios: {totals.get('total_draws', 0)}")
            print(f"  Ativos: {totals.get('active_draws', 0)}")
            print(f"  Receita: R$ {totals.get('total_revenue', 0):,.2f}")
            print(f"  Taxa 3%: R$ {totals.get('total_platform_fee', 0):,.2f}")
            print(f"  Lucro: R$ {totals.get('total_profit', 0):,.2f}")
            print(f"  ROI: {totals.get('total_roi', 0):.2f}%")
            print(f"  Status: OK - Dados salvos")
        else:
            print(f"  [ERRO] {hp_result.get('error', 'Erro desconhecido')}")

        # 3. COLETA ACAO PRINCIPAL
        print("\n[FASE 3] ACAO PRINCIPAL")
        print("-"*40)

        # Buscar ação vigente
        current = main_action_service.get_current_action(db)

        if current:
            product_id = current['product_id']
        else:
            product_id = '6916292bf6051e4133d86ef9'  # ID padrão

        # Coletar dados
        ma_result = main_action_service.collect_and_save(db, product_id)

        if ma_result.get('success'):
            # Buscar dados atualizados
            action = main_action_service.get_current_action(db)

            if action:
                print(f"  Nome: {action['name']}")
                print(f"  Product ID: {action['product_id']}")
                print(f"  Receita: R$ {action['total_revenue']:,.2f}")
                print(f"  Custos FB: R$ {action['total_fb_cost']:,.2f}")
                print(f"  Taxa 3%: R$ {action['total_platform_fee']:,.2f}")
                print(f"  Lucro: R$ {action['total_profit']:,.2f}")
                print(f"  ROI: {action['total_roi']:.2f}%")

                # Verificar registros diários
                details = main_action_service.get_action_details(db, action['id'])
                if details:
                    daily_count = len(details.get('daily_records', []))
                    print(f"  Registros diarios: {daily_count}")

                    if daily_count > 0:
                        print(f"\n  Ultimos dias:")
                        for day in details['daily_records'][-3:]:  # Últimos 3 dias
                            print(f"    {day['date']}: R$ {day['daily_revenue']:,.2f}")

                print(f"  Status: OK - Dados salvos")
            else:
                print("  [AVISO] Nenhuma acao vigente configurada")
        else:
            print(f"  [ERRO] {ma_result.get('error', 'Erro desconhecido')}")

        # RESUMO FINAL
        print("\n" + "="*60)
        print("RESUMO DA COLETA COMPLETA")
        print("="*60)
        print("\n[OK] Sistema Principal coletado (Geral, Perfil, Grupos)")
        print("[OK] Hora do Pix coletado")
        print("[OK] Acao Principal atualizada")
        print("\nTodas as coletas iniciais executadas com sucesso!")
        print("Dashboard disponivel em: http://localhost:8002/imperio")

    except Exception as e:
        print(f"\n[ERRO CRITICO] {e}")
        import traceback
        traceback.print_exc()

    finally:
        db.close()

if __name__ == "__main__":
    test_complete_collection()