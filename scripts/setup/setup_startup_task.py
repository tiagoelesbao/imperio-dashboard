#!/usr/bin/env python3
"""
Configuração de Execução Automática na Inicialização do Windows
Cria entrada no registro do Windows para executar o sistema ao iniciar
"""

import os
import sys
import winreg
import shutil
from pathlib import Path

def create_startup_batch():
    """Cria script batch otimizado para inicialização"""
    
    current_dir = Path.cwd()
    startup_bat = current_dir / "imperio_startup.bat"
    
    content = f"""@echo off
REM ================================================================
REM Sistema Imperio - Execucao Automatica na Inicializacao
REM ================================================================

REM Define variavel para identificar execucao automatica
set TASK_SCHEDULER=true

REM Aguardar sistema inicializar completamente
timeout /t 30 /nobreak >nul

REM Ir para diretorio do sistema
cd /d "{current_dir}"

REM Criar pasta de logs se nao existir
if not exist "data\\logs" mkdir "data\\logs"

REM Log de inicio
echo [%date% %time%] Sistema iniciado automaticamente >> data\\logs\\startup.log

REM Finalizar processos orfaos
taskkill /F /IM chromedriver.exe >nul 2>&1
taskkill /F /IM brave.exe /FI "WINDOWTITLE eq data:*" >nul 2>&1

REM Aguardar limpeza
timeout /t 3 /nobreak >nul

REM Executar sistema em modo minimizado
start /min "" ".\\venv\\Scripts\\python.exe" imperio.py --reset --headless

REM Registrar execucao
echo [%date% %time%] Sistema executado com sucesso >> data\\logs\\startup.log

exit
"""
    
    with open(startup_bat, 'w') as f:
        f.write(content)
    
    print(f"✅ Script de inicialização criado: {startup_bat}")
    return startup_bat

def add_to_registry_startup(script_path):
    """Adiciona entrada no registro do Windows para execução automática"""
    
    try:
        # Abrir chave do registro de inicialização do usuário atual
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        # Abrir ou criar a chave
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        # Nome da entrada no registro
        app_name = "SistemaImperio_AutoStart"
        
        # Valor: caminho completo do script
        app_path = str(script_path)
        
        # Adicionar entrada
        winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, app_path)
        winreg.CloseKey(key)
        
        print(f"✅ Entrada adicionada ao registro de inicialização")
        print(f"   Nome: {app_name}")
        print(f"   Caminho: {app_path}")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro ao adicionar ao registro: {e}")
        return False

def add_to_startup_folder(script_path):
    """Alternativa: Adiciona atalho na pasta Inicializar do Windows"""
    
    try:
        import win32com.client
        
        # Pasta de inicialização do usuário
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        if not startup_folder.exists():
            print(f"❌ Pasta de inicialização não encontrada: {startup_folder}")
            return False
        
        # Criar atalho
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut_path = startup_folder / "Sistema Imperio.lnk"
        
        shortcut = shell.CreateShortCut(str(shortcut_path))
        shortcut.Targetpath = str(script_path)
        shortcut.WorkingDirectory = str(Path.cwd())
        shortcut.WindowStyle = 7  # Minimizado
        shortcut.IconLocation = str(script_path)
        shortcut.Description = "Sistema Imperio - Coleta Automática"
        shortcut.save()
        
        print(f"✅ Atalho criado na pasta Inicializar")
        print(f"   Local: {shortcut_path}")
        
        return True
        
    except ImportError:
        # Se pywin32 não estiver instalado, copiar arquivo diretamente
        try:
            startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
            
            if startup_folder.exists():
                dest_path = startup_folder / "imperio_startup.bat"
                shutil.copy2(script_path, dest_path)
                print(f"✅ Script copiado para pasta Inicializar")
                print(f"   Local: {dest_path}")
                return True
        except Exception as e:
            print(f"⚠️ Não foi possível criar atalho: {e}")
            
    except Exception as e:
        print(f"❌ Erro ao criar atalho: {e}")
        
    return False

