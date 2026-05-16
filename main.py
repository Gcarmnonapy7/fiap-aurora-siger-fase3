"""Entry point do simulador da colônia Aurora Siger.

Executa 1 semana marciana (168 horas) e imprime um resumo do histórico.
Uso:
    python main.py
"""

import random

from colonia.hierarquias import construir_arvore_funcional, construir_arvore_criticidade
from colonia.simulador import rodar_simulacao


def main(seed=42):
    random.seed(seed)
    print("Aurora Siger — Simulação de 7 sóis marcianos\n")

    print("Árvore funcional dos subsistemas:")
    print(construir_arvore_funcional().imprimir())
    print()

    print("Árvore de criticidade dos subsistemas:")
    print(construir_arvore_criticidade().imprimir())
    print()

    _, bateria_final, historico = rodar_simulacao()

    print(f"Passos simulados: {len(historico['vento_ms'])}")
    print(f"Geração total média: {sum(historico['geracao_total_kw'])/len(historico['geracao_total_kw']):.1f} kW")
    print(f"Consumo total médio: {sum(historico['consumo_total_kw'])/len(historico['consumo_total_kw']):.1f} kW")
    print(f"Bateria final: {bateria_final['carga_atual_kwh']:.1f} / {bateria_final['capacidade_max_kwh']:.1f} kWh")
    tempestades = [t for t in historico["tempestade"] if t != "limpo"]
    print(f"Passos com tempestade: {len(tempestades)} de {len(historico['tempestade'])}")

    alertas_totais = sum(1 for a in historico["alertas"] if a)
    print(f"Passos com alerta: {alertas_totais}")


if __name__ == "__main__":
    main()
