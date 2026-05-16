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

    def buscar(self, nome):
        """Busca em profundidade pelo nome. Devolve o No ou None."""
        for no in self.percorrer_dfs():
            if no.nome == nome:
                return no
        return None

    def folhas(self):
        """Devolve lista dos módulos referenciados pelas folhas."""
        return [no.modulo for no in self.percorrer_dfs() if no.eh_folha()]

    def profundidade(self):
        """Profundidade da subárvore (raiz solitária = 1)."""
        if self.eh_folha():
            return 1
        return 1 + max(filho.profundidade() for filho in self.filhos)

    def agregar(self, valor_de_folha, inicial, combinar):
        """Agregação recursiva sobre as folhas.

        valor_de_folha: callable que recebe `modulo` da folha e devolve um valor
        inicial: valor neutro do agregador (0 para soma, 1 para produto, etc.)
        combinar: callable (a, b) → c
        """
        if self.eh_folha():
            return valor_de_folha(self.modulo)
        resultado = inicial
        for filho in self.filhos:
            resultado = combinar(resultado, filho.agregar(valor_de_folha, inicial, combinar))
        return resultado

    def imprimir(self, indent=0):
        """Devolve string pretty-print da subárvore."""
        linhas = ["  " * indent + ("- " if indent > 0 else "") + self.nome]
        for filho in self.filhos:
            linhas.append(filho.imprimir(indent + 1))
        return "\n".join(linhas)
