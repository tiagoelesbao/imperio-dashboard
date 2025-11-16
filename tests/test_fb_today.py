#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Testa coleta de custos do Facebook incluindo o dia atual"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import date, timedelta
from core.services.facebook_collector import facebook_collector
from core.services.main_action_service import main_action_service
from core.database.base import SessionLocal

def test_facebook_today():
    print("\n" + "="*80)
    print("TESTE: CUSTOS DO FACEBOOK INCLUINDO DIA ATUAL")
    print("="*80)

    # Testar coleta do Facebook para hoje
    today = date.today()
    yesterday = today - timedelta(days=1)

    print(f"\nData de hoje: {today}")
    print("-"*40)

    # Testar coleta só de hoje
    print("\n[1] Testando coleta APENAS do dia atual...")
    result_today = facebook_collector.get_facebook_costs_by_day(
        product_id="teste",
        start_date=today,
        end_date=today
    )

    if result_today:
        for day in result_today:
            print(f"   {day['date']}: R$ {day['spend']:.2f}")
    else:
        print("   Nenhum dado retornado")

    # Testar coleta dos últimos 2 dias
    print(f"\n[2] Testando coleta de {yesterday} até {today}...")
    result_period = facebook_collector.get_facebook_costs_by_day(
        product_id="teste",
        start_date=yesterday,
        end_date=today
    )

    total = 0
    if result_period:
        for day in result_period:
            spend = day['spend']
            total += spend
            print(f"   {day['date']}: R$ {spend:.2f}")
        print(f"   TOTAL: R$ {total:.2f}")
    else:
        print("   Nenhum dado retornado")

    # Agora testar coleta completa da ação principal
    print("\n[3] Testando coleta completa da ação principal...")
    print("-"*40)

    db = SessionLocal()
    try:
        product_id = "6916292bf6051e4133d86ef9"
        result = main_action_service.collect_and_save(db, product_id)

        if result.get('success'):
            print("[OK] Ação atualizada com sucesso!")

            # Buscar dados atualizados
            from core.models.main_action import MainAction, MainActionDaily

            action = db.query(MainAction).filter(MainAction.id == result.get('action_id')).first()
            if action:
                print(f"\nDados Gerais:")
                print(f"  Nome: {action.name}")
                print(f"  Receita Total: R$ {action.total_revenue:.2f}")
                print(f"  Custo Facebook Total: R$ {action.total_fb_cost:.2f}")
                print(f"  ROI Total: {action.total_roi:.2f}%")

                # Verificar dados diários
                daily_records = db.query(MainActionDaily).filter(
                    MainActionDaily.action_id == action.id
                ).order_by(MainActionDaily.date.desc()).limit(3).all()

                print(f"\nÚltimos registros diários:")
                for record in daily_records:
                    is_today = str(record.date) == str(today)
                    marker = " <-- HOJE" if is_today else ""
                    print(f"  {record.date}: Receita R$ {record.daily_revenue:.2f} | FB R$ {record.daily_fb_cost:.2f} | ROI {record.daily_roi:.2f}%{marker}")

                # Verificar se o dia atual tem custos do Facebook
                today_record = db.query(MainActionDaily).filter(
                    MainActionDaily.action_id == action.id,
                    MainActionDaily.date == today
                ).first()

                if today_record:
                    print(f"\n[INFO] Dados do dia atual ({today}):")
                    print(f"  Receita: R$ {today_record.daily_revenue:.2f}")
                    print(f"  Custo Facebook: R$ {today_record.daily_fb_cost:.2f}")
                    print(f"  Lucro: R$ {today_record.daily_profit:.2f}")
                    print(f"  ROI: {today_record.daily_roi:.2f}%")

                    if today_record.daily_fb_cost > 0:
                        print("\n✅ SUCESSO: Custos do Facebook do dia atual estão sendo rastreados!")
                        print(f"   Valor atualizado: R$ {today_record.daily_fb_cost:.2f}")
                    else:
                        print("\n⚠️  AVISO: Custos do Facebook do dia atual ainda zerados")
                        print("   Possível causa: Sem gastos hoje ou delay na API")
                else:
                    print(f"\n⚠️  Nenhum registro encontrado para hoje ({today})")

        else:
            print(f"[ERRO] Falha ao atualizar: {result.get('error')}")

    finally:
        db.close()

    print("\n" + "="*80)
    print("Teste concluído!")
    print("O scheduler atualizará automaticamente a cada 30 minutos (XX:00 e XX:30)")
    print("="*80)

if __name__ == "__main__":
    test_facebook_today()