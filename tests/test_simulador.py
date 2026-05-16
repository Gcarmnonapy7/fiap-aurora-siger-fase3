"""Testes do simulador (integração ponta-a-ponta)."""

import random
import unittest

from colonia.constantes import TOTAL_PASSOS
from colonia.modulos import MODULOS
from colonia.simulador import rodar_simulacao


class TestSimuladorIntegracao(unittest.TestCase):

    def test_historico_tem_168_pontos(self):
        random.seed(42)
        _, _, historico = rodar_simulacao()
        for chave in ["vento_ms", "temperatura_c", "geracao_total_kw", "consumo_total_kw"]:
            self.assertEqual(len(historico[chave]), TOTAL_PASSOS)

    def test_geracao_total_nunca_negativa(self):
        random.seed(42)
        _, _, historico = rodar_simulacao()
        for g in historico["geracao_total_kw"]:
            self.assertGreaterEqual(g, 0)

    def test_consumo_total_nunca_negativo(self):
        random.seed(42)
        _, _, historico = rodar_simulacao()
        for c in historico["consumo_total_kw"]:
            self.assertGreaterEqual(c, 0)

    def test_bateria_dentro_dos_limites(self):
        random.seed(42)
        _, bateria, historico = rodar_simulacao()
        for carga in historico["bateria_carga_kwh"]:
            self.assertGreaterEqual(carga, 0)
            self.assertLessEqual(carga, bateria["capacidade_max_kwh"])

    def test_evento_didatico_aparece_no_historico(self):
        random.seed(42)
        _, _, historico = rodar_simulacao()
        self.assertIn("moderada", historico["tempestade"])


if __name__ == "__main__":
    unittest.main()
