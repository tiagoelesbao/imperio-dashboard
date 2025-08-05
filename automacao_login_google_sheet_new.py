import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import json
import os
from datetime import datetime
import pytz
import time
import schedule
import logging
import traceback

# ===============================
# Configuração de Logging
# ===============================
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.FileHandler("automacao.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ===============================
# Configurações Gerais
# ===============================

# URLs das APIs de Vendas/Afiliados
URL_API_ORDERS_BY_DAY = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/684c73283d75820c0a77a42f/ordersByDay"
URL_API_AFFILIATES = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/684c73283d75820c0a77a42f/affiliates/data"
URL_LOGIN_API = "https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/auth/login"

# Configurações do Google Sheets
GOOGLE_SHEETS_KEY = "1jlhjqvDFJ28vA_fjTm4OwjoGhhPY-ljFhoa0aomK-so"
CREDENCIAIS_GOOGLE = r"C:\Users\Pichau\Desktop\Sistemas\OracleSys\Clientes\Imperio\REGISTRO_VENDAS_SCHENDULE\credenciais_google.json"

# Credenciais de acesso à API (Vendas/Afiliados)
USUARIO = "tiago"
SENHA = "Tt!1zxcqweqweasd"

# Afiliados de interesse
AFFILIADO_CODE_GRUPO_1 = "17QB25AKRL"
AFFILIADO_CODE_GRUPO_2 = "30CS8W9DP1"
AFFILIADO_CODE_INSTAGRAM = "L8UTEDVTI0"

# Abas da planilha para Vendas/Afiliados
ABA_PAGINA1 = "Página1"
ABA_INSTAGRAM = "Página2"
ABA_GRUPO = "Página3"

# -------------------------------
# Configurações do Facebook Ads ROI
# -------------------------------
FACEBOOK_ACCESS_TOKEN = 'EAAT6ZBgzXABUBO0zMuZCXBmauERl111KuLZAzkEgVhrkhs2RJT8rZAZCxyZB1YhyicYw3fe9XxmCngjv0BDmZCPeBNFIU5kGBZARZAwzPNMaENwiJia7ilwTzsNWxnzi8L2ly3PV2OQAuRzPXFyxXdNdJxWypZBBWeUvZBWrKYIDUTZBAaWsPHd8KmgfaPH8Mt8eb5U7V36T1ne1'

# ===============================
# Funções Auxiliares
# ===============================

def converter_para_numero(valor):
    try:
        return float(valor)
    except Exception:
        if isinstance(valor, str):
            valor = valor.replace("R$", "").replace(" ", "")
            valor = valor.replace(".", "").replace(",", ".")
            try:
                return float(valor)
            except Exception as e:
                logger.error(f"Não foi possível converter '{valor}': {e}")
                return 0
        return 0

def truncar_para_minuto(dt):
    return dt.replace(second=0, microsecond=0)

def configurar_gspread():
    logger.info("Configurando Google Sheets API...")
    scope = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive.file",
        "https://www.googleapis.com/auth/drive"
    ]
    creds = ServiceAccountCredentials.from_json_keyfile_name(CREDENCIAIS_GOOGLE, scope)
    client = gspread.authorize(creds)
    logger.info("Google Sheets API configurada com sucesso.")
    return client

# ===============================
# Funções de Vendas/Afiliados
# ===============================

