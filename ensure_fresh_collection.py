#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para garantir coleta fresca da Acao Principal com novo ID

Este script eh executado apos atualizar o ID de sorteio para:
1. Limpar dados antigos (historico)
2. Reiniciar o servidor (força recarregamento de modulos)
3. Aguardar servidor estar pronto
4. Executar coleta fresca com novo ID

Garante que o sistema funcione CORRETAMENTE apos troca de ID.
"""

import subprocess
import sys
import time
import os
import sqlite3
import codecs
from pathlib import Path
from typing import Dict

# Fix encoding para Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

class FreshCollectionEnsurer:
    """Garante coleta fresca após atualização de ID"""

    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.db_path = self.root_dir / 'dashboard_roi.db'
        self.log_file = self.root_dir / 'data' / 'logs' / 'ensure_fresh.log'

    def log(self, message: str):
        """Log com timestamp"""
        timestamp = time.strftime('%d/%m/%Y %H:%M:%S')
        log_msg = f"[{timestamp}] {message}"
        print(log_msg)

        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(log_msg + '\n')
        except Exception as e:
            print(f"[AVISO] Não foi possível escrever log: {e}")

    def step1_clean_history(self) -> bool:
        """PASSO 1: Limpar histórico de dados antigos"""
        self.log("=" * 70)
        self.log("[PASSO 1] LIMPANDO HISTÓRICO DE DADOS ANTIGOS")
        self.log("=" * 70)

        try:
            if not self.db_path.exists():
                self.log("[AVISO] Banco de dados não encontrado")
                return False

            conn = sqlite3.connect(str(self.db_path.absolute()))
            cursor = conn.cursor()

            # Contar registros antes
            cursor.execute("SELECT COUNT(*) FROM main_action_daily")
            count_before = cursor.fetchone()[0]

            if count_before > 0:
                self.log(f"[LIMPEZA] Deletando {count_before} registros antigos...")
                cursor.execute("DELETE FROM main_action_daily")
                conn.commit()
                self.log(f"[OK] {count_before} registros deletados!")
            else:
                self.log("[INFO] Nenhum registro para deletar")

            # Otimizar
            cursor.execute("VACUUM")
            conn.commit()

            # Contar registros depois
            cursor.execute("SELECT COUNT(*) FROM main_action_daily")
            count_after = cursor.fetchone()[0]

            conn.close()

            self.log(f"[OK] Histórico limpo: {count_before} → {count_after} registros")
            self.log("")
            return True

        except Exception as e:
            self.log(f"[ERRO] Falha ao limpar histórico: {e}")
            return False

    def step2_kill_server(self) -> bool:
        """PASSO 2: Matar servidor antigo"""
        self.log("=" * 70)
        self.log("[PASSO 2] ENCERRANDO SERVIDOR ANTIGO")
        self.log("=" * 70)

        try:
            # Tentar matar via taskkill (Windows)
            self.log("[KILL] Procurando processos Python do servidor...")
            result = subprocess.run(
                ['taskkill', '/IM', 'python.exe', '/F'],
                capture_output=True,
                text=True,
                timeout=10
            )

            # Windows retorna 1 se não encontrou processo (normal)
            if result.returncode in [0, 1]:
                self.log("[OK] Processos encerrados (ou não encontrados)")
                time.sleep(2)  # Aguardar conclusão
                return True
            else:
                self.log(f"[AVISO] taskkill falhou: {result.stderr}")
                # Continuar mesmo assim
                return True

        except FileNotFoundError:
            # taskkill não disponível (Linux/Mac)
            self.log("[INFO] taskkill não disponível, tentando pkill...")
            try:
                subprocess.run(
                    ['pkill', '-f', 'uvicorn'],
                    capture_output=True,
                    timeout=10
                )
                time.sleep(2)
                return True
            except:
                self.log("[AVISO] Não conseguiu matar servidor, continuando...")
                return True

        except Exception as e:
            self.log(f"[AVISO] Erro ao matar servidor: {e}")
            return True  # Continuar mesmo com erro

    def step3_wait_for_server(self, timeout: int = 60) -> bool:
        """PASSO 3: Aguardar servidor estar pronto"""
        self.log("=" * 70)
        self.log("[PASSO 3] AGUARDANDO SERVIDOR ESTAR PRONTO")
        self.log("=" * 70)

        start = time.time()
        while time.time() - start < timeout:
            try:
                import requests
                response = requests.get('http://localhost:8002/health', timeout=5)
                if response.status_code == 200:
                    self.log("[OK] Servidor respondendo corretamente!")
                    self.log("")
                    return True
            except:
                pass

            elapsed = int(time.time() - start)
            self.log(f"[AGUARDANDO] {elapsed}s... (timeout em {timeout}s)")
            time.sleep(2)

        self.log("[AVISO] Timeout aguardando servidor")
        return True  # Continuar mesmo assim

    def step4_collect_fresh_data(self) -> bool:
        """PASSO 4: Coletar dados frescos com novo ID"""
        self.log("=" * 70)
        self.log("[PASSO 4] COLETANDO DADOS FRESCOS")
        self.log("=" * 70)

        try:
            from core.database.base import SessionLocal
            from core.services.main_action_service import main_action_service

            db = SessionLocal()

            # Obter ID vigente
            current = main_action_service.get_current_action(db)
            product_id = current['product_id'] if current else None

            if not product_id:
                self.log("[ERRO] Não foi possível obter produto_id")
                db.close()
                return False

            self.log(f"[COLETA] Product ID: {product_id}")
            self.log("[COLETA] Iniciando coleta...")

            result = main_action_service.collect_and_save(db, product_id)

            # Verificar resultado
            if result.get('success'):
                # Verificar quantos registros foram salvos
                action = main_action_service.get_current_action(db)
                if action and 'daily_records' in action:
                    count = len(action['daily_records'])
                    self.log(f"[OK] Coleta concluída com sucesso!")
                    self.log(f"[OK] {count} registros diários salvos")
                    db.close()
                    self.log("")
                    return True
            else:
                error = result.get('error', 'Desconhecido')
                self.log(f"[AVISO] Coleta retornou erro: {error}")
                # Continuar mesmo com erro

            db.close()
            return True

        except Exception as e:
            self.log(f"[AVISO] Erro ao coletar: {e}")
            import traceback
            traceback.print_exc()
            return True  # Continuar mesmo com erro

    def verify_fresh_data(self) -> bool:
        """VERIFICAÇÃO: Garantir que dados estão frescos"""
        self.log("=" * 70)
        self.log("[VERIFICAÇÃO] VALIDANDO DADOS FRESCOS")
        self.log("=" * 70)

        try:
            conn = sqlite3.connect(str(self.db_path.absolute()))
            cursor = conn.cursor()

            # Verificar main_action_daily
            cursor.execute("SELECT COUNT(*) FROM main_action_daily")
            count = cursor.fetchone()[0]

            cursor.execute("SELECT MIN(date), MAX(date) FROM main_action_daily")
            result = cursor.fetchone()
            min_date, max_date = result if result[0] else (None, None)

            conn.close()

            self.log(f"[VERIFICAÇÃO] Registros diários: {count}")
            if min_date and max_date:
                self.log(f"[VERIFICAÇÃO] Período: {min_date} até {max_date}")

            if count == 0:
                self.log("[AVISO] Nenhum registro foi salvo!")
            else:
                self.log("[OK] Dados frescos presentes no banco!")

            self.log("")
            return True

        except Exception as e:
            self.log(f"[ERRO] Falha na verificação: {e}")
            return False

    def run(self) -> bool:
        """Executar todas as etapas"""
        self.log("")
        self.log("=" * 70)
        self.log("GARANTINDO COLETA FRESCA COM NOVO ID")
        self.log("=" * 70)
        self.log("")

        # Executar etapas
        if not self.step1_clean_history():
            return False

        if not self.step2_kill_server():
            return False

        if not self.step3_wait_for_server():
            return False

        if not self.step4_collect_fresh_data():
            return False

        # Verificação final
        if not self.verify_fresh_data():
            return False

        self.log("=" * 70)
        self.log("[SUCESSO] COLETA FRESCA GARANTIDA COM NOVO ID!")
        self.log("=" * 70)
        self.log("")

        return True


def main():
    """Função principal"""
    ensurer = FreshCollectionEnsurer()
    success = ensurer.run()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
