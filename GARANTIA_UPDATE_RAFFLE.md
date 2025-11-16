# Garantia de Funcionamento - Troca de ID de Sorteio

## Visão Geral

Este documento explica como o sistema **garante que a troca de ID de sorteio funcione corretamente** sem deixar dados antigos no banco de dados.

---

## Problema que Foi Resolvido

### Situação Anterior (16/11/2025)

Quando você atualizou o ID de sorteio para `6916292bf6051e4133d86ef9`:
- ❌ O banco de dados ainda tinha **16 dias de dados antigos** (01/11 a 16/11)
- ❌ O frontend exibia período completamente errado
- ❌ O servidor em memória usava o **ID antigo** mesmo após atualizar o arquivo

### Causa Raiz

```
1. Update raffle ID script atualizou files ✓
2. config.py foi atualizado com novo ID ✓
3. PORÉM: Servidor já estava em memória com ID antigo
4. MAIS: Dados históricos não foram limpos antes da coleta
   → Resultado: 16 dias antigos + novos ID = dados confusos
```

---

## Solução Implementada

### Três Componentes Principais

#### 1. **clean_main_action_history.py**
**Função:** Limpar dados antigos do banco

```python
# Deleta TODOS os registros de main_action_daily
cursor.execute("DELETE FROM main_action_daily")
# Otimiza espaço do banco
cursor.execute("VACUUM")
```

**Quando é executado:**
- ✓ No daily_reset.bat (Fase 4.5B)
- ✓ Ao executar update_raffle_id.py (antes de coletar)
- ✓ Manualmente quando necessário

#### 2. **main_action_service.py - Coleta Automática**
**Função:** Ao coletar dados, garantir que sejam frescos

```python
def collect_and_save(self, db, product_id):
    # ... obtém dados ...

    # ANTES de inserir novos dados, DELETA os antigos
    if action:
        db.query(MainActionDaily).filter(
            MainActionDaily.action_id == action.id
        ).delete()  # ← Garante dados frescos

    # Depois insere os novos
    # ... salva dados ...
```

**Resultado:** A cada coleta, só tem dados do momento da coleta

#### 3. **update_raffle_id.py - Orquestração Robusta**
**Função:** Executar troca de ID com garantias

```
FLUXO QUANDO VOCÊ EXECUTA update_raffle_id.py:

1. Pede novo ID e valida formato
2. Atualiza todos os arquivos Python (.py e .bat)
3. PASSO 1 - LIMPEZA:
   └─ Executa clean_main_action_history.py
   └─ Deleta registros históricos
4. PASSO 2 - COLETA FRESCA:
   └─ Coleta dados do novo ID
   └─ Salva no banco (vazio, portanto sem histórico)
5. Migra banco de dados se necessário
6. Mostra relatório completo
```

---

## Garantias do Sistema - Próxima Troca de ID

### Quando Você Trocar de ID Novamente

**Exemplo:** Trocar de `6916292bf6051e4133d86ef9` → `NOVO_ID_AQUI`

**Execução:**
```bash
python update_raffle_id.py
```

**O que acontece automaticamente:**

```
[PROCESSAMENTO] Iniciando atualização...
   De: 6916292bf6051e4133d86ef9
   Para: NOVO_ID_AQUI

[PASSO 1] LIMPANDO HISTORICO DA ACAO PRINCIPAL
  [LIMPEZA] Removendo dados antigos para preparar coleta fresca...
  [OK] Historico limpo com sucesso!

[PASSO 2] COLETANDO DADOS FRESCOS COM NOVO ID
  [COLETA] ID de sorteio: NOVO_ID_AQUI
  [COLETA] Aguardando coleta de dados frescos...
  [COLETA] Produto: NOVO_ID_AQUI
  [COLETA] Nome: [Nome do novo sorteio]
  [OK] Coleta concluida!
  [OK] X registros diarios salvos
  [PERIODO] De XXXX-XX-XX ate XXXX-XX-XX

[SUCESSO] Dados frescos coletados e salvos!
```

**Resultado no banco:**
```
ANTES:
main_action_daily → 16 registros (dados do sorteio anterior)

DEPOIS:
main_action_daily → X registros (apenas do novo sorteio, FRESCO)
```

---

## Verificação Após Atualização

### No seu PC - Imediatamente Após Trocar ID

**1. Banco de Dados:**
```bash
# Abrir SQL e executar:
SELECT COUNT(*) FROM main_action_daily;
# Resultado esperado: 3-5 registros (período do novo sorteio)
# Resultado errado: 16+ registros (histórico antigo)

SELECT DATE(date) FROM main_action_daily;
# Resultado esperado: Apenas datas do período vigente novo
```

