# Dashboard ROI - Sistema de Monitoramento de Performance

Um sistema web moderno para monitoramento em tempo real do ROI (Return on Investment) de campanhas de marketing, substituindo o Looker Studio com uma interface personalizada e otimizada.

## 🚀 Características

- **Dashboard em Tempo Real**: Atualização automática a cada 30 minutos
- **ROI por Canal**: Análise separada para Geral, Instagram e Grupos WhatsApp
- **Otimização de APIs**: Rate limiting inteligente para Facebook Ads API
- **Interface Responsiva**: Design moderno com Bootstrap 5
- **Banco de Dados**: Armazenamento histórico de dados para análises
- **APIs RESTful**: Endpoints para integração com outros sistemas

## 📊 Funcionalidades

### Dashboard Principal
- Métricas em tempo real (ROI atual, vendas do dia, gastos)
- Gráficos interativos com Chart.js
- Alertas de performance
- Comparativo entre canais

### Análise de ROI
- ROI detalhado por canal de marketing
- Gráficos de tendência e comparativos
- Filtros por período (6h, 12h, 24h, 48h)
- Tabela detalhada com status de performance

### Monitoramento de Vendas
- Dados de vendas por dia
- Análise de números vendidos e valores
- Histórico de performance

### Gestão de Afiliados
- Performance dos afiliados (Instagram, Grupos)
- Ticket médio e quantidade de pedidos
- Análise de conversão

## 🛠 Tecnologias

- **Backend**: FastAPI (Python)
- **Frontend**: HTML5, CSS3, JavaScript, Bootstrap 5
- **Banco de Dados**: SQLite (configurável para PostgreSQL)
- **Gráficos**: Chart.js
- **APIs**: Facebook Graph API, APIs internas de vendas
- **Agendamento**: Schedule + AsyncIO

## 📋 Pré-requisitos

- Python 3.8+
- pip (gerenciador de pacotes Python)
- Conta do Facebook Ads (para obter access token)
- Credenciais das APIs de vendas

## 🚀 Instalação

1. **Clone o repositório**
```bash
git clone https://github.com/seu-usuario/dashboard-roi.git
cd dashboard-roi
```

2. **Instale as dependências**
```bash
pip install -r requirements.txt
```

3. **Configure as variáveis de ambiente**
```bash
cp .env.example .env
# Edite o arquivo .env com suas credenciais
```

4. **Execute o sistema**
```bash
python run.py
```

O dashboard estará disponível em `http://localhost:8000`

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```bash
# APIs de Vendas
API_USERNAME=seu_usuario_api
API_PASSWORD=sua_senha_api

# Facebook Ads
FACEBOOK_ACCESS_TOKEN=seu_token_facebook

# Códigos dos Afiliados
AFFILIADO_CODE_INSTAGRAM=codigo_instagram
AFFILIADO_CODE_GRUPO_1=codigo_grupo_1
AFFILIADO_CODE_GRUPO_2=codigo_grupo_2

# Contas Facebook por Canal
FACEBOOK_ACCOUNT_IDS_GERAL=act_123,act_456,act_789
FACEBOOK_ACCOUNT_IDS_INSTAGRAM=act_123,act_456
FACEBOOK_ACCOUNT_IDS_GRUPO=act_789

# Configurações do Sistema
COLLECTION_INTERVAL_MINUTES=30
HOST=0.0.0.0
PORT=8000
```

### Configuração para Produção

Para ambiente de produção (Ubuntu Server), recomenda-se:

1. **Use PostgreSQL**
```bash
# Instalar PostgreSQL
sudo apt update
sudo apt install postgresql postgresql-contrib

# Configurar DATABASE_URL no .env
DATABASE_URL=postgresql://user:password@localhost/dashboard_roi
```

2. **Configure um servidor web (Nginx)**
```bash
sudo apt install nginx
# Configure proxy reverso para a aplicação
```

3. **Use um process manager (systemd)**
```bash
# Criar service file para inicialização automática
sudo nano /etc/systemd/system/dashboard-roi.service
```

## 📖 API Endpoints

### Dashboard
- `GET /api/dashboard/summary` - Resumo geral do dashboard
- `GET /api/roi/{canal}?hours=24` - Dados de ROI por canal
- `GET /api/sales/latest?limit=50` - Últimas vendas
- `GET /api/affiliates/performance?days=7` - Performance dos afiliados
- `GET /api/facebook/spend?hours=24` - Gastos do Facebook Ads

### Interface Web
- `/` - Página inicial
- `/dashboard/` - Visão geral
- `/dashboard/roi` - ROI detalhado
- `/dashboard/sales` - Vendas
- `/dashboard/affiliates` - Afiliados
- `/dashboard/facebook` - Facebook Ads

## 🔄 Agendamento Automático

O sistema inclui um agendador que:
- Coleta dados a cada 30 minutos (00:00 e 00:30 de cada hora)
- Implementa retry automático em caso de falhas
- Otimiza requisições para APIs com rate limiting
- Mantém logs detalhados de execução

## 📊 Monitoramento

### Logs
- `dashboard_roi.log` - Log principal da aplicação
- `erro_log.txt` - Log de erros específicos (compatibilidade)

### Métricas
- Status do agendador via API
- Histórico de coletas bem-sucedidas
- Monitoramento de falhas consecutivas

## 🛡️ Segurança

- Variáveis de ambiente para credenciais sensíveis
- Rate limiting para APIs externas
- Logs de segurança e auditoria
- Validação de entrada de dados

## 🚀 Deploy no Ubuntu Server

1. **Preparar servidor**
```bash
sudo apt update && sudo apt upgrade -y
sudo apt install python3 python3-pip git nginx -y
```

2. **Clonar e configurar**
```bash
git clone https://github.com/seu-usuario/dashboard-roi.git
cd dashboard-roi
pip3 install -r requirements.txt
cp .env.example .env
# Configurar .env
```

3. **Configurar serviço systemd**
```bash
sudo nano /etc/systemd/system/dashboard-roi.service
sudo systemctl enable dashboard-roi
sudo systemctl start dashboard-roi
```

4. **Configurar Nginx**
```bash
sudo nano /etc/nginx/sites-available/dashboard-roi
sudo ln -s /etc/nginx/sites-available/dashboard-roi /etc/nginx/sites-enabled/
sudo systemctl restart nginx
```

## 🤝 Contribuição

1. Fork o projeto
2. Crie uma branch para sua feature (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📝 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

## 🆘 Suporte

Para suporte, abra uma issue no GitHub ou entre em contato:
- Email: seu-email@dominio.com
- Issues: https://github.com/seu-usuario/dashboard-roi/issues

## 📈 Roadmap

- [ ] Integração com mais plataformas de ads (Google Ads, TikTok)
- [ ] Dashboard mobile responsivo
- [ ] Alertas via email/WhatsApp
- [ ] Exportação de relatórios em PDF
- [ ] Análise preditiva com Machine Learning
- [ ] API para integração com CRM
- [ ] Multi-tenancy para múltiplas empresas