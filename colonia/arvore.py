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

    def percorrer_dfs(self):
        """Percurso em profundidade (pré-ordem). Generator."""
        yield self
        for filho in self.filhos:
            yield from filho.percorrer_dfs()

    def percorrer_bfs(self):
        """Percurso em largura (por nível). Generator."""
        from collections import deque
        fila = deque([self])
        while fila:
            atual = fila.popleft()
            yield atual
            for filho in atual.filhos:
                fila.append(filho)
