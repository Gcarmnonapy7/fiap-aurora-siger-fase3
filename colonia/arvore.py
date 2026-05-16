"""Classe No — árvore N-ária genérica.

Usada para construir as duas hierarquias da colônia:
funcional (Energia, Suporte à Vida, Comando, Operações) e
criticidade (Vital, Sustento, Expansão).

Nós internos têm `modulo=None`; folhas referenciam um dict de módulo
(da lista `colonia.modulos.MODULOS`).
"""


class No:

    def __init__(self, nome, modulo=None):
        self.nome = nome
        self.modulo = modulo
        self.filhos = []

    def adicionar_filho(self, filho):
        self.filhos.append(filho)
        return filho

    def eh_folha(self):
        return len(self.filhos) == 0
