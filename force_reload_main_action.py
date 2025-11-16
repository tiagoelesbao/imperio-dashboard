#!/usr/bin/env python
"""Script para forçar atualização de dados e recoletar Ação Principal"""

import sys
sys.path.append('.')

from datetime import datetime
from core.services.main_action_collector import MainActionCollector
from core.database.base import get_db
from core.services.main_action_service import main_action_service

print("="*60)
print("FORÇANDO RECOLETA DA AÇÃO PRINCIPAL")
print("="*60)
print(f"\nTimestamp: {datetime.now()}")

PRODUCT_ID = "6916292bf6051e4133d86ef9"

print(f"\n1. Coletando dados frescos para Product ID: {PRODUCT_ID}")

db = next(get_db())

# Forçar coleta e salvamento
result = main_action_service.collect_and_save(db, PRODUCT_ID)

if result.get('success'):
    print(f"   [OK] Dados coletados e salvos com sucesso!")
    print(f"   Action ID: {result.get('action_id')}")

    # Buscar e mostrar detalhes
    action_id = result.get('action_id')
    details = main_action_service.get_action_details(db, action_id)

    if details:
        daily = details.get('daily_records', [])
        print(f"\n2. Verificando dados salvos:")
        print(f"   - Nome: {details.get('name')}")
        print(f"   - Receita Total: R$ {details.get('total_revenue', 0):,.2f}")
        print(f"   - ROI Total: {details.get('total_roi', 0):.2f}%")
        print(f"   - Registros diários: {len(daily)}")

        if daily:
            print(f"\n   Dados diários:")
            for day in daily:
                print(f"     {day.get('date')}: R$ {day.get('daily_revenue', 0):,.2f} ({day.get('daily_orders', 0)} pedidos)")
else:
    print(f"   [ERRO] {result.get('error')}")

db.close()

print("\n3. Para testar no frontend:")
print("   1. Abra: http://localhost:8002/imperio#acaoprincipal")
print("   2. Clique na barra da ação para expandir")
print("   3. A tabela de dados diários deve aparecer")
print("\n   Se não aparecer:")
print("   - Abra o console do navegador (F12)")
print("   - Veja se há erros JavaScript")
print("   - Tente recarregar a página com Ctrl+F5")

print("\n" + "="*60)