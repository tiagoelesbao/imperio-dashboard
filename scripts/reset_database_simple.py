#!/usr/bin/env python3
"""
Reset simples do banco de dados
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.database.base import Base, engine
from core.models.base import DailySnapshot, ChannelData, CollectionLog, CaptureLog
from sqlalchemy.orm import Session

def main():
    try:
        print('[RESET] Criando tabelas se não existem...')
        Base.metadata.create_all(engine)

        session = Session(engine)

        print('[RESET] Limpando dados existentes...')
        print('[RESET] IMPORTANTE: Tabelas de Ação Principal (main_actions, main_action_daily) são PRESERVADAS')
        try:
            # ATENÇÃO: NÃO deletar tabelas de MainAction e MainActionDaily
            # Estas tabelas contém dados permanentes de monitoramento de sorteios
            session.query(DailySnapshot).delete()
            session.query(ChannelData).delete()
            session.query(CollectionLog).delete()
            session.query(CaptureLog).delete()
            # MainAction e MainActionDaily NÃO são deletadas (dados permanentes)
        except Exception as e:
            print(f'[RESET] Aviso ao limpar dados: {str(e)[:50]}')
        
        session.commit()
        session.close()
        
        print('[RESET] Banco de dados criado e limpo com sucesso!')
        return True
        
    except Exception as e:
        print(f'[RESET] ERRO no reset: {str(e)[:100]}')
        return False

if __name__ == "__main__":
    main()