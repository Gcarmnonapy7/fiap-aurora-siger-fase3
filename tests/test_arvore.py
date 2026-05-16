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


if __name__ == "__main__":
    unittest.main()
