#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para corrigir mapeamento de canais do Facebook
Resolve problema de cálculo incorreto após reset do banco
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

def fix_channel_mapping():
    """Corrigir mapeamento de canais do Facebook"""
    
    print("\n" + "="*70)
    print("CORRIGINDO MAPEAMENTO DE CANAIS DO FACEBOOK")
    print("="*70)
    
    try:
        db = next(get_db())
        
        # 1. Verificar mapeamento atual
        print("\n1. MAPEAMENTO ATUAL:")
        current_mappings = db.query(FacebookAccountMapping).all()
        
        if current_mappings:
            for mapping in current_mappings:
                print(f"   {mapping.account_id} -> {mapping.channel} (ativo: {mapping.is_active})")
        else:
            print("   [PROBLEMA] Nenhum mapeamento encontrado!")
        
        # 2. Limpar e recriar mapeamentos
        print("\n2. CORRIGINDO MAPEAMENTO...")
        
        # Limpar todos os mapeamentos
        deleted_count = db.query(FacebookAccountMapping).delete()
        print(f"   Removidos {deleted_count} mapeamentos antigos")
        
        # Criar mapeamentos corretos
        # TODAS as contas vão para Instagram (canal principal)
        instagram_accounts = [
            'act_2067257390316380',
            'act_1391112848236399', 
            'act_406219475582745',
            'act_790223756353632',
            'act_772777644802886',
            'act_303402486183447'
        ]
        
        print("\n   INSTAGRAM (todas as contas do Facebook Ads):")
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
        
        print(f"\n   RESULTADO:")
        for channel, count in channels_count.items():
            print(f"   - {channel}: {count} contas")
        
        if len(new_mappings) == len(instagram_accounts):
            print(f"\n[OK] {len(new_mappings)} contas mapeadas corretamente")
        else:
            print(f"\n[AVISO] Esperado {len(instagram_accounts)}, encontrado {len(new_mappings)}")
        
        db.close()
        
        print("\n" + "="*70)
        print("MAPEAMENTO CORRIGIDO COM SUCESSO!")
        print("="*70)
        print("\nEXPLICAÇÃO DA CORREÇÃO:")
        print("- Instagram: todas as contas do Facebook Ads (campanhas)")
        print("- Grupos: vendas orgânicas (sem contas do Facebook)")
        print("- Geral: total geral da plataforma")
        print("="*70)
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Erro ao corrigir mapeamento: {e}")
        db.rollback()
        db.close()
        return False

if __name__ == "__main__":
    fix_channel_mapping()