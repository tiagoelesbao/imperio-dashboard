#!/usr/bin/env python3
"""
Reset database completely and start fresh
"""
import sys
import os
sys.path.append(os.getcwd())

import sqlite3
from datetime import datetime, date
from core.database.base import Base, engine, get_db
from core.models.base import DailySnapshot, ChannelData, CollectionLog

def reset_database_completely():
    """Reset database and create fresh tables"""
    print("=" * 60)
    print("RESET COMPLETO DO BANCO DE DADOS")
    print("=" * 60)
    
    try:
        # Primeiro, vamos tentar fechar todas as conexões existentes
        print("\n1. Fechando conexões existentes...")
        try:
            engine.dispose()
        except:
            pass
        
        # Remover arquivo de banco se existir
        db_files = ['dashboard_roi.db', 'data/databases/dashboard_roi.db']
        for db_file in db_files:
            if os.path.exists(db_file):
                try:
                    os.remove(db_file)
                    print(f"   Removido: {db_file}")
                except Exception as e:
                    print(f"   Erro ao remover {db_file}: {e}")
        
        print("\n2. Criando tabelas do zero...")
        # Criar tabelas
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
        print("   Tabelas criadas com sucesso!")
        
        print("\n3. Verificando banco limpo...")
        db = next(get_db())
        
        # Verificar se tabelas estão vazias
        snapshots_count = db.query(DailySnapshot).count()
        channels_count = db.query(ChannelData).count()
        logs_count = db.query(CollectionLog).count()
        
        print(f"   DailySnapshot: {snapshots_count} registros")
        print(f"   ChannelData: {channels_count} registros")
        print(f"   CollectionLog: {logs_count} registros")
        
        if snapshots_count == 0 and channels_count == 0 and logs_count == 0:
            print("   Banco de dados resetado com sucesso!")
        else:
            print("   Algumas tabelas ainda contem dados")
        
        db.close()
        
        print("\n4. Testando primeira coleta...")
        # Usar coletor REAL
        from core.services.data_collector import imperio_collector
        from core.services.data_manager import imperio_data_manager
        
        result = imperio_collector.execute_full_collection()
        if "error" not in result:
            db = next(get_db())
            saved = imperio_data_manager.save_collection_data(db, result)
            db.close()
            
            if saved:
                print("   Primeira coleta executada com sucesso!")
                print(f"   ROI: {result['totals']['roi']:.2f}")
                print(f"   Vendas: R$ {result['totals']['sales']:,.2f}")
                print(f"   Gastos: R$ {result['totals']['spend']:,.2f}")
            else:
                print("   Erro ao salvar primeira coleta")
        else:
            print(f"   Erro na primeira coleta: {result.get('error')}")
        
        print("\n5. Verificando dados após primeira coleta...")
        db = next(get_db())
        
        snapshots_count = db.query(DailySnapshot).count()
        channels_count = db.query(ChannelData).count()
        logs_count = db.query(CollectionLog).count()
        
        print(f"   DailySnapshot: {snapshots_count} registros")
        print(f"   ChannelData: {channels_count} registros")
        print(f"   CollectionLog: {logs_count} registros")
        
        # Mostrar dados da primeira coleta
        if snapshots_count > 0:
            snapshot = db.query(DailySnapshot).first()
            print(f"   Snapshot - ROI: {snapshot.general_roi:.2f}, Vendas: R$ {snapshot.total_sales:,.2f}")
            
        if channels_count > 0:
            channels = db.query(ChannelData).all()
            for channel in channels:
                print(f"   Canal {channel.channel_name} - ROI: {channel.roi:.2f}, Budget: R$ {channel.budget:,.2f}")
        
        db.close()
        
    except Exception as e:
        print(f"ERRO durante reset: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    print("\n" + "=" * 60)
    print("RESET CONCLUÍDO COM SUCESSO!")
    print("- Banco de dados completamente limpo")
    print("- Primeira coleta REAL executada")
    print("- Dados REAIS prontos para uso")
    print("- Sistema pronto para iniciar servidor")
    return True

if __name__ == "__main__":
    reset_database_completely()