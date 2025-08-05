#!/usr/bin/env python3
"""
Script para testar se os orçamentos por canal estão funcionando
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.data_collector import imperio_collector
import json

def test_budget_collection():
    print("\n=== TESTE DE ORÇAMENTO POR CANAL ===\n")
    
    try:
        # Executar coleta
        print("1. Executando coleta de dados...")
        result = imperio_collector.execute_full_collection()
        
        if "error" in result:
            print(f"ERRO na coleta: {result['error']}")
            return
            
        # Verificar orçamentos
        print("\n2. Orçamentos por canal:")
        for channel, data in result['channels'].items():
            budget = data.get('budget', 0)
            spend = data.get('spend', 0)
            budget_usage = (spend / budget * 100) if budget > 0 else 0
            
            print(f"\n   {channel.upper()}:")
            print(f"   - Orçamento: R$ {budget:,.2f}")
            print(f"   - Gastos: R$ {spend:,.2f}")
            print(f"   - Uso do orçamento: {budget_usage:.1f}%")
            
        # Verificar orçamento total
        total_budget = result['totals'].get('budget', 0)
        total_spend = result['totals'].get('spend', 0)
        total_usage = (total_spend / total_budget * 100) if total_budget > 0 else 0
        
        print(f"\n3. TOTAIS:")
        print(f"   - Orçamento total: R$ {total_budget:,.2f}")
        print(f"   - Gastos totais: R$ {total_spend:,.2f}")
        print(f"   - Uso do orçamento total: {total_usage:.1f}%")
        
        # Salvar resultado para análise
        with open('test_budget_result.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print("\n4. Resultado completo salvo em test_budget_result.json")
        
    except Exception as e:
        print(f"ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_budget_collection()