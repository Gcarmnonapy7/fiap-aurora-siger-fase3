"""Cálculo de consumo dos módulos.

Combina consumo base (por modo de operação) com termo térmico
(Q = U·A·ΔT) para módulos pressurizados. O termo térmico é
adicionado mesmo se o módulo está em modo 'desligado', porque
habitats pressurizados não podem ser deixados congelar.
"""

from colonia.constantes import (
    A_ENVELOPE, U_ISOLAMENTO, T_ALVO_INTERNA, GANHO_INTERNO_W, ETA_AQUECEDOR,
)


def consumo_aquecimento_kw(temperatura_externa, fator_termico):
    """Potência elétrica gasta em aquecimento (kW).

    fator_termico atua como 'tamanho relativo' do módulo: escala
    tanto a perda pelo envelope (área menor → perde menos) quanto
    o ganho interno (menos pessoas/equipamentos → menos calor de graça).

    Q_perda    = U * A_envelope * ΔT * fator_termico
    Q_ganho    = GANHO_INTERNO_W * fator_termico
    Q_liquido  = max(0, Q_perda - Q_ganho)
    Q_eletrico = Q_liquido / eta_aquecedor
    """
    if fator_termico == 0:
        return 0
    delta_t = max(0, T_ALVO_INTERNA - temperatura_externa)
    perda_W = U_ISOLAMENTO * A_ENVELOPE * delta_t * fator_termico
    liquido_W = max(0, perda_W - GANHO_INTERNO_W * fator_termico)
    return liquido_W / ETA_AQUECEDOR / 1000.0


def consumo_atual_kw(modulo, clima):
    """Consumo total do módulo neste instante (kW)."""
    base = modulo["consumo_por_modo"][modulo["modo_atual"]]
    extra_termico = consumo_aquecimento_kw(clima["temperatura_c"], modulo["fator_termico"])
    return base + extra_termico
