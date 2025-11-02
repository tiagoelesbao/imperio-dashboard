"""
Serviço de gerenciamento dos dados Hora do Pix
"""
from sqlalchemy.orm import Session
from sqlalchemy import desc, func
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

from core.services.horapix_collector import horapix_collector
from core.models.horapix import HoraPixCollection, HoraPixDraw

logger = logging.getLogger(__name__)


class HoraPixService:
    """Serviço para gerenciamento dos dados Hora do Pix"""

    def collect_and_save(self, db: Session, fetch_details: bool = False) -> Dict:
        """
        Coleta dados da API e salva no banco

        Args:
            db: Sessão do banco de dados
            fetch_details: Se True, busca detalhes de cada sorteio

        Returns:
            Dict com resultado da operação
        """
        try:
            logger.info("Iniciando coleta e salvamento Hora do Pix")

            # Coletar dados usando API com autenticação dinâmica
            result = horapix_collector.collect_all_data(fetch_details=fetch_details)

            if not result.get('success'):
                return {
                    'success': False,
                    'error': result.get('error', 'Erro desconhecido')
                }

            data = result.get('data', {})
            totals = data.get('totals', {})
            draws = data.get('draws', [])

            # Salvar registro de coleta
            collection = HoraPixCollection(
                total_draws=totals.get('total_draws', 0),
                active_draws=totals.get('active_draws', 0),
                finished_draws=totals.get('finished_draws', 0),
                total_prize_value=totals.get('total_prize_value', 0),
                total_revenue=totals.get('total_revenue', 0),
                total_platform_fee=totals.get('total_platform_fee', 0),
                total_profit=totals.get('total_profit', 0),
                total_roi=totals.get('total_roi', 0),
                raw_data=data
            )
            db.add(collection)

            # Salvar/atualizar sorteios individuais
            for draw_data in draws:
                draw_id = draw_data.get('id')
                if not draw_id:
                    continue

                # Verificar se já existe
                existing = db.query(HoraPixDraw).filter(
                    HoraPixDraw.draw_id == draw_id
                ).first()

                if existing:
                    # Atualizar todos os campos (incluindo prize_value que pode ter sido corrigido)
                    existing.title = draw_data.get('title', '')
                    existing.status = draw_data.get('status', '')
                    existing.prize_value = draw_data.get('prize_value', 0)
                    existing.price = draw_data.get('price', 0)
                    existing.qty_paid = draw_data.get('qty_paid', 0)
                    existing.qty_free = draw_data.get('qty_free', 0)
                    existing.qty_total = draw_data.get('qty_total', 0)
                    existing.revenue = draw_data.get('revenue', 0)
                    existing.platform_fee = draw_data.get('platform_fee', 0)
                    existing.profit = draw_data.get('profit', 0)
                    existing.roi = draw_data.get('roi', 0)
                    existing.participants = draw_data.get('participants', 0)
                    existing.ticket_medio = draw_data.get('ticket_medio', 0)
                    existing.top_buyers = draw_data.get('top_buyers', [])
                    existing.top_regions = draw_data.get('top_regions', [])
                else:
                    # Criar novo
                    draw = HoraPixDraw(
                        draw_id=draw_id,
                        title=draw_data.get('title', ''),
                        status=draw_data.get('status', ''),
                        prize_value=draw_data.get('prize_value', 0),
                        price=draw_data.get('price', 0),
                        qty_paid=draw_data.get('qty_paid', 0),
                        qty_free=draw_data.get('qty_free', 0),
                        qty_total=draw_data.get('qty_total', 0),
                        revenue=draw_data.get('revenue', 0),
                        platform_fee=draw_data.get('platform_fee', 0),
                        profit=draw_data.get('profit', 0),
                        roi=draw_data.get('roi', 0),
                        participants=draw_data.get('participants', 0),
                        ticket_medio=draw_data.get('ticket_medio', 0),
                        created_at=draw_data.get('created_at', ''),
                        draw_date=draw_data.get('draw_date', ''),
                        top_buyers=draw_data.get('top_buyers', []),
                        top_regions=draw_data.get('top_regions', [])
                    )
                    db.add(draw)

            db.commit()

            logger.info(f"Dados salvos: {len(draws)} sorteios")

            return {
                'success': True,
                'message': f'{len(draws)} sorteios processados e salvos',
                'data': {
                    'totals': totals,
                    'collection_id': collection.id
                }
            }

        except Exception as e:
            db.rollback()
            logger.error(f"Erro ao salvar dados: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_latest_collection(self, db: Session) -> Optional[Dict]:
        """Retorna os dados da última coleta"""
        try:
            collection = db.query(HoraPixCollection).order_by(
                desc(HoraPixCollection.collection_time)
            ).first()

            if not collection:
                return None

            return {
                'collection_time': collection.collection_time.isoformat(),
                'totals': {
                    'total_draws': collection.total_draws,
                    'active_draws': collection.active_draws,
                    'finished_draws': collection.finished_draws,
                    'total_prize_value': collection.total_prize_value,
                    'total_revenue': collection.total_revenue,
                    'total_platform_fee': collection.total_platform_fee,
                    'total_profit': collection.total_profit,
                    'total_roi': collection.total_roi
                },
                'draws': collection.raw_data.get('draws', []) if collection.raw_data else []
            }

        except Exception as e:
            logger.error(f"Erro ao buscar última coleta: {e}")
            return None

    def get_draws_today(self, db: Session) -> List[Dict]:
        """Retorna todos os sorteios do dia atual"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            draws = db.query(HoraPixDraw).filter(
                HoraPixDraw.collection_time >= today,
                HoraPixDraw.collection_time < tomorrow
            ).all()

            return [self._draw_to_dict(draw) for draw in draws]

        except Exception as e:
            logger.error(f"Erro ao buscar sorteios do dia: {e}")
            return []

    def get_draw_by_id(self, db: Session, draw_id: str) -> Optional[Dict]:
        """Retorna dados de um sorteio específico"""
        try:
            draw = db.query(HoraPixDraw).filter(
                HoraPixDraw.draw_id == draw_id
            ).first()

            if not draw:
                return None

            return self._draw_to_dict(draw)

        except Exception as e:
            logger.error(f"Erro ao buscar sorteio {draw_id}: {e}")
            return None

    def get_statistics_today(self, db: Session) -> Dict:
        """Retorna estatísticas do dia"""
        try:
            today = datetime.now().date()
            tomorrow = today + timedelta(days=1)

            # Buscar todas as coletas do dia
            collections = db.query(HoraPixCollection).filter(
                HoraPixCollection.collection_time >= today,
                HoraPixCollection.collection_time < tomorrow
            ).all()

            if not collections:
                return self._empty_statistics()

            # Última coleta
            latest = collections[-1]

            # Evolução ao longo do dia
            evolution = [
                {
                    'time': c.collection_time.strftime('%H:%M'),
                    'revenue': c.total_revenue,
                    'profit': c.total_profit,
                    'roi': c.total_roi
                }
                for c in collections
            ]

            return {
                'totals': {
                    'total_draws': latest.total_draws,
                    'active_draws': latest.active_draws,
                    'finished_draws': latest.finished_draws,
                    'total_prize_value': latest.total_prize_value,
                    'total_revenue': latest.total_revenue,
                    'total_platform_fee': latest.total_platform_fee,
                    'total_profit': latest.total_profit,
                    'total_roi': latest.total_roi
                },
                'evolution': evolution,
                'collections_count': len(collections)
            }

        except Exception as e:
            logger.error(f"Erro ao calcular estatísticas: {e}")
            return self._empty_statistics()

    def _draw_to_dict(self, draw: HoraPixDraw) -> Dict:
        """Converte modelo Draw para dicionário"""
        return {
            'id': draw.draw_id,
            'title': draw.title,
            'status': draw.status,
            'prize_value': draw.prize_value,
            'price': draw.price,
            'qty_paid': draw.qty_paid,
            'qty_free': draw.qty_free,
            'qty_total': draw.qty_total,
            'revenue': draw.revenue,
            'profit': draw.profit,
            'roi': draw.roi,
            'participants': draw.participants,
            'ticket_medio': draw.ticket_medio,
            'top_buyers': draw.top_buyers or [],
            'top_regions': draw.top_regions or [],
            'collection_time': draw.collection_time.isoformat(),
            'created_at': draw.created_at,
            'draw_date': draw.draw_date
        }

    def _empty_statistics(self) -> Dict:
        """Retorna estrutura vazia de estatísticas"""
        return {
            'totals': {
                'total_draws': 0,
                'active_draws': 0,
                'finished_draws': 0,
                'total_prize_value': 0,
                'total_revenue': 0,
                'total_platform_fee': 0,
                'total_profit': 0,
                'total_roi': 0
            },
            'evolution': [],
            'collections_count': 0
        }


# Instância global
horapix_service = HoraPixService()
