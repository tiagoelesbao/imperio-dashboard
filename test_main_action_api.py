#!/usr/bin/env python
"""Script para testar API da Ação Principal"""

import requests
import json
from datetime import datetime

# Base URL do servidor
BASE_URL = "http://localhost:8002"

print("="*60)
print("TESTANDO ENDPOINTS DA AÇÃO PRINCIPAL")
print("="*60)

# 1. Testar /api/main-action/current
print("\n1. Testando /api/main-action/current")
print("-" * 40)

url = BASE_URL + "/api/main-action/current"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    if data.get('status') == 'success':
        action_data = data.get('data', {})

        print(f"[OK] Status: {response.status_code}")
        print(f"\nAção Atual:")
        print(f"  ID: {action_data.get('id')}")
        print(f"  Product ID: {action_data.get('product_id')}")
        print(f"  Nome: {action_data.get('name')}")
        print(f"  Prêmio: R$ {action_data.get('prize_value', 0):,.2f}")
        print(f"  Status: {'Ativo' if action_data.get('is_active') else 'Finalizado'}")
        print(f"\nTotais:")
        print(f"  Receita: R$ {action_data.get('total_revenue', 0):,.2f}")
        print(f"  Custos FB: R$ {action_data.get('total_fb_cost', 0):,.2f}")
        print(f"  Taxa 3%: R$ {action_data.get('total_platform_fee', 0):,.2f}")
        print(f"  Lucro: R$ {action_data.get('total_profit', 0):,.2f}")
        print(f"  ROI: {action_data.get('total_roi', 0):.2f}%")
    else:
        print(f"[INFO] {data.get('message', 'Sem dados')}")
else:
    print(f"[ERRO] Status: {response.status_code}")

# 2. Testar /api/main-action/all
print("\n2. Testando /api/main-action/all")
print("-" * 40)

url = BASE_URL + "/api/main-action/all"
response = requests.get(url)

if response.status_code == 200:
    data = response.json()

    if data.get('status') == 'success':
        all_data = data.get('data', {})
        actions = all_data.get('actions', [])
        yearly = all_data.get('yearly_summary', {})

        print(f"[OK] Status: {response.status_code}")
        print(f"\nTotal de Ações: {len(actions)}")

        if actions:
            print("\nAcoes encontradas:")
            for action in actions:
                status = "[Vigente]" if action.get('is_current') else "         "
                print(f"  {status} {action.get('name', 'N/A')}")
                print(f"      Product ID: {action.get('product_id')}")
                print(f"      ROI: {action.get('total_roi', 0):.2f}%")

        if yearly:
            print("\nResumo Anual:")
            print(f"  Receita Total: R$ {yearly.get('total_revenue', 0):,.2f}")
            print(f"  Custos FB Total: R$ {yearly.get('total_fb_cost', 0):,.2f}")
            print(f"  Lucro Total: R$ {yearly.get('total_profit', 0):,.2f}")
            print(f"  ROI Médio: {yearly.get('avg_roi', 0):.2f}%")
else:
    print(f"[ERRO] Status: {response.status_code}")

# 3. Testar /api/main-action/{id}/details
if 'action_data' in locals() and action_data.get('id'):
    action_id = action_data['id']
    print(f"\n3. Testando /api/main-action/{action_id}/details")
    print("-" * 40)

    url = BASE_URL + f"/api/main-action/{action_id}/details"
    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        if data.get('status') == 'success':
            details = data.get('data', {})
            daily_records = details.get('daily_records', [])

            print(f"[OK] Status: {response.status_code}")
            print(f"\nDetalhes da Ação:")
            print(f"  Nome: {details.get('name')}")
            print(f"  Registros diários: {len(daily_records)}")

            if daily_records:
                print("\n  Vendas por dia:")
                for day in daily_records[:5]:  # Primeiros 5 dias
                    print(f"    {day.get('date')}:")
                    print(f"      - Vendas: R$ {day.get('daily_revenue', 0):,.2f}")
                    print(f"      - FB Ads: R$ {day.get('daily_fb_cost', 0):,.2f}")
                    print(f"      - Lucro: R$ {day.get('daily_profit', 0):,.2f}")
                    print(f"      - ROI: {day.get('daily_roi', 0):.2f}%")
    else:
        print(f"[ERRO] Status: {response.status_code}")
else:
    print("\n3. Pulando teste de details (sem action_id)")

print("\n" + "="*60)
print("TESTE FINALIZADO")
print("="*60)

print("\nPara visualizar no frontend:")
print(f"Acesse: {BASE_URL}/imperio#acaoprincipal")
print("\nOs dados devem aparecer na interface com:")
print("- Card principal com totais")
print("- Tabela expansível com vendas por dia")
print("- Integração com custos do Facebook Ads")

print("\n" + "="*60)