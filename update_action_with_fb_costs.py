#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Force update action with Facebook costs"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.database.base import SessionLocal
from core.services.main_action_service import main_action_service

def update_action_with_facebook():
    print("\n" + "="*80)
    print("ATUALIZANDO ACAO PRINCIPAL COM CUSTOS DO FACEBOOK")
    print("="*80)

    db = SessionLocal()
    try:
        # Product ID da ação atual
        product_id = "6916292bf6051e4133d86ef9"

        print(f"\nAtualizando acao do produto: {product_id}")
        print("-"*40)

        # Coletar e salvar dados completos (incluindo Facebook)
        result = main_action_service.collect_and_save(db, product_id)

        if result.get('success'):
            print(f"[OK] Acao atualizada com sucesso!")
            print(f"     Action ID: {result.get('action_id')}")

            # Buscar detalhes atualizados
            from core.models.main_action import MainAction, MainActionDaily

            action = db.query(MainAction).filter(MainAction.id == result.get('action_id')).first()
            if action:
                print(f"\n[INFO] Dados atualizados:")
                print(f"  - Nome: {action.name}")
                print(f"  - Receita Total: R$ {action.total_revenue:.2f}")
                print(f"  - Custo Facebook Total: R$ {action.total_fb_cost:.2f}")
                print(f"  - Lucro Total: R$ {action.total_profit:.2f}")
                print(f"  - ROI Total: {action.total_roi:.2f}%")

                # Mostrar alguns registros diários
                daily_records = db.query(MainActionDaily).filter(
                    MainActionDaily.action_id == action.id
                ).limit(5).all()

                print(f"\n[INFO] Primeiros registros diarios:")
                for record in daily_records:
                    print(f"  {record.date}: Receita R$ {record.daily_revenue:.2f} | FB R$ {record.daily_fb_cost:.2f} | ROI {record.daily_roi:.2f}%")

        else:
            print(f"[ERRO] Falha ao atualizar: {result.get('error')}")

    finally:
        db.close()

    print("\n" + "="*80)
    print("Pronto! Recarregue a pagina do Imperio para ver os dados atualizados.")
    print("="*80)

if __name__ == "__main__":
    update_action_with_facebook()