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
    PROB_BASE_POR_SOL, DURACAO_HORAS, LIMIAR_VENTO_BONUS, FATOR_PERIHELIO,
    SOL_EVENTO_DIDATICO, HORA_EVENTO_DIDATICO,
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


class EstadoTempestade:
    """Máquina de estados para tempestades de poeira em Marte.

    Estados: 'limpo' → 'leve' / 'moderada' / 'grave'.
    Persistência temporal: uma vez iniciada, dura horas_restantes horas.
    """

    def __init__(self):
        self.estado = "limpo"
        self.horas_restantes = 0

    def _prob_inicio(self, classe, vento_max_24h, sol):
        prob = PROB_BASE_POR_SOL[classe]
        bonus_vento = max(0.0, (vento_max_24h - LIMIAR_VENTO_BONUS) / 10.0)
        # perihélio: aproximação simples — sols 0–6 são "perihélio" por construção
        bonus_periode = FATOR_PERIHELIO
        return prob * (1 + bonus_vento) * bonus_periode

    def avancar(self, vento_max_24h, sol, hora, forcar_evento=False):
        """Avança um passo (1 hora) na máquina de estados."""
        if forcar_evento and sol == SOL_EVENTO_DIDATICO and hora == HORA_EVENTO_DIDATICO and self.estado == "limpo":
            self.estado = "moderada"
            min_h, max_h = DURACAO_HORAS["moderada"]
            self.horas_restantes = random.randint(min_h, max_h)
            return

        if self.estado != "limpo":
            self.horas_restantes -= 1
            if self.horas_restantes <= 0:
                self.estado = "limpo"
                self.horas_restantes = 0
            return

        # estado atual = limpo: sorteia se uma nova tempestade inicia
        # uma sorteio por hora; prob por sol é dividida por 24 para virar prob por hora
        for classe in ("grave", "moderada", "leve"):  # mais raras primeiro
            prob_hora = self._prob_inicio(classe, vento_max_24h, sol) / 24.0
            if random.random() < prob_hora:
                self.estado = classe
                min_h, max_h = DURACAO_HORAS[classe]
                self.horas_restantes = random.randint(min_h, max_h)
                return
