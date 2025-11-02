# Sistema Hora do Pix - Documentação Completa

## Visão Geral

Sistema completo para monitoramento de sorteios "Hora do Pix" integrado ao dashboard Império Prêmios. Utiliza o MESMO método de coleta do sistema principal (Selenium) para garantir compatibilidade e confiabilidade.

### ⚠️ Taxa da Plataforma (3%)

O sistema considera automaticamente a **taxa de 3% da plataforma** em todos os cálculos:
- **Receita Bruta**: Valor total das vendas (preço × quantidade vendida)
- **Taxa Plataforma**: 3% da receita bruta
- **Lucro Líquido**: Receita - Prêmio - Taxa (3%)
- **ROI**: (Lucro / (Prêmio + Taxa)) × 100

**Exemplo de cálculo:**
```
Receita: R$ 10.000,00
Prêmio: R$ 5.000,00
Taxa (3%): R$ 300,00
Lucro Líquido: R$ 10.000 - R$ 5.000 - R$ 300 = R$ 4.700,00
ROI: (R$ 4.700 / (R$ 5.000 + R$ 300)) × 100 = 88,68%
```

## Arquitetura

### 1. Coleta de Dados (Backend)

**Arquivo:** `core/services/horapix_collector_selenium.py`

- Usa Selenium WebDriver (igual ao sistema principal)
- Faz login automático no painel https://painel.imperiopremioss.com/
- Navega até a página de produtos/sorteios
- Extrai dados diretamente do HTML
- Processa e estrutura as informações

**Credenciais:** Carregadas do arquivo `.env`
- `API_USERNAME=tiago`
- `API_PASSWORD=Tt!1zxcqweqweasd`

### 2. Modelos de Dados

**Arquivo:** `core/models/horapix.py`

Duas tabelas principais:

#### HoraPixCollection
Armazena snapshots de coletas com totais agregados:
- `total_draws`: Total de sorteios
- `active_draws`: Sorteios ativos
- `finished_draws`: Sorteios finalizados
- `total_prize_value`: Valor total em prêmios
- `total_revenue`: Receita total bruta
- `total_platform_fee`: **Taxa total da plataforma (3% da receita)**
- `total_profit`: Lucro líquido (receita - prêmio - taxa)
- `total_roi`: ROI médio considerando prêmio + taxa
- `raw_data`: Dados brutos em JSON

#### HoraPixDraw
Armazena informações individuais de cada sorteio:
- `draw_id`: ID único do sorteio
- `title`: Título/nome do sorteio
- `status`: Status (active/done)
- `prize_value`: Valor do prêmio
- `qty_paid`: Quantidade vendida
- `qty_total`: Quantidade total
- `revenue`: Receita bruta calculada
- `platform_fee`: **Taxa da plataforma (3% da receita)**
- `profit`: Lucro líquido (receita - prêmio - taxa)
- `roi`: ROI calculado considerando prêmio + taxa

### 3. Camada de Serviço

**Arquivo:** `clients/imperio/services/horapix_service.py`

Responsável por:
- Orquestrar coletas
- Salvar dados no banco
- Recuperar últimas coletas
- Gerar estatísticas

### 4. API REST

**Arquivo:** `clients/imperio/api/routes.py` (linhas 1460-1585)

Endpoints criados:
- `POST /api/imperio/horapix/collect` - Coleta manual de dados
- `GET /api/imperio/horapix/latest` - Últimos dados coletados
- `GET /api/imperio/horapix/statistics` - Estatísticas do dia
- `GET /api/imperio/horapix/draws` - Todos os sorteios
- `GET /api/imperio/horapix/draws/{draw_id}` - Sorteio específico

### 5. Frontend

**Arquivo:** `clients/imperio/templates/imperio.html`

#### Menu (linha 639)
```html
<a href="#horapix" class="menu-item" data-view="horapix">
    <i class="fas fa-clock"></i>Hora do Pix
</a>
```

