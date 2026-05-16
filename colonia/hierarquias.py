"""Constrói as duas árvores N-árias sobre a lista plana de módulos.

Árvore funcional: agrupa por função (Energia, Suporte à Vida, Comando, Operações).
Árvore de criticidade: agrupa por nível (Vital, Sustento, Expansão).

As duas árvores compartilham referências aos mesmos dicts de módulo —
alterar `modulo["modo_atual"]` em uma se reflete na outra automaticamente.
"""

from colonia.arvore import No
from colonia.modulos import encontrar_modulo


def construir_arvore_funcional():
    raiz = No("Colônia Aurora Siger")

    energia = raiz.adicionar_filho(No("Energia"))
    energia.adicionar_filho(No("Energia Solar", modulo=encontrar_modulo(4)))
    energia.adicionar_filho(No("Energia Nuclear", modulo=encontrar_modulo(5)))
    energia.adicionar_filho(No("Energia Eólica", modulo=encontrar_modulo(13)))

    suporte_vida = raiz.adicionar_filho(No("Suporte à Vida"))
    suporte_vida.adicionar_filho(No("Suporte de Vida (ECLSS)", modulo=encontrar_modulo(2)))
    suporte_vida.adicionar_filho(No("Habitação", modulo=encontrar_modulo(3)))
    suporte_vida.adicionar_filho(No("Suporte Médico", modulo=encontrar_modulo(7)))
    suporte_vida.adicionar_filho(No("Produção de Alimentos", modulo=encontrar_modulo(8)))

    comando = raiz.adicionar_filho(No("Comando"))
    comando.adicionar_filho(No("Comando e Controle", modulo=encontrar_modulo(1)))
    comando.adicionar_filho(No("Comunicações", modulo=encontrar_modulo(6)))

    operacoes = raiz.adicionar_filho(No("Operações"))
    operacoes.adicionar_filho(No("Logística e Armazenamento", modulo=encontrar_modulo(9)))
    operacoes.adicionar_filho(No("ISRU (Recursos Locais)", modulo=encontrar_modulo(10)))
    operacoes.adicionar_filho(No("Oficina e Manutenção", modulo=encontrar_modulo(11)))
    operacoes.adicionar_filho(No("Laboratório Científico", modulo=encontrar_modulo(12)))

    return raiz


def construir_arvore_criticidade():
    raiz = No("Colônia Aurora Siger")

    vital = raiz.adicionar_filho(No("Vital"))
    vital.adicionar_filho(No("Comando e Controle", modulo=encontrar_modulo(1)))
    vital.adicionar_filho(No("Suporte de Vida (ECLSS)", modulo=encontrar_modulo(2)))
    vital.adicionar_filho(No("Suporte Médico", modulo=encontrar_modulo(7)))
    vital.adicionar_filho(No("Habitação", modulo=encontrar_modulo(3)))

    sustento = raiz.adicionar_filho(No("Sustento"))
    sustento.adicionar_filho(No("Energia Solar", modulo=encontrar_modulo(4)))
    sustento.adicionar_filho(No("Energia Nuclear", modulo=encontrar_modulo(5)))
    sustento.adicionar_filho(No("Energia Eólica", modulo=encontrar_modulo(13)))
    sustento.adicionar_filho(No("Produção de Alimentos", modulo=encontrar_modulo(8)))
    sustento.adicionar_filho(No("Comunicações", modulo=encontrar_modulo(6)))
    sustento.adicionar_filho(No("ISRU (Recursos Locais)", modulo=encontrar_modulo(10)))

    expansao = raiz.adicionar_filho(No("Expansão"))
    expansao.adicionar_filho(No("Logística e Armazenamento", modulo=encontrar_modulo(9)))
    expansao.adicionar_filho(No("Oficina e Manutenção", modulo=encontrar_modulo(11)))
    expansao.adicionar_filho(No("Laboratório Científico", modulo=encontrar_modulo(12)))

    return raiz
