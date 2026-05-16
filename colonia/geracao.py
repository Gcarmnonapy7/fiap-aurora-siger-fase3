"""Funções de geração de energia das três fontes da colônia."""

from colonia.clima import transmissao_solar
from colonia.constantes import curva_diurna_solar


def gerar_solar(modulo, clima):
    """Potência solar (kW): capacidade × curva_diurna × transmissao × fator_paineis."""
    curva = curva_diurna_solar(clima["hora"])
    transm = transmissao_solar(clima["tau"])
    return modulo["capacidade_max_kw"] * curva * transm * clima["fator_paineis"]


def gerar_eolico(modulo, clima):
    """Potência eólica (kW): modelo linear com cut-in (3 m/s) e saturação na capacidade.

    Forma: P = max(0, min(capacidade, A*v - B))
    Com A=2.5 e B=7.5: P(3)=0, P(10)=17.5, satura em v ≈ 15 m/s.
    """
    A_LINEAR = 2.5
    B_LINEAR = 7.5
    v = clima["vento_ms"]
    potencia = A_LINEAR * v - B_LINEAR
    return max(0.0, min(modulo["capacidade_max_kw"], potencia))


def gerar_nuclear(modulo, clima):
    """Potência nuclear (kW): baseload constante na capacidade nominal."""
    return modulo["capacidade_max_kw"]
