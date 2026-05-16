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


if __name__ == "__main__":
    unittest.main()
