#!/usr/bin/env python3
"""
Serviço de Captura OTIMIZADO - Versão Ultra-Rápida
Elimina delays desnecessários e timeouts excessivos
"""

import os
import time
import logging
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Logging mínimo
logger = logging.getLogger("CaptureServiceFast")

class ImperioCaptureServiceFast:
    """Serviço de captura ULTRA-RÁPIDO"""
    
    def __init__(self):
        self.pages = {
            "geral": "http://localhost:8002/imperio#geral",
            "perfil": "http://localhost:8002/imperio#perfil",
            "grupos": "http://localhost:8002/imperio#grupos",
            "horapix": "http://localhost:8002/imperio#horapix"
        }
    
    def create_fast_chrome(self):
        """Cria Chrome OTIMIZADO para máxima velocidade"""
        options = Options()
        
        # Velocidade máxima
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-extensions")
        options.add_argument("--disable-plugins")
        # Remover --disable-images e --disable-javascript pois dashboard precisa
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=VizDisplayCompositor")
        options.add_argument("--disable-ipc-flooding-protection")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-field-trial-config")
        options.add_argument("--disable-back-forward-cache")
        options.add_argument("--disable-software-rasterizer")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-hang-monitor")
        options.add_argument("--disable-prompt-on-repost")
        options.add_argument("--disable-sync")
        options.add_argument("--disable-translate")
        options.add_argument("--disable-logging")
        options.add_argument("--silent")
        
        # Perfil temporário
        temp_profile = f"C:\\temp_chrome_fast_{int(time.time())}"
        options.add_argument(f"--user-data-dir={temp_profile}")
        
        # Window size para comportar dia completo de coletas (04:30-23:30)
        options.add_argument("--window-size=1920,1800")  # Altura suficiente para 38 coletas diárias
        options.add_argument("--headless")  # Modo headless para máxima velocidade
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=options)
        
        # Timeouts adequados para scheduler automático
        driver.set_page_load_timeout(15)  # 15 segundos para carregar página
        driver.implicitly_wait(3)  # 3 segundos para encontrar elementos
        
        return driver, temp_profile
    
    async def capture_screenshots_fast(self, output_folder="screenshots"):
        """Captura screenshots de forma ULTRA-RÁPIDA"""
        os.makedirs(output_folder, exist_ok=True)
        
        driver = None
        captured_files = []
        temp_profile = None
        
        try:
            logger.info("Iniciando captura RÁPIDA...")
            driver, temp_profile = self.create_fast_chrome()
            
            for page_name, url in self.pages.items():
                try:
                    logger.info(f"Capturando {page_name}...")
                    
                    # Verificar se servidor está respondendo primeiro
                    import requests
                    try:
                        health_check = requests.get("http://localhost:8002/health", timeout=5)
                        if health_check.status_code != 200:
                            logger.error(f"Servidor não está respondendo (HTTP {health_check.status_code})")
                            continue
                    except Exception as e:
                        logger.error(f"Servidor inacessível: {str(e)[:50]}")
                        continue
                    
                    # Load page com tratamento de timeout
                    try:
                        driver.get(url)
                    except Exception as e:
                        if "timeout" in str(e).lower():
                            logger.warning(f"Timeout em {page_name}, tentando novamente...")
                            time.sleep(2)
                            driver.get(url)
                        else:
                            raise e
                    
                    # Wait para dashboard carregar - DIFERENCIADO por página
                    if page_name == "horapix":
                        # HORA DO PIX precisa aguardar chamada API + renderização
                        logger.info("Hora do Pix detectada - aguardando carregamento completo dos dados...")
                        time.sleep(5)  # Wait inicial para página carregar

                        # Aguardar até 15 segundos para dados carregarem (verificar se não tem "Carregando...")
                        max_wait = 15
                        waited = 0
                        while waited < max_wait:
                            try:
                                # Verificar se ainda está carregando
                                loading_check = driver.execute_script("""
                                    const tbody1 = document.getElementById('horaPixAtivasList');
                                    const tbody2 = document.getElementById('horaPixFinalizadasList');

                                    if (!tbody1 || !tbody2) return true; // Ainda carregando estrutura

                                    const text1 = tbody1.textContent || '';
                                    const text2 = tbody2.textContent || '';

                                    // Se tem "Carregando..." ainda está processando
                                    if (text1.includes('Carregando') || text2.includes('Carregando')) {
                                        return true;
                                    }

                                    // Verificar se KPIs foram atualizados (não estão zerados)
                                    const kpi = document.getElementById('kpiFinalizadosCount');
                                    if (kpi && kpi.textContent !== '0') {
                                        return false; // Dados carregados!
                                    }

                                    // Se tem dados nas tabelas (não tem "Nenhum")
                                    const hasData = !text1.includes('Nenhum') || !text2.includes('Nenhum');
                                    return !hasData; // False se tem dados
                                """)

                                if not loading_check:
                                    logger.info(f"Dados da Hora do Pix carregados após {waited}s")
                                    break

                                time.sleep(1)
                                waited += 1
                            except:
                                time.sleep(1)
                                waited += 1

                        if waited >= max_wait:
                            logger.warning(f"Timeout aguardando dados da Hora do Pix ({max_wait}s)")

                        # Wait adicional para garantir renderização completa
                        time.sleep(2)
                    else:
                        # Outras páginas: 8 segundos (balance velocidade/dados)
                        time.sleep(8)
                    
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
                    
                    logger.info(f"Altura real do conteúdo detectada: {content_height}px")
                    
                    # Ajustar tamanho da janela baseado no conteúdo real
                    if content_height and content_height > 0:
                        # Garantir altura suficiente para todas as coletas diárias (04:30-23:30)
                        # Sem limite máximo - precisa caber tudo!
                        adjusted_height = content_height + 200  # Margem extra para scroll/headers
                        current_size = driver.get_window_size()
                        driver.set_window_size(current_size['width'], adjusted_height)
                        logger.info(f"Janela ajustada para dia completo: {current_size['width']}x{adjusted_height} (altura para 38 coletas)")
                    
                    time.sleep(2)  # Aguardar ajustes serem aplicados
                    
                    # Screenshot imediato
                    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                    filename = f"{page_name}_{timestamp}.png"
                    file_path = os.path.join(output_folder, filename)
                    
                    driver.save_screenshot(file_path)
                    
                    # Garantir caminho absoluto para o WhatsApp
                    absolute_path = os.path.abspath(file_path)
                    file_size_kb = os.path.getsize(absolute_path) // 1024
                    captured_files.append({
                        "page": page_name,
                        "file_path": absolute_path,
                        "file_size_kb": file_size_kb
                    })
                    
                    logger.info(f"✅ {page_name}: {file_size_kb}KB")
                    
                except Exception as e:
                    logger.error(f"❌ {page_name}: {str(e)[:50]}")
            
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
        
        logger.info(f"Captura concluída: {len(captured_files)} arquivos")
        
        # REMOVIDO: Envio automático do WhatsApp para evitar duplicações
        # O imperio_server_stable.py controlará o envio via WhatsApp
        return {
            "success": len(captured_files) > 0,
            "files": captured_files,
            "total_captured": len(captured_files)
        }
    
    async def send_to_whatsapp_fast(self, files, group_name="OracleSys - Império Prêmios [ROI DIÁRIO]"):
        """Envio WhatsApp OTIMIZADO"""
        if not files:
            return {"success": False, "error": "Nenhum arquivo"}
        
        try:
            from core.services.whatsapp_smart_profile import WhatsAppSmartProfile
            
            logger.info(f"Enviando {len(files)} arquivos via WhatsApp...")
            whatsapp = WhatsAppSmartProfile()
            
            # Usar o método direto do WhatsAppSmartProfile
            result = whatsapp.send_images_smart(files)
            return result
            
        except Exception as e:
            logger.error(f"Erro WhatsApp: {str(e)[:100]}")
            return {"success": False, "error": str(e)[:100]}