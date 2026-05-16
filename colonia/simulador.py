"""Orquestrador do simulador: 1 passo + horizonte completo de 168 passos."""

import random
from collections import deque

from colonia.alocacao import alocar_energia
from colonia.clima import (
    amostrar_vento, amostrar_temperatura, calcular_tau,
    atualizar_fator_paineis, EstadoTempestade,
)
from colonia.consumo import consumo_atual_kw
from colonia.constantes import (
    HORIZONTE_SOLS, HORAS_POR_SOL, TOTAL_PASSOS,
    PROB_LIMPEZA_POR_SOL, FORCAR_EVENTO_DIDATICO,
)
from colonia.estado import estado_inicial
from colonia.geracao import gerar_solar, gerar_eolico, gerar_nuclear
from colonia.hierarquias import construir_arvore_funcional, construir_arvore_criticidade
from colonia.modulos import MODULOS


def _detalhar_geracao(arvore_funcional, clima):
    """Devolve dict {tipo: kW} para registro no histórico."""
    energia = arvore_funcional.buscar("Energia")
    detalhe = {"solar": 0.0, "eolico": 0.0, "nuclear": 0.0}
    for no in energia.percorrer_dfs():
        if not no.eh_folha():
            continue
        m = no.modulo
        if m["tipo"] == "gerador_solar":
            detalhe["solar"] += gerar_solar(m, clima)
        elif m["tipo"] == "gerador_eolico":
            detalhe["eolico"] += gerar_eolico(m, clima)
        elif m["tipo"] == "gerador_nuclear":
            detalhe["nuclear"] += gerar_nuclear(m, clima)
    return detalhe


def passo(clima, bateria, historico, arvores, tempestade_state, ultimo_vento_24h):
    """Avança a simulação em 1 hora. Mutaciona clima/bateria/historico/MODULOS in-place."""
    funcional, criticidade = arvores
    sol = clima["sol"]
    hora = clima["hora"]

    # 1. Amostrar clima
    vento = amostrar_vento(hora)
    temperatura = amostrar_temperatura(sol, hora)
    ultimo_vento_24h.append(vento)
    vento_max_24h = max(ultimo_vento_24h)

    tempestade_state.avancar(vento_max_24h, sol, hora, forcar_evento=FORCAR_EVENTO_DIDATICO)
    tau = calcular_tau(tempestade_state.estado, vento)

    # Atualizar painéis (uma vez por sol, na hora 0)
    if hora == 0:
        sorteio_limpeza = random.random() < PROB_LIMPEZA_POR_SOL
        clima["fator_paineis"] = atualizar_fator_paineis(clima["fator_paineis"], sorteio_limpeza)

    clima["vento_ms"] = vento
    clima["temperatura_c"] = temperatura
    clima["tempestade"] = tempestade_state.estado
    clima["tau"] = tau

    # 2. Geração
    detalhe = _detalhar_geracao(funcional, clima)
    soma_geracao = detalhe["solar"] + detalhe["eolico"] + detalhe["nuclear"]

    # 3. Oferta (geração + bateria disponível acima da reserva)
    bateria_disponivel = max(0, bateria["carga_atual_kwh"] - bateria["reserva_emergencia_kwh"])
    oferta = soma_geracao + bateria_disponivel

    # 4. Alocação
    alocar_energia(criticidade, oferta_kw=oferta, clima=clima)

    # 5. Consumo total
    consumo_total = sum(consumo_atual_kw(m, clima) for m in MODULOS)

    # 6. Balanço bateria
    saldo = soma_geracao - consumo_total
    bateria["carga_atual_kwh"] = max(0, min(
        bateria["capacidade_max_kwh"],
        bateria["carga_atual_kwh"] + saldo,
    ))

    # 7. Alerta de emergência
    alertas = []
    if consumo_total > soma_geracao + bateria_disponivel:
        alertas.append(f"EMERGÊNCIA sol {sol} hora {hora}: oferta insuficiente")

    # 8. Registrar histórico
    historico["vento_ms"].append(vento)
    historico["temperatura_c"].append(temperatura)
    historico["tempestade"].append(tempestade_state.estado)
    historico["tau"].append(tau)
    historico["geracao_solar_kw"].append(detalhe["solar"])
    historico["geracao_eolica_kw"].append(detalhe["eolico"])
    historico["geracao_nuclear_kw"].append(detalhe["nuclear"])
    historico["geracao_total_kw"].append(soma_geracao)
    historico["consumo_total_kw"].append(consumo_total)
    historico["bateria_carga_kwh"].append(bateria["carga_atual_kwh"])
    historico["modos_resumo"].append({m["nome"]: m["modo_atual"] for m in MODULOS})
    historico["alertas"].append(alertas)

    # 9. Avançar relógio
    clima["hora"] += 1
    if clima["hora"] >= HORAS_POR_SOL:
        clima["hora"] = 0
        clima["sol"] += 1


def rodar_simulacao():
    """Roda os 168 passos do simulador e devolve (clima_final, bateria_final, historico)."""
    clima, bateria, historico = estado_inicial()
    arvores = (construir_arvore_funcional(), construir_arvore_criticidade())
    tempestade_state = EstadoTempestade()
    ultimo_vento_24h = deque(maxlen=24)

    for _ in range(TOTAL_PASSOS):
        passo(clima, bateria, historico, arvores, tempestade_state, ultimo_vento_24h)

    return clima, bateria, historico
