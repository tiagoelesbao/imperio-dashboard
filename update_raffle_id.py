#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para atualizar o ID de sorteio em todo o projeto

Uso:
    python update_raffle_id.py

O script:
    1. Detecta o ID de sorteio atual
    2. Pede o novo ID como input
    3. Valida o formato do ID
    4. Faz a substituição em todos os arquivos
    5. Gera um relatório das alterações
"""

import os
import re
import sys
import subprocess
from pathlib import Path
from typing import Tuple, List, Dict

class RaffleIDUpdater:
    """Atualizador de ID de sorteio"""

    # Padrão para validar ID de sorteio (24 caracteres hexadecimais)
    ID_PATTERN = r'^[a-fA-F0-9]{24}$'

    # Arquivos que devem ser atualizados
    FILES_TO_UPDATE = [
        'clients/imperio/config.py',
        'core/services/data_collector.py',
        'collect_main_action.py',
        'force_reload_main_action.py',
        'update_action_with_fb_costs.py',
        'debug_database_issue.py',
        'tests/test_fb_today.py',
        'tests/test_complete_collection.py',
        'docs/ESTRUTURA_PROJETO.md',
        'imperio_daily_reset.bat'
    ]

    def __init__(self):
        """Inicializar atualizador"""
        self.root_dir = Path(__file__).parent
        self.current_id = None
        self.new_id = None
        self.replacements = []

    def validate_id(self, raffle_id: str) -> bool:
        """Validar formato do ID de sorteio"""
        if not raffle_id:
            return False

        # Remover espaços
        raffle_id = raffle_id.strip()

        # Validar padrão
        if not re.match(self.ID_PATTERN, raffle_id):
            return False

        return True

    def detect_current_id(self) -> str:
        """Detectar o ID de sorteio atual no projeto"""
        config_file = self.root_dir / 'clients/imperio/config.py'

        if not config_file.exists():
            print("[ERRO] Arquivo config.py não encontrado")
            return None

        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Buscar "product_id": "XXXXXXXXXXXXXXXXXXXXXXXXXX"
            match = re.search(r'"product_id":\s*"([a-fA-F0-9]{24})"', content)
            if match:
                return match.group(1)

            return None
        except Exception as e:
            print(f"[ERRO] Falha ao detectar ID atual: {e}")
            return None

    def get_user_input(self) -> Tuple[str, str]:
        """Obter entrada do usuário"""
        print("\n" + "="*70)
        print("ATUALIZADOR DE ID DE SORTEIO - IMPERIO")
        print("="*70)

        # Detectar ID atual
        self.current_id = self.detect_current_id()

        if self.current_id:
            print(f"\n[INFO] ID de sorteio ATUAL detectado: {self.current_id}")
        else:
            print("\n[AVISO] Não foi possível detectar o ID atual")
            print("Continuando sem detecção automática...")
            self.current_id = None

        # Pedir novo ID
        while True:
            print(f"\n[ENTRADA] Digite o NOVO ID de sorteio:")
            print("   Formato: 24 caracteres hexadecimais (0-9, a-f)")
            print("   Exemplo: 6916292bf6051e4133d86ef9")

            new_id = input("\n   Novo ID: ").strip()

            if not new_id:
                print("   [ERRO] ID não pode estar vazio!")
                continue

            if not self.validate_id(new_id):
                print("   [ERRO] Formato inválido! Deve ter exatamente 24 caracteres hexadecimais")
                continue

            # Confirmar
            print(f"\n   ID digitado: {new_id}")
            confirm = input("   Confirmar? (s/n): ").strip().lower()

            if confirm == 's':
                self.new_id = new_id
                break

        return self.current_id, self.new_id

    def update_files(self) -> bool:
        """Atualizar IDs em todos os arquivos"""
        if not self.current_id or not self.new_id:
            print("[ERRO] IDs não foram definidos")
            return False

        print(f"\n[PROCESSAMENTO] Iniciando atualização...")
        print(f"   De: {self.current_id}")
        print(f"   Para: {self.new_id}")
        print()

        total_replacements = 0

        for file_path_str in self.FILES_TO_UPDATE:
            file_path = self.root_dir / file_path_str

            if not file_path.exists():
                print(f"[AVISO] Arquivo não encontrado: {file_path_str}")
                continue

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Contar ocorrências
                old_occurrences = content.count(self.current_id)

                if old_occurrences == 0:
                    print(f"[OK] {file_path_str}: Nenhuma ocorrência encontrada")
                    continue

                # Fazer substituição
                new_content = content.replace(self.current_id, self.new_id)

                # Verificar se mudou
                if new_content == content:
                    print(f"[OK] {file_path_str}: Nenhuma alteração necessária")
                    continue

                # Salvar arquivo
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)

                print(f"[✓] {file_path_str}")
                print(f"    ├─ Substituições: {old_occurrences}")
                print(f"    └─ Status: Atualizado")

                self.replacements.append({
                    'file': file_path_str,
                    'count': old_occurrences
                })

                total_replacements += old_occurrences

            except Exception as e:
                print(f"[ERRO] Falha ao atualizar {file_path_str}: {e}")
                return False

        print()
        print("="*70)
        print(f"RESUMO: {total_replacements} substituições realizadas em {len(self.replacements)} arquivos")
        print("="*70)

        return True

    def show_report(self):
        """Exibir relatório das alterações"""
        if not self.replacements:
            print("\n[AVISO] Nenhum arquivo foi atualizado")
            return

        print("\n" + "="*70)
        print("RELATÓRIO DE ALTERAÇÕES")
        print("="*70)

        print(f"\nID de sorteio ANTERIOR: {self.current_id}")
        print(f"ID de sorteio NOVO: {self.new_id}")

        print(f"\nArquivos atualizados: {len(self.replacements)}")
        print()

        total = 0
        for i, item in enumerate(self.replacements, 1):
            print(f"{i}. {item['file']}")
            print(f"   └─ Substituições: {item['count']}")
            total += item['count']

        print()
        print("="*70)
        print(f"TOTAL DE SUBSTITUIÇÕES: {total}")
        print("="*70)

        print("\n[OK] Atualização concluída com sucesso!")
        print("\nPróximos passos:")
        print("   1. Recarregar frontend: Ctrl+F5")
        print("   2. Verificar dados em: http://localhost:8002/imperio#acaoprincipal")
        print("   3. Fazer commit: git add . && git commit")
        print("   4. Push para repositório: git push origin main")

    def collect_fresh_data(self) -> bool:
        """Coletar dados frescos da ação principal com novo ID"""
        try:
            print("\n" + "="*70)
            print("COLETANDO DADOS FRESCOS DA ACAO PRINCIPAL")
            print("="*70)
            print(f"Aguardando coleta de dados para o novo ID: {self.new_id}")
            print()

            # Executar coleta de dados
            result = subprocess.run(
                [sys.executable, 'collect_main_action.py'],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Filtrar output importante
            output_lines = result.stdout.split('\n')
            for line in output_lines:
                if any(keyword in line for keyword in ['OK', 'Dados salvos', 'COLETANDO', 'TOTAIS', 'RESUMO', '===', 'Receita:', 'Custos', 'Lucro', 'ROI', 'Prêmio', 'Período', 'Dias', 'vendas']):
                    if line.strip():
                        print(line)

            if result.returncode == 0:
                print("\n[OK] Dados frescos coletados com sucesso!")
                return True
            else:
                print("\n[AVISO] Coleta de dados finalizada")
                return True  # Não falhar a execução se coleta teve problema

        except subprocess.TimeoutExpired:
            print("[AVISO] Coleta de dados expirou (timeout)")
            return True  # Não falhar
        except Exception as e:
            print(f"[AVISO] Erro ao coletar dados: {e}")
            return True  # Não falhar

    def migrate_database(self) -> bool:
        """Migrar o banco de dados com o novo ID"""
        try:
            print("\n" + "="*70)
            print("MIGRANDO BANCO DE DADOS")
            print("="*70)

            # Executar script de migração
            result = subprocess.run(
                [sys.executable, 'migrate_raffle_id.py', self.current_id, self.new_id],
                capture_output=True,
                text=True
            )

            if result.returncode == 0:
                print(result.stdout)
                return True
            else:
                print("[ERRO] Falha na migração do banco de dados")
                print(result.stdout)
                print(result.stderr)
                return False

        except Exception as e:
            print(f"[ERRO] Falha ao executar migração: {e}")
            return False

    def run(self):
        """Executar o atualizar"""
        try:
            # Obter entrada do usuário
            self.get_user_input()

            # Se não detectou ID atual, pedir também
            if not self.current_id:
                print(f"\n[ENTRADA] Digite o ID DE SORTEIO ATUAL:")
                while True:
                    current_id = input("   ID Atual: ").strip()
                    if self.validate_id(current_id):
                        self.current_id = current_id
                        break
                    print("   [ERRO] Formato inválido!")

            # Confirmar antes de fazer alterações
            print("\n" + "="*70)
            print("CONFIRMAÇÃO DE ALTERAÇÕES")
            print("="*70)
            print(f"\nVai substituir TODOS os IDs de sorteio no projeto:")
            print(f"   De: {self.current_id}")
            print(f"   Para: {self.new_id}")
            print(f"\nArquivos que serão atualizados: {len(self.FILES_TO_UPDATE)}")
            print(f"Banco de dados será migrado automaticamente")

            confirm = input("\nDeseja continuar? (s/n): ").strip().lower()

            if confirm != 's':
                print("\n[CANCELADO] Operação cancelada pelo usuário")
                return False

            # Executar atualização de arquivos
            if not self.update_files():
                print("\n[ERRO] Falha durante a atualização dos arquivos")
                return False

            # Executar coleta de dados frescos ANTES de migrar o banco
            print()
            self.collect_fresh_data()

            # Executar migração do banco de dados
            print()
            if not self.migrate_database():
                print("\n[AVISO] Arquivos foram atualizados, mas falha na migração do banco")
                print("Execute manualmente: python migrate_raffle_id.py")
                return False

            self.show_report()
            return True

        except KeyboardInterrupt:
            print("\n\n[CANCELADO] Operação interrompida pelo usuário")
            return False
        except Exception as e:
            print(f"\n[ERRO CRÍTICO] {e}")
            import traceback
            traceback.print_exc()
            return False


def main():
    """Função principal"""
    updater = RaffleIDUpdater()
    success = updater.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
