"""Estado global do simulador: clima atual, bateria, histórico."""

from colonia.constantes import (
    BATERIA_CAPACIDADE_KWH, BATERIA_CARGA_INICIAL_KWH, BATERIA_RESERVA_EMERGENCIA_FRACAO,
)


def estado_inicial():
    """Cria estado novo da colônia (clima, bateria, histórico vazios)."""
    clima = {
        "sol": 0, "hora": 0,
        "vento_ms": 0.0,
        "tempestade": "limpo",
        "tau": 0.5,
        "temperatura_c": -60.0,
        "fator_paineis": 1.0,
    }
    bateria = {
        "carga_atual_kwh": BATERIA_CARGA_INICIAL_KWH,
        "capacidade_max_kwh": BATERIA_CAPACIDADE_KWH,
        "reserva_emergencia_kwh": BATERIA_CAPACIDADE_KWH * BATERIA_RESERVA_EMERGENCIA_FRACAO,
    }
    historico = {
        "vento_ms": [], "temperatura_c": [], "tempestade": [], "tau": [],
        "geracao_solar_kw": [], "geracao_eolica_kw": [], "geracao_nuclear_kw": [],
        "geracao_total_kw": [], "consumo_total_kw": [],
        "bateria_carga_kwh": [], "modos_resumo": [], "alertas": [],
    }
    return clima, bateria, historico
