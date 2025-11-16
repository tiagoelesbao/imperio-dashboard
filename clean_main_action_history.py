#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para limpar histórico da Ação Principal

O sistema de Ação Principal é SEMPRE FRESCO:
- Mostra apenas dados do momento da coleta atual
- Não armazena histórico de coletas anteriores
- A cada coleta, dados antigos são deletados

Este script é executado no daily_reset.bat antes da coleta
"""

import sys
import sqlite3
from pathlib import Path

class MainActionHistoryCleaner:
    """Limpador de histórico de ações principais"""

    def __init__(self, db_path: str = 'dashboard_roi.db'):
        self.db_path = Path(db_path)

    def clean_all(self) -> bool:
        """Limpar TODOS os dados históricos de main_action_daily"""
        try:
            print("="*70)
            print("LIMPEZA: Histórico de Acao Principal")
            print("="*70)
            print()

            if not self.db_path.exists():
                print(f"[AVISO] Banco de dados não encontrado: {self.db_path}")
                return False

            conn = sqlite3.connect(str(self.db_path.absolute()))
            cursor = conn.cursor()

            # Verificar quantos registros vão ser deletados
            cursor.execute("SELECT COUNT(*) FROM main_action_daily")
            count = cursor.fetchone()[0]

            if count > 0:
                print(f"[LIMPEZA] Deletando {count} registros antigos...")
                cursor.execute("DELETE FROM main_action_daily")
                conn.commit()
                print(f"[OK] {count} registros deletados!")
            else:
                print("[INFO] Nenhum registro para deletar")

            # Resetar contador de IDs (VACUUM)
            print("[LIMPEZA] Otimizando banco de dados...")
            cursor.execute("VACUUM")
            conn.commit()
            print("[OK] Banco otimizado!")

            conn.close()

            print()
            print("="*70)
            print("[OK] Limpeza concluida com sucesso!")
            print("="*70)
            print()
            print("Proximo passo: Coletar dados frescos da Acao Principal")
            print()

            return True

        except Exception as e:
            print(f"[ERRO] Falha ao limpar histórico: {e}")
            import traceback
            traceback.print_exc()
            return False

    def get_status(self) -> str:
        """Obter status atual do banco"""
        try:
            conn = sqlite3.connect(str(self.db_path.absolute()))
            cursor = conn.cursor()

            cursor.execute("SELECT COUNT(*) FROM main_action_daily")
            count = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM main_actions")
            actions = cursor.fetchone()[0]

            conn.close()

            return f"Acoes: {actions} | Registros diarios: {count}"

        except Exception as e:
            return f"Erro ao verificar status: {e}"


def main():
    """Função principal"""
    cleaner = MainActionHistoryCleaner()

    print("[INFO] Status antes da limpeza:")
    print(f"  {cleaner.get_status()}")
    print()

    if cleaner.clean_all():
        print("[INFO] Status depois da limpeza:")
        print(f"  {cleaner.get_status()}")
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
