#!/usr/bin/env python3
"""
Teste completo da coleta de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.services.data_collector import ImperioDataCollector
import json

print("\n" + "=" * 60)
print("EXECUTANDO COLETA COMPLETA DE DADOS")
print("=" * 60)

# Criar instância do coletor
collector = ImperioDataCollector()

# Executar coleta completa
result = collector.execute_full_collection()

# Exibir resultados
print("\n" + "=" * 60)
print("RESULTADO DA COLETA")
print("=" * 60)

if "error" in result:
    print(f"\n[ERRO] {result['error']}")
else:
    # Totais
    totals = result.get("totals", {})
    print("\nTOTAIS GERAIS:")
    print(f"  Vendas: R$ {totals.get('sales', 0):.2f}")
    print(f"  Gastos: R$ {totals.get('spend', 0):.2f}")
    print(f"  ROI: {totals.get('roi', 0):.2f}")
    print(f"  Lucro: R$ {totals.get('profit', 0):.2f}")
    print(f"  Ordens: {totals.get('orders', 0)}")
    
    # Por canal
    channels = result.get("channels", {})
    
    print("\nPOR CANAL:")
    for channel_name, channel_data in channels.items():
        print(f"\n  {channel_name.upper()}:")
        print(f"    Vendas: R$ {channel_data.get('sales', 0):.2f}")
        print(f"    Gastos: R$ {channel_data.get('spend', 0):.2f}")
        print(f"    ROI: {channel_data.get('roi', 0):.2f}")
        print(f"    Lucro: R$ {channel_data.get('profit', 0):.2f}")

print("\n" + "=" * 60)
print("COLETA CONCLUIDA COM SUCESSO!")
print("=" * 60)