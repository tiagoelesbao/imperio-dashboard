# Guia Completo: Atualizar ID de Sorteio

## 📋 Visão Geral

O sistema **Império** rastreia múltiplos sorteios. Quando você precisa trocar o sorteio monitorado, é necessário atualizar o ID em diversos lugares:

1. **Arquivos de código** (10 arquivos)
2. **Banco de dados** (tabelas de ações)
3. **Dados históricos** (coleta fresca dos dados)

Este guia explica como cada componente funciona e como garantir que tudo seja atualizado corretamente.

---

## 🔄 Fluxo Completo de Atualização

### Opção 1: Atualização Automática Completa (Recomendado)

```bash
python update_raffle_id.py
```

**O que acontece:**

1. ✅ **Detecção Automática**
   - Identifica o ID atual no arquivo `clients/imperio/config.py`
   - Pede o novo ID como input

2. ✅ **Atualização de Arquivos** (16 substituições em 10 arquivos)
   - `clients/imperio/config.py`
   - `core/services/data_collector.py`
   - `collect_main_action.py`
   - `force_reload_main_action.py`
   - `update_action_with_fb_costs.py`
   - `debug_database_issue.py`
   - `tests/test_fb_today.py`
   - `tests/test_complete_collection.py`
   - `docs/ESTRUTURA_PROJETO.md`
   - `imperio_daily_reset.bat`

3. ✅ **Coleta de Dados Frescos**
   - Executa `collect_main_action.py`
   - Coleta informações atualizadas da API do novo sorteio
   - Armazena dados reais (receita, custos FB, ROI, etc)

4. ✅ **Migração do Banco de Dados**
   - Atualiza tabela `main_actions` com o novo product_id
   - Marca a ação como `is_current=True`
   - Mantém histórico da ação antiga

---

## 🗂️ Estrutura de Dados: Qual ID Vai Para Onde

### 1️⃣ Ação Principal (Main Action)
- **Arquivos afetados:** Todos os 10 listados acima
- **Tabela BD:** `main_actions` e `main_action_daily`
- **Endpoint:** `GET /api/main-action/all` ou `#acaoprincipal`
- **Dados:** Histórico completo de vendas diárias, custos FB, ROI
- **Fluxo:**
  ```
  script (collect_main_action.py)
    → API do sorteio
    → MainActionCollector
    → Banco de dados
    → Frontend
  ```

---

## 📊 Dados Coletados e Armazenados

Quando você atualiza o ID, o script coleta:

### Informações da Ação
- Nome do sorteio
- Valor do prêmio
- Data de início/fim
- Status (ativo/finalizado)

### Dados Financeiros por Dia
- Receita por dia
- Número de pedidos por dia
- Custos do Facebook Ads
- Taxa de plataforma (3%)
- Lucro diário
- ROI diário

### Exemplo de Dados Coletados
```
Sorteio: RAPIDINHA VALENDO R$30.000,00 EM PREMIAÇÕES
Prêmio: R$ 30.000,00
Período: 14 a 16 de Novembro (3 dias)
Status: Ativo

Detalhamento Diário:
- 16/11: Receita R$ 8.767,97 | FB R$ 2.654,68 | ROI -30%
- 15/11: Receita R$ 6.699,61 | FB R$ 3.074,39 | ROI +50%
- 14/11: Receita R$ 718,84  | FB R$ 5.264,76 | ROI -640%

Totais:
- Receita: R$ 16.186,42
- Custos FB: R$ 10.993,83
- Lucro: -R$ 25.293,00
- ROI: -60,98%
```

---

## ⚙️ Fluxo de Reinicialização (Daily Reset)

Quando você reinicia o sistema com `imperio_daily_reset.bat`:

### Fase 4.6: Coleta Automática da Ação Principal

