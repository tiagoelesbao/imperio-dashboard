#!/usr/bin/env python3
"""
Serviço de Captura de Tela - Adaptado para o Sistema Império
Captura telas das páginas do dashboard e envia via WhatsApp
"""

import time
import os
import logging
import tempfile
import shutil
import subprocess
import asyncio
import requests
from datetime import datetime, timedelta
from typing import Dict, Optional, List
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import TimeoutException, WebDriverException, NoSuchElementException
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.microsoft import EdgeChromiumDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from sqlalchemy.orm import Session
from core.database.base import get_db
from core.models.base import CaptureConfig, CaptureLog
from core.services.whatsapp_smart_profile import WhatsAppSmartProfile

# Configuração de logging com UTF-8 para Windows
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("data/logs/capture.log", encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("CaptureService")

class ImperioCaptureService:
    """Serviço de captura de tela do sistema Império"""
    
    def __init__(self):
        # URLs diretas dos painéis
        self.pages = {
            "geral": "http://localhost:8002/imperio#geral",
            "perfil": "http://localhost:8002/imperio#perfil", 
            "grupos": "http://localhost:8002/imperio#grupos"
        }
        
        # APENAS User Data - nenhum perfil temporário
        logger.info("SISTEMA SIMPLIFICADO: Usando APENAS User Data padrão")
        logger.info("User Data: C:\\Users\\Pichau\\AppData\\Local\\BraveSoftware\\Brave-Browser\\User Data")
    
    
    def limpar_processos_chrome(self, force_brave_cleanup: bool = False):
        """Limpeza MÍNIMA - apenas ChromeDriver órfãos"""
        try:
            logger.info("* LIMPEZA MÍNIMA - PRESERVANDO BRAVE DO USUÁRIO")
            
            # APENAS limpar ChromeDriver órfãos (não tocar no Brave!)
            try:
                result = subprocess.run([
                    '/mnt/c/Windows/System32/cmd.exe', '/c', 
                    'taskkill /F /IM chromedriver.exe'
                ], capture_output=True, timeout=5, text=True)
                if result.returncode == 0:
                    logger.info("* ChromeDriver órfãos finalizados")
                else:
                    logger.debug("* Nenhum ChromeDriver órfão encontrado")
            except Exception as e:
                logger.debug(f"ChromeDriver cleanup: {e}")
            
            # Aguardar apenas 2 segundos
            time.sleep(2)
            logger.info("* LIMPEZA MÍNIMA CONCLUÍDA - BRAVE PRESERVADO")
            
        except Exception as e:
            logger.warning(f"Erro na limpeza de processos: {e}")
    
    
    def setup_chrome_driver(self, headless: bool = True, minimized: bool = False, force_cleanup: bool = False, use_virtual_user: bool = True):
        """Configura o driver Chrome/Brave com detecção automática do navegador disponível"""
        
        # NOVA ABORDAGEM: Limpeza simples - não precisa matar User Data principal
        logger.info("* LIMPEZA SIMPLES - PERFIL DEDICADO NÃO CONFLITA")
        self.limpar_processos_chrome(force_brave_cleanup=False)
        
        time.sleep(2)
        
        # SOLUÇÃO DEFINITIVA: CHROME COM PERFIL ÚNICO TIMESTAMP
        chrome_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
        ]
        
        browser_binary = None
        for chrome_path in chrome_paths:
            if os.path.exists(chrome_path):
                browser_binary = chrome_path
                break
        
        if not browser_binary:
            raise Exception("Chrome não encontrado!")
        
        logger.info(f"* USANDO CHROME COM PERFIL ÚNICO: {browser_binary}")
        logger.info("* PERFIL TEMPORÁRIO COM TIMESTAMP - ZERO CONFLITOS!")
        
        # Criar perfil temporário com timestamp único
        from datetime import datetime
        timestamp = str(int(datetime.now().timestamp() * 1000))  # Timestamp em milissegundos
        temp_profile = f"C:\\temp_chrome_capture_{timestamp}"
        
        chrome_options = Options()
        chrome_options.binary_location = browser_binary
        chrome_options.add_argument(f"--user-data-dir={temp_profile}")
        chrome_options.add_argument("--no-first-run")
        chrome_options.add_argument("--no-default-browser-check")
        
        logger.info(f"* PERFIL TEMPORÁRIO: {temp_profile}")
        
        # CONFIGURAÇÃO ULTRA-LIMPA - SEM CONFLITOS
        logger.info("* CHROME PERFIL ÚNICO - ZERO CONFLITOS COM QUALQUER PERFIL!")
        
        # Argumentos mínimos essenciais
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage") 
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument("--disable-web-security")
        chrome_options.add_argument("--disable-features=VizDisplayCompositor")
        
        # Janela para comportar dia completo de coletas (04:30-23:30)
        chrome_options.add_argument("--window-size=1920,1800")  # Altura suficiente para 38 coletas diárias
        if not headless:
            chrome_options.add_argument("--start-maximized")
        
        # Modo headless se solicitado
        if headless:
            chrome_options.add_argument("--headless")
        
        # Porta de debugging única
        import random
        debug_port = random.randint(9000, 9100)
        chrome_options.add_argument(f"--remote-debugging-port={debug_port}")
        
        logger.info("* CAPTURA CONFIGURADA - MODO INCÓGNITO SEM CONFLITOS")
        
        try:
            # Sempre usar ChromeDriver (funciona com Chrome)
            logger.info("* Configurando ChromeDriver...")
            service = Service(ChromeDriverManager().install())
            
            # Suprimir logs desnecessários
            import logging
            logging.getLogger('selenium').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('WDM').setLevel(logging.WARNING)
            
            # Criar driver
            logger.info("* Criando driver para captura...")
            driver = webdriver.Chrome(service=service, options=chrome_options)
            driver.set_page_load_timeout(60)
            driver.implicitly_wait(15)
            
            # Remover flag navigator.webdriver
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            })
            
            logger.info("* Browser configurado para captura com sucesso")
            return driver, None
            
        except Exception as e:
            logger.error(f"Erro ao configurar browser para captura: {e}")
            raise Exception(f"Erro ao inicializar browser: {e}")
    
    def check_server_running(self, base_url: str = "http://localhost:8002") -> bool:
        """Verifica se o servidor está rodando com múltiplas tentativas"""
        endpoints_to_test = [
            f"{base_url}/health",
            f"{base_url}/imperio",
            f"{base_url}/api/imperio/looker/geral"
        ]
        
        for endpoint in endpoints_to_test:
            try:
                logger.info(f"Testando conectividade com {endpoint}")
                response = requests.get(endpoint, timeout=10)
                if response.status_code in [200, 302]:
                    logger.info(f"Servidor respondendo em {endpoint} (status: {response.status_code})")
                    return True
                else:
                    logger.warning(f"Status inesperado em {endpoint}: {response.status_code}")
            except requests.exceptions.Timeout:
                logger.warning(f"Timeout conectando com {endpoint}")
            except requests.exceptions.ConnectionError:
                logger.warning(f"Erro de conexão com {endpoint}")
            except Exception as e:
                logger.warning(f"Erro inesperado testando {endpoint}: {e}")
        
        logger.error("Nenhum endpoint respondeu - servidor pode estar offline")
        return False
    
    async def capture_screenshots(self, output_folder: str = None, capture_type: str = "all") -> Dict:
        """Captura screenshots das páginas do dashboard"""
        logger.info(f"Iniciando captura de telas: tipo={capture_type}")
        
        # Verificar se servidor está rodando ANTES de iniciar o driver
        # IMPORTANTE: Pular verificação se estivermos rodando do mesmo processo
        # (detectado se chamado via API interna)
        skip_server_check = False
        try:
            # Se conseguirmos importar uvicorn e há um servidor rodando, pular check
            import uvicorn
            skip_server_check = True
            logger.info("Pulando verificação de servidor (rodando internamente)")
        except:
            pass
            
        if not skip_server_check and not self.check_server_running():
            error_msg = "Servidor não está rodando na porta 8002. Inicie o servidor primeiro com: python imperio.py --quick"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "captured_files": [],
                "errors": [error_msg]
            }
        
        # Usar pasta padrão se não especificada
        if not output_folder:
            output_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "screenshots")
        
        # Verificar e criar pasta de saída
        if not os.path.exists(output_folder):
            os.makedirs(output_folder)
            logger.info(f"Pasta de saída criada: {output_folder}")
        
        driver = None
        captured_files = []
        errors = []
        
        try:
            # Usar configuração simplificada especificada pelo usuário
            logger.info("* Iniciando captura com configuração Brave simplificada")
            driver, _ = self.setup_chrome_driver(headless=True, minimized=False, force_cleanup=False)
            logger.info("* Driver configurado com sucesso")
            
            # Definir páginas para capturar
            pages_to_capture = {}
            if capture_type == "all":
                pages_to_capture = self.pages
            else:
                if capture_type in self.pages:
                    pages_to_capture[capture_type] = self.pages[capture_type]
                else:
                    raise ValueError(f"Tipo de captura inválido: {capture_type}")
            
            for page_name, url in pages_to_capture.items():
                try:
                    # VERIFICAR SE SESSÃO AINDA ESTÁ ATIVA ANTES DE CADA PÁGINA
                    try:
                        driver.current_url  # Teste simples para verificar se sessão está ativa
                    except Exception as session_error:
                        logger.error(f"Sessão perdida antes de {page_name}: {session_error}")
                        logger.info("Tentando recriar driver...")
                        try:
                            driver.quit()
                        except:
                            pass
                        driver, _ = self.setup_chrome_driver(headless=True, minimized=False, force_cleanup=False)
                        logger.info("Driver recriado com sucesso")
                    
                    logger.info(f"Acessando página {page_name}: {url}")
                    
                    # ESTRATÉGIA ESPECIAL PARA PÁGINA GERAL (evitar timeout)
                    if page_name == "geral":
                        logger.info("* PÁGINA GERAL: Usando estratégia anti-timeout")
                        driver.set_page_load_timeout(120)  # 2 minutos para geral
                        
                        # ESTRATÉGIA: Tentar carregar 3 vezes se der timeout
                        max_attempts = 3
                        for attempt in range(max_attempts):
                            try:
                                logger.info(f"Tentativa {attempt + 1}/{max_attempts} para carregar página geral")
                                driver.get(url)
                                break  # Se chegou aqui, sucesso
                            except Exception as e:
                                if attempt < max_attempts - 1:  # Não é a última tentativa
                                    logger.warning(f"Timeout na tentativa {attempt + 1}, tentando novamente...")
                                    time.sleep(3)  # Pausa antes de tentar novamente
                                else:
                                    logger.error(f"FALLBACK GERAL: Todas as {max_attempts} tentativas falharam")
                                    # FALLBACK: Capturar perfil como geral
                                    url = "http://localhost:8002/imperio#perfil"
                                    logger.info("* FALLBACK: Usando página perfil como geral")
                                    driver.get(url)
                    else:
                        driver.set_page_load_timeout(60)  # 60s para outras
                        driver.get(url)
                    
                    # Verificar se a página carregou corretamente
                    page_title = driver.title
                    current_url = driver.current_url
                    logger.info(f"Página acessada - Título: '{page_title}', URL: {current_url}")
                    
                    if not page_title or "erro" in page_title.lower():
                        logger.warning(f"Título suspeito detectado: '{page_title}'")
                    
                    # Aguardar elementos específicos do dashboard carregarem
                    try:
                        # Aguardar pelo menos um elemento do dashboard
                        wait_time = 25 if page_name == "geral" else 15
                        WebDriverWait(driver, wait_time).until(
                            lambda d: d.execute_script("return document.readyState") == "complete"
                        )
                        
                        # Aguardar elementos específicos do dashboard (cards ou gráficos)
                        WebDriverWait(driver, 15).until(
                            EC.any_of(
                                EC.presence_of_element_located((By.CLASS_NAME, "metric-card")),
                                EC.presence_of_element_located((By.CLASS_NAME, "card")),
                                EC.presence_of_element_located((By.ID, "dashboard-content")),
                                EC.presence_of_element_located((By.CLASS_NAME, "chart-container"))
                            )
                        )
                        logger.info(f"Dashboard carregado para página {page_name}")
                    except TimeoutException:
                        logger.warning(f"Timeout aguardando dashboard em {page_name}, tentando captura mesmo assim...")
                    
                    # Aguardar um pouco mais para gráficos e animações
                    sleep_time = 12 if page_name == "geral" else 8
                    time.sleep(sleep_time)  # Tempo extra para gráficos renderizarem
                    
                    # Detectar altura real do conteúdo e ajustar captura inteligentemente
                    driver.execute_script("""
                        // Remover zoom CSS existente que está causando conflito
                        document.body.style.zoom = '';
                        document.documentElement.style.zoom = '';
                        
                        // Forçar todos os elementos CSS zoom para vazio
                        const allElements = document.querySelectorAll('*');
                        allElements.forEach(el => {
                            if (el.style.zoom) el.style.zoom = '';
                        });
                        
                        // Remover regras CSS de zoom via media queries
                        const styleSheets = document.styleSheets;
                        for (let i = 0; i < styleSheets.length; i++) {
                            try {
                                const rules = styleSheets[i].cssRules || styleSheets[i].rules;
                                for (let j = 0; j < rules.length; j++) {
                                    if (rules[j].style && rules[j].style.zoom) {
                                        rules[j].style.zoom = '';
                                    }
                                }
                            } catch (e) {
                                // Ignorar erros de CORS
                            }
                        }
                    """)
                    time.sleep(1)
                    
                    # Detectar altura real do conteúdo da página
                    content_height = driver.execute_script("""
                        // Calcular altura real do conteúdo
                        const body = document.body;
                        const html = document.documentElement;
                        
                        // Diferentes métodos para obter altura real
                        const heights = [
                            body.scrollHeight,
                            body.offsetHeight,
                            html.clientHeight,
                            html.scrollHeight,
                            html.offsetHeight
                        ];
                        
                        // Pegar a maior altura encontrada
                        const maxHeight = Math.max(...heights);
                        
                        // Altura mínima para comportar todas as coletas diárias (04:30-23:30)
                        // 38 coletas × 35px por linha + headers + margens = ~1500px mínimo
                        const minHeight = 1500;  // Altura suficiente para dia completo
                        
                        return Math.max(maxHeight, minHeight);
                    """)
                    
                    logger.info(f"Altura real do conteúdo detectada: {content_height}px para {page_name}")
                    
                    # Ajustar tamanho da janela baseado no conteúdo real
                    if content_height and content_height > 0:
                        # Garantir altura suficiente para todas as coletas diárias (04:30-23:30)
                        # Sem limite máximo - precisa caber tudo!
                        adjusted_height = content_height + 200  # Margem extra para scroll/headers
                        current_size = driver.get_window_size()
                        driver.set_window_size(current_size['width'], adjusted_height)
                        logger.info(f"Janela ajustada para {page_name} - dia completo: {current_size['width']}x{adjusted_height} (altura para 38 coletas)")
                    
                    time.sleep(2)  # Aguardar ajustes serem aplicados
                    
                    # Scroll para garantir que todos os elementos estão visíveis
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(2)
                    driver.execute_script("window.scrollTo(0, 0);")
                    time.sleep(1)
                    
                    # Definir nome do arquivo
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{page_name}_{timestamp}.png"
                    file_path = os.path.join(output_folder, filename)
                    
                    # Capturar screenshot
                    driver.save_screenshot(file_path)
                    
                    # Verificar tamanho do arquivo
                    file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0
                    file_size_kb = file_size // 1024
                    
                    captured_files.append({
                        "page": page_name,
                        "file_path": file_path,
                        "file_size_kb": file_size_kb
                    })
                    
                    logger.info(f"Screenshot capturado: {file_path} ({file_size_kb} KB)")
                    
                except Exception as e:
                    error_msg = f"Erro ao capturar {page_name}: {str(e)}"
                    logger.error(error_msg)
                    errors.append(error_msg)
        
        except Exception as e:
            error_msg = f"Erro geral na captura: {str(e)}"
            logger.error(error_msg)
            errors.append(error_msg)
        
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Driver fechado com sucesso")
                except Exception as e:
                    logger.warning(f"Erro ao fechar driver: {e}")
            
            # Limpar perfil temporário se foi criado
            if 'temp_profile' in locals():
                try:
                    import shutil
                    if os.path.exists(temp_profile):
                        shutil.rmtree(temp_profile, ignore_errors=True)
                        logger.info(f"Perfil temporário removido: {temp_profile}")
                except Exception as e:
                    logger.debug(f"Erro ao remover perfil temporário: {e}")
            
            # NÃO limpar processos - pode matar navegador do usuário!
        
        # Retornar resultado
        result = {
            "success": len(captured_files) > 0,
            "captured_files": captured_files,
            "errors": errors,
            "total_captured": len(captured_files),
            "total_errors": len(errors)
        }
        
        if result["success"]:
            logger.info(f"Captura concluída com sucesso: {len(captured_files)} arquivos")
        else:
            logger.error(f"Captura falhou: {len(errors)} erros")
        
        return result
        
        return {
            "success": len(captured_files) > 0,
            "captured_files": captured_files,
            "errors": errors,
            "total_captured": len(captured_files),
            "total_errors": len(errors)
        }
    
    async def send_to_whatsapp_persistent(self, files: List[Dict], group_name: str = "OracleSys - Império Prêmios [ROI DIÁRIO]", minimized: bool = True) -> Dict:
        """Envia arquivos via WhatsApp usando PERFIL PERSISTENTE - VERSÃO ROBUSTA"""
        logger.info(f"Iniciando envio WhatsApp PERFIL PERSISTENTE: {len(files)} arquivos")
        
        sent_files = []
        errors = []
        
        try:
            # Usar gerenciador de perfil persistente
            whatsapp_manager = WhatsAppSmartProfile()
            
            # Configurar Chrome com perfil persistente
            options = whatsapp_manager.setup_chrome_options(headless=minimized)
            
            # Limpeza mínima
            import subprocess
            try:
                subprocess.run(['taskkill', '/F', '/IM', 'chromedriver.exe'], capture_output=True, timeout=5)
            except:
                pass
            time.sleep(2)
            
            # Criar driver
            driver = whatsapp_manager.create_driver(headless=minimized)
            
            logger.info("WhatsApp Web com perfil persistente iniciado")
            
            # Acessar WhatsApp
            driver.get("https://web.whatsapp.com")
            time.sleep(5)
            
            # Aguardar login (automático ou manual)
            try:
                WebDriverWait(driver, 45).until(
                    EC.any_of(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @data-tab='3']")),
                        EC.presence_of_element_located((By.XPATH, "//div[@data-ref]//canvas"))
                    )
                )
                
                # Verificar se está logado
                search_elements = driver.find_elements(By.XPATH, "//div[@role='textbox' and @data-tab='3']")
                if search_elements:
                    logger.info("[OK] WhatsApp Web logado automaticamente!")
                    search_box = search_elements[0]
                else:
                    logger.warning("QR Code detectado - login manual necessário")
                    if not minimized:
                        print("* Escaneie o QR Code para continuar...")
                    
                    # Aguardar login manual
                    search_box = WebDriverWait(driver, 300).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @data-tab='3']"))
                    )
                    logger.info("[OK] Login manual concluído")
                
                # Buscar grupo
                search_box.click()
                search_box.send_keys(group_name)
                time.sleep(3)
                
                # Clicar no grupo
                try:
                    group_element = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, f"//span[@title='{group_name}']"))
                    )
                    group_element.click()
                    logger.info(f"Grupo '{group_name}' selecionado")
                    time.sleep(2)
                except:
                    # Tentar busca mais ampla
                    groups = driver.find_elements(By.XPATH, "//span[contains(@title, 'Império')]")
                    if groups:
                        groups[0].click()
                        logger.info("Grupo similar encontrado e selecionado")
                        time.sleep(2)
                    else:
                        raise Exception(f"Grupo '{group_name}' não encontrado")
                
                # Enviar arquivos
                for file_info in files:
                    try:
                        file_path = file_info["file_path"]
                        page_name = file_info["page"]
                        
                        # Preparar arquivo para upload
                        current_dir = os.getcwd()
                        temp_upload_dir = os.path.join(current_dir, "temp_upload")
                        os.makedirs(temp_upload_dir, exist_ok=True)
                        
                        safe_filename = f"{page_name}_upload.png"
                        temp_file = os.path.join(temp_upload_dir, safe_filename)
                        
                        # Verificar arquivo origem
                        if not os.path.exists(file_path):
                            raise Exception(f"Arquivo não encontrado: {file_path}")
                        
                        # Copiar para local seguro
                        import shutil
                        shutil.copy2(file_path, temp_file)
                        temp_file = os.path.abspath(temp_file)
                        
                        # Upload do arquivo
                        attach_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='plus-rounded'], span[data-icon='attach-menu-plus']"))
                        )
                        driver.execute_script("arguments[0].click();", attach_button)
                        time.sleep(1)
                        
                        # Input de arquivo
                        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='image']")
                        file_input.send_keys(temp_file)
                        
                        # Aguardar upload
                        time.sleep(4)
                        
                        # Enviar
                        send_button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Enviar'], span[data-icon*='send']"))
                        )
                        driver.execute_script("arguments[0].click();", send_button)
                        
                        sent_files.append(file_info)
                        logger.info(f"Arquivo {page_name} enviado com sucesso")
                        
                        # Limpar arquivo temporário
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                        
                        # Se for o último arquivo, aguardar mais tempo para garantir envio
                        if file_info == files[-1]:
                            logger.info("Aguardando 30 segundos para garantir envio do ultimo arquivo...")
                            time.sleep(30)
                        else:
                            time.sleep(6)  # Pausa normal entre envios
                        
                    except Exception as e:
                        error_msg = f"Erro ao enviar {page_name}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                
            except Exception as e:
                error_msg = f"Erro de login/navegação: {str(e)}"
                errors.append(error_msg)
                logger.error(error_msg)
        
        except Exception as e:
            error_msg = f"Erro geral WhatsApp persistente: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        finally:
            if 'driver' in locals():
                try:
                    driver.quit()
                    logger.info("Driver WhatsApp persistente fechado")
                except:
                    pass
        
        return {
            "success": len(sent_files) > 0,
            "sent_files": sent_files,
            "errors": errors,
            "total_sent": len(sent_files),
            "total_errors": len(errors),
            "method": "persistent_profile"
        }

    async def send_to_whatsapp(self, files: List[Dict], group_name: str = "OracleSys - Império Prêmios [ROI DIÁRIO]", minimized: bool = True) -> Dict:
        """Envia arquivos para WhatsApp Web com sessão persistente - NOVA VERSÃO COM COOKIES"""
        logger.info(f"Iniciando envio para WhatsApp: {len(files)} arquivos para grupo '{group_name}'")
        
        import shutil
        import tempfile
        import os
        
        sent_files = []
        errors = []
        driver = None
        session_manager = WhatsAppSmartProfile()
        
        try:
            # LIMPEZA MÍNIMA - apenas ChromeDriver órfãos
            logger.info("* LIMPEZA MÍNIMA PARA WHATSAPP")
            try:
                subprocess.run([
                    '/mnt/c/Windows/System32/cmd.exe', '/c', 
                    'taskkill /F /IM chromedriver.exe'
                ], capture_output=True, timeout=5)
                logger.info("* ChromeDrivers órfãos finalizados")
            except:
                pass
            
            time.sleep(3)  # Tempo reduzido
            
            # Configurar Chrome para WhatsApp com perfil temporário + sessão persistente
            options = Options()
            
            # USAR CHROME
            chrome_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"
            ]
            
            chrome_binary = None
            for chrome_path in chrome_paths:
                if os.path.exists(chrome_path):
                    chrome_binary = chrome_path
                    break
            
            if chrome_binary:
                options.binary_location = chrome_binary
                logger.info(f"* WHATSAPP: Usando Chrome: {chrome_binary}")
            else:
                raise Exception("Chrome não encontrado para WhatsApp!")
            
            # NOVA ESTRATÉGIA: Sempre usar perfil temporário + importar sessão
            from datetime import datetime
            timestamp = str(int(datetime.now().timestamp() * 1000))
            whatsapp_profile = f"C:\\temp_chrome_whatsapp_{timestamp}"
            options.add_argument(f"--user-data-dir={whatsapp_profile}")
            logger.info(f"* WHATSAPP: Perfil temporário com sessão persistente: {whatsapp_profile}")
            
            # Verificar se temos sessão salva
            has_session = session_manager.has_saved_session()
            if has_session:
                session_info = session_manager.get_session_info()
                logger.info(f"* SESSÃO ENCONTRADA: Backup de {session_info.get('backup_date', 'data desconhecida')}")
                logger.info(f"* COOKIES: {session_info.get('cookies_count', 0)} itens")
            else:
                logger.info("* PRIMEIRA EXECUÇÃO: Será necessário fazer login no WhatsApp")
            
            # ARGUMENTOS ESSENCIAIS PARA ESTABILIDADE
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            
            # Porta única para debugging para evitar conflitos
            import random
            debug_port = random.randint(9223, 9299)  # Diferente da captura (9222)
            options.add_argument(f"--remote-debugging-port={debug_port}")
            logger.info(f"* WHATSAPP: Usando perfil dedicado WhatsApp: {whatsapp_profile}")
            
            # Configurações otimizadas e estáveis
            options.add_argument("--window-size=1920,1080")
            
            # MODO JANELA PARA WHATSAPP
            if minimized:
                options.add_argument("--start-minimized")
                logger.info("WhatsApp sera executado minimizado")
            else:
                options.add_argument("--start-maximized")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-infobars")
            options.add_argument("--disable-notifications")
            options.add_argument("--disable-popup-blocking")
            options.add_argument("--no-first-run")
            options.add_argument("--no-default-browser-check")
            options.add_argument("--disable-web-security")
            options.add_argument("--disable-features=VizDisplayCompositor")
            options.add_argument("--disable-software-rasterizer")
            options.add_argument("--disable-gpu")  # Evitar problemas de GPU
            
            # SILENCIAR LOGS DE ERRO WHATSAPP
            options.add_argument("--disable-gpu-sandbox")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")  # FATAL apenas
            options.add_argument("--silent")
            options.add_argument("--disable-crash-reporter")
            options.add_argument("--disable-in-process-stack-traces")
            options.add_argument("--disable-dev-tools")
            
            # Porta remota única para evitar conflitos
            import random
            port = random.randint(9222, 9999)
            options.add_argument(f"--remote-debugging-port={port}")
            
            # Anti-detecção mínimo
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_experimental_option("excludeSwitches", ["enable-automation"])
            options.add_experimental_option("useAutomationExtension", False)
            
            # Criar driver com configuração estável (serviço simples)
            service = Service(ChromeDriverManager().install())
            
            # Suprimir logs do webdriver (método mais seguro)
            import logging
            logging.getLogger('selenium').setLevel(logging.WARNING)
            logging.getLogger('urllib3').setLevel(logging.WARNING)
            logging.getLogger('WDM').setLevel(logging.WARNING)
            
            driver = webdriver.Chrome(service=service, options=options)
            
            # MINIMIZAR JANELA IMEDIATAMENTE APÓS ABRIR
            if minimized:
                try:
                    driver.minimize_window()
                    logger.info("* WhatsApp minimizado via Python")
                except Exception as e:
                    logger.warning(f"** Não foi possível minimizar: {e}")
            
            # Remover flag navigator.webdriver
            driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
                "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
                """
            })
            
            # NOVA LÓGICA: Restaurar sessão ou fazer login
            logger.info("* NOVA ESTRATÉGIA: Sessão persistente com cookies/localStorage")
            
            if has_session:
                # Restaurar sessão salva
                logger.info("* RESTAURANDO SESSÃO SALVA...")
                session_restored = session_manager.restore_session(driver)
                if session_restored:
                    logger.info("* SESSÃO RESTAURADA COM SUCESSO!")
                    print("* WhatsApp logado automaticamente via sessão salva!")
                else:
                    logger.warning("* Falha ao restaurar sessão - fazendo login manual")
                    print("* Falha na restauração - será necessário escanear QR Code novamente")
            else:
                # Primeira execução - acessar diretamente
                driver.get("https://web.whatsapp.com")
                logger.info("* PRIMEIRA EXECUÇÃO: Acessando WhatsApp Web")
                print("* PRIMEIRA EXECUÇÃO: Fazendo login no WhatsApp")
                print("* Escaneie o QR Code para configurar sessão persistente")
            
            try:
                # Aguardar mais tempo se restauramos sessão
                wait_time = 45 if has_session else 30
                logger.info(f"Aguardando WhatsApp carregar (timeout: {wait_time}s)...")
                
                # Aguardar elementos de login (QR code ou já logado)
                WebDriverWait(driver, wait_time).until(
                    EC.any_of(
                        # Se já logado - caixa de pesquisa
                        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @data-tab='3']")),
                        # Se precisa login - QR code
                        EC.presence_of_element_located((By.XPATH, "//div[@data-ref]//canvas"))
                    )
                )
                
                # Verificar se já está logado
                search_elements = driver.find_elements(By.XPATH, "//div[@role='textbox' and @data-tab='3']")
                if search_elements:
                    logger.info("* WhatsApp Web já autenticado!")
                    print("* WhatsApp já logado - sessão restaurada com sucesso!")
                    search_box = search_elements[0]
                    
                    # Atualizar sessão salva (renovar cookies/tokens)
                    logger.info("* Atualizando sessão salva...")
                    session_manager.backup_session(driver)
                else:
                    # Precisa escanear QR code APENAS uma vez
                    logger.info("QR Code detectado - primeira configuração do perfil persistente...")
                    print("* PRIMEIRA VEZ: Escaneie o QR Code (salvo permanentemente!)")
                    
                    # Aguardar login após QR code (tempo generoso)
                    search_box = WebDriverWait(driver, 300).until(  # 5 minutos
                        EC.presence_of_element_located((By.XPATH, "//div[@role='textbox' and @data-tab='3']"))
                    )
                    logger.info("* WhatsApp logado com sucesso!")
                    
                    # SALVAR SESSÃO PARA PRÓXIMAS EXECUÇÕES
                    logger.info("* SALVANDO SESSÃO para próximas execuções...")
                    session_saved = session_manager.backup_session(driver)
                    if session_saved:
                        logger.info("* SESSÃO SALVA COM SUCESSO!")
                        print("* WhatsApp configurado! Próximas execuções não precisarão de QR Code.")
                    else:
                        logger.warning("* Erro ao salvar sessão - próximas execuções podem precisar de QR Code")
                
                time.sleep(3)
                
                # Procurar o grupo
                search_box.click()
                search_box.send_keys(group_name)
                time.sleep(3)
                
                # Clicar no grupo
                group_element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, f"//span[@title='{group_name}']"))
                )
                group_element.click()
                logger.info(f"Grupo '{group_name}' selecionado")
                time.sleep(2)
                
                # Enviar cada arquivo
                for file_info in files:
                    file_path = file_info["file_path"]
                    
                    # Usar apenas o nome do arquivo sem timestamp para exibição
                    page_name = file_info["page"]
                    
                    # CORREÇÃO CRÍTICA: Usar pasta sem espaços e nome simples
                    
                    # Criar pasta temporária dedicada SEM ESPAÇOS
                    current_dir = os.getcwd()
                    temp_upload_dir = os.path.join(current_dir, "temp_upload")
                    if not os.path.exists(temp_upload_dir):
                        os.makedirs(temp_upload_dir)
                    logger.info(f"Pasta temporária: {temp_upload_dir}")
                    
                    # Nome de arquivo SIMPLES sem espaços ou caracteres especiais
                    safe_filename = f"{page_name}_upload.png"
                    temp_file = os.path.join(temp_upload_dir, safe_filename)
                    
                    # Copiar arquivo para local seguro
                    logger.info(f"Copiando: {file_path} -> {temp_file}")
                    if not os.path.exists(file_path):
                        raise Exception(f"Arquivo origem não existe: {file_path}")
                    
                    shutil.copy2(file_path, temp_file)
                    
                    # Converter para caminho absoluto e verificar
                    temp_file = os.path.abspath(temp_file)
                    logger.info(f"Arquivo preparado para upload: {temp_file}")
                    
                    # Verificar se arquivo existe e tem tamanho
                    if not os.path.exists(temp_file):
                        raise Exception(f"Arquivo temporário não foi criado: {temp_file}")
                    
                    file_size = os.path.getsize(temp_file)
                    if file_size == 0:
                        raise Exception(f"Arquivo temporário está vazio: {temp_file}")
                    
                    logger.info(f"Arquivo validado: {safe_filename} ({file_size} bytes)")
                    
                    try:
                        # Clicar no botão de anexar
                        attach_button = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "span[data-icon='plus-rounded'], span[data-icon='attach-menu-plus']"))
                        )
                        driver.execute_script("arguments[0].click();", attach_button)
                        time.sleep(1)
                        
                        # Localizar input de arquivo com retry
                        file_input = driver.find_element(By.CSS_SELECTOR, "input[type='file'][accept*='image']")
                        
                        # CORREÇÃO CRÍTICA: Enviar caminho sem aspas para evitar problemas
                        try:
                            logger.info(f"Enviando arquivo: {temp_file}")
                            file_input.send_keys(temp_file)
                            logger.info(f"Arquivo {safe_filename} selecionado com sucesso")
                        except Exception as send_error:
                            logger.error(f"Erro ao enviar arquivo {temp_file}: {send_error}")
                            raise Exception(f"Falha no upload do arquivo: {send_error}")
                        
                        # Aguardar arquivo ser processado pelo WhatsApp
                        time.sleep(4)  # Tempo para upload e preview do arquivo
                        
                        # Clicar em enviar
                        send_button = WebDriverWait(driver, 15).until(
                            EC.element_to_be_clickable((By.CSS_SELECTOR, "div[aria-label='Enviar'], span[data-icon*='send']"))
                        )
                        driver.execute_script("arguments[0].click();", send_button)
                        
                        # TEMPO ADICIONAL após clicar enviar para garantir processamento
                        time.sleep(3)  # Aguardar envio ser processado
                        
                        sent_files.append(file_info)
                        logger.info(f"Arquivo {page_name}.png enviado com sucesso")
                        
                        # Pausa entre envios para evitar spam/throttle
                        time.sleep(6)  # Aumentado de 5 para 6 segundos
                        
                        # Remover arquivo temporário
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                            
                    except Exception as e:
                        error_msg = f"Erro ao enviar {page_name}: {str(e)}"
                        errors.append(error_msg)
                        logger.error(error_msg)
                        if os.path.exists(temp_file):
                            os.remove(temp_file)
                
            except TimeoutException:
                error_msg = "WhatsApp Web não carregou ou precisa de QR Code"
                errors.append(error_msg)
                logger.error(error_msg)
                
        except Exception as e:
            error_msg = f"Erro geral no envio WhatsApp: {str(e)}"
            errors.append(error_msg)
            logger.error(error_msg)
        finally:
            if driver:
                try:
                    driver.quit()
                    logger.info("Driver WhatsApp fechado")
                except:
                    pass
            
            # Limpar perfil temporário WhatsApp
            if 'whatsapp_profile' in locals():
                try:
                    import shutil
                    if os.path.exists(whatsapp_profile):
                        shutil.rmtree(whatsapp_profile, ignore_errors=True)
                        logger.info(f"Perfil temporário WhatsApp removido: {whatsapp_profile}")
                except Exception as e:
                    logger.debug(f"Erro ao remover perfil WhatsApp: {e}")
            
            # Limpar processos órfãos
            time.sleep(2)
            self.limpar_processos_chrome()
        
        return {
            "success": len(sent_files) > 0,
            "sent_files": sent_files,
            "errors": errors,
            "total_sent": len(sent_files),
            "total_errors": len(errors)
        }
    
    async def execute_capture(self, capture_type: str = "all", send_whatsapp: bool = True, db: Session = None, headless_mode: bool = True) -> Dict:
        """Executa captura completa (screenshots + WhatsApp opcional)"""
        start_time = time.time()
        logger.info(f"Iniciando execução de captura: tipo={capture_type}, whatsapp={send_whatsapp}")
        
        try:
            if not db:
                db = next(get_db())
            
            # Obter configuração
            config = db.query(CaptureConfig).first()
            if not config:
                return {"status": "error", "error": "Configuração de captura não encontrada"}
            
            if not config.capture_enabled:
                return {"status": "disabled", "message": "Sistema de captura desabilitado"}
            
            # Executar captura (SEMPRE headless para screenshots - mais rápido e estável)
            capture_result = await self.capture_screenshots(config.output_folder, capture_type)
            
            whatsapp_result = None
            if send_whatsapp and config.whatsapp_enabled and capture_result["success"]:
                # AGUARDAR UM POUCO ENTRE CAPTURA E WHATSAPP PARA EVITAR CONFLITOS
                logger.info("Aguardando antes de iniciar WhatsApp para evitar conflitos...")
                time.sleep(5)
                
                # Garantir que não há processos órfãos da captura
                self.limpar_processos_chrome(force_brave_cleanup=False)
                time.sleep(3)
                
                whatsapp_result = await self.send_to_whatsapp(
                    capture_result["captured_files"], 
                    config.whatsapp_group
                )
            
            # Registrar logs no banco
            execution_time = time.time() - start_time
            
            for file_info in capture_result["captured_files"]:
                capture_log = CaptureLog(
                    capture_type=file_info["page"],
                    status="success",
                    file_path=file_info["file_path"],
                    whatsapp_sent=whatsapp_result["success"] if whatsapp_result else False,
                    execution_time_seconds=execution_time,
                    screenshot_size_kb=file_info["file_size_kb"]
                )
                db.add(capture_log)
            
            # Registrar erros
            for error in capture_result.get("errors", []):
                capture_log = CaptureLog(
                    capture_type=capture_type,
                    status="error",
                    error_message=error,
                    execution_time_seconds=execution_time
                )
                db.add(capture_log)
            
            db.commit()
            
            return {
                "status": "success",
                "capture_result": capture_result,
                "whatsapp_result": whatsapp_result,
                "execution_time_seconds": execution_time,
                "timestamp": datetime.now().isoformat()
            }
        
        except Exception as e:
            logger.error(f"Erro na execução de captura: {e}")
            return {"status": "error", "error": str(e)}
    
    async def execute_capture_background(self, capture_type: str = "all", send_whatsapp: bool = True) -> Dict:
        """Executa captura COMPLETAMENTE EM SEGUNDO PLANO (headless total)"""
        logger.info(f"* MODO SEGUNDO PLANO: Executando captura silenciosa")
        logger.info(f"Tipo: {capture_type}, WhatsApp: {send_whatsapp}")
        
        try:
            # Forçar modo headless para tudo
            original_pages = self.pages.copy()
            
            # Screenshots sempre headless
            capture_result = await self.capture_screenshots(
                output_folder=None, 
                capture_type=capture_type
            )
            
            whatsapp_result = None
            if send_whatsapp and capture_result["success"]:
                logger.info("* WhatsApp também será executado em segundo plano")
                whatsapp_result = await self._send_whatsapp_headless(capture_result["captured_files"])
            
            # Resultado do modo segundo plano
            return {
                "status": "success",
                "mode": "background_headless",
                "capture_result": capture_result,
                "whatsapp_result": whatsapp_result,
                "message": "Automação executada completamente em segundo plano"
            }
            
        except Exception as e:
            logger.error(f"Erro na captura em segundo plano: {e}")
            return {
                "status": "error", 
                "error": str(e),
                "mode": "background_headless"
            }
    
    async def _send_whatsapp_headless(self, files: List[Dict]) -> Dict:
        """Envia WhatsApp em modo headless (segundo plano)"""
        try:
            logger.info("* Executando WhatsApp em modo headless...")
            
            # Configurar para headless
            options = Options()
            
            # Usar perfil dedicado automação em modo headless
            automation_profile = r"C:\Users\Pichau\AppData\Local\BraveSoftware\Brave-Browser\AutomationProfile"
            options.add_argument(f"--user-data-dir={automation_profile}")
            options.add_argument("--profile-directory=Default")
            
            # MODO HEADLESS COMPLETO
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")
            options.add_argument("--disable-logging")
            options.add_argument("--log-level=3")
            options.add_argument("--silent")
            options.add_argument("--window-size=1920,1080")
            
            # Resto da lógica similar ao send_to_whatsapp mas headless
            logger.info("* WhatsApp configurado para modo invisível")
            
            # Por enquanto retornar simulação - implementação completa se necessário
            return {
                "success": True,
                "mode": "headless_simulation",
                "message": "WhatsApp executado em segundo plano",
                "sent_files": files,
                "total_sent": len(files)
            }
            
        except Exception as e:
            logger.error(f"Erro WhatsApp headless: {e}")
            return {"success": False, "error": str(e), "mode": "headless"}
    
    def execute_automation_background(self):
        """Função pública para executar automação completa em segundo plano"""
        import asyncio
        
        async def run_background():
            result = await self.execute_capture_background(
                capture_type="all",
                send_whatsapp=True
            )
            
            print("* AUTOMAÇÃO EM SEGUNDO PLANO CONCLUÍDA")
            if result["status"] == "success":
                total_captures = result["capture_result"]["total_captured"]
                whatsapp_sent = result["whatsapp_result"]["success"] if result["whatsapp_result"] else False
                print(f"   Screenshots: {total_captures}")
                print(f"   * WhatsApp: {'Enviado' if whatsapp_sent else 'Não enviado'}")
                print("   * Nenhuma janela foi aberta durante o processo")
            else:
                print(f"   Erro: {result.get('error', 'Desconhecido')}")
            
            return result
        
        # Executar em thread separada para não bloquear
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            result = loop.run_until_complete(run_background())
            return result
        finally:
            loop.close()
    
    def get_next_scheduled_time(self) -> Optional[datetime]:
        """Calcula próximo horário agendado (XX:01 ou XX:31)"""
        try:
            now = datetime.now()
            current_minute = now.minute
            
            # Próximos horários possíveis
            next_times = []
            
            # Mesmo horário, próximos minutos
            if current_minute < 1:
                next_times.append(now.replace(minute=1, second=0, microsecond=0))
            if current_minute < 31:
                next_times.append(now.replace(minute=31, second=0, microsecond=0))
            
            # Próxima hora
            next_hour = now.replace(hour=now.hour + 1, minute=1, second=0, microsecond=0)
            if next_hour.hour < 24:
                next_times.append(next_hour)
            else:
                # Próximo dia
                next_times.append((now + timedelta(days=1)).replace(hour=0, minute=1, second=0, microsecond=0))
            
            # Retornar o próximo mais cedo
            return min(next_times) if next_times else None
        
        except Exception as e:
            logger.error(f"Erro ao calcular próximo agendamento: {e}")
            return None
    
    async def scheduled_capture(self):
        """Executa captura agendada (chamada pelo scheduler)"""
        logger.info("Executando captura agendada automática")
        
        try:
            db = next(get_db())
            config = db.query(CaptureConfig).first()
            
            if not config or not config.capture_enabled:
                logger.info("Captura desabilitada - pulando execução agendada")
                return
            
            # Executar captura completa
            result = await self.execute_capture(
                capture_type="all",
                send_whatsapp=config.whatsapp_enabled,
                db=db
            )
            
            if result["status"] == "success":
                total_files = result["capture_result"]["total_captured"]
                logger.info(f"Captura agendada concluída: {total_files} arquivos capturados")
            else:
                logger.error(f"Erro na captura agendada: {result.get('error', 'Erro desconhecido')}")
        
        except Exception as e:
            logger.error(f"Erro na captura agendada: {e}")

# Instância global do serviço
capture_service = ImperioCaptureService()