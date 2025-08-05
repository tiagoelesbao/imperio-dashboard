#!/usr/bin/env python3
"""
Script para configurar o mapeamento correto de canais no banco de dados
Todas as contas do Facebook devem ser mapeadas para Instagram conforme usuário
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_db
from app.models import FacebookAccountMapping

def setup_channel_mapping():
    """Configurar mapeamento de canais no banco"""
    print("CONFIGURANDO MAPEAMENTO DE CANAIS")
    print("=" * 50)
    
    # Obter conexão com banco
    db = next(get_db())
    
    try:
        # Limpar mapeamentos existentes
        print("Removendo mapeamentos antigos...")
        db.query(FacebookAccountMapping).delete()
        
        # Contas do Facebook - Instagram
        instagram_accounts = [
            'act_2067257390316380',
            'act_1391112848236399', 
            'act_406219475582745',
            'act_790223756353632',
            'act_303402486183447'
        ]
        
        # Contas do Facebook - Grupos WhatsApp
        grupos_accounts = [
            'act_772777644802886'  # Primeira conta para grupos WhatsApp
        ]
        
        print("Configurando contas para Instagram...")
        
        # Criar mapeamentos para Instagram
        for account_id in instagram_accounts:
            mapping = FacebookAccountMapping(
                account_id=account_id,
                channel="instagram",
                is_active=True
            )
            db.add(mapping)
            print(f"OK {account_id} -> instagram")
        
        print("\nConfigurando contas para Grupos WhatsApp...")
        
        # Criar mapeamentos para Grupos
        for account_id in grupos_accounts:
            mapping = FacebookAccountMapping(
                account_id=account_id,
                channel="grupos",
                is_active=True
            )
            db.add(mapping)
            print(f"OK {account_id} -> grupos")
        
        # Salvar alterações
        db.commit()
        print("\nMapeamento configurado com sucesso!")
        
        # Verificar configuração
        mappings = db.query(FacebookAccountMapping).filter(
            FacebookAccountMapping.is_active == True
        ).all()
        
        print(f"\nCONFIGURACAO ATUAL ({len(mappings)} contas):")
        channel_summary = {}
        for mapping in mappings:
            channel = mapping.channel
            if channel not in channel_summary:
                channel_summary[channel] = []
            channel_summary[channel].append(mapping.account_id)
        
        for channel, accounts in channel_summary.items():
            print(f"  {channel.upper()}: {len(accounts)} contas")
            for account in accounts:
                print(f"    - {account}")
        
        print("\nRESULTADO:")
        print("• Gastos do Facebook divididos por canal:")
        print("• Estrutura de canais:")
        print("  - Instagram: Afiliado L8UTEDVTI0 + gastos das contas Instagram") 
        print("  - Grupos: Afiliado 17QB25AKRL + gastos da conta act_772777644802886")
        print("  - Geral: VENDAS TOTAIS DA PLATAFORMA + gastos totais Facebook")
        print("\nCanal GERAL = Faturamento real da acao (nao soma de afiliados)")
        print("Conta act_772777644802886 configurada para Grupos WhatsApp")
        
    except Exception as e:
        print(f"ERRO: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_channel_mapping()