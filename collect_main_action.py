#!/usr/bin/env python
"""Script para coletar dados da Ação Principal"""

import sys
sys.path.append('.')

import logging
from datetime import datetime
from core.services.main_action_collector import MainActionCollector
from core.database.base import get_db
from core.services.main_action_service import main_action_service

logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')

# Product ID da ação atual (conforme screenshot)
PRODUCT_ID = "6904ea540d0e097d618827fc"

print("="*60)
print("COLETANDO DADOS DA AÇÃO PRINCIPAL")
print("="*60)
print(f"\nProduct ID: {PRODUCT_ID}")
print(f"Timestamp: {datetime.now()}\n")

# Inicializar coletor
collector = MainActionCollector()

# 1. Obter token
print("1. Obtendo token de autenticação...")
token = collector._get_auth_token()
if not token:
    print("   [ERRO] Falha ao obter token!")
    sys.exit(1)
print("   [OK] Token obtido com sucesso")

# 2. Buscar detalhes do produto
print("\n2. Buscando detalhes do produto...")
product_details = collector.get_product_details(PRODUCT_ID, token)
if product_details.get('success'):
    data = product_details['data']
    print(f"   Nome: {data.get('name', 'N/A')}")
    print(f"   Status: {'Ativo' if data.get('active', False) else 'Finalizado'}")
else:
    print(f"   [ERRO] {product_details.get('error')}")

# 3. Buscar vendas por dia
print("\n3. Buscando vendas por dia...")
orders_result = collector.get_orders_by_day(PRODUCT_ID, token)
if orders_result.get('success'):
    data = orders_result['data']
    somas_por_dia = data.get('somasPorDia', [])
    total_vendas = data.get('total', 0)

    print(f"   Total de vendas: R$ {total_vendas:,.2f}")
    print(f"   Dias com vendas: {len(somas_por_dia)}")

    if somas_por_dia:
        print("\n   Detalhamento por dia:")
        for dia in somas_por_dia[:5]:  # Mostrar primeiros 5 dias
            data_str = dia.get('_id', 'N/A')
            valor = dia.get('totalPorDia', 0)
            ordens = dia.get('totalOrdensPorDia', 0)
            print(f"     {data_str}: R$ {valor:,.2f} ({ordens} pedidos)")
else:
    print(f"   [ERRO] {orders_result.get('error')}")

# 4. Coletar dados completos (integrado com Facebook)
print("\n4. Coletando dados completos (vendas + Facebook)...")
full_data = collector.collect_full_action_data(PRODUCT_ID)

if full_data.get('success'):
    data = full_data.get('data', {})
    totals = data.get('totals', {})

    print("\n   === RESUMO DA AÇÃO ===")
    print(f"   Nome: {data.get('name', 'N/A')}")
    print(f"   Prêmio: R$ {data.get('prize_value', 0):,.2f}")
    print(f"   Status: {'Ativo' if data.get('is_active') else 'Finalizado'}")
    print(f"   Período: {data.get('start_date', 'N/A')} até {data.get('end_date', 'N/A')}")

    print("\n   === TOTAIS ===")
    print(f"   Receita: R$ {totals.get('revenue', 0):,.2f}")
    print(f"   Custos FB: R$ {totals.get('fb_cost', 0):,.2f}")
    print(f"   Taxa 3%: R$ {totals.get('platform_fee', 0):,.2f}")
    print(f"   Lucro: R$ {totals.get('profit', 0):,.2f}")
    print(f"   ROI: {totals.get('roi', 0):.2f}%")

    # Detalhamento por dia
    orders_by_day = data.get('orders_by_day', [])
    fb_by_day = data.get('fb_by_day', [])

    if orders_by_day:
        print(f"\n   === VENDAS POR DIA ({len(orders_by_day)} dias) ===")
        for i, day in enumerate(orders_by_day[:3]):  # Primeiros 3 dias
            date_str = day.get('_id', 'N/A')
            revenue = day.get('totalPorDia', 0)
            orders = day.get('totalOrdensPorDia', 0)

            # Buscar custo FB do mesmo dia
            fb_cost = 0
            for fb in fb_by_day:
                if fb.get('date') == date_str:
                    fb_cost = fb.get('spend', 0)
                    break

            print(f"   {date_str}:")
            print(f"     - Vendas: R$ {revenue:,.2f} ({orders} pedidos)")
            print(f"     - FB Ads: R$ {fb_cost:,.2f}")
            print(f"     - Lucro dia: R$ {revenue - fb_cost - (revenue * 0.03):,.2f}")

    # 5. Salvar no banco de dados
    print("\n5. Salvando no banco de dados...")
    db = next(get_db())
    save_result = main_action_service.collect_and_save(db, PRODUCT_ID)

    if save_result.get('success'):
        print(f"   [OK] Dados salvos com sucesso! Action ID: {save_result.get('action_id')}")
    else:
        print(f"   [ERRO] {save_result.get('error')}")

    db.close()
else:
    print(f"   [ERRO] {full_data.get('error')}")

print("\n" + "="*60)
print("COLETA FINALIZADA")
print("="*60)