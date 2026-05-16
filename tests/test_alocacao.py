"""Testes da política de alocação em 4 etapas."""

import unittest
from colonia.alocacao import alocar_energia
from colonia.modulos import MODULOS
from colonia.hierarquias import construir_arvore_criticidade


def _resetar_modos():
    """Coloca todos os módulos em 'adequado' antes de cada teste (Oficina vai para adequado também)."""
    for m in MODULOS:
        m["modo_atual"] = "adequado"


class TestAlocacao(unittest.TestCase):

    def setUp(self):
        _resetar_modos()
        self.arvore = construir_arvore_criticidade()

    def test_oferta_abundante_tudo_em_adequado(self):
        clima = {"temperatura_c": 0}
        # oferta muito alta
        alocar_energia(self.arvore, oferta_kw=500.0, clima=clima)
        for m in MODULOS:
            if m["tipo"] in ("gerador_solar", "gerador_eolico", "gerador_nuclear"):
                self.assertEqual(m["modo_atual"], "adequado")
                continue
            # Módulos que escalonam podem ter ido para "excedente"
            self.assertIn(m["modo_atual"], ("adequado", "excedente"))

    def test_oferta_minima_vital_preservado(self):
        clima = {"temperatura_c": -20}
        # oferta apenas para vital em minimo
        # consumo vital em minimo: 1+4+5+2 (CC, ECLSS, Hab, Med) = 12 kW + termico moderado
        alocar_energia(self.arvore, oferta_kw=20.0, clima=clima)
        # Módulos vitais nunca devem estar "desligados"
        for vital_id in [1, 2, 3, 7]:
            modulo = next(m for m in MODULOS if m["id"] == vital_id)
            self.assertNotEqual(modulo["modo_atual"], "desligado")

    def test_oferta_baixa_expansao_desligada(self):
        clima = {"temperatura_c": -20}
        alocar_energia(self.arvore, oferta_kw=15.0, clima=clima)
        # Expansão: Logística (9), Oficina (11), Lab (12) — devem desligar primeiro
        for exp_id in [9, 11, 12]:
            modulo = next(m for m in MODULOS if m["id"] == exp_id)
            self.assertEqual(modulo["modo_atual"], "desligado")

    def test_geradores_nunca_rebaixados(self):
        clima = {"temperatura_c": 0}
        alocar_energia(self.arvore, oferta_kw=10.0, clima=clima)
        for ger_id in [4, 5, 13]:
            modulo = next(m for m in MODULOS if m["id"] == ger_id)
            self.assertEqual(modulo["modo_atual"], "adequado")


if __name__ == "__main__":
    unittest.main()
