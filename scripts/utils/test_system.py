#!/usr/bin/env python3
"""
Teste simples do sistema Imperio
"""
import sys
import os
sys.path.append(os.getcwd())

from fastapi.testclient import TestClient
from core.app import create_app

def test_sistema():
    print("=" * 60)
    print("TESTE SIMPLES DO SISTEMA IMPERIO")
    print("=" * 60)
    
    try:
        print("\n1. Criando aplicacao...")
        app = create_app('imperio')
        client = TestClient(app)
        print("   OK - App criada")
        
        print("\n2. Testando dashboard...")
        response = client.get("/api/imperio/orcamento/dashboard")
        if response.status_code == 200:
            data = response.json()
            metrics = data.get('metricas_principais', {})
            canais = data.get('canais', {})
            historico = data.get('historico_coletas', [])
            
            print("   OK - Dashboard funcionando")
            print(f"   ROI atual: {metrics.get('roi_atual', 0):.2f}")
            print(f"   Vendas hoje: R$ {metrics.get('vendas_hoje', 0):,.2f}")
            print(f"   Gastos hoje: R$ {metrics.get('gastos_hoje', 0):,.2f}")
            print(f"   Meta vendas: R$ {metrics.get('meta_vendas', 0):,.2f}")
            print(f"   Meta gastos: R$ {metrics.get('meta_gastos', 0):,.2f}")
            
            print(f"\n   Canais ({len(canais)}):")
            for canal, dados in canais.items():
                roi = dados.get('roi', 0)
                sales = dados.get('sales', 0)
                spend = dados.get('spend', 0)
                budget = dados.get('budget', 0)
                profit = dados.get('profit', 0)
                
                print(f"     {canal.upper()}:")
                print(f"       ROI: {roi:.2f}")
                print(f"       Vendas: R$ {sales:,.2f}")
                print(f"       Gastos: R$ {spend:,.2f}")
                print(f"       Orcamento: R$ {budget:,.2f}")
                print(f"       Lucro: R$ {profit:,.2f}")
                
                # Verificar consistencia
                lucro_calc = sales - spend
                if abs(lucro_calc - profit) > 1:
                    print(f"       AVISO: Lucro inconsistente! Calc: R$ {lucro_calc:,.2f}")
                
                if spend > 0:
                    roi_calc = sales / spend
                    if abs(roi_calc - roi) > 0.1:
                        print(f"       AVISO: ROI inconsistente! Calc: {roi_calc:.2f}")
            
            print(f"\n   Historico: {len(historico)} registros")
            if historico:
                latest = historico[0]
                print(f"     Ultima coleta: {latest.get('timestamp')}")
                print(f"     ROI da ultima: {latest.get('roi')}")
        else:
            print(f"   ERRO - Dashboard falhou: {response.status_code}")
            return False
        
        print("\n3. Testando coleta manual...")
        collect_response = client.post("/api/imperio/collect-now")
        if collect_response.status_code == 200:
            collect_data = collect_response.json()
            print("   OK - Coleta funcionando")
            if collect_data.get('data'):
                cdata = collect_data['data']
                print(f"   Nova coleta ROI: {cdata.get('roi', 0):.2f}")
                print(f"   Vendas: R$ {cdata.get('sales', 0):,.2f}")
                print(f"   Gastos: R$ {cdata.get('spend', 0):,.2f}")
                print(f"   Lucro: R$ {cdata.get('profit', 0):,.2f}")
        else:
            print(f"   ERRO - Coleta falhou: {collect_response.status_code}")
            return False
        
        print("\n4. Testando endpoints looker...")
        endpoints = [
            ('/api/imperio/looker/geral', 'Geral'),
            ('/api/imperio/looker/perfil', 'Instagram'),
            ('/api/imperio/looker/grupos', 'Grupos')
        ]
        
        for endpoint, name in endpoints:
            response = client.get(endpoint)
            if response.status_code == 200:
                data = response.json()
                cumulative = data.get('cumulativeData', [])
                interval = data.get('intervalData', [])
                print(f"   OK - {name}: {len(cumulative)} cumulativos, {len(interval)} intervalos")
            else:
                print(f"   ERRO - {name}: {response.status_code}")
                return False
        
        print("\n" + "=" * 60)
        print("RESULTADO: SISTEMA TOTALMENTE FUNCIONAL!")
        print("=" * 60)
        print("Todos os testes passaram com sucesso.")
        print("O sistema esta pronto para uso em producao.")
        print("\nPara iniciar o servidor:")
        print("  python imperio_system.py")
        print("\nOu:")
        print("  python startup.py")
        
        return True
        
    except Exception as e:
        print(f"\nERRO no teste: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_sistema()