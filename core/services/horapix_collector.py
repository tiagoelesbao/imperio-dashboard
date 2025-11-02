"""
Coletor de dados da API Hora do Pix
Coleta informações de sorteios ativos e finalizados
"""
import requests
from datetime import datetime, timedelta
import logging
from typing import Dict, List, Optional
import re
import os
from pathlib import Path

logger = logging.getLogger(__name__)


class HoraPixCollector:
    """Coletor de dados dos sorteios Hora do Pix"""

    def __init__(self):
        # Configurações de API (mesmo sistema do coletor principal)
        self.base_url = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api"
        self.login_url = f"{self.base_url}/auth/login"
        self.dashboard_url = "https://painel.imperiopremioss.com/dashboard"

        # Credenciais (mesmas do sistema principal)
        self.USERNAME = "tiago"
        self.PASSWORD = "Tt!1zxcqweqweasd"

    def _get_auth_token(self) -> Optional[str]:
        """Obter token de autenticação - SEMPRE novo token a cada coleta"""
        logger.info("Obtendo novo token de autenticacao...")

        try:
            payload = {
                "email": self.USERNAME,
                "password": self.PASSWORD
            }
            headers = {
                "Content-Type": "application/json",
                "Accept": "application/json"
            }

            response = requests.post(self.login_url, json=payload, headers=headers)

            if response.status_code == 200:
                data = response.json()
                token = data.get("accessToken")
                logger.info("✅ Token obtido com sucesso")
                return token
            else:
                logger.error(f"❌ Erro ao obter token: {response.status_code} - {response.text}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro na autenticacao: {e}")
            return None

    def _create_headers(self, token: str) -> dict:
        """Cria headers de requisição com token"""
        return {
            'authorization': f'Bearer {token}',
            'accept': 'application/json, text/plain, */*',
            'origin': 'https://painel.imperiopremioss.com',
            'referer': 'https://painel.imperiopremioss.com/'
        }

    def extract_prize_value(self, title: str) -> float:
        """Extrai o valor do prêmio do título - suporta formato com ponto de milhar"""
        try:
            # Procura por padrões como "R$1.000", "R$ 1.000", "R$500", "R$ 500,00"
            # Captura: R$1.000 ou R$ 1.000,00 ou R$500
            # Regex corrigido para Python 3.13: R[$] ao invés de R\$?
            match = re.search(r'R[$]\s*([\d.,]+)', title, re.IGNORECASE)
            if match:
                value_str = match.group(1)

                # Se tem vírgula e ponto, é formato brasileiro: 1.000,00
                if '.' in value_str and ',' in value_str:
                    # Remove ponto (separador de milhar) e troca vírgula por ponto
                    value_str = value_str.replace('.', '').replace(',', '.')
                # Se tem apenas ponto e dígitos depois, pode ser milhar (1.000) ou decimal (1.5)
                elif '.' in value_str:
                    parts = value_str.split('.')
                    # Se após o ponto tem 3 dígitos, é separador de milhar (1.000 = 1000)
                    if len(parts[-1]) == 3:
                        value_str = value_str.replace('.', '')
                    # Senão, é decimal (1.5 mantém)
                # Se tem apenas vírgula, é decimal brasileiro (500,50)
                elif ',' in value_str:
                    value_str = value_str.replace(',', '.')

                return float(value_str)
            return 0.0
        except Exception as e:
            logger.error(f"Erro ao extrair valor do título '{title}': {e}")
            return 0.0

    def get_tomorrow_date(self) -> str:
        """Retorna data de amanhã no formato YYYY-MM-DD"""
        tomorrow = datetime.now() + timedelta(days=1)
        return tomorrow.strftime('%Y-%m-%d')

    def fetch_products(self, token: str) -> List[Dict]:
        """Busca produtos/sorteios do DIA SEGUINTE (Hora do Pix)"""
        try:
            # Data de amanhã para filtrar sorteios Hora do Pix
            draw_date = self.get_tomorrow_date()

            url = f"{self.base_url}/products"
            logger.info(f"Buscando sorteios Hora do Pix para {draw_date}...")

            headers = self._create_headers(token)

            # Adicionar parâmetro drawDate para filtrar apenas sorteios do dia seguinte
            params = {
                'drawDate': draw_date
            }

            response = requests.get(
                url,
                headers=headers,
                params=params,
                timeout=30
            )

            if response.status_code == 200:
                data = response.json()
                products = data.get('products', [])

                # Filtrar novamente do lado do cliente para garantir
                filtered_products = [
                    p for p in products
                    if p.get('drawDate', '').startswith(draw_date)
                ]

                logger.info(f"✅ Sorteios encontrados: {len(filtered_products)} (data: {draw_date})")

                if len(products) != len(filtered_products):
                    logger.info(f"⚠️ Filtrados {len(products) - len(filtered_products)} sorteios de outras datas")

                return filtered_products
            else:
                logger.error(f"❌ Erro ao buscar produtos: Status {response.status_code}")
                logger.error(f"Response: {response.text[:200]}")
                return []

        except Exception as e:
            logger.error(f"❌ Erro ao buscar produtos: {e}")
            return []

    def fetch_product_details(self, product_id: str, token: str) -> Optional[Dict]:
        """Busca detalhes completos de um sorteio específico"""
        try:
            url = f"{self.base_url}/products/{product_id}/dashboard"

            logger.debug(f"Buscando detalhes do sorteio {product_id}")

            headers = self._create_headers(token)
            response = requests.get(
                url,
                headers=headers,
                timeout=30
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"⚠️ Erro ao buscar detalhes do produto {product_id}: Status {response.status_code}")
                return None

        except Exception as e:
            logger.error(f"❌ Erro ao buscar detalhes do produto {product_id}: {e}")
            return None

    def process_product(self, product: Dict, details: Optional[Dict] = None) -> Dict:
        """Processa dados de um produto/sorteio"""
        try:
            product_id = product.get('_id', '')
            title = product.get('title', '')
            status = product.get('status', 'unknown')

            # Dados básicos
            numbers_config = product.get('numbersConfig', {})
            price = float(numbers_config.get('price', 0))
            qty_paid = int(numbers_config.get('qtyPaid', 0))
            qty_free = int(numbers_config.get('qtyFree', 0))
            qty_total = qty_paid + qty_free

            # Extrair valor do prêmio - SEMPRE DO TÍTULO (fonte confiável)
            # O campo 'awards' da API retorna valores incorretos/inconsistentes
            prize_value = self.extract_prize_value(title)

            # Se não conseguiu extrair do título, tentar awards como fallback
            if prize_value == 0.0:
                awards = product.get('awards', [])
                if awards and len(awards) > 0:
                    prize_value = self.extract_prize_value(awards[0])
                    logger.warning(f"⚠️ Valor extraído de 'awards' (título não tinha): {title} → R$ {prize_value}")

            # Calcular receita
            revenue = price * qty_paid

            # Calcular taxa da plataforma (3% da receita)
            platform_fee = revenue * 0.03

            # Calcular lucro (receita - prêmio - taxa)
            profit = revenue - prize_value - platform_fee

            # Calcular ROI considerando prêmio e taxa
            total_cost = prize_value + platform_fee
            roi = (profit / total_cost * 100) if total_cost > 0 else 0

            # Dados do dashboard detalhado (se disponível)
            participants = 0
            ticket_medio = 0.0
            top_buyers = []
            top_regions = []

            if details:
                paid_info = details.get('paid', {})
                participants = int(details.get('participantes', 0))
                ticket_medio = float(paid_info.get('ticketMedio', 0))
                top_buyers = details.get('top10Compradores', [])[:5]  # Top 5
                top_regions = details.get('top10Regioes', [])[:5]  # Top 5

            result = {
                'id': product_id,
                'title': title,
                'status': status,
                'prize_value': prize_value,
                'price': price,
                'qty_paid': qty_paid,
                'qty_free': qty_free,
                'qty_total': qty_total,
                'revenue': revenue,
                'platform_fee': platform_fee,
                'profit': profit,
                'roi': roi,
                'participants': participants,
                'ticket_medio': ticket_medio,
                'top_buyers': top_buyers,
                'top_regions': top_regions,
                'created_at': product.get('createdAt', ''),
                'draw_date': product.get('drawDate', '')
            }

            return result

        except Exception as e:
            logger.error(f"Erro ao processar produto: {e}")
            return {}

    def collect_all_data(self, fetch_details: bool = False) -> Dict:
        """
        Coleta todos os dados dos sorteios

        Args:
            fetch_details: Se True, busca detalhes de cada sorteio (mais lento)
        """
        try:
            logger.info("=" * 60)
            logger.info("INICIANDO COLETA HORA DO PIX")
            logger.info("=" * 60)

            # Obter token de autenticação
            token = self._get_auth_token()
            if not token:
                logger.error("❌ Falha ao obter token de autenticação")
                return {
                    'success': False,
                    'error': 'Falha na autenticação',
                    'data': None
                }

            # Buscar todos os produtos
            products = self.fetch_products(token)

            if not products:
                logger.warning("⚠️ Nenhum produto encontrado")
                return {
                    'success': False,
                    'error': 'Nenhum produto encontrado',
                    'data': None
                }

            # Processar produtos
            processed_products = []
            active_draws = []
            finished_draws = []

            for product in products:
                # Buscar detalhes se solicitado
                details = None
                if fetch_details:
                    product_id = product.get('_id')
                    if product_id:
                        details = self.fetch_product_details(product_id, token)

                # Processar produto
                processed = self.process_product(product, details)

                if processed:
                    processed_products.append(processed)

                    # Classificar por status
                    status = processed.get('status', '')
                    if status == 'done':
                        finished_draws.append(processed)
                    elif status == 'active':
                        active_draws.append(processed)

            # Calcular totais com taxa de 3%
            total_prize_value = sum(p.get('prize_value', 0) for p in processed_products)
            total_revenue = sum(p.get('revenue', 0) for p in processed_products)
            total_platform_fee = sum(p.get('platform_fee', 0) for p in processed_products)
            total_profit = total_revenue - total_prize_value - total_platform_fee
            total_cost = total_prize_value + total_platform_fee
            total_roi = (total_profit / total_cost * 100) if total_cost > 0 else 0

            result = {
                'success': True,
                'collection_time': datetime.now().isoformat(),
                'data': {
                    'draws': processed_products,
                    'active_draws': active_draws,
                    'finished_draws': finished_draws,
                    'totals': {
                        'total_draws': len(processed_products),
                        'active_draws': len(active_draws),
                        'finished_draws': len(finished_draws),
                        'total_prize_value': total_prize_value,
                        'total_revenue': total_revenue,
                        'total_platform_fee': total_platform_fee,
                        'total_profit': total_profit,
                        'total_roi': total_roi
                    }
                }
            }

            logger.info("=" * 60)
            logger.info(f"✅ COLETA CONCLUÍDA COM SUCESSO!")
            logger.info(f"📊 Sorteios: {len(processed_products)} (Ativos: {len(active_draws)}, Finalizados: {len(finished_draws)})")
            logger.info(f"💰 Receita: R$ {total_revenue:,.2f}")
            logger.info(f"🎁 Prêmios: R$ {total_prize_value:,.2f}")
            logger.info(f"💳 Taxa (3%): R$ {total_platform_fee:,.2f}")
            logger.info(f"💵 Lucro: R$ {total_profit:,.2f}")
            logger.info(f"📈 ROI: {total_roi:.2f}%")
            logger.info("=" * 60)

            return result

        except Exception as e:
            logger.error(f"❌ Erro na coleta de dados: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return {
                'success': False,
                'error': str(e),
                'data': None
            }


# Instância global
horapix_collector = HoraPixCollector()
