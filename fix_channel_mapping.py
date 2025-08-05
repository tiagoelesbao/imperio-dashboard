#!/usr/bin/env python3
"""
Script para corrigir o mapeamento de canais e atualizar dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.core.data_collector import imperio_collector
from app.database import get_db
from app.core.data_manager import imperio_data_manager

def fix_and_update():
    print("\n=== CORRIGINDO MAPEAMENTO E ATUALIZANDO DADOS ===\n")
    
    try:
        # 1. Verificar mapeamento atual
        print("1. Verificando mapeamento de canais...")
        channel_mapping = imperio_collector.get_channel_mappings()
        print(f"Mapeamento: {channel_mapping}")
        
        if "act_772777644802886" in channel_mapping.get("grupos", []):
            print("OK: Conta act_772777644802886 esta mapeada para grupos")
        else:
            print("ERRO: Conta act_772777644802886 NAO esta mapeada para grupos!")
            return
            
        # 2. Executar coleta completa
        print("\n2. Executando coleta completa...")
        result = imperio_collector.execute_full_collection()
        
        if "error" in result:
            print(f"ERRO na coleta: {result['error']}")
            return
            
        # 3. Mostrar resultados por canal
        print("\n3. Resultados por canal:")
        for channel, data in result['channels'].items():
            print(f"\n   {channel.upper()}:")
            print(f"   - Vendas: R$ {data['sales']:,.2f}")
            print(f"   - Gastos: R$ {data['spend']:,.2f}")
            print(f"   - Orçamento: R$ {data['budget']:,.2f}")
            print(f"   - ROI: {data['roi']:.2f}")
            
        # 4. Salvar no banco
        print("\n4. Salvando dados no banco...")
        db = next(get_db())
        saved = imperio_data_manager.save_collection_data(db, result)
        
        if saved:
            print("OK: Dados salvos com sucesso!")
        else:
            print("ERRO: Erro ao salvar dados")
            
        db.close()
        
        print("\n=== CORREÇÃO CONCLUÍDA ===")
        print("O dashboard deve agora mostrar os dados corretos!")
        
    except Exception as e:
        print(f"ERRO: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    fix_and_update()