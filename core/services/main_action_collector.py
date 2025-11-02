#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor de dados para Ação Principal
Coleta vendas por dia + custos Facebook Ads
"""
import re
import logging
import requests
from datetime import datetime, date
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class MainActionCollector:
    """Coletor de dados para Ação Principal"""

    def __init__(self):
        self.base_url = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br"
        self.painel_url = "https://painel.imperiopremioss.com"
        self.username, self.password = self._load_credentials()

    def _load_credentials(self) -> tuple:
        """Carrega credenciais do arquivo .env"""
        try:
            env_file = Path(__file__).parent.parent.parent / '.env'

            username = None
            password = None

            if env_file.exists():
                with open(env_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('API_USERNAME='):
                            username = line.split('=', 1)[1].strip()
                        elif line.startswith('API_PASSWORD='):
                            password = line.split('=', 1)[1].strip()

            if username and password:
                return username, password
            else:
                return "tiago", "Tt!1zxcqweqweasd"

        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            return "tiago", "Tt!1zxcqweqweasd"

    def _get_auth_token(self) -> Optional[str]:
        """Obtém token de autenticação"""
        try:
            # Usar a URL correta do backend
            login_url = f"{self.base_url}/api/auth/login"

            response = requests.post(
                login_url,
                json={"email": self.username, "password": self.password},  # Usar 'email' ao invés de 'username'
                timeout=10
            )

            if response.status_code == 200:
                data = response.json()
                token = data.get('accessToken') or data.get('token')  # Verificar ambos os campos
                if token:
                    logger.info("Token obtido com sucesso")
                    return token
                else:
                    logger.error("Token não encontrado na resposta")
                    return None
            else:
                logger.error(f"Erro ao fazer login: {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"Erro ao obter token: {e}")
            return None

    def _extract_prize_value(self, name: str) -> float:
        """Extrai o valor da premiação do nome do sorteio"""
        try:
            # Padrões para encontrar valores como "50 mil", "50k", "R$ 50.000"
            patterns = [
                r'(\d+)\s*mil',  # 50 mil
                r'(\d+)k',  # 50k
                r'R\$\s*([\d.]+\.?\d*)',  # R$ 50.000
                r'(\d+)\.000',  # 50.000
            ]

            for pattern in patterns:
                match = re.search(pattern, name, re.IGNORECASE)
                if match:
                    value_str = match.group(1).replace('.', '')
                    value = float(value_str)

                    # Se for "mil" ou "k", multiplicar por 1000
                    if 'mil' in pattern or 'k' in pattern:
                        value *= 1000

                    logger.info(f"Valor da premiação extraído: R$ {value:,.2f}")
                    return value

            logger.warning(f"Não foi possível extrair valor da premiação de: {name}")
            return 0.0

        except Exception as e:
            logger.error(f"Erro ao extrair valor da premiação: {e}")
            return 0.0

    def get_orders_by_day(self, product_id: str, token: str) -> Dict:
        """
        Busca vendas por dia do sorteio
        GET /api/product/{id}/ordersByDay
        """
        try:
            url = f"{self.base_url}/api/product/{product_id}/ordersByDay"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                logger.info(f"Vendas por dia coletadas: {len(data.get('somasPorDia', []))} dias")
                return {
                    'success': True,
                    'data': data
                }
            else:
                logger.error(f"Erro ao buscar vendas por dia: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Erro ao buscar vendas por dia: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_product_status(self, product_id: str, token: str) -> Dict:
        """
        Verifica se o sorteio está ativo
        GET /api/product/{id}/orders/total
        """
        try:
            url = f"{self.base_url}/api/product/{product_id}/orders/total"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            params = {
                "page": 0,
                "rowsPerPage": 5
            }

            response = requests.get(url, headers=headers, params=params, timeout=15)

            if response.status_code == 200:
                data = response.json()
                is_active = data.get('active', True)
                logger.info(f"Status do sorteio: {'Ativo' if is_active else 'Finalizado'}")
                return {
                    'success': True,
                    'is_active': is_active,
                    'data': data
                }
            else:
                logger.error(f"Erro ao buscar status: {response.status_code}")
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Erro ao buscar status: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_product_details(self, product_id: str, token: str) -> Dict:
        """Busca detalhes do produto (nome, etc)"""
        try:
            url = f"{self.base_url}/api/product/{product_id}"

            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers, timeout=15)

            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'data': data
                }
            else:
                return {
                    'success': False,
                    'error': f'HTTP {response.status_code}'
                }

        except Exception as e:
            logger.error(f"Erro ao buscar detalhes: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def get_facebook_costs_for_action(self, start_date: date, end_date: date = None) -> Dict:
        """
        Busca custos do Facebook Ads no período da ação
        Usa o mesmo sistema do ROI geral/perfil/grupo

        IMPORTANTE: Usa data de INÍCIO do sorteio até DIA ANTERIOR ao atual
        Para coleta hoje (23/10), busca 15/10 até 22/10 (dia anterior)
        """
        try:
            from core.services.data_collector import ImperioDataCollector
            from datetime import timedelta

            # Se end_date não fornecido, usar hoje
            if end_date is None:
                end_date = date.today()

            logger.info(f"Buscando custos FB: {start_date} até {end_date}")

            # Usar o coletor principal para buscar dados do Facebook
            collector = ImperioDataCollector()

            # Coletar dados do Facebook para todas as contas
            fb_by_day = []
            total_spend = 0.0

            # Para cada dia no período
            current_date = start_date
            while current_date <= end_date:
                day_spend = 0.0

                # Buscar gastos de todas as contas para este dia
                for account_id in collector.FACEBOOK_ACCOUNTS:
                    try:
                        spend_data = collector._collect_facebook_account(account_id, "today")
                        if spend_data and spend_data.get('spend_today', 0) > 0:
                            day_spend += spend_data['spend_today']
                    except Exception as e:
                        logger.warning(f"Erro ao buscar conta {account_id}: {e}")

                if day_spend > 0:
                    fb_by_day.append({
                        'date': current_date.strftime('%Y-%m-%d'),
                        'spend': day_spend
                    })
                    total_spend += day_spend

                current_date += timedelta(days=1)

            logger.info(f"Custos FB coletados: R$ {total_spend:,.2f}")

            return {
                'success': True,
                'total_spend': total_spend,
                'by_day': fb_by_day
            }

        except Exception as e:
            logger.error(f"Erro ao buscar custos Facebook: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def collect_full_action_data(self, product_id: str) -> Dict:
        """
        Coleta dados completos de uma ação principal
        """
        try:
            logger.info(f"Iniciando coleta de dados para ação: {product_id}")

            # Obter token
            token = self._get_auth_token()
            if not token:
                return {
                    'success': False,
                    'error': 'Falha ao obter token de autenticação'
                }

            # Buscar detalhes do produto
            details_result = self.get_product_details(product_id, token)
            if not details_result.get('success'):
                return {
                    'success': False,
                    'error': 'Falha ao buscar detalhes do produto'
                }

            product_data = details_result.get('data', {})
            product_name = product_data.get('title', 'Sorteio sem nome')

            # Extrair valor da premiação
            prize_value = self._extract_prize_value(product_name)

            # Buscar vendas por dia
            orders_result = self.get_orders_by_day(product_id, token)
            if not orders_result.get('success'):
                return {
                    'success': False,
                    'error': 'Falha ao buscar vendas por dia'
                }

            orders_data = orders_result.get('data', {})
            orders_by_day = orders_data.get('somasPorDia', [])
            total_revenue = orders_data.get('totalGeral', 0.0)

            # Buscar status
            status_result = self.get_product_status(product_id, token)
            is_active = status_result.get('is_active', True) if status_result.get('success') else True

            # Determinar período baseado na PRIMEIRA venda
            if orders_by_day:
                dates = [datetime.strptime(d['_id'], '%Y-%m-%d').date() for d in orders_by_day]
                start_date = min(dates)  # PRIMEIRA venda (ex: 15/10)
                end_date = max(dates)     # ÚLTIMA venda registrada

                logger.info(f"Período do sorteio: {start_date} até {end_date}")
                logger.info(f"Total de dias com vendas: {len(dates)}")
            else:
                # Se não há vendas, usar hoje como referência
                start_date = date.today()
                end_date = date.today()
                logger.warning("Nenhuma venda encontrada, usando data atual")

            # Buscar custos Facebook usando período correto
            # IMPORTANTE: start_date = primeira venda, end_date = dia anterior ao atual
            fb_result = self.get_facebook_costs_for_action(start_date, end_date=None)
            total_fb_cost = fb_result.get('total_spend', 0.0) if fb_result.get('success') else 0.0
            fb_by_day = fb_result.get('by_day', []) if fb_result.get('success') else []

            logger.info(f"Custos Facebook acumulados: R$ {total_fb_cost:,.2f}")

            # Calcular totais
            total_orders = sum(d.get('totalOrdensPorDia', 0) for d in orders_by_day)
            total_tickets = sum(d.get('totalNumerosPorDia', 0) for d in orders_by_day)
            total_platform_fee = total_revenue * 0.03  # Taxa 3%
            total_cost = prize_value + total_fb_cost + total_platform_fee
            total_profit = total_revenue - total_cost
            total_roi = (total_profit / total_cost * 100) if total_cost > 0 else 0

            return {
                'success': True,
                'data': {
                    'product_id': product_id,
                    'name': product_name,
                    'prize_value': prize_value,
                    'start_date': start_date.isoformat(),
                    'end_date': end_date.isoformat(),
                    'is_active': is_active,
                    'totals': {
                        'revenue': total_revenue,
                        'orders': total_orders,
                        'tickets': total_tickets,
                        'fb_cost': total_fb_cost,
                        'platform_fee': total_platform_fee,
                        'prize_cost': prize_value,
                        'total_cost': total_cost,
                        'profit': total_profit,
                        'roi': total_roi
                    },
                    'orders_by_day': orders_by_day,
                    'fb_by_day': fb_by_day,
                    'raw_product_data': product_data
                }
            }

        except Exception as e:
            logger.error(f"Erro na coleta completa: {e}")
            return {
                'success': False,
                'error': str(e)
            }


# Instância global
main_action_collector = MainActionCollector()
