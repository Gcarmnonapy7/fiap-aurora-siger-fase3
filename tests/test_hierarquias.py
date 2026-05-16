"""Testes da construção das duas árvores sobre a lista de módulos."""

import unittest
from colonia.hierarquias import construir_arvore_funcional, construir_arvore_criticidade


class TestArvoreFuncional(unittest.TestCase):

    def setUp(self):
        self.raiz = construir_arvore_funcional()

    def test_raiz_nome(self):
        self.assertEqual(self.raiz.nome, "Colônia Aurora Siger")

    def test_quatro_ramos(self):
        ramos = [f.nome for f in self.raiz.filhos]
        self.assertEqual(set(ramos), {"Energia", "Suporte à Vida", "Comando", "Operações"})

    def test_energia_tem_solar_nuclear_eolica(self):
        energia = self.raiz.buscar("Energia")
        nomes = {f.nome for f in energia.filhos}
        self.assertEqual(nomes, {"Energia Solar", "Energia Nuclear", "Energia Eólica"})

    def test_total_de_folhas(self):
        self.assertEqual(len(self.raiz.folhas()), 13)


class TestArvoreCriticidade(unittest.TestCase):

    def setUp(self):
        self.raiz = construir_arvore_criticidade()

    def test_tres_niveis(self):
        ramos = [f.nome for f in self.raiz.filhos]
        self.assertEqual(ramos, ["Vital", "Sustento", "Expansão"])

    def test_vital_contem_eclss_e_habitacao(self):
        vital = self.raiz.buscar("Vital")
        nomes = {f.nome for f in vital.filhos}
        self.assertIn("Suporte de Vida (ECLSS)", nomes)
        self.assertIn("Habitação", nomes)

    def test_expansao_contem_oficina_e_lab(self):
        expansao = self.raiz.buscar("Expansão")
        nomes = {f.nome for f in expansao.filhos}
        self.assertIn("Oficina e Manutenção", nomes)
        self.assertIn("Laboratório Científico", nomes)

    def test_total_de_folhas(self):
        self.assertEqual(len(self.raiz.folhas()), 13)


class TestCompartilhamentoDeReferencias(unittest.TestCase):
    """Verifica que as duas árvores referenciam os MESMOS dicts de módulo."""

    def test_mesma_referencia_para_eclss(self):
        funcional = construir_arvore_funcional()
        criticidade = construir_arvore_criticidade()
        eclss_f = funcional.buscar("Suporte de Vida (ECLSS)").modulo
        eclss_c = criticidade.buscar("Suporte de Vida (ECLSS)").modulo
        self.assertIs(eclss_f, eclss_c)


if __name__ == "__main__":
    unittest.main()