#### Interface (linhas 904-1033)
- Header com gradient roxo
- **5 Cards de KPIs principais:**
  * **Prêmios**: Valor total em prêmios
  * **Receita**: Receita total bruta
  * **Taxa (3%)**: Taxa da plataforma (destaque vermelho)
  * **Lucro Líquido**: Lucro após descontar prêmio e taxa
  * **ROI Médio**: Retorno sobre investimento
- 3 Tabs:
  * **Sorteios Ativos**: Cards com detalhes de cada sorteio ativo
  * **Sorteios Finalizados**: Cards de sorteios já concluídos
  * **Estatísticas**: Gráficos e análises (gráficos)
- Botão "Atualizar Agora" para coleta manual

**Cards Individuais de Sorteios:**
Cada sorteio exibe:
- Título e status (ativo/finalizado)
- Progresso de vendas (barra de progresso)
- Prêmio, Receita, Taxa (3% em destaque vermelho)
- Lucro Líquido e ROI (cores verde/vermelho conforme resultado)

#### JavaScript (linhas 1948-2178)
Funções principais:
- `loadHoraPixData()` - Carrega dados da API
- `updateHoraPixUI()` - Atualiza interface com dados
- `renderDraws()` - Renderiza lista de sorteios
- `createDrawCard()` - Cria card individual de sorteio
- `collectHoraPixNow()` - Trigger para coleta manual
- `showHoraPixView()` - Exibe a view Hora do Pix

### 6. Sistema de Captura Automática

**Arquivo:** `core/services/capture_service_fast.py` (linha 30)

A aba Hora do Pix foi adicionada às páginas capturadas:
```python
self.pages = {
    "geral": "http://localhost:8002/imperio#geral",
    "perfil": "http://localhost:8002/imperio#perfil",
    "grupos": "http://localhost:8002/imperio#grupos",
    "horapix": "http://localhost:8002/imperio#horapix"  # NOVO
}
```

O sistema de captura automática (executado a cada 30 minutos) já inclui:
1. Navegação para localhost:8002/imperio#horapix
2. Aguardar carregamento da página (8 segundos)
3. Captura de screenshot completo
4. Envio automático para WhatsApp

## Fluxo de Funcionamento

### Coleta Automática (Backend)
```
1. Scheduler executa a cada 30 minutos
2. HoraPixCollectorSelenium inicia
3. Chrome headless faz login no painel
4. Navega para página de produtos
5. Extrai dados do HTML
6. Processa e calcula métricas
7. HoraPixService salva no banco de dados
8. Dados ficam disponíveis via API
```

### Captura de Tela (Sistema Principal)
```
1. Capture Monitor detecta horário (XX:01 e XX:31)
2. ImperioCaptureServiceFast inicia
3. Chrome headless navega para localhost:8002/imperio#horapix
4. Aguarda carregamento (JavaScript busca dados da API)
5. Captura screenshot da interface renderizada
6. Salva em screenshots/horapix_YYYYMMDD_HHMMSS.png
7. Envia para WhatsApp junto com outros screenshots
```

### Visualização (Frontend)
```
1. Usuário acessa localhost:8002/imperio
2. Clica no menu "Hora do Pix"
3. JavaScript executa loadHoraPixData()
4. Busca dados de /api/imperio/horapix/latest
5. Renderiza interface com KPIs e sorteios
6. Atualiza automaticamente a cada visualização
```

## Testes

### Teste do Coletor
```bash
./venv/Scripts/python.exe test_horapix_selenium.py
```

### Teste da Captura
```bash
./venv/Scripts/python.exe execute_capture.py
```

### Criação/Verificação das Tabelas
```bash
./venv/Scripts/python.exe scripts/maintenance/create_horapix_tables.py
```

### Migração para Adicionar Taxa de 3%
```bash
./venv/Scripts/python.exe scripts/maintenance/upgrade_horapix_add_fee.py
```
Este script:
- Adiciona coluna `platform_fee` nas tabelas
- Recalcula lucros e ROI considerando a taxa
- Atualiza dados existentes automaticamente

## Arquivos Criados/Modificados

