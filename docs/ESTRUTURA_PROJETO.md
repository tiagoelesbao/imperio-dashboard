# Estrutura do Projeto - Sistema Imperio

## Última Atualização: 02/11/2025

## 📁 Estrutura de Diretórios

```
REGISTRO_VENDAS_SCHENDULE/
│
├── 📂 clients/                    # Cliente Imperio
│   └── imperio/
│       ├── api/                   # APIs do sistema
│       │   ├── main_action_routes.py  # Rotas da Ação Principal
│       │   ├── pages.py               # Páginas web
│       │   └── routes.py              # Rotas gerais
│       ├── services/              # Serviços
│       │   ├── horapix_service.py         # Hora do Pix
│       │   ├── imperio_data_service.py    # Dados gerais
│       │   ├── imperio_database_service.py # Banco de dados
│       │   └── imperio_google_sheets.py   # Google Sheets (legado)
│       ├── templates/             # Templates HTML
│       │   ├── imperio.html              # Dashboard principal
│       │   ├── _main_action_section.html # Seção Ação Principal
│       │   └── _main_action_javascript.js # JS Ação Principal
│       └── config.py              # Configurações do cliente
│
├── 📂 core/                       # Sistema Core
│   ├── app.py                     # FastAPI app principal
│   ├── database/                  # Configuração do banco
│   │   └── base.py
│   ├── models/                    # Modelos de dados
│   │   ├── base.py                      # Modelos principais
│   │   ├── horapix.py                   # Modelo Hora do Pix
│   │   └── main_action.py               # Modelo Ação Principal
│   ├── services/                  # Serviços core
│   │   ├── data_collector.py            # Coletor de dados
│   │   ├── data_manager.py              # Gerenciador de dados
│   │   ├── main_action_collector.py     # Coletor Ação Principal
│   │   ├── main_action_service.py       # Serviço Ação Principal
│   │   ├── facebook_collector.py        # Coletor Facebook
│   │   ├── capture_service.py           # Captura screenshots
│   │   ├── capture_service_fast.py      # Captura otimizada
│   │   └── error_handler.py             # Tratamento de erros
│   └── utils/                     # Utilitários
│       └── scheduler.py                 # Agendador de tarefas
│
├── 📂 scripts/                    # Scripts auxiliares
│   ├── collect_horapix_initial.py       # Coleta inicial Hora do Pix
│   ├── reset_database_simple.py         # Reset do banco (preserva Ação Principal)
│   ├── send_whatsapp_screenshots.py     # Envio WhatsApp
│   ├── TESTAR_ACAO_PRINCIPAL.bat        # Teste Ação Principal
│   ├── TESTAR_COLETA_COMPLETA.bat       # Teste coleta completa
│   └── configurar_whatsapp.bat          # Configurar WhatsApp
│
├── 📂 tests/                      # Testes do sistema
│   ├── test_full_collection.py          # Teste coleta completa
│   ├── test_main_action.py              # Teste Ação Principal
│   ├── test_horapix.py                  # Teste Hora do Pix
│   └── test_horapix_quick.py            # Teste rápido Hora do Pix
│
├── 📂 docs/                       # Documentação
│   ├── ACAO_PRINCIPAL_IMPLEMENTACAO.md  # Documentação Ação Principal
│   ├── ATUALIZACAO_PRODUCT_ID_02112025.md # Atualização Product ID
│   ├── CORRECOES_02112025.md            # Correções recentes
│   └── ESTRUTURA_PROJETO.md             # Este arquivo
│
├── 📂 data/                       # Dados do sistema
│   ├── imperio.db                       # Banco SQLite
│   ├── logs/                            # Arquivos de log
│   └── whatsapp_session/                # Sessão WhatsApp
│
├── 📂 static/                     # Arquivos estáticos
│   ├── css/                             # Estilos CSS
│   └── js/                              # JavaScript
│
├── 📂 screenshots/                # Screenshots capturados
│
├── 📂 temp_upload/                # Uploads temporários
│
├── 📂 venv/                       # Ambiente virtual Python
│
├── 📜 .env                        # Variáveis de ambiente
├── 📜 .env.example                # Exemplo de variáveis
├── 📜 .env.horapix                # Configuração Hora do Pix
├── 📜 requirements.txt            # Dependências Python
│
├── 🚀 imperio_start.bat           # Iniciar sistema
├── 🔄 imperio_daily_reset.bat     # Reset diário
└── 📸 imperio_capture_send_v2.bat # Captura e envio

```

## 🎯 Funcionalidades Principais

### 1. **Ação Principal**
- Monitoramento de sorteios específicos
- Dados permanentes (não resetados)
- Dashboard em: `/imperio#acaoprincipal`

### 2. **Hora do Pix**
- Coleta de sorteios ativos
- Taxa de 3% calculada
- Integrado ao scheduler

### 3. **Monitoramento por Canal**
- **Geral:** Visão consolidada
- **Perfil/Instagram:** Vendas do Instagram
- **Grupos:** Vendas WhatsApp/Telegram

### 4. **Orçamento Atual**
- Exibição de budget por canal
- ROI em tempo real
- Gastos Facebook Ads

## 🔧 Scripts de Execução

### Produção
```bash
# Iniciar sistema
imperio_start.bat

# Reset diário (preserva Ação Principal)
imperio_daily_reset.bat

# Captura e envio WhatsApp
imperio_capture_send_v2.bat
```

### Testes
```bash
# Testar coleta completa
cd tests && python test_full_collection.py

# Testar Ação Principal
cd tests && python test_main_action.py

# Testar Hora do Pix
cd tests && python test_horapix.py
```

## 📊 Banco de Dados

### Tabelas Principais
- `daily_snapshots` - Snapshots diários
- `channel_data` - Dados por canal
- `collection_logs` - Logs de coleta
- `capture_logs` - Logs de captura
- `horapix_draws` - Sorteios Hora do Pix
- `main_actions` - Ações principais (PERMANENTE)
- `main_action_daily` - Dados diários das ações (PERMANENTE)

### Importante
- Tabelas `main_actions` e `main_action_daily` **NUNCA são resetadas**
- Demais tabelas são limpas no reset diário

## 🔄 Scheduler Automático

### Coletas (XX:00 e XX:30)
1. Sistema Principal (Imperio + Facebook)
2. Hora do Pix
3. Ação Principal

### Capturas (XX:01 e XX:31)
- Screenshots otimizados
- Envio automático WhatsApp

## 🛠️ Configurações

### Product ID Atual
```
6904ea540d0e097d618827fc
```

### Arquivo de Configuração
- `/clients/imperio/config.py`

### Variáveis de Ambiente
- `.env` - Configurações principais
- `.env.horapix` - Configuração Hora do Pix

## 📝 Arquivos Removidos

Durante a organização, foram removidos:
- 17 arquivos de teste temporários
- 8 scripts obsoletos
- Arquivos duplicados
- Código legado não utilizado

## 🚀 Como Usar

1. **Desenvolvimento**
   ```bash
   cd tests
   python test_full_collection.py
   ```

2. **Produção**
   ```bash
   imperio_start.bat
   ```

3. **Dashboard**
   - http://localhost:8002/imperio
   - http://localhost:8002/imperio#acaoprincipal

## ✅ Status do Sistema

- **Core:** ✅ Funcionando
- **Ação Principal:** ✅ Operacional
- **Hora do Pix:** ✅ Ativo
- **Monitoramento:** ✅ Online
- **Scheduler:** ✅ Rodando

---

*Projeto organizado e otimizado em 02/11/2025*