def obter_token_via_requests(email, password):
    logger.info("Fazendo login via API para obter o token...")
    payload = {"email": email, "password": password}
    headers = {"Content-Type": "application/json", "Accept": "application/json"}
    response = requests.post(URL_LOGIN_API, json=payload, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if "accessToken" in data:
            logger.info("Token obtido via requests.")
            return data["accessToken"]
        else:
            raise Exception("'accessToken' não encontrado no JSON.")
    else:
        raise Exception(f"Falha ao autenticar: {response.status_code} - {response.text}")

def obter_dados_orders_by_day(token):
    logger.info("Fazendo requisição à API (ordersByDay)...")
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    r = requests.get(URL_API_ORDERS_BY_DAY, headers=headers)
    if r.status_code == 200:
        logger.info("Dados obtidos de ordersByDay.")
        return r.json()
    else:
        raise Exception(f"Falha ordersByDay: {r.status_code} - {r.text}")

def processar_dados_pagina1(dados_json):
    logger.info("Processando dados para Página1...")
    dados_formatados = []
    for item in dados_json.get("somasPorDia", []):
        date_str = item["_id"]  # "YYYY-MM-DD"
        dt = datetime.strptime(date_str, '%Y-%m-%d')
        formatted = dt.strftime('%d/%m/%Y')
        dados_formatados.append([
            formatted,
            item["totalOrdensPorDia"],
            item["totalNumerosPorDia"],
            item["totalPorDia"]
        ])
    return dados_formatados

def registrar_dados_pagina1(dados):
    logger.info("Registrando dados na Página1...")
    client = configurar_gspread()
    sheet = client.open_by_key(GOOGLE_SHEETS_KEY).worksheet(ABA_PAGINA1)
    dados.reverse()
    last_row_needed = 1 + len(dados)
    range_name = f"A2:D{last_row_needed}"
    
    sheet.update(values=dados, range_name=range_name, value_input_option="USER_ENTERED")
    sheet.format("A2:A", {"numberFormat": {"type": "DATE_TIME", "pattern": "dd/MM/yyyy HH:mm:ss"}})
    sheet.format("B2:B", {"numberFormat": {"type": "NUMBER"}})
    sheet.format("C2:C", {"numberFormat": {"type": "NUMBER"}})
    sheet.format("D2:D", {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}})
    logger.info("Página1 atualizada com sucesso.")

def obter_dados_afiliados(token):
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    now_local = datetime.now(tz_brasilia)
    start_of_day_local = now_local.replace(hour=0, minute=1, second=0, microsecond=0)
    now_utc = now_local.astimezone(pytz.UTC)
    start_of_day_utc = start_of_day_local.astimezone(pytz.UTC)
    init = start_of_day_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')
    end = now_utc.strftime('%Y-%m-%dT%H:%M:%S.000Z')

    logger.info(f"Afiliados entre {init} e {end} (UTC).")
    params = {"init": init, "end": end, "name": "", "affiliateCode": ""}
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    resp = requests.get(URL_API_AFFILIATES, headers=headers, params=params)
    if resp.status_code == 200:
        logger.info("Dados de afiliados obtidos.")
        return resp.json()
    else:
        raise Exception(f"Falha afiliados: {resp.status_code} - {resp.text}")

def processar_dados_afiliados(data):
    resultado = {}
    for item in data:
        code = item["user"].get("affiliateCode", "")
        paid = item.get("totalPaidOrders", 0)
        count = item.get("orderCount", 0)
        resultado[code] = {"totalPaidOrders": paid, "orderCount": count}
    return resultado

def update_or_insert_by_date(sheet, date_str, row_data):
    all_values = sheet.get_all_values()
    for i, row in enumerate(all_values[1:], start=2):
        if row and row[0] and row[0][:10] == date_str:
            sheet.update(values=[row_data], range_name=f"A{i}:D{i}", value_input_option="USER_ENTERED")
            return
    new_row = len(all_values) + 1
    sheet.update(values=[row_data], range_name=f"A{new_row}:D{new_row}", value_input_option="USER_ENTERED")

def registrar_dados_google_sheets_afiliado(aba_planilha, dados_afiliado):
    client = configurar_gspread()
    sheet = client.open_by_key(GOOGLE_SHEETS_KEY).worksheet(aba_planilha)
    tz_brasilia = pytz.timezone('America/Sao_Paulo')
    date_str = datetime.now(tz_brasilia).strftime('%d/%m/%Y')
    total = dados_afiliado["totalPaidOrders"]
    qtd = dados_afiliado["orderCount"]
    ticket = total / qtd if qtd > 0 else 0
    row_data = [date_str, ticket, qtd, total]
    update_or_insert_by_date(sheet, date_str, row_data)

    sheet.format("A2:A", {"numberFormat": {"type": "DATE_TIME", "pattern": "dd/MM/yyyy HH:mm:ss"}})
    sheet.format("B2:B", {"numberFormat": {"type": "NUMBER", "pattern": "0.00"}})
    sheet.format("C2:C", {"numberFormat": {"type": "NUMBER"}})
    sheet.format("D2:D", {"numberFormat": {"type": "CURRENCY", "pattern": "R$ #,##0.00"}})
    logger.info(f"Afiliado '{aba_planilha}' atualizado com sucesso.")

# ===============================
# Funções de ROI do Facebook Ads
# ===============================

