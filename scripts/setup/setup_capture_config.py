#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Configurar sistema de captura no banco de dados
"""
import sys
import os
sys.path.append(os.getcwd())

from sqlalchemy.orm import Session
from core.database.base import SessionLocal, engine, Base
from core.models.base import CaptureConfig

def setup_capture_config():
    """Configura o sistema de captura no banco"""
    print("=" * 60)
    print("CONFIGURACAO DO SISTEMA DE CAPTURA")
    print("=" * 60)
    
    # Criar tabelas se não existirem
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar se já existe configuração
        config = db.query(CaptureConfig).first()
        
        if config:
            print(f"[INFO] Configuracao existente encontrada:")
            print(f"   Captura habilitada: {config.capture_enabled}")
            print(f"   WhatsApp habilitado: {config.whatsapp_enabled}")
            print(f"   Grupo WhatsApp: {config.whatsapp_group}")
            print(f"   Output folder: {config.output_folder}")
        else:
            # Criar configuração padrão
            config = CaptureConfig(
                output_folder="screenshots",
                capture_enabled=True,
                whatsapp_enabled=True,
                whatsapp_group="OracleSys - Imperio Premios [ROI DIARIO]"
            )
            db.add(config)
            db.commit()
            print("[SUCESSO] Configuracao padrao criada!")
        
        # Atualizar configuração se necessário
        config.capture_enabled = True
        config.whatsapp_enabled = True
        db.commit()
        
        print("\n[OK] Sistema de captura configurado e habilitado!")
        print("   Captura: HABILITADA")
        print("   WhatsApp: HABILITADO")
        print(f"   Grupo: {config.whatsapp_group}")
        print(f"   Pasta: {config.output_folder}")
        
    except Exception as e:
        print(f"[ERRO] Falha ao configurar: {e}")
        db.rollback()
        return False
    
    finally:
        db.close()
    
    return True

if __name__ == "__main__":
    setup_capture_config()