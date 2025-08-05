#!/usr/bin/env python3
"""
Script de teste para verificar se a coleta está funcionando corretamente
com o novo mapeamento de canais
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.data_collector import imperio_collector
from app.database import get_db
from app.core.data_manager import imperio_data_manager
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_collection():
    """Testar coleta completa e verificar cálculos"""
    print("\n=== TESTE DE COLETA DE DADOS ===\n")
    
    try:
        # 1. Verificar mapeamento de canais
        print("1. Verificando mapeamento de canais...")
        channel_mapping = imperio_collector.get_channel_mappings()
        print(f"Mapeamento atual: {channel_mapping}")
        
        # Verificar se act_772777644802886 está mapeada para grupos
        grupos_accounts = channel_mapping.get("grupos", [])
        if "act_772777644802886" in grupos_accounts:
            print("OK: Conta act_772777644802886 corretamente mapeada para grupos")
        else:
            print("ERRO: Conta act_772777644802886 NAO esta mapeada para grupos!")
            
        # 2. Executar coleta completa
        print("\n2. Executando coleta completa...")
        result = imperio_collector.execute_full_collection()
        
        if "error" in result:
            print(f"ERRO na coleta: {result['error']}")
            return
            
        # 3. Verificar resultados
        print("\n3. Resultados da coleta:")
        print(f"   - Total de vendas: R$ {result['totals']['sales']:,.2f}")
        print(f"   - Total de gastos: R$ {result['totals']['spend']:,.2f}")
        print(f"   - ROI geral: {result['totals']['roi']:.2f}")
        
        print("\n4. Resultados por canal:")
        for channel, data in result['channels'].items():
            print(f"\n   {channel.upper()}:")
            print(f"   - Vendas: R$ {data['sales']:,.2f}")
            print(f"   - Gastos: R$ {data['spend']:,.2f}")
            print(f"   - ROI: {data['roi']:.2f}")
            print(f"   - Lucro: R$ {data['profit']:,.2f}")
            
        # 5. Salvar no banco para verificar persistência
        print("\n5. Salvando dados no banco...")
        db = next(get_db())
        saved = imperio_data_manager.save_collection_data(db, result)
        
        if saved:
            print("OK: Dados salvos com sucesso!")
            
            # Verificar se os dados foram salvos corretamente
            today_data = imperio_data_manager.get_today_data(db)
            if today_data:
                print("\n6. Dados recuperados do banco:")
                print(f"   - Canal grupos tem gastos: R$ {today_data['channels']['grupos']['spend']:,.2f}")
            else:
                print("ERRO ao recuperar dados do banco")
        else:
            print("ERRO ao salvar dados")
            
        db.close()
        
    except Exception as e:
        print(f"ERRO durante o teste: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_collection()