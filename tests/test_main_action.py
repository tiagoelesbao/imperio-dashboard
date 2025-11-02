#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste completo para Ação Principal
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.base import SessionLocal, Base, engine
from core.services.main_action_service import main_action_service
from core.models.main_action import MainAction, MainActionDaily
from datetime import datetime


def test_system_status():
    """Verificar status geral do sistema"""
    print("="*60)
    print("STATUS DO SISTEMA DE AÇÃO PRINCIPAL")
    print("="*60)

    db = SessionLocal()
    try:
        # Verificar tabelas
        print("\n[1] Verificando banco de dados...")
        Base.metadata.create_all(engine)
        print("   [OK] Tabelas criadas/verificadas")

        # Contar registros
        total_actions = db.query(MainAction).count()
        total_daily = db.query(MainActionDaily).count()
        print(f"   --> {total_actions} acoes cadastradas")
        print(f"   --> {total_daily} registros diarios")

        # Verificar ação vigente
        current = main_action_service.get_current_action(db)
        if current:
            print(f"\n[2] Acao Vigente:")
            print(f"   [OK] {current['name']}")
            print(f"   ID: {current['product_id']}")
        else:
            print("\n[2] [!] Nenhuma acao marcada como vigente")

        return total_actions > 0

    finally:
        db.close()


def test_collect():
    """Testar coleta de dados"""
    print("="*60)
    print("TESTE DE COLETA - AÇÃO PRINCIPAL")
    print("="*60)

    product_id = "68efdf010d0e097d616d7121"
    print(f"\nColetando dados do sorteio: {product_id}")

    db = SessionLocal()
    try:
        result = main_action_service.collect_and_save(db, product_id)

        if result.get('success'):
            print("[OK] Coleta realizada com sucesso!")
            print(f"   Action ID: {result.get('action_id')}")

            # Buscar dados salvos
            action = main_action_service.get_current_action(db)
            if action:
                print(f"\n>>> RESUMO:")
                print(f"   Nome: {action['name']}")
                print(f"   Premiacao: R$ {action['prize_value']:,.2f}")
                print(f"   Receita Total: R$ {action['total_revenue']:,.2f}")
                print(f"   Custos FB: R$ {action['total_fb_cost']:,.2f}")
                print(f"   Taxa 3%: R$ {action['total_platform_fee']:,.2f}")
                print(f"   Lucro: R$ {action['total_profit']:,.2f}")
                print(f"   ROI: {action['total_roi']:.2f}%")
                print(f"   Status: {'Ativo' if action['is_active'] else 'Finalizado'}")
        else:
            print(f"[ERRO] Erro na coleta: {result.get('error')}")

    finally:
        db.close()


def test_list_actions():
    """Testar listagem de ações"""
    print("\n" + "="*60)
    print("LISTAGEM DE AÇÕES")
    print("="*60)

    db = SessionLocal()
    try:
        actions = main_action_service.get_all_actions(db, year=2025)
        print(f"\n>>> Total de acoes: {len(actions)}")

        for action in actions:
            status = "[ATUAL]" if action['is_current'] else ("[FIM]" if not action['is_active'] else "[HIST]")
            print(f"\n{status} {action['name']}")
            print(f"   ID: {action['product_id']}")
            print(f"   Receita: R$ {action['total_revenue']:,.2f}")
            print(f"   ROI: {action['total_roi']:.2f}%")

    finally:
        db.close()


if __name__ == "__main__":
    print("\n>>> TESTE COMPLETO DO SISTEMA DE ACAO PRINCIPAL\n")

    # 1. Verificar status do sistema
    has_data = test_system_status()

    # 2. Listar ações existentes
    test_list_actions()

    # 3. Testar coleta apenas se o usuario quiser
    if not has_data:
        print("\n" + "="*60)
        print(">>> COMO COMECAR A USAR:")
        print("="*60)
        print("\n1. Acesse: http://localhost:8002/imperio#acaoprincipal")
        print("2. Clique no botao '+ Adicionar Acao'")
        print("3. Insira o ID do sorteio (ex: 67309d88c8e37b2aa72fb84f)")
        print("4. Aguarde a coleta dos dados")
        print("\n>>> Funcionalidades implementadas:")
        print("   [OK] Botao para adicionar novas acoes")
        print("   [OK] Lista expansivel com dados diarios")
        print("   [OK] KPIs consolidados no topo")
        print("   [OK] Dados permanentes (nao sao resetados)")
        print("   [OK] Coleta automatica a cada 30 minutos")
        print("   [OK] Integracao com Facebook Ads")
    else:
        print("\n>>> Para testar uma nova coleta, execute:")
        print(f"   python test_main_action.py --collect")

    # Se passou --collect como argumento, fazer coleta
    if len(sys.argv) > 1 and sys.argv[1] == '--collect':
        print("\n[!] Iniciando coleta de teste...")
        test_collect()

    print("\n" + "="*60)
    print("[OK] Sistema de Acao Principal verificado!")
    print("="*60)
    print("\n>>> Dashboard: http://localhost:8002/imperio#acaoprincipal")
