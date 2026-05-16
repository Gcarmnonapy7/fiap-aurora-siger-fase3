"""Lista plana dos 13 módulos da colônia Aurora Siger.

Os 12 primeiros mantêm a identidade da Fase 2 (mesmos nomes e prioridades).
O 13º — Energia Eólica — é acréscimo da Fase 3, justificado pelo item 1.3
do enunciado que pede regressão linear sobre dados de vento e energia eólica.
"""

MODULOS = [
    {
        "id": 1, "nome": "Comando e Controle", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 8, "excedente": 8},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 2, "nome": "Suporte de Vida (ECLSS)", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 4, "adequado": 12, "excedente": 12},
        "escalona_com_excedente": False,
        "fator_termico": 0.4,
        "modo_atual": "adequado",
    },
    {
        "id": 3, "nome": "Habitação", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 5, "adequado": 15, "excedente": 15},
        "escalona_com_excedente": False,
        "fator_termico": 1.0,
        "modo_atual": "adequado",
    },
    {
        "id": 4, "nome": "Energia Solar", "tipo": "gerador_solar",
        "capacidade_max_kw": 100.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 0.5, "adequado": 1, "excedente": 1},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 5, "nome": "Energia Nuclear", "tipo": "gerador_nuclear",
        "capacidade_max_kw": 80.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 3, "excedente": 3},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 6, "nome": "Comunicações", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 5, "excedente": 5},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 7, "nome": "Suporte Médico", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 6, "excedente": 6},
        "escalona_com_excedente": False,
        "fator_termico": 0.2,
        "modo_atual": "adequado",
    },
    {
        "id": 8, "nome": "Produção de Alimentos", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 3, "adequado": 10, "excedente": 18},
        "escalona_com_excedente": True,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 9, "nome": "Logística e Armazenamento", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 4, "excedente": 4},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 10, "nome": "ISRU (Recursos Locais)", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 8, "excedente": 20},
        "escalona_com_excedente": True,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 11, "nome": "Oficina e Manutenção", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 0.5, "adequado": 3, "excedente": 3},
        "escalona_com_excedente": False,
        "fator_termico": 0.2,
        "modo_atual": "desligado",
    },
    {
        "id": 12, "nome": "Laboratório Científico", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 5, "excedente": 12},
        "escalona_com_excedente": True,
        "fator_termico": 0.2,
        "modo_atual": "adequado",
    },
    {
        "id": 13, "nome": "Energia Eólica", "tipo": "gerador_eolico",
        "capacidade_max_kw": 30.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 0.3, "adequado": 0.5, "excedente": 0.5},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
]


def encontrar_modulo(id_):
    """Devolve o módulo com o id fornecido. Levanta KeyError se não existir."""
    for m in MODULOS:
        if m["id"] == id_:
            return m
    raise KeyError(f"Módulo com id={id_} não encontrado")