def verificar_token_facebook(token):
    """
    Função para verificar o status do token do Facebook
    """
    logger.info("Verificando token do Facebook...")
    try:
        # Teste básico do token
        verify_url = f"https://graph.facebook.com/v18.0/me?access_token={token}"
        verify_resp = requests.get(verify_url)
        
        if verify_resp.status_code != 200:
            logger.warning(f"Token do Facebook pode estar com problemas: {verify_resp.status_code}")
            return False
        
        logger.info("Verificação básica do token bem-sucedida")
        return True
    except Exception as e:
        logger.error(f"Erro ao verificar token: {e}")
        return False

def obter_dados_facebook_ads(account_ids, access_token, sheet_scrap_roi):
    client = configurar_gspread()
    sheet = sheet_scrap_roi
    
    # Verificar token primeiro
    token_ok = verificar_token_facebook(access_token)
    
    all_vals = sheet.get_all_values()
    if not all_vals:
        sheet.update(values=[["Extraction Datetime", "Account Name", "Spend"]], range_name="A1:C1", value_input_option="USER_ENTERED")

    for act_id in account_ids:
        if act_id == 'act_' or not act_id:
            logger.warning(f"ID de conta inválido ignorado: '{act_id}'")
            continue
        
        # Se o token não está ok, use valor zero para não quebrar o fluxo
        if not token_ok:
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            all_vals = sheet.get_all_values()
            new_row = len(all_vals) + 1
            sheet.update(values=[[now_str, act_id, 0]], range_name=f"A{new_row}:C{new_row}", value_input_option="USER_ENTERED")
            logger.warning(f"Usando valor zero para {act_id} devido a problemas com o token")
            continue
            
        # Tentar versão mais recente da API primeiro
        urls = [
            f"https://graph.facebook.com/v18.0/{act_id}/insights?fields=spend&date_preset=today&access_token={access_token}",
            f"https://graph.facebook.com/v17.0/{act_id}/insights?fields=spend&date_preset=today&access_token={access_token}",
            f"https://graph.facebook.com/v16.0/{act_id}/insights?fields=spend&date_preset=today&access_token={access_token}"
        ]
        
        success = False
        for url in urls:
            try:
                logger.info(f"Tentando API com URL: {url[:50]}...")
                resp = requests.get(url)
                if resp.status_code == 200:
                    data = resp.json()
                    spend_val = 0
                    if "data" in data and len(data["data"]) > 0:
                        try:
                            spend_val = float(data["data"][0]["spend"])
                            logger.info(f"Dados de gastos obtidos com sucesso para {act_id}: {spend_val}")
                        except Exception as e:
                            logger.error(f"Falha parse spend em {act_id}: {e}")
                    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                    all_vals = sheet.get_all_values()
                    new_row = len(all_vals) + 1
                    sheet.update(values=[[now_str, act_id, spend_val]], range_name=f"A{new_row}:C{new_row}", value_input_option="USER_ENTERED")
                    success = True
                    break
                elif "OAuthException" in resp.text:
                    # Problemas específicos de autenticação, tentar próxima versão
                    logger.warning(f"Erro de autenticação na API: {resp.status_code}")
                    continue
                else:
                    logger.error(f"Erro na API {url[:30]}: {resp.status_code} - {resp.text[:100]}")
            except Exception as e:
                logger.error(f"Erro ao buscar {act_id}: {e}")
        
        # Se nenhuma das versões funcionou, use valor zero
        if not success:
            now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            all_vals = sheet.get_all_values()
            new_row = len(all_vals) + 1
            sheet.update(values=[[now_str, act_id, 0]], range_name=f"A{new_row}:C{new_row}", value_input_option="USER_ENTERED")
            logger.warning(f"Usado valor zero para {act_id} após falhas nas tentativas de API")

def gravar_historico_roi(sheet_pagina, sheet_scrap_roi, sheet_historico):
    pagina_vals = sheet_pagina.get_all_values()
    if len(pagina_vals) < 2:
        logger.error("Vazio em página de vendas.")
        return
    last_pagina = pagina_vals[-1]
    vendas_amz = converter_para_numero(last_pagina[3])

    scrap_vals = sheet_scrap_roi.get_all_values()
    if len(scrap_vals) < 2:
        logger.error("Vazio em scrap ROI.")
        return

    try:
        ultima_hora = datetime.strptime(scrap_vals[-1][0], "%d/%m/%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Falha parse data do scrap: {e}")
        return
    ultima_trunc = truncar_para_minuto(ultima_hora)

    total_gasto = 0
    for row in scrap_vals[1:]:
        try:
            dt_row = datetime.strptime(row[0], "%d/%m/%Y %H:%M:%S")
        except:
            continue
        if truncar_para_minuto(dt_row) == ultima_trunc:
            total_gasto += converter_para_numero(row[2])

    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    roi = vendas_amz / total_gasto if total_gasto > 0 else 0

    historico_vals = sheet_historico.get_all_values()
    new_row = len(historico_vals) + 1
    sheet_historico.update(
        values=[[now_str, total_gasto, vendas_amz, roi]], 
        range_name=f"A{new_row}:D{new_row}",
        value_input_option="USER_ENTERED"
    )
    sheet_historico.format("A:A", {"numberFormat": {"type": "DATE_TIME", "pattern": "dd/MM/yyyy HH:mm:ss"}})
    logger.info(f"gravar_historico_roi: Vendas={vendas_amz}, Gasto={total_gasto}, ROI={roi}")

