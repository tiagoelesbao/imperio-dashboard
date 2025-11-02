#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Correção final do mapeamento de canais conforme especificação do usuário
act_772777644802886 deve representar campanhas para GRUPOS
"""

import sys

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from app.database import get_db
from app.models import FacebookAccountMapping
from datetime import datetime

def fix_channel_mapping_final():
    """Corrigir mapeamento final conforme especificação do usuário"""
    
    print("\n" + "="*70)
    print("CORREÇÃO FINAL DO MAPEAMENTO DE CANAIS")
    print("="*70)
    print("Configuração correta:")
    print("- act_772777644802886 -> GRUPOS (campanhas para grupos)")
    print("- Demais contas -> INSTAGRAM")
    
    try:
        db = next(get_db())
        
        # 1. Verificar mapeamento atual
        print("\n1. MAPEAMENTO ATUAL:")
        current_mappings = db.query(FacebookAccountMapping).all()
        
        if current_mappings:
            for mapping in current_mappings:
                print(f"   {mapping.account_id} -> {mapping.channel}")
        else:
            print("   Nenhum mapeamento encontrado")
        
        # 2. Limpar e recriar mapeamentos corretos
        print("\n2. APLICANDO CORREÇÃO...")
        
        # Limpar todos os mapeamentos
        deleted_count = db.query(FacebookAccountMapping).delete()
        print(f"   Removidos {deleted_count} mapeamentos antigos")
        
        # Mapeamento CORRETO conforme especificação:
        
        # GRUPOS: act_772777644802886 (campanhas específicas para grupos)
        grupos_account = 'act_772777644802886'
        mapping_grupos = FacebookAccountMapping(
            account_id=grupos_account,
            channel="grupos",
            is_active=True
        )
        db.add(mapping_grupos)
        print(f"\n   GRUPOS (campanhas para grupos):")
        print(f"   + {grupos_account}")
        
        # INSTAGRAM: todas as demais contas (campanhas para Instagram)
        instagram_accounts = [
            'act_2067257390316380',
            'act_1391112848236399', 
            'act_406219475582745',
            'act_790223756353632',
            'act_303402486183447'  # Removido act_772777644802886 que agora é grupos
        ]
        
        print(f"\n   INSTAGRAM (campanhas para Instagram):")
        for account_id in instagram_accounts:
            mapping = FacebookAccountMapping(
                account_id=account_id,
                channel="instagram",
                is_active=True
            )
            db.add(mapping)
            print(f"   + {account_id}")
        
        # Commit das alterações
        db.commit()
        
        # 3. Verificar correção
        print("\n3. VERIFICANDO CORREÇÃO...")
        new_mappings = db.query(FacebookAccountMapping).all()
        
        channels_count = {}
        for mapping in new_mappings:
            channel = mapping.channel
            if channel not in channels_count:
                channels_count[channel] = 0
            channels_count[channel] += 1
        
        print(f"\n   RESULTADO FINAL:")
        for channel, count in channels_count.items():
            print(f"   - {channel}: {count} conta(s)")
            
            # Mostrar quais contas estão em cada canal
            channel_accounts = [m.account_id for m in new_mappings if m.channel == channel]
            for acc in channel_accounts:
                print(f"     {acc}")
        
        total_expected = 1 + len(instagram_accounts)  # 1 para grupos + 5 para instagram
        if len(new_mappings) == total_expected:
            print(f"\n[OK] {len(new_mappings)} contas mapeadas corretamente")
        else:
            print(f"\n[AVISO] Esperado {total_expected}, encontrado {len(new_mappings)}")
        
        db.close()
        
        print("\n" + "="*70)
        print("MAPEAMENTO CORRIGIDO COM SUCESSO!")
        print("="*70)
        print("\nCONFIGURAÇÃO FINAL:")
        print("🟠 GRUPOS: act_772777644802886 (campanhas para grupos)")
        print("🟢 INSTAGRAM: 5 contas restantes (campanhas para Instagram)")
        print("🔵 GERAL: soma total de vendas da plataforma")
        print("\nAgora o dashboard mostrará:")
        print("- Grupos: gastos e ROI da conta específica para grupos")
        print("- Instagram: gastos e ROI das contas para Instagram")
        print("- Geral: visão completa de toda a operação")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Erro ao corrigir mapeamento: {e}")
        db.rollback()
        db.close()
        return False

if __name__ == "__main__":
    fix_channel_mapping_final()