**2. Frontend (http://localhost:8002/imperio#acaoprincipal):**
```
✓ Cabeçalho mostra novo ID
✓ Tabela tem apenas dias do novo período
✓ Totais correspondem ao novo período
✓ Nenhum dado do sorteio anterior
```

**3. Logs:**
```
data/logs/ensure_fresh.log (se usar ensure_fresh_collection.py)
ou
Ver output direto do update_raffle_id.py
```

---

## Arquivo por Arquivo - O que Mudou

### 1. core/services/main_action_service.py
```python
# NOVO: Limpar antes de inserir
if action:
    db.query(MainActionDaily).filter(
        MainActionDaily.action_id == action.id
    ).delete()  # ← GARANTIA 1: Sem histórico
    logger.info(f"Dados históricos deletados")
```

**Garantia:** A cada `collect_and_save()`, começa do zero

---

### 2. imperio_daily_reset.bat
```batch
REM NOVA FASE 4.5B
echo [FASE 4.5B] LIMPANDO HISTORICO DA ACAO PRINCIPAL
.\venv\Scripts\python.exe clean_main_action_history.py

REM DEPOIS coleta
echo [FASE 4.6] EXECUTANDO COLETA ACAO PRINCIPAL
```

**Garantia:** Cada daily reset limpa antes de coletar

---

### 3. update_raffle_id.py - Método collect_fresh_data()
```python
def collect_fresh_data(self) -> bool:
    # PASSO 1: Limpar dados antigos
    result = subprocess.run(
        [sys.executable, 'clean_main_action_history.py'],
        ...
    )

    # PASSO 2: Coletar dados frescos
    result = subprocess.run(
        [sys.executable, '-c', collect_script],
        ...
    )
```

**Garantia:** Automaticamente garante processo correto na próxima troca

---

### 4. clean_main_action_history.py (NOVO)
```python
class MainActionHistoryCleaner:
    def clean_all(self) -> bool:
        # DELETE FROM main_action_daily
        # VACUUM
```

**Garantia:** Script dedicado para limpeza robusta

---

### 5. ensure_fresh_collection.py (NOVO)
```python
class FreshCollectionEnsurer:
    def step1_clean_history()  # Limpa
    def step2_kill_server()    # Mata servidor antigo
    def step3_wait_for_server() # Aguarda iniciar
    def step4_collect_fresh_data() # Coleta nova
    def verify_fresh_data()    # Valida resultado
```

**Garantia:** Processo completo e verificado

---

## O Que Garante Funcionamento Correto?

### Triplo Sistema de Segurança

| Nível | O que faz | Quando | Garantia |
|-------|-----------|--------|----------|
| **1. Código da Coleta** | `collect_and_save()` deleta antes de inserir | A cada coleta (scheduler) | Sem histórico durante o dia |
| **2. Daily Reset** | Fase 4.5B limpa explicitamente | 05:00 AM (startup) | Reset diário garantido |
| **3. Update Script** | Limpa antes de coletar com novo ID | Ao trocar ID | Troca sem confusão de dados |

### Cenários Cobertos

#### Cenário 1: Daily Reset Amanhã
```
05:00 AM - daily_reset.bat executa
  ├─ Fase 2: Reset banco de dados
  ├─ Fase 4.5B: LIMPA main_action_daily
  ├─ Fase 4.6: Coleta dados frescos
  └─ Resultado: Dados frescos do dia
```

#### Cenário 2: Scheduler a Cada 30 Minutos
```
00:30, 01:00, 01:30... - Scheduler dispara
  ├─ collect_and_save() deleta dados antigos
  ├─ Coleta dados atualizados
  └─ Resultado: Métricas sempre frescas
```

#### Cenário 3: Trocar ID de Sorteio
```
Você executa: python update_raffle_id.py
  ├─ PASSO 1: Limpa histórico
  ├─ PASSO 2: Coleta dados do novo ID
  ├─ Migração do banco
  └─ Resultado: Novo sorteio com dados frescos
```

---

## Checklist de Validação

### Após atualizar o ID, verificar:

- [ ] **Banco de Dados:**
  ```bash
  SELECT COUNT(*) FROM main_action_daily;
  # Deve ser: 3-5 (período do sorteio)
  # Não deve ser: 16+ (histórico antigo)
  ```

- [ ] **Frontend:**
  - [ ] Product ID correto
  - [ ] Período correto
  - [ ] Tabela expansível mostra apenas dias atuais
  - [ ] Nenhum dado do sorteio anterior visível

- [ ] **Logs:**
  - [ ] data/logs/ensure_fresh.log (se foi executado)
  - [ ] Output do update_raffle_id.py mostra sucesso

- [ ] **Próximas 24h:**
  - [ ] Daily reset amanhã executa sem erros
  - [ ] Dados continuam frescos (3-5 dias)
  - [ ] Scheduler atualiza a cada 30min

---

## Troubleshooting

### Problema: Ainda tem dados antigos após atualizar

**Solução:**
```bash
# 1. Limpar manualmente
python clean_main_action_history.py

# 2. Reiniciar servidor
# Feche imperio_start.bat e abra novamente

# 3. Forçar coleta fresca
python ensure_fresh_collection.py
```

### Problema: Servidor não pega novo ID

**Causa:** Módulo em memória com ID antigo

**Solução:**
```bash
# 1. Matar todos os processos Python
taskkill /IM python.exe /F

# 2. Reiniciar servidor
imperio_start.bat
```

### Problema: Coleta falha com erro de conexão

**Solução:**
```bash
# Garantir que servidor está rodando
imperio_start.bat

# Depois executar coleta
python ensure_fresh_collection.py
```

---

## Resumo de Garantias

```
✅ Dados históricos são SEMPRE deletados antes de coletar
✅ Daily reset garante limpeza no startup
✅ Scheduler mantém dados frescos (DELETE + INSERT)
✅ Update raffle ID script automatiza processo
✅ Próxima troca de ID funcionará corretamente
✅ Sistema é robusto a restarts de servidor
✅ Documentado em ACAO_PRINCIPAL_SEMPRE_FRESCA.md
```

---

## Próximas Trocas de ID

Quando você precisar trocar o ID novamente:

```bash
# Simples assim:
python update_raffle_id.py

# O script garante que TUDO seja feito corretamente:
# ✓ Arquivos atualizados
# ✓ Histórico limpo
# ✓ Dados coletados frescos
# ✓ Banco migrado
# ✓ Tudo pronto para uso
```

---

**Última atualização:** 16/11/2025
**Versão:** 2.0 (Garantia com 3 camadas de segurança)
