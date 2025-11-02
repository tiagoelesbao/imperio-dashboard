#!/usr/bin/env python
"""Script para testar se a correção funcionou."""

import requests
import json
from datetime import datetime

# Base URL do servidor
BASE_URL = "http://localhost:8002"

print("="*60)
print("TESTANDO CORREÇÃO DOS ENDPOINTS")
print("="*60)

# Testar os 3 endpoints que estavam com problema
endpoints = [
    "/api/imperio/looker/geral",
    "/api/imperio/looker/perfil",
    "/api/imperio/looker/grupos"
]

for endpoint in endpoints:
    url = BASE_URL + endpoint
    print(f"\nTestando: {endpoint}")
    print("-" * 40)

    try:
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()

            # Verificar se há dados
            cumulative_count = len(data.get('cumulativeData', []))
            interval_count = len(data.get('intervalData', []))

            print(f"[OK] Status: {response.status_code}")
            print(f"Date Range: {data.get('dateRange', 'N/A')}")
            print(f"Cumulative Data: {cumulative_count} registros")
            print(f"Interval Data: {interval_count} registros")

            if cumulative_count > 0:
                print("\nPrimeiro registro cumulativo:")
                first = data['cumulativeData'][0]
                print(f"  - DateTime: {first.get('dateTime')}")
                print(f"  - Valor Usado: R$ {first.get('valorUsado', 0):.2f}")
                print(f"  - Vendas: R$ {first.get('vendas', 0):.2f}")
                print(f"  - ROI: {first.get('roi', 0):.2f}")

                if cumulative_count > 1:
                    print("\nUltimo registro cumulativo:")
                    last = data['cumulativeData'][-1]
                    print(f"  - DateTime: {last.get('dateTime')}")
                    print(f"  - Valor Usado: R$ {last.get('valorUsado', 0):.2f}")
                    print(f"  - Vendas: R$ {last.get('vendas', 0):.2f}")
                    print(f"  - ROI: {last.get('roi', 0):.2f}")
            else:
                print("[!] NENHUM DADO CUMULATIVO RETORNADO")

            if interval_count > 0:
                print(f"\n[OK] Dados de intervalo também presentes ({interval_count} registros)")

        else:
            print(f"[ERRO] Status: {response.status_code}")
            print(f"Response: {response.text[:200]}")

    except requests.exceptions.ConnectionError:
        print("[ERRO] Não foi possível conectar ao servidor")
        print("Certifique-se de que o servidor está rodando em http://localhost:8002")
        break
    except Exception as e:
        print(f"[ERRO] {str(e)}")

print("\n" + "="*60)
print("RESULTADO DO TESTE")
print("="*60)

print("\nSe os endpoints estão retornando dados (cumulative > 0):")
print("  [OK] A correção funcionou! Os dados estão sendo exibidos.")
print("\nSe ainda não há dados:")
print("  [!] Verifique se o servidor foi reiniciado após a correção.")
print("  [!] Execute: taskkill /F /IM python.exe && imperio_daily_reset.bat")

print("\n" + "="*60)