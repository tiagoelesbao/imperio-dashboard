#!/usr/bin/env python3
"""
Teste rápido para verificar se há dados Hora do Pix no banco
"""
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.database import SessionLocal
from core.models.horapix import HoraPixCollection, HoraPixDraw

def main():
    """Teste rápido"""
    print("=" * 60)
    print("VERIFICACAO RAPIDA - HORA DO PIX")
    print("=" * 60)
    print()

    db = SessionLocal()

    try:
        # Verificar coletas
        collections_count = db.query(HoraPixCollection).count()
        draws_count = db.query(HoraPixDraw).count()

        print(f"Colecoes no banco: {collections_count}")
        print(f"Sorteios no banco: {draws_count}")
        print()

        if collections_count == 0:
            print("AVISO: Nenhuma coleta encontrada!")
            print("Execute: POST http://localhost:8002/api/imperio/horapix/collect")
            print("Ou teste o coletor: python test_horapix_selenium.py")
        else:
            # Mostrar última coleta
            latest = db.query(HoraPixCollection).order_by(
                HoraPixCollection.collection_time.desc()
            ).first()

            print(f"Ultima coleta: {latest.collection_time}")
            print(f"  Total sorteios: {latest.total_draws}")
            print(f"  Receita: R$ {latest.total_revenue:.2f}")
            print(f"  Taxa (3%): R$ {latest.total_platform_fee:.2f}")
            print(f"  Lucro: R$ {latest.total_profit:.2f}")
            print(f"  ROI: {latest.total_roi:.2f}%")

    finally:
        db.close()

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
