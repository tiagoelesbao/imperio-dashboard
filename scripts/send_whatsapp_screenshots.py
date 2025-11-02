#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script dedicado para envio de screenshots via WhatsApp
Resolve problemas de encoding do Windows CMD
"""
import sys
import os
import glob

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.services.whatsapp_smart_profile import WhatsAppSmartProfile


def main():
    """Enviar screenshots separados por grupo"""
    try:
        # Encontrar todos os screenshots
        all_files = sorted(glob.glob('screenshots/*.png'))[-4:]

        if not all_files:
            print('[WHATSAPP] Nenhum screenshot encontrado')
            return 0

        # Separar arquivos por tipo
        files_imperio = [
            {
                'page': os.path.basename(f).split('_')[0],
                'file_path': os.path.abspath(f),
                'file_size_kb': os.path.getsize(f) // 1024
            }
            for f in all_files
            if not os.path.basename(f).startswith('horapix')
        ]

        files_horapix = [
            {
                'page': os.path.basename(f).split('_')[0],
                'file_path': os.path.abspath(f),
                'file_size_kb': os.path.getsize(f) // 1024
            }
            for f in all_files
            if os.path.basename(f).startswith('horapix')
        ]

        # Inicializar serviço
        service = WhatsAppSmartProfile()

        print(f'[WHATSAPP] Império: {len(files_imperio)} arquivos | Hora do Pix: {len(files_horapix)} arquivos')

        # Enviar Império Prêmios
        result_imperio = None
        if files_imperio:
            result_imperio = service.send_images_smart(
                files_imperio,
                'OracleSys - Império Prêmios [ROI DIÁRIO]'
            )
            sent_imperio = result_imperio.get('total_sent', 0) if result_imperio else 0
            print(f'[WHATSAPP] Império: {sent_imperio} enviados')

        # Enviar Hora do Pix
        result_horapix = None
        if files_horapix:
            result_horapix = service.send_images_smart(
                files_horapix,
                'OracleSys - Hora do Pix [ROI DIÁRIO]'
            )
            sent_horapix = result_horapix.get('total_sent', 0) if result_horapix else 0
            print(f'[WHATSAPP] Hora do Pix: {sent_horapix} enviados')

        return 0

    except Exception as e:
        print(f'[WHATSAPP] ERRO: {e}')
        return 1


if __name__ == '__main__':
    sys.exit(main())