def gravar_historico_roi_ultima_hora(sheet_historico, sheet_historico_ultima_hora):
    vals = sheet_historico.get_all_values()
    if len(vals) < 3:
        logger.error("Poucos registros no HISTÓRICO ROI.")
        return
    data_rows = vals[1:]
    last_row = data_rows[-1]
    prev_row = data_rows[-2]
    try:
        last_spend = converter_para_numero(last_row[1])
        last_sales = converter_para_numero(last_row[2])
        prev_spend = converter_para_numero(prev_row[1])
        prev_sales = converter_para_numero(prev_row[2])
    except Exception as e:
        logger.error(f"Falha parse para ROI última hora: {e}")
        return

    delta_spend = last_spend - prev_spend
    delta_sales = last_sales - prev_sales
    roi_int = delta_sales / delta_spend if delta_spend > 0 else 0

    try:
        dt_atual = datetime.strptime(last_row[0], "%d/%m/%Y %H:%M:%S")
        dt_anterior = datetime.strptime(prev_row[0], "%d/%m/%Y %H:%M:%S")
    except Exception as e:
        logger.error(f"Falha parse datas hist: {e}")
        return

    periodo = dt_anterior.strftime("%d/%m/%Y %H:%M:%S") + " às " + dt_atual.strftime("%H:%M:%S")

    ultima_vals = sheet_historico_ultima_hora.get_all_values()
    new_row = len(ultima_vals) + 1
    sheet_historico_ultima_hora.update(
        values=[[periodo, delta_spend, delta_sales, roi_int]],
        range_name=f"A{new_row}:D{new_row}",
        value_input_option="USER_ENTERED"
    )
    logger.info(f"ROI última hora: Vendas={delta_sales}, Gasto={delta_spend}, ROI={roi_int}")

def replicar_data_hora_historico(sheet_historico, sheet_historico_ultima_hora):
    hist_vals = sheet_historico.get_all_values()
    if len(hist_vals) < 2:
        logger.error("Poucos registros no hist para replicar dt.")
        return
    dt_val = hist_vals[-1][0]
    ultima_vals = sheet_historico_ultima_hora.get_all_values()
    new_row = len(ultima_vals)
    if new_row < 1:
        new_row = 1
    cell_label = f"F{new_row}"
    sheet_historico_ultima_hora.update(values=[[dt_val]], range_name=cell_label, value_input_option="USER_ENTERED")
    sheet_historico_ultima_hora.format("F:F", {"numberFormat": {"type": "DATE_TIME", "pattern": "dd/MM/yyyy HH:mm:ss"}})
    logger.info(f"Data/hora replicada no col F: {dt_val}")

def adicionar_data_hora_execucao(sheet_historico):
    vals = sheet_historico.get_all_values()
    if len(vals) < 2:
        logger.error("Poucos registros no hist para inserir dt na col F.")
        return
    last_row = len(vals)
    now_str = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    cell_label = f"F{last_row}"
    sheet_historico.update(values=[[now_str]], range_name=cell_label, value_input_option="USER_ENTERED")
    sheet_historico.format("F:F", {"numberFormat": {"type": "DATE_TIME", "pattern": "dd/MM/yyyy HH:mm:ss"}})
    logger.info(f"Execução registrada em F{last_row}: {now_str}")

def executar_etapa(account_ids, access_token, sheet_scrap_roi, sheet_pagina, sheet_historico, sheet_historico_ultima_hora):
    obter_dados_facebook_ads(account_ids, access_token, sheet_scrap_roi)
    gravar_historico_roi(sheet_pagina, sheet_scrap_roi, sheet_historico)
    gravar_historico_roi_ultima_hora(sheet_historico, sheet_historico_ultima_hora)
    replicar_data_hora_historico(sheet_historico, sheet_historico_ultima_hora)
    adicionar_data_hora_execucao(sheet_historico)

