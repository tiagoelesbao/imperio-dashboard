#!/usr/bin/env python3
"""
Popula o banco de dados com dados realistas para substituir o Google Sheets
"""
import sys
import os
from datetime import datetime, date, timedelta
import random
from pathlib import Path

# Adicionar o diretório raiz ao path
current_dir = Path(__file__).parent.parent.parent
sys.path.insert(0, str(current_dir))

from sqlalchemy.orm import Session
from core.database.base import get_db, engine, Base
from core.models.base import (
    DailySnapshot, ChannelData, FacebookAccount, 
    AffiliateSnapshot, CollectionLog, Campaign, FacebookAccountMapping
)

def create_campaign():
    """Criar campanha ativa padrão"""
    db = next(get_db())
    
    # Verificar se já existe
    existing = db.query(Campaign).filter(Campaign.is_active == True).first()
    if existing:
        print(f"OK - Campanha ja existe: {existing.name}")
        return existing
    
    campaign = Campaign(
        product_id="68e7dc390d0e097d616ae52d",
        name="Sorteio 200mil",
        description="Campanha principal do Imperio Premios",
        roi_goal=2.0,
        daily_budget=10000.0,
        target_sales=30000.0,
        is_active=True
    )
    
    db.add(campaign)
    db.commit()
    print(f"OK - Campanha criada: {campaign.name}")
    return campaign

def create_facebook_mappings():
    """Criar mapeamento de contas Facebook por canal"""
    db = next(get_db())
    
    # Verificar se já existe
    existing = db.query(FacebookAccountMapping).first()
    if existing:
        print("OK - Mapeamentos Facebook ja existem")
        return
    
    mappings = [
        # Instagram (seguindo o mapeamento do config.py)
        {"account_id": "act_2067257390316380", "channel": "instagram"},
        {"account_id": "act_1391112848236399", "channel": "instagram"},
        {"account_id": "act_406219475582745", "channel": "instagram"},
        {"account_id": "act_790223756353632", "channel": "instagram"},
        {"account_id": "act_303402486183447", "channel": "instagram"},
        {"account_id": "act_765524492538546", "channel": "instagram"},

        # Grupos
        {"account_id": "act_772777644802886", "channel": "grupos"},
    ]
    
    for mapping_data in mappings:
        mapping = FacebookAccountMapping(**mapping_data)
        db.add(mapping)
    
    db.commit()
    print(f"OK - {len(mappings)} mapeamentos Facebook criados")

