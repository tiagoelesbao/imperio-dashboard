#!/usr/bin/env python
"""Script para verificar se a correção está aplicada no código em execução."""

import sys
sys.path.append('.')

print("="*60)
print("VERIFICANDO SE A CORREÇÃO FOI APLICADA")
print("="*60)

# Importar o serviço diretamente
from clients.imperio.services.imperio_database_service import ImperioDatabaseService

# Ler o código atual do arquivo
with open('clients/imperio/services/imperio_database_service.py', 'r') as f:
    content = f.read()

# Verificar qual product_id está no código
old_product_id = '6904ea540d0e097d618827fc'
new_product_id = '68ff78f80d0e097d617d472b'

count_old = content.count(old_product_id)
count_new = content.count(new_product_id)

print(f"\nAnálise do arquivo imperio_database_service.py:")
print(f"  - Ocorrências do product_id ANTIGO ({old_product_id}): {count_old}")
print(f"  - Ocorrências do product_id NOVO ({new_product_id}): {count_new}")

if count_old == 0 and count_new > 0:
    print("\n[OK] O código FOI corrigido! Product_id atualizado.")
else:
    print("\n[X] O código NÃO foi corrigido corretamente.")

# Testar diretamente o serviço
print("\n" + "="*60)
print("TESTANDO SERVIÇO DIRETAMENTE (sem API)")
print("="*60)

service = ImperioDatabaseService()

# Testar função geral
print("\nTestando get_looker_geral_data()...")
data = service.get_looker_geral_data()
print(f"  - Date Range: {data.get('dateRange')}")
print(f"  - Cumulative Data: {len(data.get('cumulativeData', []))} registros")
print(f"  - Interval Data: {len(data.get('intervalData', []))} registros")

if data.get('cumulativeData'):
    print("  [OK] Dados encontrados!")
    first = data['cumulativeData'][0]
    print(f"    Primeiro registro: {first.get('dateTime')} - ROI: {first.get('roi'):.2f}")
else:
    print("  [!] Nenhum dado retornado")

# Testar função perfil
print("\nTestando get_looker_perfil_data()...")
data = service.get_looker_perfil_data()
print(f"  - Date Range: {data.get('dateRange')}")
print(f"  - Cumulative Data: {len(data.get('cumulativeData', []))} registros")

if data.get('cumulativeData'):
    print("  [OK] Dados encontrados!")
else:
    print("  [!] Nenhum dado retornado")

# Testar função grupos
print("\nTestando get_looker_grupos_data()...")
data = service.get_looker_grupos_data()
print(f"  - Date Range: {data.get('dateRange')}")
print(f"  - Cumulative Data: {len(data.get('cumulativeData', []))} registros")

if data.get('cumulativeData'):
    print("  [OK] Dados encontrados!")
else:
    print("  [!] Nenhum dado retornado")

print("\n" + "="*60)
print("CONCLUSÃO")
print("="*60)

print("\nSe os dados ainda não aparecem mas o código foi corrigido:")
print("  1. O servidor precisa ser REINICIADO para carregar o código novo")
print("  2. Execute: taskkill /F /IM python.exe")
print("  3. Depois: imperio_daily_reset.bat")
print("\nOu simplesmente reinicie o servidor manualmente.")

print("\n" + "="*60)