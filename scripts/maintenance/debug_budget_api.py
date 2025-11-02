#!/usr/bin/env python3
"""
Debug dos orçamentos na API
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.core.data_manager import imperio_data_manager
import json

def debug_budget():
    print("\n=== DEBUG ORÇAMENTOS NA API ===\n")
    
    try:
        db = next(get_db())
        
        # Obter dados de hoje
        today_data = imperio_data_manager.get_today_data(db)
        
        if today_data:
            print("OK: Dados encontrados no banco:")
            print(f"Data: {today_data['date']}")
            print(f"Última atualização: {today_data['last_update']}")
            
            print("\nCanais:")
            for channel, data in today_data['channels'].items():
                budget = data.get('budget', 'NÃO ENCONTRADO')
                print(f"\n{channel.upper()}:")
                print(f"  - Vendas: R$ {data.get('sales', 0):,.2f}")
                print(f"  - Gastos: R$ {data.get('spend', 0):,.2f}")
                print(f"  - Orçamento: {budget}")
                print(f"  - ROI: {data.get('roi', 0):.2f}")
                
            print("\nTotais:")
            totals = today_data['totals']
            total_budget = totals.get('budget', 'NÃO ENCONTRADO')
            print(f"  - Orçamento total: {total_budget}")
            print(f"  - Vendas totais: R$ {totals.get('sales', 0):,.2f}")
            print(f"  - Gastos totais: R$ {totals.get('spend', 0):,.2f}")
            
            # Salvar para análise
            with open('debug_api_data.json', 'w', encoding='utf-8') as f:
                json.dump(today_data, f, indent=2, ensure_ascii=False)
            print("\nDados completos salvos em debug_api_data.json")
            
        else:
            print("ERRO: Nenhum dado encontrado no banco")
            
        db.close()
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_budget()