### Novos Arquivos
- `core/services/horapix_collector_selenium.py` - Coletor Selenium com cálculo de taxa
- `core/models/horapix.py` - Modelos de dados incluindo `platform_fee`
- `clients/imperio/services/horapix_service.py` - Camada de serviço
- `test_horapix_selenium.py` - Script de teste
- `scripts/maintenance/create_horapix_tables.py` - Criação inicial das tabelas
- `scripts/maintenance/upgrade_horapix_add_fee.py` - **Migração para adicionar taxa de 3%**
- `docs/HORA_DO_PIX_SISTEMA.md` - Esta documentação

### Arquivos Modificados
- `clients/imperio/api/routes.py` - 5 novos endpoints (linhas 1460-1585)
- `clients/imperio/templates/imperio.html`:
  * Menu: linha 639-641
  * Interface HTML: linhas 904-1033
  * JavaScript: linhas 1948-2178
  * View switcher: linhas 1394-1397
- `core/services/capture_service_fast.py` - Adicionada URL #horapix (linha 30)

## Banco de Dados

**Localização:** `dashboard_roi.db`

**Tabelas criadas:**
- `horapix_collections` - Histórico de coletas (11 colunas)
  * Inclui `total_platform_fee` para taxa de 3%
  * Lucro e ROI calculados considerando a taxa
- `horapix_draws` - Detalhes dos sorteios (20 colunas)
  * Inclui `platform_fee` para taxa individual
  * Lucro e ROI calculados considerando a taxa

**Verificar estrutura das tabelas:**
```bash
sqlite3 dashboard_roi.db ".schema horapix_collections"
sqlite3 dashboard_roi.db ".schema horapix_draws"
```

**Ver dados:**
```bash
# Ver últimas coletas com taxa
sqlite3 dashboard_roi.db "SELECT collection_time, total_revenue, total_platform_fee, total_profit, total_roi FROM horapix_collections ORDER BY collection_time DESC LIMIT 5;"

# Ver sorteios com taxa
sqlite3 dashboard_roi.db "SELECT title, revenue, platform_fee, profit, roi FROM horapix_draws ORDER BY collection_time DESC LIMIT 5;"
```

## Próximos Passos

1. ✅ Sistema de coleta Selenium implementado
2. ✅ Modelos de banco de dados criados (incluindo `platform_fee`)
3. ✅ API REST implementada
4. ✅ Interface frontend completa (5 KPIs com taxa destacada)
5. ✅ Integrado ao sistema de captura
6. ✅ **Taxa de 3% implementada em todo o sistema**
7. ⏳ Aguardando teste real de coleta
8. ⏳ Aguardando primeiro screenshot automático

## Notas Importantes

- **Taxa de 3% da plataforma** - Calculada automaticamente e exibida em vermelho
- **Lucro Líquido** - Sempre considera: Receita - Prêmio - Taxa (3%)
- **ROI Real** - Calculado sobre o investimento total: (Prêmio + Taxa)
- **Não precisa de token JWT** - Sistema usa Selenium com login normal
- **Coleta automática** - Mesma frequência do sistema principal (30 min)
- **Screenshots automáticos** - Incluídos nas capturas XX:01 e XX:31
- **WhatsApp automático** - Enviado junto com outros dashboards
- **Zero configuração adicional** - Tudo já integrado ao fluxo existente

## Troubleshooting

### Se a coleta não funcionar:
1. Verificar credenciais no `.env`
2. Testar login manual no painel
3. Executar teste com `headless=False` para ver o navegador
4. Verificar logs do sistema

### Se a interface não carregar:
1. Verificar se tabelas foram criadas
2. Verificar se API está respondendo: `GET /api/imperio/horapix/latest`
3. Abrir console do navegador (F12) para ver erros JavaScript

### Se o screenshot estiver vazio:
1. Aguardar 30 minutos para primeira coleta automática
2. Ou executar coleta manual via botão "Atualizar Agora"
3. Verificar se dados existem no banco de dados

## Contato e Suporte

Para questões sobre este sistema, consultar:
- Documentação do sistema principal
- Arquivo `.env` para configurações
- Logs em `data/logs/`
