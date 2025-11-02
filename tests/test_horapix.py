#!/usr/bin/env python3
"""
Script de teste do coletor Hora do Pix
"""
import sys
import os
import json
from datetime import datetime

# Adicionar path do projeto
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from core.services.horapix_collector import horapix_collector


def test_collector():
    """Testar o coletor de dados"""
    print("=" * 80)
    print("TESTANDO COLETOR HORA DO PIX")
    print("=" * 80)
    print()

    # Testar coleta simples (sem detalhes)
    print("[1] Testando coleta básica (sem detalhes)...")
    print("-" * 80)

    result = horapix_collector.collect_all_data(fetch_details=False)

    if result.get('success'):
        print("✅ Coleta bem-sucedida!")
        print()

        data = result.get('data', {})
        totals = data.get('totals', {})
        draws = data.get('draws', [])
        active = data.get('active_draws', [])
        finished = data.get('finished_draws', [])

        print("TOTAIS:")
        print(f"  Total de sorteios: {totals.get('total_draws', 0)}")
        print(f"  Sorteios ativos: {totals.get('active_draws', 0)}")
        print(f"  Sorteios finalizados: {totals.get('finished_draws', 0)}")
        print(f"  Valor total em prêmios: R$ {totals.get('total_prize_value', 0):,.2f}")
        print(f"  Receita total: R$ {totals.get('total_revenue', 0):,.2f}")
        print(f"  Lucro total: R$ {totals.get('total_profit', 0):,.2f}")
        print(f"  ROI total: {totals.get('total_roi', 0):.2f}%")
        print()

        if draws:
            print("PRIMEIROS 3 SORTEIOS:")
            for i, draw in enumerate(draws[:3], 1):
                print(f"\n  [{i}] {draw.get('title', 'Sem título')[:60]}")
                print(f"      ID: {draw.get('id', 'N/A')}")
                print(f"      Status: {draw.get('status', 'N/A')}")
                print(f"      Prêmio: R$ {draw.get('prize_value', 0):,.2f}")
                print(f"      Preço: R$ {draw.get('price', 0):.2f}")
                print(f"      Vendidos: {draw.get('qty_paid', 0)}/{draw.get('qty_total', 0)}")
                print(f"      Receita: R$ {draw.get('revenue', 0):,.2f}")
                print(f"      Lucro: R$ {draw.get('profit', 0):,.2f}")
                print(f"      ROI: {draw.get('roi', 0):.2f}%")

        print()
        print("=" * 80)

        # Salvar dados completos em arquivo JSON para análise
        output_file = f"test_horapix_output_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

        print(f"✅ Dados completos salvos em: {output_file}")
        print()

        return True

    else:
        print("❌ Erro na coleta!")
        print(f"Erro: {result.get('error', 'Desconhecido')}")
        return False


def test_single_draw():
    """Testar busca de detalhes de um sorteio"""
    print()
    print("=" * 80)
    print("[2] Testando busca de detalhes de sorteio específico...")
    print("-" * 80)

    # Primeiro pegar um ID
    result = horapix_collector.collect_all_data(fetch_details=False)

    if result.get('success'):
        draws = result.get('data', {}).get('draws', [])
        if draws:
            first_draw_id = draws[0].get('id')
            print(f"Testando com sorteio ID: {first_draw_id}")
            print()

            details = horapix_collector.fetch_product_details(first_draw_id)

            if details:
                print("✅ Detalhes obtidos com sucesso!")
                print()

                product = details.get('product', {})
                paid = details.get('paid', {})

                print(f"Título: {product.get('title', 'N/A')}")
                print(f"Status: {product.get('status', 'N/A')}")
                print()
                print("MÉTRICAS DE VENDA:")
                print(f"  Participantes: {details.get('participantes', 0)}")
                print(f"  Total pago: R$ {paid.get('total', 0)}")
                print(f"  Quantidade: {paid.get('qty', 0)}")
                print(f"  Ticket médio: R$ {paid.get('ticketMedio', 0)}")
                print()

                top_buyers = details.get('top10Compradores', [])[:3]
                if top_buyers:
                    print("TOP 3 COMPRADORES:")
                    for i, buyer in enumerate(top_buyers, 1):
                        user = buyer.get('user', {})
                        print(f"  {i}. {user.get('name', 'N/A')}")
                        print(f"     Quantidade: {buyer.get('quantity', 0)}")
                        print(f"     Total: R$ {buyer.get('total', 0):.2f}")

                print()
                return True
            else:
                print("❌ Não foi possível obter detalhes")
                return False
        else:
            print("❌ Nenhum sorteio encontrado para testar")
            return False
    else:
        print("❌ Erro na coleta inicial")
        return False


if __name__ == "__main__":
    print()
    print("SISTEMA HORA DO PIX - TESTE DE COLETA")
    print()

    # Teste 1: Coleta básica
    test1_ok = test_collector()

    # Teste 2: Detalhes de sorteio
    test2_ok = test_single_draw()

    print()
    print("=" * 80)
    print("RESUMO DOS TESTES")
    print("=" * 80)
    print(f"[1] Coleta básica: {'✅ OK' if test1_ok else '❌ FALHOU'}")
    print(f"[2] Detalhes de sorteio: {'✅ OK' if test2_ok else '❌ FALHOU'}")
    print()

    if test1_ok and test2_ok:
        print("✅ TODOS OS TESTES PASSARAM!")
        print()
        print("Próximos passos:")
        print("1. Criar interface HTML")
        print("2. Adicionar aba no menu")
        print("3. Criar JavaScript para visualização")
    else:
        print("❌ ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima antes de continuar")

    print()
