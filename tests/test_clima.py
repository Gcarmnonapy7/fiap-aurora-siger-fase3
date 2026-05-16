"""Testes do modelo climático."""

import random
import unittest
from colonia.clima import amostrar_vento, amostrar_temperatura


class TestVento(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_vento_eh_nao_negativo(self):
        for hora in range(24):
            v = amostrar_vento(hora)
            self.assertGreaterEqual(v, 0)

    def test_vento_pico_diurno_maior_que_madrugada(self):
        """Vento entre 13–15h em média maior que vento entre 2–4h."""
        random.seed(42)
        ventos_dia = [amostrar_vento(h) for h in [13, 14, 15] for _ in range(50)]
        random.seed(42)
        ventos_noite = [amostrar_vento(h) for h in [2, 3, 4] for _ in range(50)]
        media_dia = sum(ventos_dia) / len(ventos_dia)
        media_noite = sum(ventos_noite) / len(ventos_noite)
        self.assertGreater(media_dia, media_noite)


class TestTemperatura(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_temperatura_meio_dia_maior_que_madrugada(self):
        random.seed(42)
        temps_dia = [amostrar_temperatura(0, 14) for _ in range(50)]
        random.seed(42)
        temps_noite = [amostrar_temperatura(0, 4) for _ in range(50)]
        self.assertGreater(sum(temps_dia)/len(temps_dia), sum(temps_noite)/len(temps_noite))

    def test_temperatura_em_faixa_marciana(self):
        """Temperaturas observadas devem estar entre -100 e +20 °C."""
        for sol in range(7):
            for hora in range(24):
                t = amostrar_temperatura(sol, hora)
                self.assertGreater(t, -100)
                self.assertLess(t, 20)


if __name__ == "__main__":
    unittest.main()
