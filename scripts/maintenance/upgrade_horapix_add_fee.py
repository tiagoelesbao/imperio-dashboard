#!/usr/bin/env python3
"""
Script para adicionar coluna platform_fee nas tabelas Hora do Pix
"""

import sys
import os
import sqlite3

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database import engine


def upgrade_horapix_tables():
    """Adiciona coluna platform_fee nas tabelas Hora do Pix"""
    print("\n=== UPGRADE TABELAS HORA DO PIX ===\n")

    try:
        # Conectar direto no SQLite
        db_path = './dashboard_roi.db'

        if not os.path.exists(db_path):
            print(f"ERRO: Banco de dados nao encontrado em {db_path}")
            print("Execute primeiro: python scripts/maintenance/create_horapix_tables.py")
            return False

        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # 1. Adicionar coluna platform_fee na tabela horapix_collections
        print("1. Adicionando coluna platform_fee em horapix_collections...")
        try:
            cursor.execute("ALTER TABLE horapix_collections ADD COLUMN total_platform_fee REAL DEFAULT 0.0")
            print("   OK: Coluna total_platform_fee adicionada com sucesso!")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   OK: Coluna total_platform_fee ja existe")
            else:
                print(f"   ERRO: {e}")
                return False

        # 2. Adicionar coluna platform_fee na tabela horapix_draws
        print("\n2. Adicionando coluna platform_fee em horapix_draws...")
        try:
            cursor.execute("ALTER TABLE horapix_draws ADD COLUMN platform_fee REAL DEFAULT 0.0")
            print("   OK: Coluna platform_fee adicionada com sucesso!")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("   OK: Coluna platform_fee ja existe")
            else:
                print(f"   ERRO: {e}")
                return False

        # 3. Atualizar dados existentes com calculo da taxa (3% da receita)
        print("\n3. Atualizando dados existentes com calculo da taxa...")

        # Atualizar horapix_collections
        try:
            cursor.execute("""
                UPDATE horapix_collections
                SET total_platform_fee = total_revenue * 0.03
                WHERE total_platform_fee = 0.0 OR total_platform_fee IS NULL
            """)
            rows_updated = cursor.rowcount
            print(f"   OK: {rows_updated} colecoes atualizadas")
        except Exception as e:
            print(f"   ERRO ao atualizar collections: {e}")

        # Atualizar horapix_draws
        try:
            cursor.execute("""
                UPDATE horapix_draws
                SET platform_fee = revenue * 0.03
                WHERE platform_fee = 0.0 OR platform_fee IS NULL
            """)
            rows_updated = cursor.rowcount
            print(f"   OK: {rows_updated} sorteios atualizados")
        except Exception as e:
            print(f"   ERRO ao atualizar draws: {e}")

        # 4. Recalcular lucros e ROI considerando a taxa
        print("\n4. Recalculando lucros e ROI com a taxa...")

        # Recalcular horapix_collections
        try:
            cursor.execute("""
                UPDATE horapix_collections
                SET total_profit = total_revenue - total_prize_value - total_platform_fee,
                    total_roi = CASE
                        WHEN (total_prize_value + total_platform_fee) > 0
                        THEN ((total_revenue - total_prize_value - total_platform_fee) / (total_prize_value + total_platform_fee) * 100)
                        ELSE 0
                    END
            """)
            print(f"   OK: Lucros e ROI das colecoes recalculados")
        except Exception as e:
            print(f"   ERRO ao recalcular collections: {e}")

        # Recalcular horapix_draws
        try:
            cursor.execute("""
                UPDATE horapix_draws
                SET profit = revenue - prize_value - platform_fee,
                    roi = CASE
                        WHEN (prize_value + platform_fee) > 0
                        THEN ((revenue - prize_value - platform_fee) / (prize_value + platform_fee) * 100)
                        ELSE 0
                    END
            """)
            print(f"   OK: Lucros e ROI dos sorteios recalculados")
        except Exception as e:
            print(f"   ERRO ao recalcular draws: {e}")

        conn.commit()
        conn.close()

        print("\n=== UPGRADE CONCLUIDO ===")
        print("As tabelas agora incluem a taxa de 3% da plataforma!")
        print("\nProximos passos:")
        print("  1. Testar interface: http://localhost:8002/imperio#horapix")
        print("  2. Verificar se os valores estao corretos")
        print("  3. Fazer nova coleta para validar: POST /api/imperio/horapix/collect")

        return True

    except Exception as e:
        print(f"\nERRO durante upgrade: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = upgrade_horapix_tables()
    sys.exit(0 if success else 1)
