#!/usr/bin/env python3
"""
Script de reinicialização rápida do sistema Imperio
Para usar quando o sistema trava ou para completamente
"""

import subprocess
import time
import os
import signal
import sys

def kill_related_processes():
    """Finalizar todos os processos relacionados"""
    print("🧹 Finalizando processos relacionados...")
    
    processes = [
        "python.*imperio",
        "chromedriver",
        "brave",
        "uvicorn.*imperio"
    ]
    
    for process in processes:
        try:
            subprocess.run(["pkill", "-f", process], capture_output=True)
            print(f"   ✅ Finalizado: {process}")
        except:
            print(f"   ⚠️ Não encontrado: {process}")
    
    time.sleep(2)

def clean_locks():
    """Limpar arquivos de lock problemáticos"""
    print("🔓 Limpando arquivos de lock...")
    
    lock_files = [
        "data/whatsapp_profile/Default/LOCK",
        "data/temp_profiles/automation_profile/LOCK"
    ]
    
    for lock_file in lock_files:
        try:
            if os.path.exists(lock_file):
                os.remove(lock_file)
                print(f"   ✅ Removido: {lock_file}")
        except Exception as e:
            print(f"   ⚠️ Erro ao remover {lock_file}: {e}")

def clear_temp_profiles():
    """Limpar perfis temporários órfãos"""
    print("🗂️ Limpando perfis temporários...")
    
    import shutil
    import glob
    
    # Limpar perfis no AppData
    appdata_path = "/mnt/c/Users/Pichau/AppData/Roaming/ImperioCapture/profiles/"
    if os.path.exists(appdata_path):
        for profile in glob.glob(os.path.join(appdata_path, "capture_*")):
            try:
                shutil.rmtree(profile)
                print(f"   ✅ Removido: {os.path.basename(profile)}")
            except:
                pass
    
    # Remover perfil de automação local
    automation_profile = "data/temp_profiles/automation_profile"
    if os.path.exists(automation_profile):
        try:
            shutil.rmtree(automation_profile)
            print(f"   ✅ Removido: automation_profile")
        except:
            pass

def restart_system():
    """Reiniciar o sistema"""
    print("🚀 Reiniciando sistema...")
    
    try:
        # Executar o sistema em modo reset
        cmd = [sys.executable, "imperio.py", "--reset"]
        print(f"   📋 Comando: {' '.join(cmd)}")
        
        # Iniciar em background para não bloquear
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.getcwd()
        )
        
        print(f"   ✅ Sistema iniciado (PID: {process.pid})")
        print("   ⏳ Aguardando inicialização...")
        
        # Aguardar um pouco para o sistema iniciar
        time.sleep(10)
        
        return process
        
    except Exception as e:
        print(f"   ❌ Erro ao reiniciar: {e}")
        return None

if __name__ == "__main__":
    print("🔄 REINICIALIZAÇÃO SISTEMA IMPERIO")
    print("=" * 50)
    
    try:
        # Passo 1: Finalizar processos
        kill_related_processes()
        
        # Passo 2: Limpar locks
        clean_locks()
        
        # Passo 3: Limpar perfis temporários
        clear_temp_profiles()
        
        # Passo 4: Aguardar um pouco
        print("⏳ Aguardando limpeza completa...")
        time.sleep(3)
        
        # Passo 5: Reiniciar
        process = restart_system()
        
        if process:
            print("\n🎉 Sistema reiniciado com sucesso!")
            print("📊 Dashboard: http://localhost:8002/imperio")
            print("⚠️ Aguarde alguns segundos para o sistema ficar totalmente operacional")
        else:
            print("\n❌ Falha na reinicialização")
            
    except KeyboardInterrupt:
        print("\n⚠️ Interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante reinicialização: {e}")