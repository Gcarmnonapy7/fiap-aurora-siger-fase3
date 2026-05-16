"""Testes da lista plana de módulos da colônia."""

import unittest
from colonia.modulos import MODULOS, encontrar_modulo


class TestModulos(unittest.TestCase):

    def test_total_de_modulos(self):
        """Devem existir 13 módulos: 12 da Fase 2 + Eólica nova."""
        self.assertEqual(len(MODULOS), 13)

    def test_ids_sequenciais(self):
        """IDs devem ser 1..13 sem buracos."""
        ids = [m["id"] for m in MODULOS]
        self.assertEqual(ids, list(range(1, 14)))

    def test_eolica_existe_e_eh_id_13(self):
        eolica = encontrar_modulo(13)
        self.assertEqual(eolica["nome"], "Energia Eólica")
        self.assertEqual(eolica["tipo"], "gerador_eolico")

    def test_geradores_tem_capacidade(self):
        """Solar (4), Nuclear (5), Eólica (13) precisam de capacidade_max_kw."""
        for id_ in [4, 5, 13]:
            self.assertIn("capacidade_max_kw", encontrar_modulo(id_))

    def test_modulos_pressurizados_tem_fator_termico_positivo(self):
        """Habitação, ECLSS, Médico, Laboratório, Oficina."""
        pressurizados = {3, 2, 7, 12, 11}
        for m in MODULOS:
            if m["id"] in pressurizados:
                self.assertGreater(m["fator_termico"], 0)

    def test_modulos_que_escalonam_excedente(self):
        """Alimentos (8), ISRU (10), Laboratório (12)."""
        esperados = {8, 10, 12}
        encontrados = {m["id"] for m in MODULOS if m["escalona_com_excedente"]}
        self.assertEqual(encontrados, esperados)

    def test_consumo_minimo_menor_que_adequado(self):
        for m in MODULOS:
            c = m["consumo_por_modo"]
            self.assertLessEqual(c["minimo"], c["adequado"])


if __name__ == "__main__":
    unittest.main()
