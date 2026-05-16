"""Testes do modelo de geração de energia."""

import unittest
from colonia.geracao import gerar_solar, gerar_eolico, gerar_nuclear
from colonia.modulos import encontrar_modulo


class TestSolar(unittest.TestCase):

    def setUp(self):
        self.solar = encontrar_modulo(4)

    def test_solar_zero_a_noite(self):
        clima = {"hora": 2, "tau": 0.5, "fator_paineis": 1.0}
        self.assertEqual(gerar_solar(self.solar, clima), 0.0)

    def test_solar_pico_meio_dia_limpo(self):
        clima = {"hora": 12, "tau": 0.5, "fator_paineis": 1.0}
        # capacidade 100 * 1.0 * exp(-0.5) * 1.0 ≈ 60.65
        self.assertAlmostEqual(gerar_solar(self.solar, clima), 60.65, places=1)

    def test_solar_tempestade_grave_quase_zero(self):
        clima = {"hora": 12, "tau": 8.0, "fator_paineis": 1.0}
        self.assertLess(gerar_solar(self.solar, clima), 0.1)

    def test_solar_paineis_degradados(self):
        clima_limpo = {"hora": 12, "tau": 0.5, "fator_paineis": 1.0}
        clima_sujo = {"hora": 12, "tau": 0.5, "fator_paineis": 0.5}
        self.assertGreater(gerar_solar(self.solar, clima_limpo), gerar_solar(self.solar, clima_sujo))


class TestEolico(unittest.TestCase):

    def setUp(self):
        self.eolico = encontrar_modulo(13)

    def test_cut_in_a_3_m_s(self):
        """Abaixo de v=3 m/s não gera (cut-in)."""
        self.assertEqual(gerar_eolico(self.eolico, {"vento_ms": 2.0}), 0.0)
        self.assertEqual(gerar_eolico(self.eolico, {"vento_ms": 3.0}), 0.0)

    def test_gera_em_vento_medio(self):
        # P = 2.5*10 - 7.5 = 17.5 kW
        self.assertAlmostEqual(gerar_eolico(self.eolico, {"vento_ms": 10.0}), 17.5)

    def test_satura_em_capacidade(self):
        # capacidade 30 kW; vento alto deve saturar
        self.assertEqual(gerar_eolico(self.eolico, {"vento_ms": 25.0}), 30.0)


class TestNuclear(unittest.TestCase):

    def test_nuclear_constante(self):
        nuclear = encontrar_modulo(5)
        for hora in range(24):
            clima = {"hora": hora, "tau": 0.5}
            self.assertEqual(gerar_nuclear(nuclear, clima), 80.0)


if __name__ == "__main__":
    unittest.main()
