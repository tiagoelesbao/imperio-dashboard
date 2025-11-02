#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para inicializar o banco de dados com configurações padrão
Executar sempre após resetar o banco
"""

import sys
import os

# Force UTF-8 encoding on Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

from datetime import datetime
from app.database import get_db, engine, Base
from app.models import Campaign, FacebookAccountMapping

def initialize_database():
    """Inicializar banco com dados padrão"""
    
    print("\n" + "="*70)
    print("INICIALIZANDO BANCO DE DADOS")
    print("="*70)
    
    # 1. Criar tabelas se não existirem
    print("\n1. CRIANDO ESTRUTURA DO BANCO...")
    try:
        Base.metadata.create_all(bind=engine)
        print("[OK] Estrutura criada/verificada")
    except Exception as e:
        print(f"[ERRO] Erro ao criar estrutura: {e}")
        return False
    
    # 2. Configurar campanha padrão
    print("\n2. CONFIGURANDO CAMPANHA PADRAO...")
    try:
        db = next(get_db())
        
        # Verificar se já existe campanha
        existing_campaign = db.query(Campaign).filter(
            Campaign.product_id == "68e7dc390d0e097d616ae52d"
        ).first()
        
        if not existing_campaign:
            campaign = Campaign(
                product_id="68e7dc390d0e097d616ae52d",
                name="Sorteio 200mil",
                description="Campanha principal Império - Sorteio 200mil",
                roi_goal=2.0,
                daily_budget=10000.0,
                target_sales=30000.0,
                is_active=True
            )
            db.add(campaign)
            db.commit()
            print("[OK] Campanha criada: Sorteio 200mil")
        else:
            print("[INFO] Campanha ja existe")
        
        db.close()
    except Exception as e:
        print(f"[ERRO] Erro ao configurar campanha: {e}")
        db.rollback()
        db.close()
        return False
    
    # 3. Configurar mapeamento de canais do Facebook
    print("\n3. CONFIGURANDO MAPEAMENTO DE CANAIS DO FACEBOOK...")
    try:
        db = next(get_db())
        
        # Limpar mapeamentos existentes
        db.query(FacebookAccountMapping).delete()
        
        # Mapeamento correto conforme especificação do usuário:
        
        # GRUPOS: act_772777644802886 (campanhas específicas para grupos)
        grupos_account = 'act_772777644802886'
        mapping_grupos = FacebookAccountMapping(
            account_id=grupos_account,
            channel="grupos",
            is_active=True
        )
        db.add(mapping_grupos)
        print(f"\n   Canal GRUPOS (campanhas para grupos):")
        print(f"   - {grupos_account}")
        
        # INSTAGRAM: demais contas (campanhas para Instagram)
        instagram_accounts = [
            'act_2067257390316380',
            'act_1391112848236399',
            'act_406219475582745',
            'act_790223756353632',
            'act_303402486183447',
            'act_765524492538546'
        ]
        
        print(f"\n   Canal INSTAGRAM (campanhas para Instagram):")
        for account_id in instagram_accounts:
            mapping = FacebookAccountMapping(
                account_id=account_id,
                channel="instagram",
                is_active=True
            )
            db.add(mapping)
            print(f"   - {account_id}")
        
        db.commit()
        print("\n[OK] Mapeamento configurado com sucesso")
        
        # Verificar mapeamento
        total_mappings = db.query(FacebookAccountMapping).count()
        print(f"[INFO] Total de {total_mappings} contas mapeadas")
        
        # Mostrar resumo por canal
        grupos_count = db.query(FacebookAccountMapping).filter(FacebookAccountMapping.channel == "grupos").count()
        instagram_count = db.query(FacebookAccountMapping).filter(FacebookAccountMapping.channel == "instagram").count()
        print(f"[INFO] Grupos: {grupos_count} conta, Instagram: {instagram_count} contas")
        
        db.close()
        
    except Exception as e:
        print(f"[ERRO] Erro ao configurar mapeamento: {e}")
        db.rollback()
        db.close()
        return False
    
    print("\n" + "="*70)
    print("BANCO DE DADOS INICIALIZADO COM SUCESSO!")
    print("="*70)
    print("\nPROXIMOS PASSOS:")
    print("1. Execute 'python run_server.py' para iniciar o sistema")
    print("2. O sistema fara a primeira coleta automaticamente")
    print("3. Acesse http://localhost:8000 para ver o dashboard")
    print("="*70)
    
    return True

if __name__ == "__main__":
    initialize_database()