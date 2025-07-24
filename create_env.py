#!/usr/bin/env python3
"""Script para criar arquivo .env"""

env_content = """# Configurações da API
API_USERNAME=tiago
API_PASSWORD=Tt!1zxcqweqweasd

# URLs da API
URL_API_ORDERS_BY_DAY=https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/684c73283d75820c0a77a42f/ordersByDay
URL_API_AFFILIATES=https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/product/684c73283d75820c0a77a42f/affiliates/data
URL_LOGIN_API=https://node209534-imperiopremioss.sp1.br.saveincloud.net.br/api/auth/login

# Google Sheets
GOOGLE_SHEETS_KEY=1jlhjqvDFJ28vA_fjTm4OwjoGhhPY-ljFhoa0aomK-so
GOOGLE_CREDENTIALS_PATH=./credenciais_google.json

# Facebook Ads
FACEBOOK_ACCESS_TOKEN=EAAT6ZBgzXABUBO0zMuZCXBmauERl111KuLZAzkEgVhrkhs2RJT8rZAZCxyZB1YhyicYw3fe9XxmCngjv0BDmZCPeBNFIU5kGBZARZAwzPNMaENwiJia7ilwTzsNWxnzi8L2ly3PV2OQAuRzPXFyxXdNdJxWypZBBWeUvZBWrKYIDUTZBAaWsPHd8KmgfaPH8Mt8eb5U7V36T1ne1

# Códigos dos Afiliados
AFFILIADO_CODE_GRUPO_1=17QB25AKRL
AFFILIADO_CODE_GRUPO_2=30CS8W9DP1
AFFILIADO_CODE_INSTAGRAM=L8UTEDVTI0

# Configurações das Abas
ABA_PAGINA1=Página1
ABA_INSTAGRAM=Página2
ABA_GRUPO=Página3

# Contas do Facebook Ads por Canal (separadas por vírgula)
FACEBOOK_ACCOUNT_IDS_GERAL=act_790223756353632,act_2067257390316380,act_406219475582745,act_1391112848236399
FACEBOOK_ACCOUNT_IDS_INSTAGRAM=act_790223756353632,act_2067257390316380
FACEBOOK_ACCOUNT_IDS_GRUPO=act_406219475582745,act_1391112848236399

# Banco de Dados (SQLite para Windows)
DATABASE_URL=sqlite:///./dashboard_roi.db

# Configurações do Servidor
HOST=0.0.0.0
PORT=8000
DEBUG=False

# Configurações de Agendamento
COLLECTION_INTERVAL_MINUTES=30
MAX_RETRIES=3
RETRY_DELAY_SECONDS=60"""

with open('.env', 'w', encoding='utf-8') as f:
    f.write(env_content)

print("Arquivo .env criado com sucesso!")