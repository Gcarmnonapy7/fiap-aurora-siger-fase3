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


class TestTempestade(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_inicia_em_limpo(self):
        from colonia.clima import EstadoTempestade
        e = EstadoTempestade()
        self.assertEqual(e.estado, "limpo")
        self.assertEqual(e.horas_restantes, 0)

    def test_avancar_sem_tempestade_pode_ficar_limpo(self):
        from colonia.clima import EstadoTempestade
        e = EstadoTempestade()
        for _ in range(100):
            e.avancar(vento_max_24h=5.0, sol=0, hora=12)
            self.assertIn(e.estado, ("limpo", "leve", "moderada", "grave"))

    def test_forcar_evento_didatico_no_sol_3(self):
        from colonia.clima import EstadoTempestade
        e = EstadoTempestade()
        e.avancar(vento_max_24h=5.0, sol=3, hora=8, forcar_evento=True)
        self.assertEqual(e.estado, "moderada")
        self.assertGreater(e.horas_restantes, 0)

    def test_duracao_da_leve_decrementa(self):
        from colonia.clima import EstadoTempestade
        e = EstadoTempestade()
        e.estado = "leve"
        e.horas_restantes = 5
        e.avancar(vento_max_24h=5.0, sol=0, hora=12)
        self.assertEqual(e.horas_restantes, 4)

    def test_termina_quando_horas_chegam_a_zero(self):
        from colonia.clima import EstadoTempestade
        e = EstadoTempestade()
        e.estado = "leve"
        e.horas_restantes = 1
        e.avancar(vento_max_24h=5.0, sol=0, hora=12)
        self.assertEqual(e.estado, "limpo")
        self.assertEqual(e.horas_restantes, 0)


class TestTauEPaineis(unittest.TestCase):

    def test_tau_limpo_baixo(self):
        from colonia.clima import calcular_tau, transmissao_solar
        self.assertAlmostEqual(calcular_tau("limpo", vento=2.0), 0.5)

    def test_tau_grave_alto(self):
        from colonia.clima import calcular_tau
        self.assertAlmostEqual(calcular_tau("grave", vento=2.0), 8.0)

    def test_tau_aumenta_com_vento(self):
        from colonia.clima import calcular_tau
        baixo = calcular_tau("limpo", vento=5.0)
        alto  = calcular_tau("limpo", vento=15.0)
        self.assertGreater(alto, baixo)

    def test_transmissao_solar_em_limpo_aproxima_60_porcento(self):
        from colonia.clima import transmissao_solar
        # exp(-0.5) ≈ 0.606
        self.assertAlmostEqual(transmissao_solar(0.5), 0.6065, places=3)

    def test_transmissao_grave_quase_zero(self):
        from colonia.clima import transmissao_solar
        # exp(-8) ≈ 0.000335
        self.assertLess(transmissao_solar(8.0), 0.001)


class TestFatorPaineis(unittest.TestCase):

    def setUp(self):
        random.seed(42)

    def test_deposicao_reduz_fator(self):
        from colonia.clima import atualizar_fator_paineis
        novo = atualizar_fator_paineis(fator_atual=1.0, sorteio_limpeza=False)
        self.assertLess(novo, 1.0)
        self.assertAlmostEqual(novo, 1.0 - 0.002, places=4)

    def test_limpeza_recupera_fator(self):
        from colonia.clima import atualizar_fator_paineis
        novo = atualizar_fator_paineis(fator_atual=0.5, sorteio_limpeza=True)
        self.assertGreater(novo, 0.5)

    def test_fator_nao_baixa_do_piso(self):
        from colonia.clima import atualizar_fator_paineis
        from colonia.constantes import PISO_FATOR_PAINEIS
        novo = atualizar_fator_paineis(fator_atual=PISO_FATOR_PAINEIS, sorteio_limpeza=False)
        self.assertGreaterEqual(novo, PISO_FATOR_PAINEIS)


if __name__ == "__main__":
    unittest.main()
