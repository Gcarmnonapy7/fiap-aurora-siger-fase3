"""Testes da classe No (árvore N-ária)."""

import unittest
from colonia.arvore import No


class TestNoEstrutura(unittest.TestCase):

    def test_no_folha_recebe_modulo(self):
        n = No("Solar", modulo={"id": 4})
        self.assertEqual(n.nome, "Solar")
        self.assertEqual(n.modulo, {"id": 4})
        self.assertEqual(n.filhos, [])

    def test_no_interno_nao_tem_modulo(self):
        n = No("Energia")
        self.assertIsNone(n.modulo)
        self.assertEqual(n.filhos, [])

    def test_adicionar_filho(self):
        raiz = No("Energia")
        folha = No("Solar", modulo={"id": 4})
        raiz.adicionar_filho(folha)
        self.assertEqual(len(raiz.filhos), 1)
        self.assertIs(raiz.filhos[0], folha)

    def test_eh_folha(self):
        raiz = No("Energia")
        folha = No("Solar", modulo={"id": 4})
        raiz.adicionar_filho(folha)
        self.assertFalse(raiz.eh_folha())
        self.assertTrue(folha.eh_folha())


class TestNoPercursos(unittest.TestCase):

    def _arvore_exemplo(self):
        # Energia
        #   ├── Renovavel
        #   │     ├── Solar
        #   │     └── Eolica
        #   └── Nuclear
        raiz = No("Energia")
        renovavel = No("Renovavel")
        raiz.adicionar_filho(renovavel)
        renovavel.adicionar_filho(No("Solar", modulo={"id": 4}))
        renovavel.adicionar_filho(No("Eolica", modulo={"id": 13}))
        raiz.adicionar_filho(No("Nuclear", modulo={"id": 5}))
        return raiz

    def test_dfs_pre_ordem(self):
        raiz = self._arvore_exemplo()
        ordem = [n.nome for n in raiz.percorrer_dfs()]
        self.assertEqual(ordem, ["Energia", "Renovavel", "Solar", "Eolica", "Nuclear"])

    def test_bfs_por_nivel(self):
        raiz = self._arvore_exemplo()
        ordem = [n.nome for n in raiz.percorrer_bfs()]
        self.assertEqual(ordem, ["Energia", "Renovavel", "Nuclear", "Solar", "Eolica"])


class TestNoOperacoes(unittest.TestCase):

    def _arvore_exemplo(self):
        raiz = No("Energia")
        renovavel = No("Renovavel")
        raiz.adicionar_filho(renovavel)
        renovavel.adicionar_filho(No("Solar", modulo={"id": 4, "gerado": 80}))
        renovavel.adicionar_filho(No("Eolica", modulo={"id": 13, "gerado": 20}))
        raiz.adicionar_filho(No("Nuclear", modulo={"id": 5, "gerado": 80}))
        return raiz

    def test_buscar_por_nome_encontra(self):
        raiz = self._arvore_exemplo()
        n = raiz.buscar("Solar")
        self.assertIsNotNone(n)
        self.assertEqual(n.modulo["id"], 4)

    def test_buscar_por_nome_nao_encontra(self):
        raiz = self._arvore_exemplo()
        self.assertIsNone(raiz.buscar("Inexistente"))

    def test_folhas_devolve_apenas_modulos(self):
        raiz = self._arvore_exemplo()
        ids = sorted(m["id"] for m in raiz.folhas())
        self.assertEqual(ids, [4, 5, 13])

    def test_profundidade(self):
        raiz = self._arvore_exemplo()
        self.assertEqual(raiz.profundidade(), 3)  # Energia → Renovavel → Solar

    def test_agregar_soma_geracao(self):
        raiz = self._arvore_exemplo()
        total = raiz.agregar(lambda m: m["gerado"], inicial=0, combinar=lambda a, b: a + b)
        self.assertEqual(total, 180)

    def test_imprimir_inclui_todos_os_nomes(self):
        raiz = self._arvore_exemplo()
        saida = raiz.imprimir()
        for nome in ["Energia", "Renovavel", "Solar", "Eolica", "Nuclear"]:
            self.assertIn(nome, saida)


if __name__ == "__main__":
    unittest.main()
