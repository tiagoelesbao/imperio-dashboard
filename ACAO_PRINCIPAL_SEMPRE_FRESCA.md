# Ação Principal: Sempre Fresca (Sem Histórico)

## 📋 Conceito

A aba **Ação Principal** não armazena histórico de coletas anteriores. É sempre **FRESCA** e mostra **APENAS dados do momento atual da coleta**.

```
┌─────────────────────────────────────────┐
│      COLETA (00:00 ou 00:30)            │
├─────────────────────────────────────────┤
│ 1. Limpar dados antigos                 │
│ 2. Coletar dados da API                 │
│ 3. Armazenar dados NOVOS                │
│ 4. Exibir no frontend (FRESCO)          │
└─────────────────────────────────────────┘
         ↓
    24 HORAS DEPOIS
         ↓
┌─────────────────────────────────────────┐
│      PRÓXIMA COLETA (00:00 ou 00:30)    │
├─────────────────────────────────────────┤
│ 1. Limpar dados ANTIGOS (delete)        │
│ 2. Coletar dados NOVOS da API           │
│ 3. Armazenar dados NOVOS                │
│ 4. Exibir no frontend (ATUALIZADO)      │
└─────────────────────────────────────────┘
```

---

## 🔄 Fluxo Automático

### 1. Daily Reset (Primeiro do dia - Ex: 00:00)

```bash
.\imperio_daily_reset.bat
```

**Fases:**
- **4.5B** - Limpar histórico
  ```bash
  python clean_main_action_history.py
  # DELETE FROM main_action_daily  (remove tudo)
  ```

- **4.6** - Coletar dados frescos
  ```bash
  python -c "main_action_service.collect_and_save()"
  # Coleta dados da API
  # Insere novos registros LIMPOS (sem histórico)
  ```

**Resultado:** Dados de 00:00 aparecem no dashboard

---

### 2. Scheduler (A cada meia hora - Ex: 00:30, 01:00, 01:30...)

**O scheduler integrado no core.app:**

```python
# Coleta automática a cada 30 minutos
@scheduler.scheduled_job('cron', minute='*/30')
def collect_main_action():
    db = SessionLocal()
    # IMPORTANTE: collect_and_save() agora deleta dados antigos!
    main_action_service.collect_and_save(db, current_product_id)
    db.close()
```

**Resultado:**
- 00:30 → Dados atualizados
- 01:00 → Dados atualizados
- 01:30 → Dados atualizados
- etc...

---

## 🗂️ Estrutura do Banco de Dados

### Antes (Histórico Acumulado)
```
main_action_daily
├── 01/11 - R$ 578,76 (ANTIGO)
├── 02/11 - R$ 4.930,76 (ANTIGO)
├── 03/11 - R$ 13.976,52 (ANTIGO)
├── ... (mais 13 dias antigos)
└── 16/11 - R$ 8.767,97 (ATUAL)
```

### Depois (Sempre Fresco)
```
main_action_daily
├── 14/11 - R$ 718,84 (COLETA ATUAL)
├── 15/11 - R$ 6.699,61 (COLETA ATUAL)
└── 16/11 - R$ 8.767,97 (COLETA ATUAL)
```

---

## 📊 Dados Exibidos

### O que você vê no frontend

| Momento | O que aparece | Número de Dias |
|---------|--------------|---|
| Logo após daily_reset | Dados do sorteio VIGENTE | Depende do período |
| 00:30 (primeiro scheduler) | Dados atualizados | Mesmo sorteio |
| 01:00 (próximo scheduler) | Dados mais frescos | Mesmo sorteio |
| Próximo dia (novo daily_reset) | Novos dados do sorteio | Recomeça do zero |

---

## 🔧 Como Funciona a Limpeza

### Script: clean_main_action_history.py

```python
# 1. Conecta ao banco
# 2. DELETE FROM main_action_daily  (remove tudo)
# 3. VACUUM (otimiza espaço)
```

**Executado em:**
- ✅ Daily Reset (antes de coletar)
- ✅ update_raffle_id.py (antes de coletar dados novos)
- ✅ Scheduler (implícito no collect_and_save)

---

## 📝 Modificações no Código

### 1. main_action_service.py

