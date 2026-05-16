"""Política de alocação de energia (load shedding em 4 etapas).

Percorre a árvore de criticidade e define o modo de cada módulo conforme
a oferta de energia disponível. Geradores ficam sempre em 'adequado'
(consumo próprio pequeno, geração definida pela física, não pela política).

Etapa 1: tenta todos em 'adequado'; se cabe, distribui excedente.
Etapa 2: rebaixa Expansão → Sustento → Vital para 'mínimo', bottom-up.
Etapa 3: desliga Expansão → Sustento (Vital nunca).
Etapa 4: emergência — alerta crítico (a reserva da bateria é gerenciada
fora desta função, em estado.py / simulador.py).
"""

from colonia.consumo import consumo_aquecimento_kw


GERADORES = ("gerador_solar", "gerador_eolico", "gerador_nuclear")


def _consumo_no_modo(modulo, modo, clima):
    """Consumo do módulo SE estivesse no modo dado (não altera modo_atual)."""
    base = modulo["consumo_por_modo"][modo]
    extra = consumo_aquecimento_kw(clima["temperatura_c"], modulo["fator_termico"])
    return base + extra


def _folhas_por_nivel(arvore):
    """Devolve (consumidores_por_nivel, geradores)."""
    niveis = {}
    geradores = []
    for filho_nivel in arvore.filhos:
        consumidores = []
        for m in filho_nivel.folhas():
            (geradores if m["tipo"] in GERADORES else consumidores).append(m)
        # ordena por id (menor = mais prioritário) para tie-breaker consistente
        consumidores.sort(key=lambda m: m["id"])
        niveis[filho_nivel.nome] = consumidores
    return niveis, geradores


def alocar_energia(arvore_criticidade, oferta_kw, clima):
    """Aplica política de 4 etapas. Mutaciona modulo['modo_atual'] in-place.

    Geradores não são rebaixados pela política (modo fixo 'adequado'), mas seu
    consumo próprio ENTRA no cálculo de custo — caso contrário a política
    sub-estimaria a demanda e violaria a oferta silenciosamente.
    """
    niveis, geradores = _folhas_por_nivel(arvore_criticidade)
    todos = niveis["Vital"] + niveis["Sustento"] + niveis["Expansão"]

    # Etapa 1: tudo em adequado
    for m in todos:
        m["modo_atual"] = "adequado"
    custo_consumidores = sum(_consumo_no_modo(m, "adequado", clima) for m in todos)
    custo_geradores_fixo = sum(_consumo_no_modo(m, "adequado", clima) for m in geradores)
    custo = custo_consumidores + custo_geradores_fixo

    if custo <= oferta_kw:
        # distribui excedente para escalonáveis (ordem por id menor primeiro)
        sobra = oferta_kw - custo
        for m in sorted([x for x in todos if x["escalona_com_excedente"]], key=lambda x: x["id"]):
            delta = _consumo_no_modo(m, "excedente", clima) - _consumo_no_modo(m, "adequado", clima)
            if sobra >= delta:
                m["modo_atual"] = "excedente"
                sobra -= delta
        return

    # Etapa 2: rebaixa bottom-up
    for nivel_nome in ("Expansão", "Sustento", "Vital"):
        for m in reversed(niveis[nivel_nome]):  # menor prioridade primeiro = maior id primeiro
            if custo <= oferta_kw:
                return
            antes = _consumo_no_modo(m, m["modo_atual"], clima)
            m["modo_atual"] = "minimo"
            depois = _consumo_no_modo(m, "minimo", clima)
            custo -= (antes - depois)

    if custo <= oferta_kw:
        return

    # Etapa 3: desliga bottom-up (Vital nunca)
    for nivel_nome in ("Expansão", "Sustento"):
        for m in reversed(niveis[nivel_nome]):
            if custo <= oferta_kw:
                return
            antes = _consumo_no_modo(m, m["modo_atual"], clima)
            m["modo_atual"] = "desligado"
            depois = _consumo_no_modo(m, "desligado", clima)
            custo -= (antes - depois)

    # Etapa 4: emergência — Vital permanece em 'minimo' mesmo com saldo negativo.
    # O alerta é emitido pelo simulador comparando consumo_total vs oferta após esta chamada.
