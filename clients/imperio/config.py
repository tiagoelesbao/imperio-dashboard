"""
Configuração específica do cliente Império
"""
import os
from typing import Dict, Any

# Configurações do cliente
IMPERIO_CONFIG = {
    "name": "imperio",
    "title": "Império Prêmios",
    "product_id": "6916292bf6051e4133d86ef9",
    "campaign_name": "Sorteio Principal",
    "roi_goal": 2.0,
    "daily_budget": 10000.0,
    
    # Configurações de canais
    "channels": {
        "geral": {
            "name": "Geral",
            "description": "Dados consolidados de todos os canais"
        },
        "instagram": {
            "name": "Instagram",
            "description": "Performance do canal Instagram",
            "facebook_accounts": [
                "act_2067257390316380",
                "act_1391112848236399",
                "act_406219475582745",
                "act_790223756353632",
                "act_303402486183447"
            ]
        },
        "grupos": {
            "name": "Grupos",
            "description": "Performance dos grupos WhatsApp/Telegram",
            "facebook_accounts": [
                "act_772777644802886"
            ]
        }
    },
    
    # Configurações de afiliados
    "affiliates": {
        "instagram": "L8UTEDVTI0",
        "grupos_1": "17QB25AKRL", 
        "grupos_2": "30CS8W9DP1"
    },
    
    # Configurações do Google Sheets
    "google_sheets": {
        "key": "1jlhjqvDFJ28vA_fjTm4OwjoGhhPY-ljFhoa0aomK-so",
        "credentials_path": "data/credentials/credenciais_google.json"
    },
    
    # Configurações de coleta
    "collection": {
        "interval_minutes": 30,
        "retry_attempts": 3,
        "timeout_seconds": 30
    }
}

def get_config() -> Dict[str, Any]:
    """Retorna configuração do cliente Império"""
    return IMPERIO_CONFIG