```batch
.\venv\Scripts\python.exe -c "
  from core.database.base import SessionLocal
  from core.services.main_action_service import main_action_service

  db = SessionLocal()
  current = main_action_service.get_current_action(db)  # Busca ação com is_current=True
  product_id = current['product_id'] if current else '6916292bf6051e4133d86ef9'
  result = main_action_service.collect_and_save(db, product_id)  # Coleta dados frescos
  db.close()
"
```

**O que acontece:**

1. Sistema procura por ação com `is_current=True` no banco
2. Usa o product_id dessa ação para coletar dados
3. Se não houver, usa o ID padrão como fallback
4. Coleta dados FRESCOS da API
5. Atualiza banco de dados com dados atualizados
6. Frontend exibe dados corretos ao reiniciar

---

## 🔀 Como os Dados São Rastreados

### Banco de Dados Estrutura

```sql
main_actions (uma ação = um sorteio)
├── id: 1
├── product_id: "6916292bf6051e4133d86ef9"  ← ID do sorteio
├── name: "RAPIDINHA VALENDO R$30.000,00..."
├── is_current: TRUE                        ← Marca como ação atual
├── total_revenue: 16186.42
├── total_fb_cost: 10993.83
└── ... (outros campos)

main_action_daily (dados dia a dia)
├── action_id: 1
├── date: "2025-11-16"
├── daily_revenue: 8767.97
├── daily_fb_cost: 2654.68
├── daily_roi: -30.5
└── ... (outros campos)
```

---

## 🔄 Ciclo Completo de Atualização

### Antes da Atualização
```
Banco de Dados:
├── main_actions[id=1]
│   └── product_id: "6904ea540d0e097d618827fc" (ANTIGO)
│   └── is_current: TRUE
├── main_action_daily (15 registros com dados antigos)

Arquivos:
├── config.py: product_id = "6904ea540d0e097d618827fc"
├── routes.py: multiple hardcoded IDs
└── ... (outros 8 arquivos)

Frontend:
└── Exibe dados da ação antiga
```

### Durante a Execução de `update_raffle_id.py`
```
[PASSO 1] Atualiza 10 arquivos
├── Substitui 16 ocorrências do ID antigo
└── Status: ✓ Completo

[PASSO 2] Coleta dados frescos
├── Conecta à API do novo sorteio
├── Baixa: vendas, pedidos, custos FB
└── Status: ✓ Completo

[PASSO 3] Migra banco de dados
├── Atualiza product_id na tabela main_actions
├── Marca como is_current=TRUE
└── Status: ✓ Completo
```

### Depois da Atualização
```
Banco de Dados:
├── main_actions[id=1]
│   └── product_id: "6916292bf6051e4133d86ef9" (NOVO)
│   └── is_current: TRUE
├── main_action_daily (3 registros com dados NOVOS)

Arquivos:
├── config.py: product_id = "6916292bf6051e4133d86ef9"
├── routes.py: multiple updated IDs
└── ... (todos 10 arquivos atualizados)

Frontend (após Ctrl+F5):
└── Exibe dados da ação nova (CORRETO!)
```

---

## 🚀 Uso Prático

### Cenário 1: Trocar o Sorteio Monitorado

```bash
# Executar o script
python update_raffle_id.py

# Entrada esperada:
# ID Atual: 6916292bf6051e4133d86ef9
# Novo ID: 6916292bf6051e4133d86ef9 (qual quer que seja o novo)
# Confirmar? (s/n): s

# O script vai:
# 1. Atualizar 10 arquivos
# 2. Coletar dados frescos da API
# 3. Migrar banco de dados
# 4. Exibir relatório

# Resultado esperado:
# [OK] Dados salvos com sucesso!
# [OK] Atualização concluída com sucesso!
```

### Cenário 2: Apenas Migrar Banco (se arquivos já foram atualizados)

```bash
python migrate_raffle_id.py 6904ea540d0e097d618827fc 6916292bf6051e4133d86ef9

# Resultado:
# [OK] 1 ação(ões) encontrada(s)
# [OK] MIGRAÇÃO CONCLUÍDA COM SUCESSO!
```

