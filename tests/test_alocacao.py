"""Testes da política de alocação em 4 etapas."""

import unittest
from colonia.alocacao import alocar_energia
from colonia.modulos import MODULOS, encontrar_modulo
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
            self.assertNotEqual(encontrar_modulo(vital_id)["modo_atual"], "desligado")

    def test_oferta_baixa_expansao_desligada(self):
        clima = {"temperatura_c": -20}
        alocar_energia(self.arvore, oferta_kw=15.0, clima=clima)
        # Expansão: Logística (9), Oficina (11), Lab (12) — devem desligar primeiro
        for exp_id in [9, 11, 12]:
            self.assertEqual(encontrar_modulo(exp_id)["modo_atual"], "desligado")

    def test_geradores_nunca_rebaixados(self):
        clima = {"temperatura_c": 0}
        alocar_energia(self.arvore, oferta_kw=10.0, clima=clima)
        for ger_id in [4, 5, 13]:
            self.assertEqual(encontrar_modulo(ger_id)["modo_atual"], "adequado")

    def test_custo_inclui_consumo_proprio_dos_geradores(self):
        """Política deve considerar consumo próprio dos geradores (4.5 kW total
        em 'adequado': solar 1 + nuclear 3 + eólica 0.5) ao decidir cabe ou não.

        Cenário: consumo dos consumidores em 'adequado' soma exatamente a oferta,
        mas o consumo próprio dos geradores estoura a margem. Política deve
        rebaixar pelo menos um módulo de Expansão.
        """
        clima = {"temperatura_c": 0}
        # soma exata dos consumidores em "adequado" (sem termo térmico a 0°C):
        # 8+12+15+5+6+10+4+8+3+5 = 76 kW
        # com geradores: +4.5 = 80.5 kW
        alocar_energia(self.arvore, oferta_kw=76.0, clima=clima)
        # Sem incluir geradores, política acharia que cabe 76→76 e nada rebaixa.
        # Com geradores, custo 80.5 > 76 → pelo menos 1 expansão precisa ser rebaixada.
        modos_expansao = [encontrar_modulo(i)["modo_atual"] for i in (9, 11, 12)]
        self.assertTrue(
            any(m in ("minimo", "desligado") for m in modos_expansao),
            f"Esperava rebaixamento na Expansão, mas vi {modos_expansao}",
        )


if __name__ == "__main__":
    unittest.main()
