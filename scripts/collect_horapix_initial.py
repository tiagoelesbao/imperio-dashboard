#!/usr/bin/env python3
"""
Script para executar coleta inicial do Hora do Pix
Usado pelos scripts .bat de inicialização
"""
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def main():
    """Executar coleta inicial do Hora do Pix"""
    try:
        print("[HORAPIX] Iniciando coleta dos sorteios...")

        from core.database import SessionLocal
        from clients.imperio.services.horapix_service import horapix_service

        # Criar sessão do banco
        db = SessionLocal()

        try:
            # Executar coleta
            result = horapix_service.collect_and_save(db, fetch_details=False)

            if result.get('success'):
                data = result.get('data', {})
                totals = data.get('totals', {})

                print(f"[HORAPIX] Coleta realizada com sucesso!")
                print(f"[HORAPIX] Sorteios: {totals.get('total_draws', 0)}")
                print(f"[HORAPIX] Receita: R$ {totals.get('total_revenue', 0):,.2f}")
                print(f"[HORAPIX] Taxa (3%): R$ {totals.get('total_platform_fee', 0):,.2f}")
                print(f"[HORAPIX] Lucro: R$ {totals.get('total_profit', 0):,.2f}")
                print(f"[HORAPIX] ROI: {totals.get('total_roi', 0):.2f}%")
                print(f"[HORAPIX] Dados salvos no banco!")
                return 0
            else:
                error = result.get('error', 'Erro desconhecido')
                print(f"[HORAPIX] ERRO na coleta: {error}")
                return 1

        finally:
            db.close()

    except Exception as e:
        print(f"[HORAPIX] ERRO: {str(e)[:200]}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
