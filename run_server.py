#!/usr/bin/env python3
"""
Sistema ROI Império - Servidor Simplificado
Executa o servidor diretamente sem problemas de imports
"""

import os
import sys
import subprocess
import sqlite3
from pathlib import Path

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_header():
    print("=" * 70)
    print("🎯 SISTEMA ROI IMPÉRIO - SORTEIO 200MIL")
    print("=" * 70)
    print("📋 Produto ID: 684c73283d75820c0a77a42f")
    print("🎯 Campanha: Sorteio 200mil")
    print("=" * 70)
    print()

def check_dependencies():
    """Verificar e instalar dependências necessárias"""
    print("🔍 Verificando dependências...")
    
    required_packages = [
        'fastapi',
        'uvicorn[standard]',
        'sqlalchemy', 
        'apscheduler',
        'requests',
        'pytz',
        'jinja2',
        'python-multipart',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            if package == 'uvicorn[standard]':
                import uvicorn
            elif package == 'python-multipart':
                import multipart
            elif package == 'python-dotenv':
                import dotenv
            else:
                __import__(package)
            print(f"✅ {package}")
        except ImportError:
            print(f"❌ {package} - NÃO ENCONTRADO")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n📦 Instalando {len(missing_packages)} pacote(s) em falta...")
        
        for package in missing_packages:
            try:
                print(f"🔄 Instalando {package}...")
                subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])
            except subprocess.CalledProcessError as e:
                print(f"❌ Erro ao instalar {package}: {e}")
                return False
        
        print("✅ Todas as dependências foram instaladas!")
    else:
        print("✅ Todas as dependências estão OK!")
    
    return True

def reset_database():
    """Resetar banco de dados"""
    print("\n🗑️  RESET DO BANCO DE DADOS")
    print("=" * 50)
    
    # Listar bancos existentes
    db_files = [f for f in os.listdir('.') if f.endswith('.db')]
    
    if db_files:
        print(f"📊 Bancos encontrados: {', '.join(db_files)}")
    else:
        print("📄 Nenhum banco de dados encontrado")
    
    print("\n⚠️  Esta ação irá remover TODOS os dados!")
    confirm = input("❓ Confirmar reset? (s/n): ").lower()
    
    if confirm in ['s', 'sim', 'y', 'yes']:
        for db_file in db_files:
            try:
                os.remove(db_file)
                print(f"🗑️  Removido: {db_file}")
            except Exception as e:
                print(f"⚠️  Erro: {e}")
        print("✅ Reset concluído!")
        return True
    else:
        print("❌ Reset cancelado")
        return False

def main():
    clear_screen()
    print_header()
    
    # Menu
    print("🎛️  OPÇÕES:")
    print("1. 🚀 Iniciar sistema")
    print("2. 🗑️  Resetar banco + Iniciar")
    print("3. ❌ Sair")
    print("=" * 30)
    
    choice = input("🔢 Escolha (1-3): ").strip()
    
    if choice == '2':
        if not reset_database():
            return
    elif choice == '3':
        print("👋 Saindo...")
        return
    elif choice != '1':
        print("❌ Opção inválida!")
        return
    
    # Verificar dependências
    print("\n" + "="*50)
    if not check_dependencies():
        print("❌ Falha nas dependências")
        input("Pressione Enter para sair...")
        return
    
    # Iniciar servidor
    print("\n🚀 INICIANDO SERVIDOR...")
    print("=" * 50)
    print("🌐 URL: http://localhost:8000")
    print("📊 Dashboard: http://localhost:8000/dashboard")
    print("⚙️  Configurações: http://localhost:8000/config")
    print("🎯 Campanhas: http://localhost:8000/campaigns")
    print("=" * 50)
    print("🔄 Para parar: Ctrl+C")
    print("=" * 50)
    
    try:
        # Executar uvicorn diretamente com caminho correto
        subprocess.run([
            sys.executable, '-m', 'uvicorn', 
            'app.main:app', 
            '--host', '0.0.0.0', 
            '--port', '8000', 
            '--reload'
        ])
    except KeyboardInterrupt:
        print("\n\n🛑 Servidor parado")
    except Exception as e:
        print(f"\n❌ Erro: {e}")

if __name__ == "__main__":
    main()