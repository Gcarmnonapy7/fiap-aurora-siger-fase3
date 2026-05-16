"""Parâmetros físicos e operacionais do simulador.

Valores derivados de literatura científica — ver Seção 6 do spec
em docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md
"""

import math

# Horizonte da simulação
HORIZONTE_SOLS = 7
HORAS_POR_SOL = 24
TOTAL_PASSOS = HORIZONTE_SOLS * HORAS_POR_SOL  # 168

# --- Vento ---
V_BASE = 2.5
V_AMPLITUDE = 7.0
FATOR_SAZONAL = 1.2  # perihélio
V_RUIDO_SIGMA = 1.5

# --- Tempestades de poeira ---
ESTADOS_TEMPESTADE = ("limpo", "leve", "moderada", "grave")

PROB_BASE_POR_SOL = {
    "leve":     0.40,
    "moderada": 0.04,
    "grave":    0.002,
}

DURACAO_HORAS = {
    "leve":     (12, 72),
    "moderada": (72, 168),
    "grave":    (168, 720),
}

LIMIAR_VENTO_BONUS = 15.0  # m/s acima disso aumenta prob de tempestade
FATOR_PERIHELIO = 1.5

FORCAR_EVENTO_DIDATICO = True
SOL_EVENTO_DIDATICO = 3
HORA_EVENTO_DIDATICO = 8

# --- Opacidade atmosférica (tau) ---
TAU_BASE = {
    "limpo":    0.5,
    "leve":     1.5,
    "moderada": 3.0,
    "grave":    8.0,
}
TAU_VENTO_FATOR = 0.05  # tau extra por m/s acima de 5 m/s
TAU_VENTO_LIMIAR = 5.0

# --- Painéis solares ---
PERDA_PAINEIS_POR_SOL = 0.002        # 0.2% por sol
PROB_LIMPEZA_POR_SOL = 0.005         # ~1 evento a cada 200 sols
LIMPEZA_RECUPERACAO = (0.30, 0.70)   # range de recuperação por dust devil
PISO_FATOR_PAINEIS = 0.30            # piso por limpeza manual humana

# --- Temperatura ---
T_MEDIA = -60.0
A_DIURNA = 35.0
A_SAZONAL = 18.0
PHI_DIURNO = 9  # pico ~15h local
SOLS_POR_ANO_MARCIANO = 668
T_RUIDO_SIGMA = 2.0

# --- Consumo térmico (Q = U·A·ΔT) ---
A_ENVELOPE = 250.0          # m²
U_ISOLAMENTO = 0.15         # W/m²·K
T_ALVO_INTERNA = 20.0       # °C
GANHO_INTERNO_W = 4000.0    # W
ETA_AQUECEDOR = 0.95

# --- Bateria ---
BATERIA_CAPACIDADE_KWH = 500.0
BATERIA_CARGA_INICIAL_KWH = 250.0
BATERIA_RESERVA_EMERGENCIA_FRACAO = 0.20  # 20% intocável

# --- Curva solar ---
def curva_diurna_solar(hora):
    """Fração de irradiância em função da hora (0 a 1, formato sino entre 06–18h)."""
    return max(0.0, math.sin(math.pi * (hora - 6) / 12))
