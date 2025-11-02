#!/usr/bin/env python3
"""
Script para criar tabelas do Hora do Pix no banco de dados
"""

import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import engine, Base
from core.models.horapix import HoraPixCollection, HoraPixDraw


def create_horapix_tables():
    """Cria tabelas do Hora do Pix"""
    print("\n=== CRIAÇÃO DAS TABELAS HORA DO PIX ===\n")

    try:
        # Importar todos os modelos para garantir que sejam registrados
        print("1. Importando modelos...")
        print(f"   - HoraPixCollection: {HoraPixCollection.__tablename__}")
        print(f"   - HoraPixDraw: {HoraPixDraw.__tablename__}")
        print("   OK: Modelos importados")

        # Criar todas as tabelas
        print("\n2. Criando tabelas no banco de dados...")
        Base.metadata.create_all(bind=engine)
        print("   OK: Tabelas criadas/verificadas com sucesso!")

        # Verificar se as tabelas foram criadas
        print("\n3. Verificando tabelas criadas...")
        from sqlalchemy import inspect

        inspector = inspect(engine)
        tables = inspector.get_table_names()

        if 'horapix_collections' in tables:
            print("   OK: Tabela 'horapix_collections' criada")

            # Mostrar colunas
            columns = inspector.get_columns('horapix_collections')
            print("      Colunas:")
            for col in columns:
                print(f"        - {col['name']}: {col['type']}")
        else:
            print("   ERRO: Tabela 'horapix_collections' NAO foi criada")

        if 'horapix_draws' in tables:
            print("   OK: Tabela 'horapix_draws' criada")

            # Mostrar colunas
            columns = inspector.get_columns('horapix_draws')
            print("      Colunas:")
            for col in columns:
                print(f"        - {col['name']}: {col['type']}")
        else:
            print("   ERRO: Tabela 'horapix_draws' NAO foi criada")

        print("\n=== CRIAÇÃO CONCLUÍDA ===")
        print("As tabelas do Hora do Pix foram criadas com sucesso!")
        print("\nPróximos passos:")
        print("  1. Testar coleta: python test_horapix_selenium.py")
        print("  2. Testar API: python -m uvicorn core.app:app --reload --port 8002")
        print("  3. Acessar: http://localhost:8002/imperio#horapix")

    except Exception as e:
        print(f"\nERRO durante criacao das tabelas: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    create_horapix_tables()
