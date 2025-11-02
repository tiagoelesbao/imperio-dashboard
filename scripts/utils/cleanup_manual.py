#!/usr/bin/env python3
"""
Limpeza Manual de Arquivos Temporários
Script independente para limpar todos os arquivos temporários do sistema
"""
import os
import shutil
import glob
import subprocess

def limpar_processos_chrome():
    """Finalizar processos ChromeDriver órfãos"""
    try:
        subprocess.run('taskkill /F /IM chromedriver.exe', shell=True, capture_output=True)
        print("✅ Processos ChromeDriver finalizados")
    except:
        print("⚠️ Não foi possível finalizar processos ChromeDriver")

def limpar_arquivos_temporarios():
    """Limpar todos os arquivos temporários do sistema"""
    print("\n🧹 LIMPEZA MANUAL DE ARQUIVOS TEMPORÁRIOS")
    print("=" * 50)
    
    cleaned_files = 0
    cleaned_folders = 0
    
    try:
        # 1. SCREENSHOTS
        screenshots_folder = "screenshots"
        if os.path.exists(screenshots_folder):
            screenshot_files = glob.glob(os.path.join(screenshots_folder, "*.png"))
            for file in screenshot_files:
                try:
                    os.remove(file)
                    cleaned_files += 1
                except:
                    pass
            if len(screenshot_files) > 0:
                print(f"✅ {len(screenshot_files)} screenshots removidos")
        
        # 2. LOGS
        logs_folder = os.path.join("data", "logs")
        if os.path.exists(logs_folder):
            log_files = glob.glob(os.path.join(logs_folder, "*.log"))
            log_files.extend(glob.glob(os.path.join(logs_folder, "*.json")))
            for file in log_files:
                try:
                    os.remove(file)
                    cleaned_files += 1
                except:
                    pass
            if len(log_files) > 0:
                print(f"✅ {len(log_files)} arquivos de log removidos")
        
        # 3. PERFIS TEMPORÁRIOS
        temp_profiles_folder = os.path.join("data", "temp_profiles")
        if os.path.exists(temp_profiles_folder):
            for item in os.listdir(temp_profiles_folder):
                if item.startswith("chrome_temp_"):
                    temp_path = os.path.join(temp_profiles_folder, item)
                    try:
                        shutil.rmtree(temp_path, ignore_errors=True)
                        cleaned_folders += 1
                    except:
                        pass
            if cleaned_folders > 0:
                print(f"✅ {cleaned_folders} perfis temporários removidos")
        
        # 4. CACHE E ARQUIVOS DIVERSOS
        cache_patterns = ["*.tmp", "*.cache", "chromedriver.log", "debug*.json"]
        for pattern in cache_patterns:
            files = glob.glob(pattern, recursive=True)
            for file in files:
                try:
                    os.remove(file)
                    cleaned_files += 1
                except:
                    pass
        
        # 5. BANCOS ANTIGOS (exceto o principal)
        db_files = glob.glob("*.db")
        for db_file in db_files:
            if "dashboard_roi.db" in db_file or "roi_dashboard.db" in db_file:
                continue
            try:
                os.remove(db_file)
                cleaned_files += 1
                print(f"✅ Banco antigo removido: {db_file}")
            except:
                pass
        
        print(f"\n🎯 LIMPEZA CONCLUÍDA:")
        print(f"   • {cleaned_files} arquivos removidos")
        print(f"   • {cleaned_folders} pastas removidas")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na limpeza: {e}")
        return False

def verificar_espaco_liberado():
    """Verificar quanto espaço foi liberado"""
    try:
        # Contar arquivos restantes
        remaining_files = 0
        
        # Screenshots
        if os.path.exists("screenshots"):
            remaining_files += len(glob.glob("screenshots/*.png"))
        
        # Logs
        if os.path.exists("data/logs"):
            remaining_files += len(glob.glob("data/logs/*.log"))
            remaining_files += len(glob.glob("data/logs/*.json"))
        
        # Temp profiles
        if os.path.exists("data/temp_profiles"):
            temp_dirs = [item for item in os.listdir("data/temp_profiles") if item.startswith("chrome_temp_")]
            remaining_files += len(temp_dirs)
        
        print(f"\n📊 ARQUIVOS TEMPORÁRIOS RESTANTES: {remaining_files}")
        
        if remaining_files == 0:
            print("🎉 SISTEMA COMPLETAMENTE LIMPO!")
        else:
            print("⚠️ Alguns arquivos podem não ter sido removidos")
            
    except Exception as e:
        print(f"Erro ao verificar espaço: {e}")

def main():
    """Executar limpeza manual completa"""
    print("=" * 60)
    print("🧹 LIMPEZA MANUAL - SISTEMA IMPÉRIO")
    print("=" * 60)
    print("Este script remove TODOS os arquivos temporários:")
    print("• Screenshots antigos")
    print("• Logs de execução") 
    print("• Perfis temporários do Chrome/Brave")
    print("• Arquivos de cache")
    print("• Processos ChromeDriver órfãos")
    print()
    
    resposta = input("Deseja continuar com a limpeza? (s/N): ").strip().lower()
    
    if resposta in ['s', 'sim', 'y', 'yes']:
        print("\n🚀 Iniciando limpeza...")
        
        # Finalizar processos
        limpar_processos_chrome()
        
        # Limpar arquivos
        if limpar_arquivos_temporarios():
            # Verificar resultado
            verificar_espaco_liberado()
            
            print("\n✨ LIMPEZA MANUAL CONCLUÍDA COM SUCESSO!")
            print("Agora você pode executar start_server.bat normalmente.")
        else:
            print("\n❌ Erro durante a limpeza")
    else:
        print("Limpeza cancelada.")
    
    print("\n" + "=" * 60)

if __name__ == "__main__":
    main()