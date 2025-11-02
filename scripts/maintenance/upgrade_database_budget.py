#!/usr/bin/env python3
"""
Script para adicionar coluna budget ao banco de dados
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import sqlite3
from app.database import engine
from app.models import Base

def upgrade_database():
    print("\n=== UPGRADE DO BANCO DE DADOS ===\n")
    
    try:
        # 1. Adicionar coluna budget se não existir
        print("1. Adicionando coluna budget na tabela channel_data...")
        
        # Conectar direto no SQLite
        db_path = './dashboard_roi.db'
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        try:
            # Tentar adicionar a coluna
            cursor.execute("ALTER TABLE channel_data ADD COLUMN budget REAL DEFAULT 0.0")
            print("OK: Coluna budget adicionada com sucesso!")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("OK: Coluna budget ja existe")
            else:
                print(f"Erro ao adicionar coluna: {e}")
        
        conn.commit()
        conn.close()
        
        # 2. Recriar as tabelas se necessário
        print("\n2. Verificando estrutura das tabelas...")
        Base.metadata.create_all(bind=engine)
        print("OK: Estrutura do banco verificada e atualizada!")
        
        print("\n=== UPGRADE CONCLUÍDO ===")
        print("O banco agora suporta orçamentos por canal!")
        
    except Exception as e:
        print(f"ERRO durante upgrade: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    upgrade_database()