#!/usr/bin/env python3
"""
Migração para adicionar tabelas de captura
"""

import sys
import os
sys.path.append(os.getcwd())

from core.database.base import engine, Base
from core.models.base import CaptureConfig, CaptureLog

def migrate_capture_tables():
    """Criar tabelas de captura se não existirem"""
    try:
        print("Criando tabelas de captura...")
        
        # Criar todas as tabelas do Base
        Base.metadata.create_all(bind=engine)
        
        print("✅ Tabelas de captura criadas com sucesso!")
        print("- capture_config")
        print("- capture_logs")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao criar tabelas de captura: {e}")
        return False

if __name__ == "__main__":
    migrate_capture_tables()