def generate_realistic_daily_progression():
    """Gera progressão realística de dados ao longo do dia"""
    
    # Data de hoje e ontem
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    dates_to_populate = [yesterday, today]
    
    db = next(get_db())
    
    for target_date in dates_to_populate:
        print(f"\nGerando dados para {target_date.strftime('%d/%m/%Y')}...")
        
        # Limpar dados existentes para esta data
        db.query(DailySnapshot).filter(DailySnapshot.date == target_date).delete()
        db.query(ChannelData).filter(ChannelData.date == target_date).delete()
        db.query(FacebookAccount).filter(FacebookAccount.date == target_date).delete()
        db.query(AffiliateSnapshot).filter(AffiliateSnapshot.date == target_date).delete()
        db.query(CollectionLog).filter(CollectionLog.date == target_date).delete()
        
        # Definir metas e progressão para o dia
        is_today = target_date == today
        
        if is_today:
            # Para hoje, simular progresso ao longo do dia até o momento atual
            current_hour = datetime.now().hour
            progress_factor = min(current_hour / 24.0, 0.9)  # Máximo 90% das metas
            base_sales = 25000 + random.uniform(-2000, 3000)
            base_spend = 12000 + random.uniform(-1000, 1500)
        else:
            # Para ontem, usar dados completos do dia
            progress_factor = 0.85 + random.uniform(0, 0.1)  # Entre 85-95%
            base_sales = 22000 + random.uniform(-1500, 2500)
            base_spend = 11500 + random.uniform(-800, 1200)
        
        final_sales = base_sales * progress_factor
        final_spend = base_spend * progress_factor
        final_roi = final_sales / final_spend if final_spend > 0 else 0
        final_profit = final_sales - final_spend
        final_margin = (final_profit / final_sales * 100) if final_sales > 0 else 0
        
        # Gerar snapshots horários realistas
        hours_to_generate = current_hour if is_today else 24
        
        for hour in range(8, min(hours_to_generate + 1, 24)):  # Começar às 8h
            # Progressão cumulativa realística
            hour_progress = (hour - 8) / (24 - 8)  # Progresso baseado em horas de trabalho
            hour_progress = min(hour_progress, 1.0)
            
            # Adicionar variação horária realística
            hour_variation = 1.0 + random.uniform(-0.1, 0.15)
            
            cumulative_sales = final_sales * hour_progress * hour_variation
            cumulative_spend = final_spend * hour_progress * hour_variation
            cumulative_roi = cumulative_sales / cumulative_spend if cumulative_spend > 0 else 0
            cumulative_profit = cumulative_sales - cumulative_spend
            cumulative_margin = (cumulative_profit / cumulative_sales * 100) if cumulative_sales > 0 else 0
            
            # Timestamp para a coleta
            collection_time = datetime.combine(target_date, datetime.min.time().replace(hour=hour, minute=random.randint(0, 59)))
            
            # Daily Snapshot
            daily_snapshot = DailySnapshot(
                date=target_date,
                product_id="68e7dc390d0e097d616ae52d",
                total_sales=cumulative_sales,
                total_orders=int(cumulative_sales / 280),  # Ticket médio ~R$ 280
                total_numbers=int(cumulative_sales / 280) * 50,  # ~50 números por pedido
                total_spend=cumulative_spend,
                total_budget=15000.0,
                general_roi=cumulative_roi,
                profit=cumulative_profit,
                margin_percent=cumulative_margin,
                collected_at=collection_time
            )
            db.add(daily_snapshot)
            
            # Channel Data - Geral (55% dos dados totais)
            geral_sales = cumulative_sales * 0.55
            geral_spend = cumulative_spend * 0.55
            geral_roi = geral_sales / geral_spend if geral_spend > 0 else 0
            
            channel_geral = ChannelData(
                date=target_date,
                product_id="68e7dc390d0e097d616ae52d",
                channel_name="geral",
                sales=geral_sales,
                spend=geral_spend,
                budget=8000.0,
                roi=geral_roi,
                profit=geral_sales - geral_spend,
                margin_percent=((geral_sales - geral_spend) / geral_sales * 100) if geral_sales > 0 else 0,
                collected_at=collection_time
            )
            db.add(channel_geral)
            
            # Channel Data - Instagram (30% dos dados totais)
            instagram_sales = cumulative_sales * 0.30
            instagram_spend = cumulative_spend * 0.30
            instagram_roi = instagram_sales / instagram_spend if instagram_spend > 0 else 0
            
            channel_instagram = ChannelData(
                date=target_date,
                product_id="68e7dc390d0e097d616ae52d",
                channel_name="instagram",
                sales=instagram_sales,
                spend=instagram_spend,
                budget=4500.0,
                roi=instagram_roi,
                profit=instagram_sales - instagram_spend,
                margin_percent=((instagram_sales - instagram_spend) / instagram_sales * 100) if instagram_sales > 0 else 0,
                collected_at=collection_time
            )
            db.add(channel_instagram)
            
            # Channel Data - Grupos (15% dos dados totais)
            grupos_sales = cumulative_sales * 0.15
            grupos_spend = cumulative_spend * 0.15
            grupos_roi = grupos_sales / grupos_spend if grupos_spend > 0 else 0
            
            channel_grupos = ChannelData(
                date=target_date,
                product_id="68e7dc390d0e097d616ae52d",
                channel_name="grupos",
                sales=grupos_sales,
                spend=grupos_spend,
                budget=2500.0,
                roi=grupos_roi,
                profit=grupos_sales - grupos_spend,
                margin_percent=((grupos_sales - grupos_spend) / grupos_sales * 100) if grupos_sales > 0 else 0,
                collected_at=collection_time
            )
            db.add(channel_grupos)
            
            # Facebook Accounts
            facebook_accounts = [
                {"account_id": "act_2067257390316380", "channel": "instagram", "percentage": 0.16},
                {"account_id": "act_1391112848236399", "channel": "instagram", "percentage": 0.15},
                {"account_id": "act_406219475582745", "channel": "instagram", "percentage": 0.15},
                {"account_id": "act_790223756353632", "channel": "instagram", "percentage": 0.15},
                {"account_id": "act_303402486183447", "channel": "instagram", "percentage": 0.14},
                {"account_id": "act_765524492538546", "channel": "instagram", "percentage": 0.13},
                {"account_id": "act_772777644802886", "channel": "grupos", "percentage": 0.12},
            ]
            
            for fb_account in facebook_accounts:
                fb_spend = cumulative_spend * fb_account["percentage"]
                
                facebook_data = FacebookAccount(
                    date=target_date,
                    account_id=fb_account["account_id"],
                    spend=fb_spend,
                    api_version="v18.0",
                    channel=fb_account["channel"],
                    collected_at=collection_time
                )
                db.add(facebook_data)
            
            # Affiliate Snapshots
            affiliates = [
                {"code": "L8UTEDVTI0", "name": "Instagram Oficial", "channel": "instagram", "percentage": 0.30},
                {"code": "17QB25AKRL", "name": "Grupo WhatsApp 1", "channel": "grupos", "percentage": 0.10},
                {"code": "30CS8W9DP1", "name": "Grupo WhatsApp 2", "channel": "grupos", "percentage": 0.05},
            ]
            
            for affiliate in affiliates:
                affiliate_sales = cumulative_sales * affiliate["percentage"]
                affiliate_orders = int(affiliate_sales / 280)
                
                affiliate_data = AffiliateSnapshot(
                    date=target_date,
                    product_id="68e7dc390d0e097d616ae52d",
                    affiliate_code=affiliate["code"],
                    affiliate_name=affiliate["name"],
                    total_paid_orders=affiliate_sales,
                    order_count=affiliate_orders,
                    average_ticket=affiliate_sales / affiliate_orders if affiliate_orders > 0 else 0,
                    channel=affiliate["channel"],
                    collected_at=collection_time
                )
                db.add(affiliate_data)
            
            # Collection Log
            collection_log = CollectionLog(
                date=target_date,
                collection_time=collection_time,
                status="success",
                sales_collected=True,
                affiliates_collected=True,
                facebook_collected=True,
                total_sales=cumulative_sales,
                total_spend=cumulative_spend,
                general_roi=cumulative_roi,
                message=f"Coleta automática realizada às {collection_time.strftime('%H:%M')}"
            )
            db.add(collection_log)
        
        db.commit()
        print(f"OK - {hours_to_generate} snapshots gerados para {target_date.strftime('%d/%m/%Y')}")
    
    db.close()

def main():
    """Função principal"""
    print("POPULANDO BANCO DE DADOS COM DADOS REALISTAS")
    print("=" * 60)
    
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    print("OK - Tabelas criadas/verificadas")
    
    # Criar campanha
    create_campaign()
    
    # Criar mapeamentos Facebook
    create_facebook_mappings()
    
    # Gerar dados realistas
    generate_realistic_daily_progression()
    
    print("\n" + "=" * 60)
    print("BANCO DE DADOS POPULADO COM SUCESSO!")
    print("Dados disponíveis para ontem e hoje")
    print("Sistema pronto para usar banco em vez de Google Sheets")

if __name__ == "__main__":
    main()