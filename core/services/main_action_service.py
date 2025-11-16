#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Serviço de gerenciamento de Ações Principais
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional

from core.services.main_action_collector import main_action_collector
from core.models.main_action import MainAction, MainActionDaily

logger = logging.getLogger(__name__)


class MainActionService:
    """Serviço para gerenciamento de Ações Principais"""

    def collect_and_save(self, db: Session, product_id: str) -> Dict:
        """Coleta e salva dados de uma ação (sempre fresco, sem histórico)"""
        try:
            # Coletar dados
            result = main_action_collector.collect_full_action_data(product_id)

            if not result.get('success'):
                return result

            data = result.get('data', {})
            totals = data.get('totals', {})

            # Buscar ou criar ação
            action = db.query(MainAction).filter(
                MainAction.product_id == product_id
            ).first()

            # LIMPAR DADOS HISTÓRICOS ANTIGOS (para sempre manter apenas dados atuais)
            if action:
                db.query(MainActionDaily).filter(
                    MainActionDaily.action_id == action.id
                ).delete()
                logger.info(f"Dados históricos deletados para action_id={action.id}")

            if not action:
                action = MainAction(
                    product_id=product_id,
                    name=data.get('name'),
                    prize_value=data.get('prize_value'),
                    start_date=datetime.fromisoformat(data.get('start_date')).date() if data.get('start_date') else date.today(),
                    is_current=True
                )
                db.add(action)
                db.flush()  # Flush para obter o ID antes de usar

            # Atualizar dados
            action.name = data.get('name')
            action.prize_value = data.get('prize_value')
            action.end_date = datetime.fromisoformat(data.get('end_date')).date() if data.get('end_date') else None
            action.is_active = data.get('is_active', True)
            action.total_revenue = totals.get('revenue')
            action.total_orders = totals.get('orders')
            action.total_tickets = totals.get('tickets')
            action.total_fb_cost = totals.get('fb_cost')
            action.total_platform_fee = totals.get('platform_fee')
            action.total_profit = totals.get('profit')
            action.total_roi = totals.get('roi')
            action.raw_data = data
            action.updated_at = datetime.now()

            # Salvar registros diários
            orders_by_day = data.get('orders_by_day', [])
            fb_by_day_dict = {d['date']: d['spend'] for d in data.get('fb_by_day', [])}

            for order_day in orders_by_day:
                day_date = datetime.strptime(order_day['_id'], '%Y-%m-%d').date()
                daily_revenue = order_day.get('totalPorDia', 0)
                daily_orders = order_day.get('totalOrdensPorDia', 0)
                daily_tickets = order_day.get('totalNumerosPorDia', 0)
                daily_fb_cost = fb_by_day_dict.get(order_day['_id'], 0.0)
                daily_platform_fee = daily_revenue * 0.03

                # Buscar ou criar registro
                daily = db.query(MainActionDaily).filter(
                    MainActionDaily.action_id == action.id,
                    MainActionDaily.date == day_date
                ).first()

                if not daily:
                    daily = MainActionDaily(action_id=action.id, date=day_date)
                    db.add(daily)

                daily.daily_revenue = daily_revenue
                daily.daily_orders = daily_orders
                daily.daily_tickets = daily_tickets
                daily.daily_fb_cost = daily_fb_cost
                daily.daily_platform_fee = daily_platform_fee
                daily.daily_profit = daily_revenue - daily_fb_cost - daily_platform_fee
                daily.daily_roi = (daily.daily_profit / (daily_fb_cost + daily_platform_fee) * 100) if (daily_fb_cost + daily_platform_fee) > 0 else 0
                daily.daily_margin = (daily.daily_profit / daily_revenue * 100) if daily_revenue > 0 else 0

            db.commit()

            return {'success': True, 'action_id': action.id}

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao salvar: {e}")
            return {'success': False, 'error': str(e)}

    def get_all_actions(self, db: Session, year: int = None) -> List[Dict]:
        """Busca todas as ações (atual + históricas)"""
        try:
            query = db.query(MainAction).order_by(desc(MainAction.is_current), desc(MainAction.start_date))

            if year:
                start = date(year, 1, 1)
                end = date(year, 12, 31)
                query = query.filter(MainAction.start_date >= start, MainAction.start_date <= end)

            actions = query.all()

            return [self._action_to_dict(action) for action in actions]

        except Exception as e:
            logger.error(f"Erro ao buscar ações: {e}")
            return []

    def get_current_action(self, db: Session) -> Optional[Dict]:
        """Busca ação atual"""
        try:
            action = db.query(MainAction).filter(MainAction.is_current == True).first()
            return self._action_to_dict(action) if action else None
        except Exception as e:
            logger.error(f"Erro: {e}")
            return None

    def get_action_details(self, db: Session, action_id: int) -> Optional[Dict]:
        """Busca detalhes de uma ação com todos os dias"""
        try:
            action = db.query(MainAction).filter(MainAction.id == action_id).first()
            if not action:
                return None

            daily_records = db.query(MainActionDaily).filter(
                MainActionDaily.action_id == action_id
            ).order_by(MainActionDaily.date).all()

            return {
                **self._action_to_dict(action),
                'daily_records': [self._daily_to_dict(d) for d in daily_records]
            }

        except Exception as e:
            logger.error(f"Erro: {e}")
            return None

    def set_current_action(self, db: Session, product_id: str) -> Dict:
        """Define qual é a ação atual"""
        try:
            # Desmarcar todas
            db.query(MainAction).update({'is_current': False})

            # Marcar a especificada
            action = db.query(MainAction).filter(MainAction.product_id == product_id).first()
            if action:
                action.is_current = True
                db.commit()
                return {'success': True}
            else:
                return {'success': False, 'error': 'Ação não encontrada'}

        except Exception as e:
            db.rollback()
            logger.error(f"Erro: {e}")
            return {'success': False, 'error': str(e)}

    def _action_to_dict(self, action: MainAction) -> Dict:
        """Converte ação para dict"""
        return {
            'id': action.id,
            'product_id': action.product_id,
            'name': action.name,
            'prize_value': action.prize_value,
            'start_date': action.start_date.isoformat(),
            'end_date': action.end_date.isoformat() if action.end_date else None,
            'is_active': action.is_active,
            'is_current': action.is_current,
            'total_revenue': action.total_revenue,
            'total_orders': action.total_orders,
            'total_tickets': action.total_tickets,
            'total_fb_cost': action.total_fb_cost,
            'total_platform_fee': action.total_platform_fee,
            'total_profit': action.total_profit,
            'total_roi': action.total_roi
        }

    def _daily_to_dict(self, daily: MainActionDaily) -> Dict:
        """Converte registro diário para dict"""
        return {
            'date': daily.date.isoformat(),
            'daily_revenue': daily.daily_revenue,
            'daily_orders': daily.daily_orders,
            'daily_tickets': daily.daily_tickets,
            'daily_fb_cost': daily.daily_fb_cost,
            'daily_platform_fee': daily.daily_platform_fee,
            'daily_profit': daily.daily_profit,
            'daily_roi': daily.daily_roi,
            'daily_margin': daily.daily_margin
        }


# Instância global
main_action_service = MainActionService()