def executar_rotina_completa_roi():
    client = configurar_gspread()
    ss = client.open_by_key(GOOGLE_SHEETS_KEY)

    # Definir estrutura de dados para evitar repetição
    configs = [
        {
            'accounts': ['act_790223756353632', 'act_772777644802886', 'act_2067257390316380', 'act_406219475582745', 'act_1391112848236399', 'act_303402486183447'],
            'scrap': 'SCRAP ROI POR HORÁRIO',
            'pagina': 'Página1',
            'hist': 'HISTÓRICO ROI',
            'hist_ultima': 'HISTÓRICO ROI última hora'
        },
        {
            'accounts': ['act_790223756353632', 'act_2067257390316380', 'act_406219475582745', 'act_1391112848236399', 'act_303402486183447'],
            'scrap': 'SCRAP ROI POR HORÁRIO 2',
            'pagina': 'Página2',
            'hist': 'HISTÓRICO ROI 2',
            'hist_ultima': 'HISTÓRICO ROI última hora 2'
        },
        {
            'accounts': ['act_772777644802886'],  # Lista vazia
            'scrap': 'SCRAP ROI POR HORÁRIO 3',
            'pagina': 'Página3',
            'hist': 'HISTÓRICO ROI 3',
            'hist_ultima': 'HISTÓRICO ROI última hora 3'
        }
    ]
    
    for i, config in enumerate(configs, 1):
        logger.info(f"Executando PARTE ROI {i}")
        executar_etapa(
            config['accounts'],
            FACEBOOK_ACCESS_TOKEN,
            ss.worksheet(config['scrap']),
            ss.worksheet(config['pagina']),
            ss.worksheet(config['hist']),
            ss.worksheet(config['hist_ultima'])
        )

    logger.info("Rotina ROI finalizada com sucesso.")

def executar_automacao():
    try:
        logger.info("Iniciando automação completa...")
        token = obter_token_via_requests(USUARIO, SENHA)

        # 1) Vendas do Dia
        orders_data = obter_dados_orders_by_day(token)
        dados_p1 = processar_dados_pagina1(orders_data)
        registrar_dados_pagina1(dados_p1)

        # 2) Afiliados
        afiliados_data = obter_dados_afiliados(token)
        afiliados_proc = processar_dados_afiliados(afiliados_data)

        if AFFILIADO_CODE_INSTAGRAM not in afiliados_proc:
            raise Exception("Afiliado Instagram não encontrado no JSON.")
        insta_vals = afiliados_proc[AFFILIADO_CODE_INSTAGRAM]

        grupo1_vals = afiliados_proc.get(AFFILIADO_CODE_GRUPO_1, {"totalPaidOrders": 0, "orderCount": 0})
        grupo2_vals = afiliados_proc.get(AFFILIADO_CODE_GRUPO_2, {"totalPaidOrders": 0, "orderCount": 0})
        grupo_somado = {
            "totalPaidOrders": grupo1_vals["totalPaidOrders"] + grupo2_vals["totalPaidOrders"],
            "orderCount": grupo1_vals["orderCount"] + grupo2_vals["orderCount"]
        }

        registrar_dados_google_sheets_afiliado(ABA_INSTAGRAM, insta_vals)
        registrar_dados_google_sheets_afiliado(ABA_GRUPO, grupo_somado)
        logger.info("Afiliados finalizado.")

        # 3) ROI
        executar_rotina_completa_roi()
        logger.info("Automação completa finalizada.")

    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de conexão: {e}")
        with open("erro_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: Erro de conexão: {e}\n")
    except json.JSONDecodeError as e:
        logger.error(f"Erro ao decodificar JSON: {e}")
        with open("erro_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: Erro ao decodificar JSON: {e}\n")
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        with open("erro_log.txt", "a", encoding="utf-8") as f:
            f.write(f"{datetime.now()}: {str(e)}\n{traceback.format_exc()}\n")

def agendar_automacao():
    # Corrigindo o tempo de agendamento
    schedule.every().hour.at(":00").do(executar_automacao)
    schedule.every().hour.at(":30").do(executar_automacao)
    logger.info("Agendamento iniciado (xx:00 e xx:30).")
    
    # Executar imediatamente no início
    executar_automacao()
    
    while True:
        schedule.run_pending()
        time.sleep(10)

if __name__ == "__main__":
    agendar_automacao()