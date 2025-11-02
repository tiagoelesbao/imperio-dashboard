#!/usr/bin/env python3
"""
WhatsApp INTELIGENTE - Usa perfil persistente mas com proteção contra conflitos
"""
import os
import time
import subprocess
import psutil
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class WhatsAppSmartProfile:
    def __init__(self):
        # Perfil PERSISTENTE fixo - mas com detecção de conflitos
        self.whatsapp_profile = r"C:\Users\Pichau\AppData\Local\Chrome_WhatsApp_Persistente"
        self.debug_port = 9223  # Porta fixa para WhatsApp
        self.ensure_profile_exists()
        
    def ensure_profile_exists(self):
        """Garante que o perfil persistente existe"""
        if not os.path.exists(self.whatsapp_profile):
            os.makedirs(self.whatsapp_profile, exist_ok=True)
            print(f"[PERFIL] Perfil persistente criado: {self.whatsapp_profile}")
        else:
            print(f"[PERFIL] Usando perfil persistente existente")
    
    def is_profile_in_use(self):
        """Verifica se perfil WhatsApp BRAVE já está sendo usado"""
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                if proc.info['name'] in ['brave.exe', 'chrome.exe']:
                    cmdline = ' '.join(proc.info['cmdline'] or [])
                    if 'Chrome_WhatsApp_Persistente' in cmdline:
                        print(f"[CONFLITO] Brave WhatsApp já em uso (PID: {proc.info['pid']})")
                        return True
            except:
                pass
        return False
    
    def wait_for_profile_available(self, max_wait=10):
        """Aguarda perfil ficar disponível"""
        for i in range(max_wait):
            if not self.is_profile_in_use():
                return True
            print(f"[AGUARDO] Perfil em uso, aguardando... ({i+1}/{max_wait})")
            time.sleep(1)
        return False
    
    def setup_brave_options(self, headless=False):
        """Configuração BRAVE com perfil persistente - SEM conflitar com Chrome"""
        from selenium.webdriver.chrome.options import Options
        options = Options()
        
        # Usar BRAVE ao invés de Chrome
        brave_paths = [
            r"C:\Program Files\BraveSoftware\Brave-Browser\Application\brave.exe",
            r"C:\Program Files (x86)\BraveSoftware\Brave-Browser\Application\brave.exe"
        ]
        
        brave_path = None
        for path in brave_paths:
            if os.path.exists(path):
                brave_path = path
                break
        
        if brave_path:
            options.binary_location = brave_path
        
        # Perfil persistente BRAVE
        options.add_argument(f"--user-data-dir={self.whatsapp_profile}")
        options.add_argument(f"--remote-debugging-port={self.debug_port}")
        
        # Configurações essenciais
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--disable-gpu")
        options.add_argument("--disable-background-timer-throttling")
        options.add_argument("--disable-backgrounding-occluded-windows")
        options.add_argument("--disable-renderer-backgrounding")
        options.add_argument("--disable-web-security")
        options.add_argument("--disable-features=TranslateUI")
        options.add_argument("--disable-ipc-flooding-protection")
        
        # User Agent
        options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        if headless:
            options.add_argument("--headless")
            
        return options
    
    def send_images_smart(self, files, group_name="OracleSys - Império Prêmios [ROI DIÁRIO]"):
        """Envio inteligente - aguarda perfil livre

        Args:
            files: Lista de arquivos para enviar
            group_name: Nome do grupo WhatsApp (padrão: Império Prêmios)
        """
        try:
            # Verificar se perfil está em uso
            if self.is_profile_in_use():
                print("[CONFLITO] Perfil WhatsApp já está sendo usado")
                if not self.wait_for_profile_available():
                    return {"success": False, "error": "Perfil WhatsApp ocupado"}
            
            print(f"[WHATSAPP] Usando BRAVE com perfil persistente na porta {self.debug_port}")
            
            # Setup Brave (compatível com ChromeDriver)
            options = self.setup_brave_options()
            service = Service(ChromeDriverManager().install())
            
            driver = webdriver.Chrome(service=service, options=options)
            driver.set_page_load_timeout(15)
            
            try:
                # Acessar WhatsApp Web
                print("[WHATSAPP] Abrindo WhatsApp Web...")
                driver.get("https://web.whatsapp.com")
                
                # Aguardar carregamento (máximo 30s)
                wait = WebDriverWait(driver, 30)
                
                # Verificar se está logado ou precisa escanear QR
                try:
                    # Verificar múltiplos sinais de login
                    login_indicators = [
                        '[data-testid="chat-list"]',
                        '[data-testid="side"]', 
                        '#side',
                        '.three'  # Div principal do WhatsApp
                    ]
                    
                    # Tentar detectar qualquer indicador de login
                    for indicator in login_indicators:
                        try:
                            wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, indicator)))
                            print("[WHATSAPP] OK Login existente detectado!")
                            break
                        except:
                            continue
                    else:
                        # Se chegou aqui, não encontrou indicadores
                        raise Exception("Nenhum indicador de login encontrado")
                    
                    # Procurar grupo específico - NOME COMPLETO EXATO (passado como parâmetro)
                    grupo_nome_completo = group_name
                    print(f"[WHATSAPP] Procurando grupo: {grupo_nome_completo}")
                    
                    # Buscar pelo grupo - usando seletores robustos do código antigo
                    search_selectors = [
                        (By.CSS_SELECTOR, "div[role='textbox'][aria-label='Caixa de texto de pesquisa']"),
                        (By.CSS_SELECTOR, "div[role='textbox'][aria-placeholder='Pesquisar ou começar uma nova conversa']"),
                        (By.XPATH, "//div[@role='textbox' and contains(@aria-label, 'Pesquisar')]"),
                        (By.XPATH, "//button[@aria-label='Pesquisar ou começar uma nova conversa']"),
                        (By.XPATH, "//div[contains(@class, 'x10l6tqk')]"),
                        (By.XPATH, "//div[contains(@class, 'lexical-rich-text-input')]//div[@role='textbox']"),
                        (By.CSS_SELECTOR, '[data-testid="search-input"]'),
                        (By.CSS_SELECTOR, 'input[type="text"]')
                    ]
                    
                    search_box = None
                    for method, selector in search_selectors:
                        try:
                            search_box = wait.until(EC.element_to_be_clickable((method, selector)))
                            driver.execute_script("arguments[0].click();", search_box)
                            print(f"[WHATSAPP] Campo de busca encontrado: {selector[:50]}")
                            break
                        except:
                            continue
                    
                    if search_box:
                        search_box.clear()
                        # Usar nome COMPLETO na busca para ser específico
                        search_box.send_keys(grupo_nome_completo)
                        print(f"[WHATSAPP] Texto de busca inserido: {grupo_nome_completo}")
                        time.sleep(4)  # Aguardar mais tempo para carregar resultados
                        
                        # Tentar encontrar o grupo - SOMENTE nome completo exato
                        group_selectors = [
                            # Busca EXATA pelo título completo
                            (By.XPATH, f"//span[@title='{grupo_nome_completo}']"),
                            # Busca EXATA pelo texto completo
                            (By.XPATH, f"//span[text()='{grupo_nome_completo}']"),
                            # Busca EXATA em div
                            (By.XPATH, f"//div[text()='{grupo_nome_completo}']"),
                            # Busca por span que contenha EXATAMENTE todo o texto
                            (By.XPATH, f"//span[contains(text(), '{grupo_nome_completo}')]"),
                            # Busca por elemento que contenha o texto completo
                            (By.XPATH, f"//*[contains(text(), '{grupo_nome_completo}')]"),
                            # Fallback: primeiro resultado se a busca foi específica
                            (By.CSS_SELECTOR, '[data-testid="cell-frame-container"]:first-child'),
                        ]
                        
                        group_found = False
                        for method, selector in group_selectors:
                            try:
                                group_element = wait.until(EC.element_to_be_clickable((method, selector)))
                                group_element.click()
                                print(f"[WHATSAPP] Grupo encontrado e clicado: {selector[:50]}")
                                group_found = True
                                time.sleep(2)
                                break
                            except:
                                continue
                        
                        if not group_found:
                            print("[WHATSAPP] ERRO Grupo nao encontrado")
                            return {"success": False, "error": "Grupo nao encontrado"}
                    else:
                        print("[WHATSAPP] ERRO Nao conseguiu encontrar campo de busca")
                        return {"success": False, "error": "Campo busca nao encontrado"}
                    
                    # Enviar arquivos
                    sent_count = 0
                    for file_info in files:
                        try:
                            # Envio robusto usando seletores do código antigo
                            print(f"[WHATSAPP] Enviando: {file_info['page']} ({file_info['file_size_kb']} KB)")
                            
                            # 1. Clicar no botão anexar
                            attach_selectors = [
                                (By.CSS_SELECTOR, "span[data-icon='plus-rounded']"),
                                (By.CSS_SELECTOR, "span[data-icon='attach-menu-plus']"),
                                (By.CSS_SELECTOR, "button[aria-label='Anexar']"),
                                (By.CSS_SELECTOR, "button[title='Anexar']"),
                                (By.XPATH, "//span[contains(@data-icon, 'plus')]"),
                                (By.XPATH, "//div[contains(@role, 'button') and contains(@aria-label, 'Anexar')]"),
                                (By.CSS_SELECTOR, '[data-testid="attach-menu-plus"]')
                            ]
                            
                            clip_clicked = False
                            for method, selector in attach_selectors:
                                try:
                                    # Aumentar timeout para encontrar botão anexar
                                    clip_button = WebDriverWait(driver, 15).until(EC.element_to_be_clickable((method, selector)))
                                    driver.execute_script("arguments[0].click();", clip_button)
                                    print(f"[WHATSAPP] Botao anexar clicado: {selector[:40]}")
                                    clip_clicked = True
                                    time.sleep(3)  # Aguardar menu aparecer
                                    break
                                except:
                                    continue
                            
                            if not clip_clicked:
                                print(f"[WHATSAPP] ERRO Nao conseguiu clicar em anexar")
                                continue
                            
                            # 2. Buscar "Fotos e vídeos" OU input de arquivo diretamente (como código antigo)
                            photos_selectors = [
                                (By.XPATH, "//span[contains(text(), 'Fotos e vídeos')]"),
                                (By.CSS_SELECTOR, "span.xdod15v:contains('Fotos e vídeos')"),
                                (By.XPATH, "//div[contains(@role, 'button')]//span[contains(text(), 'Fotos')]"),
                                # IMPORTANTE: Input de arquivo TAMBÉM nos seletores de fotos (como código antigo)
                                (By.XPATH, "//input[@type='file'][@accept='image/*,video/mp4,video/3gpp,video/quicktime']"),
                                (By.CSS_SELECTOR, "li[data-animate-dropdown-item='true']")
                            ]
                            
                            # Tentar clicar em fotos e vídeos OU encontrar input diretamente
                            photos_clicked = False
                            file_input_found = None
                            
                            for method, selector in photos_selectors:
                                try:
                                    element = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((method, selector)))
                                    
                                    # Se é input de arquivo, guardar para usar depois
                                    if 'input' in selector:
                                        file_input_found = element
                                        print(f"[WHATSAPP] Input de arquivo encontrado diretamente: {selector[:40]}")
                                        photos_clicked = True
                                        break
                                    else:
                                        # Se não é input, tentar clicar (botão fotos e vídeos)
                                        driver.execute_script("arguments[0].click();", element)
                                        print(f"[WHATSAPP] Opcao fotos clicada: {selector[:40]}")
                                        photos_clicked = True
                                        time.sleep(2)
                                        break
                                except:
                                    continue
                            
                            if not photos_clicked:
                                print("[WHATSAPP] ERRO Nao conseguiu encontrar opcao fotos nem input")
                                continue
                            
                            # 3. Enviar arquivo via input (buscar se não encontrou antes)
                            if file_input_found is None:
                                file_input_selectors = [
                                    (By.CSS_SELECTOR, "input[type='file'][accept*='image/*']"),
                                    (By.XPATH, "//input[@type='file']"),
                                    (By.XPATH, "//input[@accept='image/*,video/mp4,video/3gpp,video/quicktime']"),
                                    (By.CSS_SELECTOR, '[data-testid="attach-input"]')
                                ]
                                
                                for method, selector in file_input_selectors:
                                    try:
                                        file_input_found = WebDriverWait(driver, 30).until(EC.presence_of_element_located((method, selector)))
                                        print(f"[WHATSAPP] Input encontrado apos fotos: {selector[:40]}")
                                        break
                                    except:
                                        continue
                            
                            # Enviar arquivo
                            if file_input_found:
                                try:
                                    print(f"[WHATSAPP] Enviando arquivo: {file_info['file_path']}")
                                    file_input_found.send_keys(file_info['file_path'])
                                    print(f"[WHATSAPP] Arquivo {file_info['page']} selecionado com sucesso")
                                    time.sleep(5)  # Aguardar arquivo carregar
                                    
                                    # 4. Clicar no botão enviar (seletores do código antigo)
                                    send_selectors = [
                                        (By.CSS_SELECTOR, "div[aria-label='Enviar']"),
                                        (By.XPATH, "//div[@aria-label='Enviar']"),
                                        (By.XPATH, "//span[@data-icon='wds-ic-send-filled']"),
                                        (By.CSS_SELECTOR, "button[aria-label='Enviar']"),
                                        (By.CSS_SELECTOR, "div[role='button'][aria-label='Enviar']"),
                                        (By.XPATH, "//div[contains(@class, 'x14yjl9h')]"),
                                        (By.XPATH, "//div[@role='button' and contains(@class, 'x78zum5')]"),
                                        (By.CSS_SELECTOR, '[data-testid="send-btn"]')
                                    ]
                                    
                                    send_clicked = False
                                    for send_method, send_selector in send_selectors:
                                        try:
                                            send_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable((send_method, send_selector)))
                                            driver.execute_script("arguments[0].click();", send_button)
                                            print(f"[WHATSAPP] OK Enviado: {file_info['page']} via {send_selector[:30]}")
                                            sent_count += 1
                                            send_clicked = True
                                            time.sleep(8)  # Tempo maior para garantir envio (como código antigo)
                                            break
                                        except:
                                            continue
                                    
                                    if not send_clicked:
                                        print(f"[WHATSAPP] ERRO Nao conseguiu clicar em enviar para {file_info['page']}")
                                        
                                except Exception as e:
                                    print(f"[WHATSAPP] ERRO ao enviar arquivo {file_info['page']}: {str(e)[:50]}")
                            else:
                                print(f"[WHATSAPP] ERRO Input de arquivo nao encontrado para {file_info['page']}")
                            
                        except Exception as e:
                            print(f"[WHATSAPP] ERRO enviando {file_info['page']}: {str(e)[:50]}")
                    
                    # Aguardar mais tempo no final para garantir que todas mensagens foram enviadas
                    if sent_count > 0:
                        print(f"[WHATSAPP] Aguardando 15 segundos para garantir que todas mensagens foram carregadas e enviadas...")
                        time.sleep(15)  # Pausa maior como no código antigo (time.sleep(10))
                    
                    print(f"[WHATSAPP] OK Enviados {sent_count}/{len(files)} arquivos")
                    
                    # Só considerar sucesso se enviou pelo menos 1 arquivo
                    success = sent_count > 0
                    return {"success": success, "total_sent": sent_count}
                    
                except:
                    print("[WHATSAPP] ERRO QR Code necessario - perfil nao esta logado")
                    # Manter o driver aberto para escaneamento manual
                    print("[WHATSAPP] Deixando Chrome aberto para configuracao manual...")
                    print("[WHATSAPP] Escaneie o QR Code e feche o Chrome manualmente")
                    
                    # Aguardar até 2 minutos para escaneamento manual
                    time.sleep(120)
                    return {"success": False, "error": "QR Code necessario - configure manualmente"}
                    
            finally:
                try:
                    driver.quit()
                except:
                    pass
                
        except Exception as e:
            print(f"[WHATSAPP] ERRO geral: {str(e)[:100]}")
            return {"success": False, "error": str(e)[:100]}
    
    def setup_chrome_options(self, headless=False):
        """Compatibilidade com outros serviços - retorna options BRAVE"""
        return self.setup_brave_options(headless=headless)
    
    def send_screenshots(self, files, group_name="OracleSys - Império Prêmios [ROI DIÁRIO]"):
        """Compatibilidade com outros serviços"""
        return self.send_images_smart(files)