```python
def collect_and_save(self, db: Session, product_id: str) -> Dict:
    """Coleta e salva dados de uma ação (sempre fresco, sem histórico)"""
    # ...

    # NOVO: Limpar dados históricos antigos
    if action:
        db.query(MainActionDaily).filter(
            MainActionDaily.action_id == action.id
        ).delete()  # ← DELETA TUDO ANTES DE INSERIR NOVO

    # Depois coleta e insere novos dados
```

### 2. imperio_daily_reset.bat

**Nova Fase 4.5B:**
```batch
echo [FASE 4.5B] LIMPANDO HISTORICO DA ACAO PRINCIPAL
.\venv\Scripts\python.exe clean_main_action_history.py
```

### 3. update_raffle_id.py

**Método collect_fresh_data() agora:**
1. Limpa histórico
2. Coleta dados novos
3. Migra banco de dados

---

## 🎯 Garantias do Sistema

| Situação | O que acontece |
|----------|---|
| **Daily Reset** | Dados limpos + novos coletados |
| **Scheduler a cada 30min** | Dados limpos + novos coletados |
| **Trocar sorteio** | Dados limpos + novos do sorteio novo |
| **Reiniciar servidor** | Dados não são perdidos, continuam frescos |

---

## 📋 Timeline de Exemplo (24 horas)

```
00:00 - DAILY RESET
├─ Limpar histórico: main_action_daily vazia
├─ Coletar dados: 2025-11-14, 2025-11-15, 2025-11-16
└─ Frontend: Mostra 3 dias (período atual do sorteio)

00:30 - SCHEDULER
├─ Limpar histórico: main_action_daily vazia
├─ Coletar dados: dados MAIS FRESCOS
└─ Frontend: Atualizado (mesmo 3 dias, com valores atualizados)

01:00 - SCHEDULER
├─ Limpar: vazia
├─ Coletar: dados AINDA MAIS FRESCOS
└─ Frontend: Atualizado novamente

...

23:30 - SCHEDULER (última coleta do dia)
├─ Limpar: vazia
├─ Coletar: dados FINAIS do dia
└─ Frontend: Mostra estado final antes do daily reset

00:00 (PRÓXIMO DIA) - NOVO DAILY RESET
└─ Ciclo recomeça (possivelmente com novo sorteio)
```

---

## ✅ Verificação

### Como saber se está funcionando corretamente

**1. Imediatamente após daily_reset:**
```
Frontend: Ação Principal
├─ Produto ID: Correto
├─ Período: Período do sorteio atual
├─ Duração: 3-5 dias (período vigente)
├─ Tabela: Dados correspondem ao período
└─ Totais: Receita, ROI, etc. são corretos
```

**2. Após 30 minutos (primeiro scheduler):**
```
Frontend: Mesmo, mas com valores possivelmente atualizados
```

**3. Banco de dados:**
```bash
SELECT COUNT(*) FROM main_action_daily;
# Deve retornar: 3-5 (apenas dados atuais)
# NÃO deve retornar: 16+ (histórico antigo)
```

---

## 🚀 Comportamento em Produção

### Seu PC amanhã cedo (Task Scheduler)

```
05:00 AM - Task Scheduler executa imperio_daily_reset.bat
├─ Servidor inicia
├─ Banco de dados conecta
├─ FASE 4.5B: Limpa histórico
├─ FASE 4.6: Coleta dados do sorteio vigente
└─ Dashboard mostra dados FRESCOS

05:30 AM - Scheduler automático coleta
├─ Limpa dados antigos
├─ Coleta dados mais recentes
└─ Dashboard atualizado

06:00 AM - Scheduler automático coleta
└─ ... (repetição a cada 30 min)

... (durante todo o dia)

23:30 PM - Último scheduler do dia
├─ Coleta dados finais
└─ Dashboard mostra estado final

00:00 (PRÓXIMO DIA) - Novo daily_reset
└─ Ciclo recomeça
```

---

## 💡 Por que assim?

**Vantagens:**

✅ **Sempre fresco** - Dados nunca ficam obsoletos
✅ **Sem clutter** - Sem histórico desnecessário
✅ **Perfomático** - Banco não cresce indefinidamente
✅ **Rastreável** - Cada coleta é claramente separada
✅ **Automático** - Não precisa de intervenção manual
✅ **Preciso** - Mostra exatamente o momento da coleta

---

**Última atualização:** 16/11/2025
**Versão:** 3.0 (Ação Principal sempre fresca)