def create_task_scheduler_xml():
    """Cria arquivo XML para importação manual no Agendador de Tarefas"""
    
    current_dir = Path.cwd()
    script_path = current_dir / "imperio_startup.bat"
    xml_path = current_dir / "task_imperio_startup.xml"
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>Sistema Imperio - Execução automática na inicialização</Description>
  </RegistrationInfo>
  <Triggers>
    <LogonTrigger>
      <Enabled>true</Enabled>
      <Delay>PT1M</Delay>
    </LogonTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>false</RunOnlyIfNetworkAvailable>
    <IdleSettings>
      <StopOnIdleEnd>false</StopOnIdleEnd>
      <RestartOnIdle>false</RestartOnIdle>
    </IdleSettings>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>true</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{script_path}</Command>
      <WorkingDirectory>{current_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    with open(xml_path, 'w', encoding='utf-16') as f:
        f.write(xml_content)
    
    print(f"✅ Arquivo XML criado para importação manual: {xml_path}")
    return xml_path

def remove_from_startup():
    """Remove a execução automática"""
    
    removed = False
    
    # Remover do registro
    try:
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            r"Software\Microsoft\Windows\CurrentVersion\Run",
            0,
            winreg.KEY_ALL_ACCESS
        )
        
        try:
            winreg.DeleteValue(key, "SistemaImperio_AutoStart")
            print("✅ Removido do registro de inicialização")
            removed = True
        except FileNotFoundError:
            print("ℹ️ Entrada não encontrada no registro")
        
        winreg.CloseKey(key)
        
    except Exception as e:
        print(f"⚠️ Erro ao acessar registro: {e}")
    
    # Remover da pasta Inicializar
    try:
        startup_folder = Path.home() / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"
        
        # Remover atalho
        shortcut_path = startup_folder / "Sistema Imperio.lnk"
        if shortcut_path.exists():
            shortcut_path.unlink()
            print("✅ Atalho removido da pasta Inicializar")
            removed = True
        
        # Remover script copiado
        bat_path = startup_folder / "imperio_startup.bat"
        if bat_path.exists():
            bat_path.unlink()
            print("✅ Script removido da pasta Inicializar")
            removed = True
            
    except Exception as e:
        print(f"⚠️ Erro ao remover da pasta Inicializar: {e}")
    
    if not removed:
        print("ℹ️ Nenhuma entrada de inicialização encontrada")
    
    return removed

def main():
    """Função principal"""
    
    print("=" * 60)
    print("CONFIGURAÇÃO DE INICIALIZAÇÃO AUTOMÁTICA - SISTEMA IMPÉRIO")
    print("=" * 60)
    print()
    
    print("Este script configurará o sistema para iniciar automaticamente")
    print("quando o Windows for iniciado.")
    print()
    
    print("Opções disponíveis:")
    print("1. Configurar inicialização automática")
    print("2. Remover inicialização automática")
    print("3. Criar arquivo para importação manual")
    print("4. Sair")
    print()
    
    choice = input("Escolha uma opção (1-4): ").strip()
    
    if choice == "1":
        print("\n🔧 CONFIGURANDO INICIALIZAÇÃO AUTOMÁTICA...")
        print("-" * 40)
        
        # Criar script de inicialização
        script_path = create_startup_batch()
        
        # Método 1: Registro do Windows (mais confiável)
        print("\n📝 Método 1: Registro do Windows")
        if add_to_registry_startup(script_path):
            print("✅ Configurado com sucesso via registro!")
        
        # Método 2: Pasta Inicializar (backup)
        print("\n📁 Método 2: Pasta Inicializar (backup)")
        if add_to_startup_folder(script_path):
            print("✅ Configurado com sucesso via pasta Inicializar!")
        
        print("\n✅ INICIALIZAÇÃO AUTOMÁTICA CONFIGURADA!")
        print("\nO sistema será executado automaticamente quando o Windows iniciar.")
        print("Aguardará 30 segundos para garantir que todos os serviços estejam prontos.")
        print("\n📊 Logs de execução: data\\logs\\startup.log")
        
    elif choice == "2":
        print("\n🗑️ REMOVENDO INICIALIZAÇÃO AUTOMÁTICA...")
        print("-" * 40)
        
        if remove_from_startup():
            print("\n✅ INICIALIZAÇÃO AUTOMÁTICA REMOVIDA!")
        else:
            print("\n❌ Nada para remover")
    
    elif choice == "3":
        print("\n📄 CRIANDO ARQUIVO PARA IMPORTAÇÃO MANUAL...")
        print("-" * 40)
        
        # Criar script de inicialização
        script_path = create_startup_batch()
        
        # Criar XML
        xml_path = create_task_scheduler_xml()
        
        print("\n📋 INSTRUÇÕES PARA IMPORTAÇÃO MANUAL:")
        print("1. Abra o Agendador de Tarefas (taskschd.msc)")
        print("2. Clique em 'Importar Tarefa' no menu Ação")
        print(f"3. Selecione o arquivo: {xml_path}")
        print("4. Clique em OK para criar a tarefa")
        print("\n✅ Arquivos criados com sucesso!")
        
    elif choice == "4":
        print("\nSaindo...")
        return
    
    else:
        print("\n❌ Opção inválida!")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperação cancelada pelo usuário.")
    except Exception as e:
        print(f"\n❌ Erro inesperado: {e}")
    
    print("\n" + "=" * 60)
    input("Pressione ENTER para sair...")