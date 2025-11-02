#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criar tabelas de Ação Principal
"""
import sys
import os

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from core.database.base import engine, Base
from core.models.main_action import MainAction, MainActionDaily


def create_tables():
    """Criar tabelas"""
    print("Criando tabelas de Ação Principal...")

    # Criar tabelas
    Base.metadata.create_all(bind=engine, tables=[
        MainAction.__table__,
        MainActionDaily.__table__
    ])

    print("✅ Tabelas criadas com sucesso!")


if __name__ == "__main__":
    create_tables()
