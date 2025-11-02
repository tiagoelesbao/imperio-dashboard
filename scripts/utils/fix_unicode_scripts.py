#!/usr/bin/env python3
"""
Script para remover emojis e caracteres Unicode problemáticos
"""

import re
import os

def remove_emojis_from_file(file_path):
    """Remover emojis de um arquivo"""
    print(f"Processando: {file_path}")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Backup original
        backup_path = file_path + '.backup'
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Mapeamento de emojis para texto
        emoji_replacements = {
            '🧪': 'TESTE',
            '🔍': 'DIAGNOSTICO',
            '✅': 'OK',
            '❌': 'ERRO',
            '⚠️': 'AVISO',
            '🐍': 'Python',
            '📁': 'Arquivo',
            '📂': 'Diretorio',
            '📦': 'Pacote',
            '🔧': 'Config',
            '🚀': 'Executando',
            '📥': 'Download',
            '⚙️': 'Configurando',
            '🎉': 'SUCESSO',
            '💡': 'Dica',
            '🌐': 'Web',
        }
        
        # Substituir emojis conhecidos
        for emoji, replacement in emoji_replacements.items():
            content = content.replace(emoji, replacement)
        
        # Remover outros emojis Unicode usando regex
        # Remove emojis na faixa U+1F600-U+1F64F (emoticons)
        # Remove emojis na faixa U+1F300-U+1F5FF (misc symbols)
        # Remove emojis na faixa U+1F680-U+1F6FF (transport and map)
        # Remove emojis na faixa U+1F1E0-U+1F1FF (flags)
        emoji_pattern = re.compile("["
                                   u"\U0001F600-\U0001F64F"  # emoticons
                                   u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                                   u"\U0001F680-\U0001F6FF"  # transport & map symbols
                                   u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                                   u"\U00002702-\U000027B0"
                                   u"\U000024C2-\U0001F251"
                                   "]+", flags=re.UNICODE)
        
        content = emoji_pattern.sub('', content)
        
        # Escrever arquivo corrigido
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"   OK - Corrigido")
        return True
        
    except Exception as e:
        print(f"   ERRO: {e}")
        return False

def main():
    """Função principal"""
    print("REMOVENDO EMOJIS DOS SCRIPTS DE TESTE")
    print("=" * 50)
    
    files_to_fix = [
        'test_env_debug.py',
        'test_basic_debug.py',
        'test_simple_capture.py'
    ]
    
    for file_name in files_to_fix:
        if os.path.exists(file_name):
            remove_emojis_from_file(file_name)
        else:
            print(f"Arquivo nao encontrado: {file_name}")
    
    print("\n" + "=" * 50)
    print("CORRECAO CONCLUIDA!")

if __name__ == "__main__":
    main()