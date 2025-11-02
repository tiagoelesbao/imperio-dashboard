#!/usr/bin/env python3
"""
Configuração do Windows Task Scheduler para o Sistema Império
Cria uma tarefa agendada que executa diariamente às 6h da manhã
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

def create_task_xml(task_name, script_path, work_dir, user_account):
    """Cria o XML de configuração da tarefa"""
    
    xml_content = f"""<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Date>2025-08-14T00:00:00</Date>
    <Author>{user_account}</Author>
    <Description>Sistema Imperio - Coleta automatica de dados e captura de telas</Description>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2025-08-14T06:00:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <UserId>{user_account}</UserId>
      <LogonType>S4U</LogonType>
      <RunLevel>HighestAvailable</RunLevel>
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
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <DisallowStartOnRemoteAppSession>false</DisallowStartOnRemoteAppSession>
    <UseUnifiedSchedulingEngine>true</UseUnifiedSchedulingEngine>
    <WakeToRun>true</WakeToRun>
    <ExecutionTimeLimit>PT2H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>cmd.exe</Command>
      <Arguments>/c "{script_path}"</Arguments>
      <WorkingDirectory>{work_dir}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>"""
    
    return xml_content

def setup_task_scheduler():
    """Configura a tarefa no Windows Task Scheduler"""
    
    print("=" * 60)
    print("CONFIGURAÇÃO DO TASK SCHEDULER - SISTEMA IMPÉRIO")
    print("=" * 60)
    
    # Obter informações do sistema
    current_dir = Path.cwd()
    script_path = current_dir / "start_scheduler.bat"
    
    if not script_path.exists():
        print(f"❌ ERRO: Script {script_path} não encontrado!")
        print("Execute este script no diretório do sistema.")
        return False
    
    # Obter usuário atual
    try:
        result = subprocess.run(["whoami"], capture_output=True, text=True, shell=True)
        user_account = result.stdout.strip()
    except:
        user_account = os.environ.get("USERNAME", "SYSTEM")
    
    print(f"📁 Diretório: {current_dir}")
    print(f"📄 Script: {script_path}")
    print(f"👤 Usuário: {user_account}")
    print()
    
    # Nome da tarefa
    task_name = "SistemaImperio_ColetaDiaria"
    
    # Criar XML temporário
    xml_path = current_dir / "task_config.xml"
    xml_content = create_task_xml(task_name, str(script_path), str(current_dir), user_account)
    
    with open(xml_path, "w", encoding="utf-16") as f:
        f.write(xml_content)
    
    print("📝 Criando tarefa agendada...")
    
    # Deletar tarefa existente se houver
    subprocess.run(
        f'schtasks /delete /tn "{task_name}" /f',
        shell=True,
        capture_output=True
    )
    
    # Criar nova tarefa
    cmd = f'schtasks /create /xml "{xml_path}" /tn "{task_name}"'
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Tarefa criada com sucesso!")
        print()
        print("📅 AGENDAMENTO CONFIGURADO:")
        print("   - Execução: Diariamente às 06:00")
        print("   - Script: start_scheduler.bat")
        print("   - Modo: Execução em background (sem janela)")
        print()
        
        # Verificar status da tarefa
        print("📊 Verificando status da tarefa...")
        result = subprocess.run(
            f'schtasks /query /tn "{task_name}" /fo LIST',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if "Ready" in result.stdout or "Pronto" in result.stdout:
            print("✅ Tarefa está ATIVA e pronta para execução")
        else:
            print("⚠️ Verifique o status da tarefa no Agendador de Tarefas")
        
        print()
        print("🔧 COMANDOS ÚTEIS:")
        print(f'   Testar agora: schtasks /run /tn "{task_name}"')
        print(f'   Ver status:   schtasks /query /tn "{task_name}"')
        print(f'   Desativar:    schtasks /change /tn "{task_name}" /disable')
        print(f'   Reativar:     schtasks /change /tn "{task_name}" /enable')
        print(f'   Deletar:      schtasks /delete /tn "{task_name}" /f')
        
    else:
        print("❌ Erro ao criar tarefa:")
        print(result.stderr)
        return False
    
    # Limpar XML temporário
    try:
        xml_path.unlink()
    except:
        pass
    
    return True

def test_execution():
    """Testa a execução imediata da tarefa"""
    task_name = "SistemaImperio_ColetaDiaria"
    
    print()
    print("🧪 TESTE DE EXECUÇÃO")
    print("=" * 40)
    
    response = input("Deseja executar a tarefa agora para teste? (s/n): ")
    if response.lower() == 's':
        print("Executando tarefa...")
        result = subprocess.run(
            f'schtasks /run /tn "{task_name}"',
            shell=True,
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Tarefa iniciada com sucesso!")
            print("Verifique os logs em: data/logs/scheduler.log")
        else:
            print("❌ Erro ao executar tarefa:")
            print(result.stderr)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configurar Task Scheduler para Sistema Imperio")
    parser.add_argument("--test", action="store_true", help="Executar teste após configuração")
    args = parser.parse_args()
    
    success = setup_task_scheduler()
    
    if success and args.test:
        test_execution()
    
    print()
    input("Pressione ENTER para sair...")