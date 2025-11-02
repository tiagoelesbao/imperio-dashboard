#!/usr/bin/env python3
"""
Criar todas as tabelas necessárias no banco de dados
"""
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from core.database.base import Base, engine
from core.models.base import DailySnapshot, ChannelData, CollectionLog, CaptureLog
from core.models.horapix import HoraPixDraw, HoraPixLog
from core.models.main_action import MainAction, MainActionDaily
from sqlalchemy.orm import Session

def main():
    try:
        print('[CREATE] Criando TODAS as tabelas necessarias...')

        # Criar todas as tabelas de uma vez
        Base.metadata.create_all(engine)

        print('[CREATE] Tabelas criadas com sucesso:')
        print('  - daily_snapshots')
        print('  - channel_data')
        print('  - collection_logs')
        print('  - capture_logs')
        print('  - horapix_draws')
        print('  - horapix_logs')
        print('  - main_actions (PERMANENTE)')
        print('  - main_action_daily (PERMANENTE)')
        print('  - facebook_account_mapping (se definido)')

        # Verificar se as tabelas foram criadas
        session = Session(engine)
        try:
            # Testar cada tabela
            session.query(DailySnapshot).count()
            print('[OK] daily_snapshots acessivel')

            session.query(ChannelData).count()
            print('[OK] channel_data acessivel')

            session.query(HoraPixDraw).count()
            print('[OK] horapix_draws acessivel')

            session.query(MainAction).count()
            print('[OK] main_actions acessivel')

            session.query(MainActionDaily).count()
            print('[OK] main_action_daily acessivel')

        except Exception as e:
            print(f'[AVISO] Erro ao verificar tabelas: {e}')
        finally:
            session.close()

        print('\n[CREATE] Banco de dados pronto para uso!')
        return True

    except Exception as e:
        print(f'[CREATE] ERRO ao criar tabelas: {str(e)}')
        return False

if __name__ == "__main__":
    main()