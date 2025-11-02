#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Coletor de dados do Facebook Ads
"""
import logging
from typing import Dict, List
from datetime import date

logger = logging.getLogger(__name__)

class FacebookCollector:
    """Coletor de dados do Facebook Ads"""

    def get_facebook_costs_by_day(self, product_id: str, start_date: date, end_date: date) -> List[Dict]:
        """
        Retorna custos do Facebook por dia
        NOTA: Por enquanto retorna dados vazios
        """
        logger.info(f"Buscando custos Facebook para produto {product_id}")

        # Por enquanto retorna lista vazia
        # Os custos do Facebook são coletados pelo data_collector principal
        return []

# Instância global
facebook_collector = FacebookCollector()