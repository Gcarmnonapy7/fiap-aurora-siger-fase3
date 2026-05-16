"""Testes do cálculo de consumo (base + termo térmico)."""

import unittest
from colonia.consumo import consumo_aquecimento_kw, consumo_atual_kw
from colonia.modulos import encontrar_modulo


class TestAquecimento(unittest.TestCase):

    def test_modulo_sem_fator_termico_nao_aquece(self):
        # ISRU tem fator_termico = 0
        self.assertEqual(consumo_aquecimento_kw(temperatura_externa=-70, fator_termico=0.0), 0)

    def test_habitacao_a_minus_70_consome_alguns_kw(self):
        # fator_termico = 1.0 (Habitação)
        c = consumo_aquecimento_kw(temperatura_externa=-70, fator_termico=1.0)
        # Q_perda = 0.15 * 250 * 90 = 3375 W; menos ganho 4000*1.0 = 4000; clamp 0
        # Resultado: 0
        self.assertEqual(c, 0)

    def test_habitacao_a_minus_90_consome(self):
        # T_alvo=20, ΔT=110, Q_perda=0.15*250*110=4125 W; ganho 4000; líquido 125 W; /0.95 = ~131 W = 0.131 kW
        c = consumo_aquecimento_kw(temperatura_externa=-90, fator_termico=1.0)
        self.assertGreater(c, 0)
        self.assertAlmostEqual(c, 0.131, places=2)

    def test_temperatura_acima_do_alvo_nao_aquece(self):
        c = consumo_aquecimento_kw(temperatura_externa=25, fator_termico=1.0)
        self.assertEqual(c, 0)


class TestConsumoAtual(unittest.TestCase):

    def test_consumo_modo_adequado_modulo_sem_termico(self):
        comando = encontrar_modulo(1)  # fator_termico=0, modo_atual="adequado", consumo=8
        clima = {"temperatura_c": -70}
        self.assertEqual(consumo_atual_kw(comando, clima), 8)

    def test_consumo_modo_desligado_sem_termico(self):
        oficina = encontrar_modulo(11)
        # fator_termico = 0.2, modo_atual = "desligado"
        # Mesmo desligado, aquece — mas a -50°C ainda dá clamp 0
        clima = {"temperatura_c": -50}
        self.assertEqual(consumo_atual_kw(oficina, clima), 0)


if __name__ == "__main__":
    unittest.main()
