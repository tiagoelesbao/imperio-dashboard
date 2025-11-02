#!/usr/bin/env python3
"""
Coletor de dados Hora do Pix usando Selenium
Usa o MESMO método do sistema principal - navegação com Selenium
"""

import os
import time
import logging
import re
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

logger = logging.getLogger(__name__)


class HoraPixCollectorSelenium:
    """Coletor de dados Hora do Pix usando Selenium"""

    def __init__(self):
        # Carregar credenciais do .env
        self.username, self.password = self._load_credentials()

        self.base_url = "https://painel.imperiopremioss.com"
        self.login_url = f"{self.base_url}/login"
        self.products_url = f"{self.base_url}/products"

    def _load_credentials(self) -> tuple:
        """Carrega credenciais do arquivo .env"""
        try:
            env_file = Path(__file__).parent.parent.parent / '.env'

            username = None
            password = None

            if env_file.exists():
                with open(env_file, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith('API_USERNAME='):
                            username = line.split('=', 1)[1].strip()
                        elif line.startswith('API_PASSWORD='):
                            password = line.split('=', 1)[1].strip()

            if username and password:
                logger.info("Credenciais carregadas do .env")
                return username, password
            else:
                logger.error("Credenciais não encontradas no .env")
                return "tiago", "Tt!1zxcqweqweasd"

        except Exception as e:
            logger.error(f"Erro ao carregar credenciais: {e}")
            return "tiago", "Tt!1zxcqweqweasd"

    def create_chrome_driver(self, headless=True):
        """Cria driver Chrome otimizado"""
        options = Options()

        if headless:
            options.add_argument("--headless")

        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--window-size=1920,1080")

        # Perfil temporário
        temp_profile = f"C:\\temp_chrome_horapix_{int(time.time())}"
        options.add_argument(f"--user-data-dir={temp_profile}")

        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)

        driver.set_page_load_timeout(30)
        driver.implicitly_wait(5)

        return driver, temp_profile

    def login(self, driver):
        """Faz login no painel"""
        try:
            logger.info("Acessando página de login...")
            driver.get(self.login_url)
            time.sleep(2)

            # Preencher credenciais
            logger.info("Preenchendo credenciais...")

            # Aguardar campos de login
            wait = WebDriverWait(driver, 10)

            # Tentar diferentes seletores comuns
            username_field = None
            password_field = None

            # Tentar por name
            try:
                username_field = driver.find_element(By.NAME, "username")
                password_field = driver.find_element(By.NAME, "password")
            except:
                pass

            # Tentar por type
            if not username_field:
                try:
                    username_field = driver.find_element(By.CSS_SELECTOR, "input[type='text'], input[type='email']")
                    password_field = driver.find_element(By.CSS_SELECTOR, "input[type='password']")
                except:
                    pass

            # Tentar por ID
            if not username_field:
                try:
                    username_field = driver.find_element(By.ID, "username")
                    password_field = driver.find_element(By.ID, "password")
                except:
                    pass

            if not username_field or not password_field:
                logger.error("Campos de login não encontrados")
                return False

            # Preencher
            username_field.clear()
            username_field.send_keys(self.username)

            password_field.clear()
            password_field.send_keys(self.password)

            time.sleep(1)

            # Clicar no botão de login
            try:
                login_btn = driver.find_element(By.CSS_SELECTOR, "button[type='submit']")
                login_btn.click()
            except:
                # Tentar submeter o formulário
                password_field.submit()

            logger.info("Aguardando login...")
            time.sleep(5)

            # Verificar se login foi bem-sucedido
            current_url = driver.current_url
            if "dashboard" in current_url or "products" in current_url:
                logger.info("✅ Login realizado com sucesso!")
                return True
            else:
                logger.warning(f"Login pode ter falhado. URL atual: {current_url}")
                return False

        except Exception as e:
            logger.error(f"Erro no login: {e}")
            return False

    def extract_prize_value(self, title: str) -> float:
        """Extrai o valor do prêmio do título"""
        try:
            match = re.search(r'R\\$?\\s*(\\d+(?:[.,]\\d+)?)', title, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '.')
                return float(value_str)
            return 0.0
        except Exception as e:
            logger.error(f"Erro ao extrair valor do título '{title}': {e}")
            return 0.0

    def scrape_products_page(self, driver) -> List[Dict]:
        """Extrai dados da página de produtos"""
        try:
            logger.info("Navegando para página de produtos...")
            driver.get(self.products_url)
            time.sleep(5)

            products = []

            # Tentar encontrar elementos de produtos
            # Isso depende da estrutura HTML do painel
            # Vamos tentar alguns seletores comuns

            product_elements = []

            # Tentar por classe
            try:
                product_elements = driver.find_elements(By.CLASS_NAME, "product-card")
            except:
                pass

            if not product_elements:
                try:
                    product_elements = driver.find_elements(By.CSS_SELECTOR, ".product, .card, .item")
                except:
                    pass

            if not product_elements:
                logger.warning("Nenhum elemento de produto encontrado na página")
                # Tentar capturar todo o HTML para debug
                page_html = driver.page_source
                logger.debug(f"HTML da página (primeiros 500 chars): {page_html[:500]}")
                return []

            logger.info(f"Encontrados {len(product_elements)} elementos de produto")

            for elem in product_elements:
                try:
                    # Extrair dados do elemento
                    # A estrutura exata depende do HTML do painel
                    # Vamos fazer uma extração genérica

                    text = elem.text

                    product = {
                        'id': '',
                        'title': '',
                        'status': 'active',
                        'prize_value': 0.0,
                        'qty_paid': 0,
                        'qty_total': 0,
                        'price': 0.0
                    }

                    # Tentar extrair informações do texto
                    lines = text.split('\\n')

                    for line in lines:
                        line = line.strip()

                        # Título geralmente é a primeira linha significativa
                        if not product['title'] and len(line) > 5:
                            product['title'] = line

                        # Procurar por números que podem ser quantidade
                        if '/' in line:
                            parts = line.split('/')
                            if len(parts) == 2:
                                try:
                                    product['qty_paid'] = int(parts[0].strip())
                                    product['qty_total'] = int(parts[1].strip())
                                except:
                                    pass

                    # Extrair valor do prêmio do título
                    if product['title']:
                        product['prize_value'] = self.extract_prize_value(product['title'])

                    if product['title']:
                        products.append(product)

                except Exception as e:
                    logger.warning(f"Erro ao processar elemento de produto: {e}")
                    continue

            return products

        except Exception as e:
            logger.error(f"Erro ao fazer scraping da página de produtos: {e}")
            return []

    def collect_all_data(self, headless=True) -> Dict:
        """
        Coleta todos os dados dos sorteios usando Selenium
        """
        driver = None
        temp_profile = None

        try:
            logger.info("Iniciando coleta Hora do Pix com Selenium...")

            # Criar driver
            driver, temp_profile = self.create_chrome_driver(headless=headless)

            # Fazer login
            if not self.login(driver):
                return {
                    'success': False,
                    'error': 'Falha no login',
                    'data': None
                }

            # Fazer scraping dos produtos
            products_raw = self.scrape_products_page(driver)

            if not products_raw:
                logger.warning("Nenhum produto coletado")
                return {
                    'success': False,
                    'error': 'Nenhum produto encontrado',
                    'data': None
                }

            # Processar produtos
            processed_products = []
            active_draws = []
            finished_draws = []

            for product in products_raw:
                # Calcular campos derivados
                price = product.get('price', 0.0)
                qty_paid = product.get('qty_paid', 0)
                prize_value = product.get('prize_value', 0.0)

                # Calcular receita
                revenue = price * qty_paid

                # Calcular taxa da plataforma (3% da receita)
                platform_fee = revenue * 0.03

                # Calcular lucro (receita - prêmio - taxa)
                profit = revenue - prize_value - platform_fee

                # Calcular ROI considerando prêmio e taxa
                total_cost = prize_value + platform_fee
                roi = (profit / total_cost * 100) if total_cost > 0 else 0

                processed = {
                    **product,
                    'revenue': revenue,
                    'platform_fee': platform_fee,
                    'profit': profit,
                    'roi': roi,
                    'qty_free': product.get('qty_total', 0) - qty_paid
                }

                processed_products.append(processed)

                status = processed.get('status', 'active')
                if status == 'done':
                    finished_draws.append(processed)
                else:
                    active_draws.append(processed)

            # Calcular totais
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

            logger.info(f"Coleta concluída: {len(processed_products)} sorteios")
            return result

        except Exception as e:
            logger.error(f"Erro na coleta de dados: {e}")
            return {
                'success': False,
                'error': str(e),
                'data': None
            }

        finally:
            if driver:
                try:
                    driver.quit()
                except:
                    pass

            # Limpar perfil temporário
            if temp_profile and os.path.exists(temp_profile):
                try:
                    import shutil
                    shutil.rmtree(temp_profile, ignore_errors=True)
                except:
                    pass


# Instância global
horapix_collector_selenium = HoraPixCollectorSelenium()
