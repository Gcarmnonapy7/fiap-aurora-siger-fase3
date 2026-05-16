"""Modelo climático realista da colônia Aurora Siger.

Baseado em literatura NASA/ESA (vide spec, seção 6).
Vento: ciclo diurno + ruído gaussiano + modulação sazonal.
Temperatura: ciclo diurno senoidal + variação sazonal + ruído.
Tempestades: máquina de estados (limpo → leve/moderada/grave).
Painéis: deposição contínua + limpeza estocástica (dust devils).
"""

import math
import random

from colonia.constantes import (
    V_BASE, V_AMPLITUDE, FATOR_SAZONAL, V_RUIDO_SIGMA,
    T_MEDIA, A_DIURNA, A_SAZONAL, PHI_DIURNO, T_RUIDO_SIGMA,
    SOLS_POR_ANO_MARCIANO,
)


def amostrar_vento(hora):
    """Devolve velocidade do vento em m/s para a hora local dada (0–23)."""
    componente_diurno = V_AMPLITUDE * max(0.0, math.sin(math.pi * (hora - 6) / 12))
    ruido = random.gauss(0, V_RUIDO_SIGMA)
    return max(0.0, (V_BASE + componente_diurno) * FATOR_SAZONAL + ruido)


def amostrar_temperatura(sol, hora):
    """Devolve temperatura em °C para o sol e hora dados."""
    diurno = A_DIURNA * math.sin(2 * math.pi * (hora - PHI_DIURNO) / 24)
    sazonal = A_SAZONAL * math.sin(2 * math.pi * sol / SOLS_POR_ANO_MARCIANO)
    ruido = random.gauss(0, T_RUIDO_SIGMA)
    return T_MEDIA + diurno + sazonal + ruido
