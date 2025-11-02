#!/usr/bin/env python
"""Script para debugar problema de exibição de dados no dashboard."""

import sys
sys.path.append('.')

from datetime import datetime, timedelta
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from core.models.base import DailySnapshot, ChannelData
from core.database.base import get_db
import pytz

# Conectar ao banco
db = next(get_db())

# Timezone Brasil
tz_brasilia = pytz.timezone('America/Sao_Paulo')
today_brazil = datetime.now(tz_brasilia).date()
yesterday = today_brazil - timedelta(days=1)

print("="*60)
print("DIAGNOSTICO DO PROBLEMA DE DADOS NO DASHBOARD")
print("="*60)
print(f"\nData atual (Brasil): {today_brazil.strftime('%d/%m/%Y')}")
print(f"Ontem: {yesterday.strftime('%d/%m/%Y')}")

# 1. Verificar DailySnapshot
print("\n" + "="*60)
print("1. TABELA: DailySnapshot")
print("="*60)

# Contar total de registros
total_snapshots = db.query(DailySnapshot).count()
print(f"Total de registros: {total_snapshots}")

# Verificar registros de hoje
today_snapshots = db.query(DailySnapshot).filter(
    DailySnapshot.date >= today_brazil
).all()
print(f"Registros de hoje: {len(today_snapshots)}")

# Listar product_ids únicos
unique_products = db.query(DailySnapshot.product_id).distinct().all()
print(f"\nProduct_ids únicos encontrados:")
for product in unique_products:
    count = db.query(DailySnapshot).filter(
        DailySnapshot.product_id == product[0]
    ).count()
    print(f"  - {product[0]}: {count} registros")

# Verificar últimos 5 registros
print("\nUltimos 5 registros em DailySnapshot:")
last_snapshots = db.query(DailySnapshot).order_by(
    DailySnapshot.collected_at.desc()
).limit(5).all()

for snapshot in last_snapshots:
    print(f"\n  ID: {snapshot.id}")
    print(f"  Data: {snapshot.date}")
    print(f"  Hora coleta: {snapshot.collected_at}")
    print(f"  Product ID: {snapshot.product_id}")
    print(f"  Vendas: R$ {snapshot.total_sales:.2f}")
    print(f"  Gastos: R$ {snapshot.total_spend:.2f}")
    print(f"  ROI: {snapshot.general_roi:.2f}")

# 2. Verificar ChannelData
print("\n" + "="*60)
print("2. TABELA: ChannelData")
print("="*60)

# Contar total de registros
total_channels = db.query(ChannelData).count()
print(f"Total de registros: {total_channels}")

# Verificar registros de hoje
today_channels = db.query(ChannelData).filter(
    ChannelData.date >= today_brazil
).all()
print(f"Registros de hoje: {len(today_channels)}")

# Listar product_ids únicos em ChannelData
unique_channel_products = db.query(ChannelData.product_id).distinct().all()
print(f"\nProduct_ids únicos encontrados em ChannelData:")
for product in unique_channel_products:
    count = db.query(ChannelData).filter(
        ChannelData.product_id == product[0]
    ).count()
    print(f"  - {product[0]}: {count} registros")

# Verificar últimos registros por canal
print("\nUltimos registros por canal:")
for channel in ['geral', 'instagram', 'grupos']:
    last_channel = db.query(ChannelData).filter(
        ChannelData.channel_name == channel
    ).order_by(ChannelData.collected_at.desc()).first()

    if last_channel:
        print(f"\n  Canal: {channel}")
        print(f"  Data: {last_channel.date}")
        print(f"  Hora coleta: {last_channel.collected_at}")
        print(f"  Product ID: {last_channel.product_id}")
        print(f"  Vendas: R$ {last_channel.sales:.2f}")
        print(f"  Gastos: R$ {last_channel.spend:.2f}")
        print(f"  ROI: {last_channel.roi:.2f}")
    else:
        print(f"\n  Canal: {channel} - SEM DADOS")

# 3. Testar query específica do problema
print("\n" + "="*60)
print("3. TESTE DA QUERY DO PROBLEMA")
print("="*60)

# Query exata usada no imperio_db_service.get_looker_geral_data()
print("\nTestando query para 'geral' com product_id='6904ea540d0e097d618827fc':")
snapshots_test = db.query(DailySnapshot).filter(
    DailySnapshot.date >= today_brazil,
    DailySnapshot.product_id == "6904ea540d0e097d618827fc"
).order_by(DailySnapshot.collected_at.asc()).all()

print(f"Registros encontrados: {len(snapshots_test)}")

if len(snapshots_test) == 0:
    print("\n[!] PROBLEMA IDENTIFICADO!")
    print("Nao ha registros com product_id='6904ea540d0e097d618827fc' para hoje.")

    # Verificar se há registros com outro product_id
    print("\nVerificando registros de hoje com QUALQUER product_id:")
    any_snapshots = db.query(DailySnapshot).filter(
        DailySnapshot.date >= today_brazil
    ).all()

    if any_snapshots:
        print(f"[OK] Existem {len(any_snapshots)} registros de hoje, mas com product_ids diferentes:")
        for snap in any_snapshots[:3]:  # Mostrar primeiros 3
            print(f"   - Product ID: {snap.product_id}")
            print(f"     Vendas: R$ {snap.total_sales:.2f}, ROI: {snap.general_roi:.2f}")
    else:
        print("[X] Nao ha registros de hoje em DailySnapshot")

# 4. Verificar configuração atual
print("\n" + "="*60)
print("4. CONFIGURAÇÃO ATUAL DO SISTEMA")
print("="*60)

# Verificar qual product_id está sendo usado pelo coletor
try:
    from core.services.data_manager import imperio_data_manager
    print(f"Product ID no data_manager: {imperio_data_manager.product_id}")
except Exception as e:
    print(f"Erro ao verificar data_manager: {e}")

# Verificar config.py
try:
    from config import IMPERIO_CONFIG
    print(f"Product ID no config.py: {IMPERIO_CONFIG.get('product_id', 'NÃO DEFINIDO')}")
except Exception as e:
    print(f"Erro ao verificar config.py: {e}")

print("\n" + "="*60)
print("5. DIAGNÓSTICO FINAL")
print("="*60)

if len(snapshots_test) == 0:
    print("[X] PROBLEMA CONFIRMADO:")
    print("   O servico esta buscando product_id='6904ea540d0e097d618827fc'")
    print("   mas os dados estao sendo salvos com outro product_id.")
    print("\n[SOLUCAO NECESSARIA]:")
    print("   1. Atualizar o product_id no imperio_database_service.py")
    print("   2. OU atualizar o product_id usado na coleta de dados")
    print("   3. Garantir que ambos usem o mesmo product_id")
else:
    print("[OK] Dados encontrados com o product_id esperado")

db.close()
print("\n" + "="*60)
print("FIM DO DIAGNÓSTICO")
print("="*60)