### Cenário 3: Sistema Reinicia (daily_reset.bat)

```bash
# Executar daily reset (manual ou Task Scheduler)
.\imperio_daily_reset.bat

# O sistema vai:
# FASE 4.6: Executar coleta da Ação Principal
#   ✓ Buscar ação com is_current=TRUE
#   ✓ Coletar dados frescos
#   ✓ Atualizar banco de dados
#   ✓ Exibir resumo

# Resultado no frontend:
# Dados atualizados com a coleta mais recente
```

---

## ✅ Verificação Pós-Atualização

Após atualizar, verifique:

### 1. Frontend
```
http://localhost:8002/imperio#acaoprincipal

✓ Product ID é o novo
✓ Nome do sorteio é correto
✓ Número de dias corresponde ao período atual
✓ Valores financeiros fazem sentido
```

### 2. Banco de Dados
```bash
# Verificar no SQLite
sqlite3 dashboard_roi.db

# Query:
SELECT id, product_id, name, is_current, total_revenue
FROM main_actions
WHERE is_current = 1;

# Esperado:
# 1 | 6916292bf6051e4133d86ef9 | RAPIDINHA... | 1 | 16186.42
```

### 3. Logs
```bash
# Verificar coleta
cat data/logs/daily_reset.log | grep "ACAO PRINCIPAL"

# Esperado:
# [ACAO PRINCIPAL] Nome: RAPIDINHA...
# [ACAO PRINCIPAL] Receita: R$ 16.186,42
# [ACAO PRINCIPAL] Coleta concluida com sucesso!
```

---

## 📝 Resumo Técnico

| Componente | O que muda | Quando muda | Impacto |
|------------|-----------|------------|--------|
| **Arquivos Code** | 10 arquivos | Quando roda `update_raffle_id.py` | Código usa novo ID |
| **Banco main_actions** | product_id e is_current | Na migração BD | Backend sabe qual ação é atual |
| **Banco main_action_daily** | Dados novos são inseridos | Na coleta (collect_main_action) | Frontend exibe dados corretos |
| **Frontend** | Exibe novo ID e dados | Após Ctrl+F5 | Usuário vê informações atualizadas |
| **APIs** | Usam novo product_id | Próxima coleta automática | Dados coletados do sorteio certo |

---

## 🔧 Troubleshooting

### Problema: Frontend ainda exibe dados antigos após atualizar
**Solução:**
```bash
# 1. Limpar cache do navegador
Ctrl+Shift+Del (Windows) ou Cmd+Shift+Del (Mac)

# 2. Recarregar com cache limpo
Ctrl+F5 (Windows) ou Cmd+Shift+R (Mac)

# 3. Verificar que coleta foi executada
cat data/logs/daily_reset.log | tail -20

# 4. Se necessário, executar coleta manualmente
python collect_main_action.py
```

### Problema: Banco de dados não foi migrado
**Solução:**
```bash
# Executar migração manualmente
python migrate_raffle_id.py <id_antigo> <id_novo>

# Verificar banco
sqlite3 dashboard_roi.db "SELECT product_id FROM main_actions WHERE is_current=1;"
```

### Problema: Dados não são coletados
**Solução:**
```bash
# Verificar credenciais de API
cat .env | grep API

# Testar coleta manualmente
python collect_main_action.py

# Verificar logs
cat data/logs/*.log | grep ERROR
```

---

## 📚 Referência de Arquivos

- **update_raffle_id.py** - Script principal para atualizar tudo
- **migrate_raffle_id.py** - Script para apenas migrar banco
- **collect_main_action.py** - Script para coletar dados frescos
- **imperio_daily_reset.bat** - Script que reinicia sistema e coleta dados
- **config.py** - Configuração com ID padrão

---

**Última atualização:** 16/11/2025
**Versão:** 2.0 (com coleta automática de dados)
