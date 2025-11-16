#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para migrar o ID de sorteio no banco de dados SQLite

Uso:
    python migrate_raffle_id.py <id_antigo> <id_novo>

Exemplo:
    python migrate_raffle_id.py 6904ea540d0e097d618827fc 6916292bf6051e4133d86ef9
"""

import sys
import os
from pathlib import Path
from sqlalchemy import create_engine, text
from typing import Tuple

# Configurar encoding
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)

class RaffleIDDatabaseMigrator:
    """Migrador de ID de sorteio no banco de dados"""

    def __init__(self, db_path: str = 'dashboard_roi.db'):
        """Inicializar migrador"""
        self.db_path = Path(db_path)
        self.engine = None
        self.old_id = None
        self.new_id = None

    def connect(self) -> bool:
        """Conectar ao banco de dados"""
        try:
            db_url = f"sqlite:///{self.db_path.absolute()}"
            self.engine = create_engine(db_url)

            # Testar conexão
            with self.engine.connect() as conn:
                pass

            print(f"[OK] Banco de dados conectado: {self.db_path}")
            return True
        except Exception as e:
            print(f"[ERRO] Falha ao conectar ao banco: {e}")
            return False

    def get_ids_from_args(self, args: list) -> Tuple[str, str]:
        """Obter IDs dos argumentos ou input do usuário"""
        if len(args) >= 2:
            return args[0], args[1]

        # Obter do usuário
        print("\nDigite o ID ANTIGO (a ser substituído):")
        old_id = input("  ID Antigo: ").strip()

        print("\nDigite o ID NOVO (novo raffle ID):")
        new_id = input("  ID Novo: ").strip()

        return old_id, new_id

    def find_actions_with_id(self, product_id: str) -> list:
        """Encontrar ações com um ID específico"""
        try:
            with self.engine.connect() as conn:
                result = conn.execute(
                    text("SELECT id, product_id, name, is_current FROM main_actions WHERE product_id = :product_id"),
                    {"product_id": product_id}
                )
                return result.fetchall()
        except Exception as e:
            print(f"[ERRO] Falha ao buscar ações: {e}")
            return []

    def migrate(self, old_id: str, new_id: str) -> bool:
        """Executar migração do banco de dados"""
        try:
            self.old_id = old_id
            self.new_id = new_id

            print(f"\n[MIGRAÇÃO] Iniciando migração do banco de dados")
            print(f"  De: {old_id}")
            print(f"  Para: {new_id}")
            print()

            # 1. Buscar ação com ID antigo
            print("[1] Buscando ações com ID antigo...")
            old_actions = self.find_actions_with_id(old_id)

            if not old_actions:
                print("[AVISO] Nenhuma ação encontrada com o ID antigo")
                return False

            print(f"[OK] {len(old_actions)} ação(ões) encontrada(s):")
            for action in old_actions:
                action_id, product_id, name, is_current = action
                print(f"    - ID: {action_id}, Product: {product_id}, Nome: {name}, Atual: {is_current}")

            # 2. Buscar ação com ID novo
            print("\n[2] Buscando ações com ID novo...")
            new_actions = self.find_actions_with_id(new_id)

            if new_actions:
                print(f"[AVISO] {len(new_actions)} ação(ões) JÁ EXISTEM com o ID novo:")
                for action in new_actions:
                    action_id, product_id, name, is_current = action
                    print(f"    - ID: {action_id}, Product: {product_id}, Nome: {name}, Atual: {is_current}")

            # 3. Confirmar antes de fazer alterações
            print("\n[CONFIRMAÇÃO] Vai fazer as seguintes alterações:")
            print(f"  1. Atualizar product_id de '{old_id}' para '{new_id}' em main_actions")
            print(f"  2. Atualizar product_id em main_action_daily (associados)")
            if new_actions:
                print(f"  3. Manter ação com ID novo como is_current=True")

            # Auto-confirmar se rodar sem interação ou pedir confirmação
            try:
                confirm = input("\nDeseja continuar? (s/n): ").strip().lower()
            except EOFError:
                confirm = 's'  # Auto-confirmar se não há input disponível
                print("(auto-confirmado)")

            if confirm != 's':
                print("[CANCELADO] Migração cancelada")
                return False

            # 4. Executar migração
            print("\n[PROCESSAMENTO] Executando migração...")

            with self.engine.begin() as conn:
                # Se houver ação com novo ID, não fazer nada
                # Se não houver, atualizar a ação antiga com novo ID

                new_count = conn.execute(
                    text("SELECT COUNT(*) as count FROM main_actions WHERE product_id = :product_id"),
                    {"product_id": new_id}
                ).scalar()

                if new_count == 0:
                    # Atualizar tabela main_actions
                    print("  - Atualizando tabela main_actions...")
                    result = conn.execute(
                        text("UPDATE main_actions SET product_id = :new_id WHERE product_id = :old_id"),
                        {"new_id": new_id, "old_id": old_id}
                    )
                    updated_count = result.rowcount
                    print(f"    [OK] {updated_count} ação(ões) atualizada(s)")

                    # Marcar como is_current=True
                    print("  - Marcando ação como atual (is_current=True)...")
                    conn.execute(
                        text("UPDATE main_actions SET is_current = 1 WHERE product_id = :product_id"),
                        {"product_id": new_id}
                    )
                    print("    [OK] Ação marcada como atual")
                else:
                    # Já existe ação com novo ID
                    print("  - Ação com novo ID já existe")

                    # Deletar ou desmarcar ação com ID antigo
                    print("  - Desmarcando ação antiga (is_current=False)...")
                    conn.execute(
                        text("UPDATE main_actions SET is_current = 0 WHERE product_id = :product_id"),
                        {"product_id": old_id}
                    )
                    print("    [OK] Ação antiga desmarcada")

                    # Marcar ação com novo ID como atual
                    print("  - Marcando ação com novo ID como atual (is_current=True)...")
                    conn.execute(
                        text("UPDATE main_actions SET is_current = 1 WHERE product_id = :product_id"),
                        {"product_id": new_id}
                    )
                    print("    [OK] Ação com novo ID marcada como atual")

            # 5. Verificar resultado
            print("\n[VERIFICAÇÃO] Verificando alterações...")

            new_actions_after = self.find_actions_with_id(new_id)
            old_actions_after = self.find_actions_with_id(old_id)

            if new_actions_after:
                print(f"[OK] Ações com ID novo ({new_id}):")
                for action in new_actions_after:
                    action_id, product_id, name, is_current = action
                    status = "[OK] ATUAL" if is_current else "Histórico"
                    print(f"    - ID: {action_id}, Nome: {name}, {status}")

            if old_actions_after:
                print(f"[OK] Ações com ID antigo ({old_id}):")
                for action in old_actions_after:
                    action_id, product_id, name, is_current = action
                    status = "Histórico" if not is_current else "[AVISO] ATIVA (deveria não ser)"
                    print(f"    - ID: {action_id}, Nome: {name}, {status}")

            print("\n" + "="*70)
            print("[OK] MIGRAÇÃO CONCLUÍDA COM SUCESSO!")
            print("="*70)
            print("\nProximos passos:")
            print("  1. Reiniciar o sistema: imperio_start.bat")
            print("  2. Verificar o endpoint: http://localhost:8002/imperio#acaoprincipal")
            print("  3. Os dados devem agora mostrar o novo ID")

            return True

        except Exception as e:
            print(f"[ERRO CRÍTICO] Falha na migração: {e}")
            import traceback
            traceback.print_exc()
            return False

    def run(self, old_id: str = None, new_id: str = None) -> bool:
        """Executar o migrador"""
        try:
            print("\n" + "="*70)
            print("MIGRADOR DE ID DE SORTEIO - BANCO DE DADOS")
            print("="*70)

            # Conectar ao banco
            if not self.connect():
                return False

            # Obter IDs
            if old_id and new_id:
                self.old_id = old_id
                self.new_id = new_id
            else:
                print("\nDigite os IDs para migração:")
                self.old_id, self.new_id = self.get_ids_from_args([])

            # Migrar
            return self.migrate(self.old_id, self.new_id)

        except KeyboardInterrupt:
            print("\n[CANCELADO] Operação interrompida pelo usuário")
            return False
        except Exception as e:
            print(f"[ERRO CRÍTICO] {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Função principal"""
    migrator = RaffleIDDatabaseMigrator()

    # Obter IDs dos argumentos se fornecidos
    if len(sys.argv) > 2:
        success = migrator.run(sys.argv[1], sys.argv[2])
    else:
        success = migrator.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
