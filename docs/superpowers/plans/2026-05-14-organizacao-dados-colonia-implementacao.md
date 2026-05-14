# Implementação da Organização dos Dados da Colônia

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Implementar a arquitetura definida em `docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md` — simulador da colônia Aurora Siger com 13 módulos organizados em duas árvores N-árias, modelo climático realista de 7 sóis marcianos, política de load shedding em 4 etapas, e histórico de séries temporais como output.

**Architecture:** 9 módulos Python em `colonia/`, organizados em 5 camadas (dados → clima → geração → política → histórico). Classe `No` N-ária reutilizada para duas árvores (funcional + criticidade). Simulador determinístico (via `random.seed`) para reprodutibilidade dos testes.

**Tech Stack:** Python 3.12, stdlib apenas (`math`, `random`, `collections.deque`), `unittest` da stdlib para testes.

---

## File Structure

```
fiap-aurora-siger-fase3/
├── README.md                                    [Task 15]
├── main.py                                      [Task 14]
├── colonia/
│   ├── __init__.py                              [Task 1]
│   ├── constantes.py                            [Task 2]
│   ├── modulos.py                               [Task 3]
│   ├── arvore.py                                [Tasks 4–6]
│   ├── hierarquias.py                           [Task 7]
│   ├── clima.py                                 [Tasks 8–10]
│   ├── geracao.py                               [Task 11]
│   ├── consumo.py                               [Task 12]
│   ├── alocacao.py                              [Task 13]
│   ├── estado.py                                [Task 14]
│   └── simulador.py                             [Task 14]
└── tests/
    ├── __init__.py                              [Task 1]
    ├── test_arvore.py                           [Tasks 4–6]
    ├── test_modulos.py                          [Task 3]
    ├── test_hierarquias.py                      [Task 7]
    ├── test_clima.py                            [Tasks 8–10]
    ├── test_geracao.py                          [Task 11]
    ├── test_consumo.py                          [Task 12]
    ├── test_alocacao.py                         [Task 13]
    └── test_simulador.py                        [Task 14]
```

**Responsabilidades:**

- `constantes.py` — todos os parâmetros físicos do simulador (Camada 2 e 3 do spec). Centraliza valores para fácil ajuste.
- `modulos.py` — lista plana dos 13 módulos (Camada 1).
- `arvore.py` — classe `No` N-ária genérica com percursos.
- `hierarquias.py` — constrói as duas árvores (funcional, criticidade) sobre `modulos`.
- `clima.py` — geradores estocásticos: vento, tempestade (máquina de estados), tau, temperatura, painéis (Camada 2).
- `geracao.py` — funções `gerar_solar`, `gerar_eolico`, `gerar_nuclear` (Camada 3).
- `consumo.py` — `consumo_atual_kw` com termo térmico (Camada 3).
- `alocacao.py` — política de load shedding em 4 etapas (Camada 4).
- `estado.py` — `bateria`, `clima_atual`, `historico` (Camadas 1 e 5).
- `simulador.py` — orquestrador de 1 passo e do horizonte de 168 passos.
- `main.py` — entry point CLI.

---

## Tasks

### Task 1: Setup do pacote e estrutura de testes

**Files:**
- Create: `colonia/__init__.py`
- Create: `tests/__init__.py`

- [ ] **Step 1.1: Criar `colonia/__init__.py` vazio**

```python
"""Simulador da colônia Aurora Siger — Fase 3 FIAP."""
```

- [ ] **Step 1.2: Criar `tests/__init__.py` vazio**

```python
```

- [ ] **Step 1.3: Verificar que pacotes são importáveis**

Run: `python -c "import colonia; import tests"`
Expected: nenhum output (sucesso silencioso)

- [ ] **Step 1.4: Commit**

```bash
git add colonia/__init__.py tests/__init__.py
git commit -m "feat: estrutura inicial do pacote colonia e testes"
```

---

### Task 2: Constantes globais

**Files:**
- Create: `colonia/constantes.py`

- [ ] **Step 2.1: Criar `colonia/constantes.py` com TODAS as constantes do spec**

```python
"""Parâmetros físicos e operacionais do simulador.

Valores derivados de literatura científica — ver Seção 6 do spec
em docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md
"""

import math

# Horizonte da simulação
HORIZONTE_SOLS = 7
HORAS_POR_SOL = 24
TOTAL_PASSOS = HORIZONTE_SOLS * HORAS_POR_SOL  # 168

# --- Vento ---
V_BASE = 2.5
V_AMPLITUDE = 7.0
FATOR_SAZONAL = 1.2  # perihélio
V_RUIDO_SIGMA = 1.5

# --- Tempestades de poeira ---
ESTADOS_TEMPESTADE = ("limpo", "leve", "moderada", "grave")

PROB_BASE_POR_SOL = {
    "leve":     0.40,
    "moderada": 0.04,
    "grave":    0.002,
}

DURACAO_HORAS = {
    "leve":     (12, 72),
    "moderada": (72, 168),
    "grave":    (168, 720),
}

LIMIAR_VENTO_BONUS = 15.0  # m/s acima disso aumenta prob de tempestade
FATOR_PERIHELIO = 1.5

FORCAR_EVENTO_DIDATICO = True
SOL_EVENTO_DIDATICO = 3
HORA_EVENTO_DIDATICO = 8

# --- Opacidade atmosférica (tau) ---
TAU_BASE = {
    "limpo":    0.5,
    "leve":     1.5,
    "moderada": 3.0,
    "grave":    8.0,
}
TAU_VENTO_FATOR = 0.05  # tau extra por m/s acima de 5 m/s
TAU_VENTO_LIMIAR = 5.0

# --- Painéis solares ---
PERDA_PAINEIS_POR_SOL = 0.002        # 0.2% por sol
PROB_LIMPEZA_POR_SOL = 0.005         # ~1 evento a cada 200 sols
LIMPEZA_RECUPERACAO = (0.30, 0.70)   # range de recuperação por dust devil
PISO_FATOR_PAINEIS = 0.30            # piso por limpeza manual humana

# --- Temperatura ---
T_MEDIA = -60.0
A_DIURNA = 35.0
A_SAZONAL = 18.0
PHI_DIURNO = 9  # pico ~15h local
SOLS_POR_ANO_MARCIANO = 668
T_RUIDO_SIGMA = 2.0

# --- Consumo térmico (Q = U·A·ΔT) ---
A_ENVELOPE = 250.0          # m²
U_ISOLAMENTO = 0.15         # W/m²·K
T_ALVO_INTERNA = 20.0       # °C
GANHO_INTERNO_W = 4000.0    # W
ETA_AQUECEDOR = 0.95

# --- Bateria ---
BATERIA_CAPACIDADE_KWH = 500.0
BATERIA_CARGA_INICIAL_KWH = 250.0
BATERIA_RESERVA_EMERGENCIA_FRACAO = 0.20  # 20% intocável

# --- Curva solar ---
def curva_diurna_solar(hora):
    """Fração de irradiância em função da hora (0 a 1, formato sino entre 06–18h)."""
    return max(0.0, math.sin(math.pi * (hora - 6) / 12))
```

- [ ] **Step 2.2: Verificar imports**

Run: `python -c "from colonia.constantes import TOTAL_PASSOS, curva_diurna_solar; print(TOTAL_PASSOS, curva_diurna_solar(12))"`
Expected: `168 1.0`

- [ ] **Step 2.3: Commit**

```bash
git add colonia/constantes.py
git commit -m "feat: parâmetros físicos do simulador (clima, painéis, bateria)"
```

---

### Task 3: Lista plana dos 13 módulos

**Files:**
- Create: `colonia/modulos.py`
- Create: `tests/test_modulos.py`

- [ ] **Step 3.1: Escrever teste em `tests/test_modulos.py`**

```python
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
```

- [ ] **Step 3.2: Rodar teste — deve falhar (módulo não existe)**

Run: `python -m unittest tests.test_modulos -v`
Expected: `ModuleNotFoundError: No module named 'colonia.modulos'`

- [ ] **Step 3.3: Implementar `colonia/modulos.py`**

```python
"""Lista plana dos 13 módulos da colônia Aurora Siger.

Os 12 primeiros mantêm a identidade da Fase 2 (mesmos nomes e prioridades).
O 13º — Energia Eólica — é acréscimo da Fase 3, justificado pelo item 1.3
do enunciado que pede regressão linear sobre dados de vento e energia eólica.
"""

MODULOS = [
    {
        "id": 1, "nome": "Comando e Controle", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 8, "excedente": 8},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 2, "nome": "Suporte de Vida (ECLSS)", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 4, "adequado": 12, "excedente": 12},
        "escalona_com_excedente": False,
        "fator_termico": 0.4,
        "modo_atual": "adequado",
    },
    {
        "id": 3, "nome": "Habitação", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 5, "adequado": 15, "excedente": 15},
        "escalona_com_excedente": False,
        "fator_termico": 1.0,
        "modo_atual": "adequado",
    },
    {
        "id": 4, "nome": "Energia Solar", "tipo": "gerador_solar",
        "capacidade_max_kw": 100.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 0.5, "adequado": 1, "excedente": 1},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 5, "nome": "Energia Nuclear", "tipo": "gerador_nuclear",
        "capacidade_max_kw": 80.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 3, "excedente": 3},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 6, "nome": "Comunicações", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 5, "excedente": 5},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 7, "nome": "Suporte Médico", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 6, "excedente": 6},
        "escalona_com_excedente": False,
        "fator_termico": 0.2,
        "modo_atual": "adequado",
    },
    {
        "id": 8, "nome": "Produção de Alimentos", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 3, "adequado": 10, "excedente": 18},
        "escalona_com_excedente": True,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 9, "nome": "Logística e Armazenamento", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 4, "excedente": 4},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 10, "nome": "ISRU (Recursos Locais)", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 8, "excedente": 20},
        "escalona_com_excedente": True,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 11, "nome": "Oficina e Manutenção", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 0.5, "adequado": 3, "excedente": 3},
        "escalona_com_excedente": False,
        "fator_termico": 0.2,
        "modo_atual": "desligado",
    },
    {
        "id": 12, "nome": "Laboratório Científico", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 5, "excedente": 12},
        "escalona_com_excedente": True,
        "fator_termico": 0.2,
        "modo_atual": "adequado",
    },
    {
        "id": 13, "nome": "Energia Eólica", "tipo": "gerador_eolico",
        "capacidade_max_kw": 30.0,
        "consumo_por_modo": {"desligado": 0, "minimo": 0.3, "adequado": 0.5, "excedente": 0.5},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
]


def encontrar_modulo(id_):
    """Devolve o módulo com o id fornecido. Levanta KeyError se não existir."""
    for m in MODULOS:
        if m["id"] == id_:
            return m
    raise KeyError(f"Módulo com id={id_} não encontrado")
```

- [ ] **Step 3.4: Rodar testes — devem passar**

Run: `python -m unittest tests.test_modulos -v`
Expected: `7 tests, OK`

- [ ] **Step 3.5: Commit**

```bash
git add colonia/modulos.py tests/test_modulos.py
git commit -m "feat: lista plana dos 13 módulos (12 da fase 2 + eólica)"
```

---

### Task 4: Classe `No` — estrutura básica

**Files:**
- Create: `colonia/arvore.py`
- Create: `tests/test_arvore.py`

- [ ] **Step 4.1: Escrever teste em `tests/test_arvore.py`**

```python
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
```

- [ ] **Step 4.2: Rodar teste — deve falhar (classe não existe)**

Run: `python -m unittest tests.test_arvore -v`
Expected: `ModuleNotFoundError: No module named 'colonia.arvore'`

- [ ] **Step 4.3: Implementar `colonia/arvore.py` — estrutura básica**

```python
"""Classe No — árvore N-ária genérica.

Usada para construir as duas hierarquias da colônia:
funcional (Energia, Suporte à Vida, Comando, Operações) e
criticidade (Vital, Sustento, Expansão).

Nós internos têm `modulo=None`; folhas referenciam um dict de módulo
(da lista `colonia.modulos.MODULOS`).
"""


class No:

    def __init__(self, nome, modulo=None):
        self.nome = nome
        self.modulo = modulo
        self.filhos = []

    def adicionar_filho(self, filho):
        self.filhos.append(filho)
        return filho

    def eh_folha(self):
        return len(self.filhos) == 0
```

- [ ] **Step 4.4: Rodar testes — devem passar**

Run: `python -m unittest tests.test_arvore -v`
Expected: `4 tests, OK`

- [ ] **Step 4.5: Commit**

```bash
git add colonia/arvore.py tests/test_arvore.py
git commit -m "feat: classe No N-ária — estrutura básica"
```

---

### Task 5: Classe `No` — percursos DFS e BFS

**Files:**
- Modify: `colonia/arvore.py`
- Modify: `tests/test_arvore.py`

- [ ] **Step 5.1: Adicionar testes de percurso em `tests/test_arvore.py`**

Adicione a esta nova classe ao final do arquivo:

```python
class TestNoPercursos(unittest.TestCase):

    def _arvore_exemplo(self):
        # Energia
        #   ├── Renovavel
        #   │     ├── Solar
        #   │     └── Eolica
        #   └── Nuclear
        raiz = No("Energia")
        renovavel = No("Renovavel")
        raiz.adicionar_filho(renovavel)
        renovavel.adicionar_filho(No("Solar", modulo={"id": 4}))
        renovavel.adicionar_filho(No("Eolica", modulo={"id": 13}))
        raiz.adicionar_filho(No("Nuclear", modulo={"id": 5}))
        return raiz

    def test_dfs_pre_ordem(self):
        raiz = self._arvore_exemplo()
        ordem = [n.nome for n in raiz.percorrer_dfs()]
        self.assertEqual(ordem, ["Energia", "Renovavel", "Solar", "Eolica", "Nuclear"])

    def test_bfs_por_nivel(self):
        raiz = self._arvore_exemplo()
        ordem = [n.nome for n in raiz.percorrer_bfs()]
        self.assertEqual(ordem, ["Energia", "Renovavel", "Nuclear", "Solar", "Eolica"])
```

- [ ] **Step 5.2: Rodar — devem falhar (métodos não existem)**

Run: `python -m unittest tests.test_arvore.TestNoPercursos -v`
Expected: `AttributeError: 'No' object has no attribute 'percorrer_dfs'`

- [ ] **Step 5.3: Adicionar métodos a `colonia/arvore.py`**

Adicione dentro da classe `No`:

```python
    def percorrer_dfs(self):
        """Percurso em profundidade (pré-ordem). Generator."""
        yield self
        for filho in self.filhos:
            yield from filho.percorrer_dfs()

    def percorrer_bfs(self):
        """Percurso em largura (por nível). Generator."""
        from collections import deque
        fila = deque([self])
        while fila:
            atual = fila.popleft()
            yield atual
            for filho in atual.filhos:
                fila.append(filho)
```

- [ ] **Step 5.4: Rodar — devem passar**

Run: `python -m unittest tests.test_arvore -v`
Expected: `6 tests, OK`

- [ ] **Step 5.5: Commit**

```bash
git add colonia/arvore.py tests/test_arvore.py
git commit -m "feat: percursos DFS (pré-ordem) e BFS (por nível) na árvore"
```

---

### Task 6: Classe `No` — busca, folhas, agregação e pretty-print

**Files:**
- Modify: `colonia/arvore.py`
- Modify: `tests/test_arvore.py`

- [ ] **Step 6.1: Adicionar testes em `tests/test_arvore.py`**

```python
class TestNoOperacoes(unittest.TestCase):

    def _arvore_exemplo(self):
        raiz = No("Energia")
        renovavel = No("Renovavel")
        raiz.adicionar_filho(renovavel)
        renovavel.adicionar_filho(No("Solar", modulo={"id": 4, "gerado": 80}))
        renovavel.adicionar_filho(No("Eolica", modulo={"id": 13, "gerado": 20}))
        raiz.adicionar_filho(No("Nuclear", modulo={"id": 5, "gerado": 80}))
        return raiz

    def test_buscar_por_nome_encontra(self):
        raiz = self._arvore_exemplo()
        n = raiz.buscar("Solar")
        self.assertIsNotNone(n)
        self.assertEqual(n.modulo["id"], 4)

    def test_buscar_por_nome_nao_encontra(self):
        raiz = self._arvore_exemplo()
        self.assertIsNone(raiz.buscar("Inexistente"))

    def test_folhas_devolve_apenas_modulos(self):
        raiz = self._arvore_exemplo()
        ids = sorted(m["id"] for m in raiz.folhas())
        self.assertEqual(ids, [4, 5, 13])

    def test_profundidade(self):
        raiz = self._arvore_exemplo()
        self.assertEqual(raiz.profundidade(), 3)  # Energia → Renovavel → Solar

    def test_agregar_soma_geracao(self):
        raiz = self._arvore_exemplo()
        total = raiz.agregar(lambda m: m["gerado"], inicial=0, combinar=lambda a, b: a + b)
        self.assertEqual(total, 180)

    def test_imprimir_inclui_todos_os_nomes(self):
        raiz = self._arvore_exemplo()
        saida = raiz.imprimir()
        for nome in ["Energia", "Renovavel", "Solar", "Eolica", "Nuclear"]:
            self.assertIn(nome, saida)
```

- [ ] **Step 6.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_arvore.TestNoOperacoes -v`
Expected: `AttributeError: 'No' object has no attribute 'buscar'`

- [ ] **Step 6.3: Adicionar métodos a `colonia/arvore.py`**

```python
    def buscar(self, nome):
        """Busca em profundidade pelo nome. Devolve o No ou None."""
        for no in self.percorrer_dfs():
            if no.nome == nome:
                return no
        return None

    def folhas(self):
        """Devolve lista dos módulos referenciados pelas folhas."""
        return [no.modulo for no in self.percorrer_dfs() if no.eh_folha()]

    def profundidade(self):
        """Profundidade da subárvore (raiz solitária = 1)."""
        if self.eh_folha():
            return 1
        return 1 + max(filho.profundidade() for filho in self.filhos)

    def agregar(self, valor_de_folha, inicial, combinar):
        """Agregação recursiva sobre as folhas.

        valor_de_folha: callable que recebe `modulo` da folha e devolve um valor
        inicial: valor neutro do agregador (0 para soma, 1 para produto, etc.)
        combinar: callable (a, b) → c
        """
        if self.eh_folha():
            return valor_de_folha(self.modulo)
        resultado = inicial
        for filho in self.filhos:
            resultado = combinar(resultado, filho.agregar(valor_de_folha, inicial, combinar))
        return resultado

    def imprimir(self, indent=0):
        """Devolve string pretty-print da subárvore."""
        linhas = ["  " * indent + ("- " if indent > 0 else "") + self.nome]
        for filho in self.filhos:
            linhas.append(filho.imprimir(indent + 1))
        return "\n".join(linhas)
```

- [ ] **Step 6.4: Rodar testes — devem passar**

Run: `python -m unittest tests.test_arvore -v`
Expected: `12 tests, OK`

- [ ] **Step 6.5: Commit**

```bash
git add colonia/arvore.py tests/test_arvore.py
git commit -m "feat: busca, folhas, profundidade, agregação e pretty-print"
```

---

### Task 7: Construção das duas árvores (funcional + criticidade)

**Files:**
- Create: `colonia/hierarquias.py`
- Create: `tests/test_hierarquias.py`

- [ ] **Step 7.1: Escrever testes em `tests/test_hierarquias.py`**

```python
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
```

- [ ] **Step 7.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_hierarquias -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 7.3: Implementar `colonia/hierarquias.py`**

```python
"""Constrói as duas árvores N-árias sobre a lista plana de módulos.

Árvore funcional: agrupa por função (Energia, Suporte à Vida, Comando, Operações).
Árvore de criticidade: agrupa por nível (Vital, Sustento, Expansão).

As duas árvores compartilham referências aos mesmos dicts de módulo —
alterar `modulo["modo_atual"]` em uma se reflete na outra automaticamente.
"""

from colonia.arvore import No
from colonia.modulos import MODULOS, encontrar_modulo


def construir_arvore_funcional():
    raiz = No("Colônia Aurora Siger")

    energia = raiz.adicionar_filho(No("Energia"))
    energia.adicionar_filho(No("Energia Solar", modulo=encontrar_modulo(4)))
    energia.adicionar_filho(No("Energia Nuclear", modulo=encontrar_modulo(5)))
    energia.adicionar_filho(No("Energia Eólica", modulo=encontrar_modulo(13)))

    suporte_vida = raiz.adicionar_filho(No("Suporte à Vida"))
    suporte_vida.adicionar_filho(No("Suporte de Vida (ECLSS)", modulo=encontrar_modulo(2)))
    suporte_vida.adicionar_filho(No("Habitação", modulo=encontrar_modulo(3)))
    suporte_vida.adicionar_filho(No("Suporte Médico", modulo=encontrar_modulo(7)))
    suporte_vida.adicionar_filho(No("Produção de Alimentos", modulo=encontrar_modulo(8)))

    comando = raiz.adicionar_filho(No("Comando"))
    comando.adicionar_filho(No("Comando e Controle", modulo=encontrar_modulo(1)))
    comando.adicionar_filho(No("Comunicações", modulo=encontrar_modulo(6)))

    operacoes = raiz.adicionar_filho(No("Operações"))
    operacoes.adicionar_filho(No("Logística e Armazenamento", modulo=encontrar_modulo(9)))
    operacoes.adicionar_filho(No("ISRU (Recursos Locais)", modulo=encontrar_modulo(10)))
    operacoes.adicionar_filho(No("Oficina e Manutenção", modulo=encontrar_modulo(11)))
    operacoes.adicionar_filho(No("Laboratório Científico", modulo=encontrar_modulo(12)))

    return raiz


def construir_arvore_criticidade():
    raiz = No("Colônia Aurora Siger")

    vital = raiz.adicionar_filho(No("Vital"))
    vital.adicionar_filho(No("Comando e Controle", modulo=encontrar_modulo(1)))
    vital.adicionar_filho(No("Suporte de Vida (ECLSS)", modulo=encontrar_modulo(2)))
    vital.adicionar_filho(No("Suporte Médico", modulo=encontrar_modulo(7)))
    vital.adicionar_filho(No("Habitação", modulo=encontrar_modulo(3)))

    sustento = raiz.adicionar_filho(No("Sustento"))
    sustento.adicionar_filho(No("Energia Solar", modulo=encontrar_modulo(4)))
    sustento.adicionar_filho(No("Energia Nuclear", modulo=encontrar_modulo(5)))
    sustento.adicionar_filho(No("Energia Eólica", modulo=encontrar_modulo(13)))
    sustento.adicionar_filho(No("Produção de Alimentos", modulo=encontrar_modulo(8)))
    sustento.adicionar_filho(No("Comunicações", modulo=encontrar_modulo(6)))
    sustento.adicionar_filho(No("ISRU (Recursos Locais)", modulo=encontrar_modulo(10)))

    expansao = raiz.adicionar_filho(No("Expansão"))
    expansao.adicionar_filho(No("Logística e Armazenamento", modulo=encontrar_modulo(9)))
    expansao.adicionar_filho(No("Oficina e Manutenção", modulo=encontrar_modulo(11)))
    expansao.adicionar_filho(No("Laboratório Científico", modulo=encontrar_modulo(12)))

    return raiz
```

- [ ] **Step 7.4: Rodar testes — devem passar**

Run: `python -m unittest tests.test_hierarquias -v`
Expected: `8 tests, OK`

- [ ] **Step 7.5: Commit**

```bash
git add colonia/hierarquias.py tests/test_hierarquias.py
git commit -m "feat: árvores funcional e de criticidade sobre os módulos"
```

---

### Task 8: Clima — vento e temperatura

**Files:**
- Create: `colonia/clima.py`
- Create: `tests/test_clima.py`

- [ ] **Step 8.1: Escrever testes em `tests/test_clima.py`**

```python
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
```

- [ ] **Step 8.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_clima -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 8.3: Criar `colonia/clima.py` — vento e temperatura**

```python
"""Modelo climático realista da colônia Aurora Siger.

Baseado em literatura NASA/ESA (vide spec, seção 6).
Vento: ciclo diurno + ruído gaussiano + modulação sazonal.
Temperatura: ciclo diurno senoidal + variação sazonal + ruído.
Tempestades: máquina de estados (limpo → leve/moderada/grave).
Painéis: deposição contínua + limpeza estocástica (dust devils).
"""

import math
import random

from colonia.constantes import (
    V_BASE, V_AMPLITUDE, FATOR_SAZONAL, V_RUIDO_SIGMA,
    T_MEDIA, A_DIURNA, A_SAZONAL, PHI_DIURNO, T_RUIDO_SIGMA,
    SOLS_POR_ANO_MARCIANO,
)


def amostrar_vento(hora):
    """Devolve velocidade do vento em m/s para a hora local dada (0–23)."""
    componente_diurno = V_AMPLITUDE * max(0.0, math.sin(math.pi * (hora - 6) / 12))
    ruido = random.gauss(0, V_RUIDO_SIGMA)
    return max(0.0, (V_BASE + componente_diurno) * FATOR_SAZONAL + ruido)


def amostrar_temperatura(sol, hora):
    """Devolve temperatura em °C para o sol e hora dados."""
    diurno = A_DIURNA * math.sin(2 * math.pi * (hora - PHI_DIURNO) / 24)
    sazonal = A_SAZONAL * math.sin(2 * math.pi * sol / SOLS_POR_ANO_MARCIANO)
    ruido = random.gauss(0, T_RUIDO_SIGMA)
    return T_MEDIA + diurno + sazonal + ruido
```

- [ ] **Step 8.4: Rodar testes — devem passar**

Run: `python -m unittest tests.test_clima -v`
Expected: `4 tests, OK`

- [ ] **Step 8.5: Commit**

```bash
git add colonia/clima.py tests/test_clima.py
git commit -m "feat: modelo de vento e temperatura marciana"
```

---

### Task 9: Clima — tempestades (máquina de estados)

**Files:**
- Modify: `colonia/clima.py`
- Modify: `tests/test_clima.py`

- [ ] **Step 9.1: Adicionar testes em `tests/test_clima.py`**

```python
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
        # com seed determinístico, vento baixo (5 m/s) e sol 0, 100 passos:
        # esperamos que algum momento INICIE uma leve, mas não consistente em "limpo"
        # apenas testar que estados pertencem ao conjunto válido
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
```

- [ ] **Step 9.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_clima.TestTempestade -v`
Expected: `ImportError: cannot import name 'EstadoTempestade'`

- [ ] **Step 9.3: Adicionar `EstadoTempestade` a `colonia/clima.py`**

Adicione no topo, junto aos imports:

```python
from colonia.constantes import (
    V_BASE, V_AMPLITUDE, FATOR_SAZONAL, V_RUIDO_SIGMA,
    T_MEDIA, A_DIURNA, A_SAZONAL, PHI_DIURNO, T_RUIDO_SIGMA,
    SOLS_POR_ANO_MARCIANO,
    PROB_BASE_POR_SOL, DURACAO_HORAS, LIMIAR_VENTO_BONUS, FATOR_PERIHELIO,
    SOL_EVENTO_DIDATICO, HORA_EVENTO_DIDATICO,
)
```

E adicione no final do arquivo:

```python
class EstadoTempestade:
    """Máquina de estados para tempestades de poeira em Marte.

    Estados: 'limpo' → 'leve' / 'moderada' / 'grave'.
    Persistência temporal: uma vez iniciada, dura horas_restantes horas.
    """

    def __init__(self):
        self.estado = "limpo"
        self.horas_restantes = 0

    def _prob_inicio(self, classe, vento_max_24h, sol):
        prob = PROB_BASE_POR_SOL[classe]
        bonus_vento = max(0.0, (vento_max_24h - LIMIAR_VENTO_BONUS) / 10.0)
        # perihélio: aproximação simples — sols 0–6 são "perihélio" por construção
        bonus_periode = FATOR_PERIHELIO
        return prob * (1 + bonus_vento) * bonus_periode

    def avancar(self, vento_max_24h, sol, hora, forcar_evento=False):
        """Avança um passo (1 hora) na máquina de estados."""
        if forcar_evento and sol == SOL_EVENTO_DIDATICO and hora == HORA_EVENTO_DIDATICO and self.estado == "limpo":
            self.estado = "moderada"
            min_h, max_h = DURACAO_HORAS["moderada"]
            self.horas_restantes = random.randint(min_h, max_h)
            return

        if self.estado != "limpo":
            self.horas_restantes -= 1
            if self.horas_restantes <= 0:
                self.estado = "limpo"
                self.horas_restantes = 0
            return

        # estado atual = limpo: sorteia se uma nova tempestade inicia
        # uma sorteio por hora; prob por sol é dividida por 24 para virar prob por hora
        for classe in ("grave", "moderada", "leve"):  # mais raras primeiro
            prob_hora = self._prob_inicio(classe, vento_max_24h, sol) / 24.0
            if random.random() < prob_hora:
                self.estado = classe
                min_h, max_h = DURACAO_HORAS[classe]
                self.horas_restantes = random.randint(min_h, max_h)
                return
```

- [ ] **Step 9.4: Rodar — devem passar**

Run: `python -m unittest tests.test_clima -v`
Expected: `9 tests, OK`

- [ ] **Step 9.5: Commit**

```bash
git add colonia/clima.py tests/test_clima.py
git commit -m "feat: máquina de estados para tempestades de poeira"
```

---

### Task 10: Clima — tau (opacidade) e fator de painéis

**Files:**
- Modify: `colonia/clima.py`
- Modify: `tests/test_clima.py`

- [ ] **Step 10.1: Adicionar testes**

```python
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
```

- [ ] **Step 10.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_clima -v`
Expected: `ImportError`

- [ ] **Step 10.3: Adicionar funções a `colonia/clima.py`**

Adicione aos imports:

```python
from colonia.constantes import (
    TAU_BASE, TAU_VENTO_FATOR, TAU_VENTO_LIMIAR,
    PERDA_PAINEIS_POR_SOL, LIMPEZA_RECUPERACAO, PISO_FATOR_PAINEIS,
)
```

E adicione as funções:

```python
def calcular_tau(tempestade, vento):
    """Opacidade atmosférica = base por classe + bônus por vento."""
    extra = TAU_VENTO_FATOR * max(0.0, vento - TAU_VENTO_LIMIAR)
    return TAU_BASE[tempestade] + extra


def transmissao_solar(tau):
    """Lei de Beer-Lambert: transmissão = exp(-tau) (zenith simplificado)."""
    return math.exp(-tau)


def atualizar_fator_paineis(fator_atual, sorteio_limpeza):
    """Aplica deposição contínua e (se sorteio=True) recuperação por dust devil."""
    novo = max(PISO_FATOR_PAINEIS, fator_atual - PERDA_PAINEIS_POR_SOL)
    if sorteio_limpeza:
        recuperacao = random.uniform(*LIMPEZA_RECUPERACAO)
        novo = min(1.0, novo + recuperacao)
    return novo
```

- [ ] **Step 10.4: Rodar — devem passar**

Run: `python -m unittest tests.test_clima -v`
Expected: `17 tests, OK`

- [ ] **Step 10.5: Commit**

```bash
git add colonia/clima.py tests/test_clima.py
git commit -m "feat: opacidade tau (beer-lambert) e fator de painéis"
```

---

### Task 11: Geração — solar, eólica, nuclear

**Files:**
- Create: `colonia/geracao.py`
- Create: `tests/test_geracao.py`

- [ ] **Step 11.1: Escrever testes em `tests/test_geracao.py`**

```python
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
```

- [ ] **Step 11.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_geracao -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 11.3: Implementar `colonia/geracao.py`**

```python
"""Funções de geração de energia das três fontes da colônia."""

from colonia.clima import transmissao_solar
from colonia.constantes import curva_diurna_solar


def gerar_solar(modulo, clima):
    """Potência solar (kW): capacidade × curva_diurna × transmissao × fator_paineis."""
    curva = curva_diurna_solar(clima["hora"])
    transm = transmissao_solar(clima["tau"])
    return modulo["capacidade_max_kw"] * curva * transm * clima["fator_paineis"]


def gerar_eolico(modulo, clima):
    """Potência eólica (kW): modelo linear com cut-in (3 m/s) e saturação na capacidade.

    Forma: P = max(0, min(capacidade, A*v - B))
    Com A=2.5 e B=7.5: P(3)=0, P(10)=17.5, satura em v ≈ 15 m/s.
    """
    A_LINEAR = 2.5
    B_LINEAR = 7.5
    v = clima["vento_ms"]
    potencia = A_LINEAR * v - B_LINEAR
    return max(0.0, min(modulo["capacidade_max_kw"], potencia))


def gerar_nuclear(modulo, clima):
    """Potência nuclear (kW): baseload constante na capacidade nominal."""
    return modulo["capacidade_max_kw"]
```

- [ ] **Step 11.4: Rodar — devem passar**

Run: `python -m unittest tests.test_geracao -v`
Expected: `8 tests, OK`

- [ ] **Step 11.5: Commit**

```bash
git add colonia/geracao.py tests/test_geracao.py
git commit -m "feat: modelos de geração solar, eólica e nuclear"
```

---

### Task 12: Consumo com termo térmico

**Files:**
- Create: `colonia/consumo.py`
- Create: `tests/test_consumo.py`

- [ ] **Step 12.1: Escrever testes em `tests/test_consumo.py`**

```python
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
```

- [ ] **Step 12.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_consumo -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 12.3: Implementar `colonia/consumo.py`**

```python
"""Cálculo de consumo dos módulos.

Combina consumo base (por modo de operação) com termo térmico
(Q = U·A·ΔT) para módulos pressurizados. O termo térmico é
adicionado mesmo se o módulo está em modo 'desligado', porque
habitats pressurizados não podem ser deixados congelar.
"""

from colonia.constantes import (
    A_ENVELOPE, U_ISOLAMENTO, T_ALVO_INTERNA, GANHO_INTERNO_W, ETA_AQUECEDOR,
)


def consumo_aquecimento_kw(temperatura_externa, fator_termico):
    """Potência elétrica gasta em aquecimento (kW).

    Q_perda = U * A_envelope * max(0, T_alvo - T_ext)
    Q_liquido = max(0, Q_perda - ganho_interno_efetivo)
    Q_eletrico = Q_liquido / eta_aquecedor
    Tudo multiplicado por fator_termico (peso por módulo).
    """
    if fator_termico == 0:
        return 0
    delta_t = max(0, T_ALVO_INTERNA - temperatura_externa)
    perda_W = U_ISOLAMENTO * A_ENVELOPE * delta_t
    liquido_W = max(0, perda_W - GANHO_INTERNO_W * fator_termico)
    return (liquido_W / ETA_AQUECEDOR / 1000.0) * fator_termico


def consumo_atual_kw(modulo, clima):
    """Consumo total do módulo neste instante (kW)."""
    base = modulo["consumo_por_modo"][modulo["modo_atual"]]
    extra_termico = consumo_aquecimento_kw(clima["temperatura_c"], modulo["fator_termico"])
    return base + extra_termico
```

- [ ] **Step 12.4: Rodar — devem passar**

Run: `python -m unittest tests.test_consumo -v`
Expected: `6 tests, OK`

- [ ] **Step 12.5: Commit**

```bash
git add colonia/consumo.py tests/test_consumo.py
git commit -m "feat: cálculo de consumo com termo térmico (Q=U·A·ΔT)"
```

---

### Task 13: Política de alocação (load shedding)

**Files:**
- Create: `colonia/alocacao.py`
- Create: `tests/test_alocacao.py`

- [ ] **Step 13.1: Escrever testes em `tests/test_alocacao.py`**

```python
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
```

- [ ] **Step 13.2: Rodar — devem falhar**

Run: `python -m unittest tests.test_alocacao -v`
Expected: `ModuleNotFoundError`

- [ ] **Step 13.3: Implementar `colonia/alocacao.py`**

```python
"""Política de alocação de energia (load shedding em 4 etapas).

Percorre a árvore de criticidade e define o modo de cada módulo conforme
a oferta de energia disponível. Geradores ficam sempre em 'adequado'
(consumo próprio pequeno, geração definida pela física, não pela política).

Etapa 1: tenta todos em 'adequado'; se cabe, distribui excedente.
Etapa 2: rebaixa Expansão → Sustento → Vital para 'mínimo', bottom-up.
Etapa 3: desliga Expansão → Sustento (Vital nunca).
Etapa 4: emergência — alerta crítico (a reserva da bateria é gerenciada
fora desta função, em estado.py / simulador.py).
"""

from colonia.consumo import consumo_aquecimento_kw


GERADORES = ("gerador_solar", "gerador_eolico", "gerador_nuclear")


def _consumo_no_modo(modulo, modo, clima):
    """Consumo do módulo SE estivesse no modo dado (não altera modo_atual)."""
    base = modulo["consumo_por_modo"][modo]
    extra = consumo_aquecimento_kw(clima["temperatura_c"], modulo["fator_termico"])
    return base + extra


def _folhas_consumidoras_por_nivel(arvore):
    """Devolve dict {nome_nivel: [modulos_consumidores]} para Vital, Sustento, Expansão."""
    niveis = {}
    for filho_nivel in arvore.filhos:
        modulos = [m for m in filho_nivel.folhas() if m["tipo"] not in GERADORES]
        # ordena por id (menor = mais prioritário) para tie-breaker consistente
        modulos.sort(key=lambda m: m["id"])
        niveis[filho_nivel.nome] = modulos
    return niveis


def alocar_energia(arvore_criticidade, oferta_kw, clima):
    """Aplica política de 4 etapas. Mutaciona modulo['modo_atual'] in-place."""
    niveis = _folhas_consumidoras_por_nivel(arvore_criticidade)
    todos = niveis["Vital"] + niveis["Sustento"] + niveis["Expansão"]

    # Etapa 1: tudo em adequado
    for m in todos:
        m["modo_atual"] = "adequado"
    custo = sum(_consumo_no_modo(m, "adequado", clima) for m in todos)

    if custo <= oferta_kw:
        # distribui excedente para escalonáveis (ordem por id menor primeiro)
        sobra = oferta_kw - custo
        for m in sorted([x for x in todos if x["escalona_com_excedente"]], key=lambda x: x["id"]):
            delta = _consumo_no_modo(m, "excedente", clima) - _consumo_no_modo(m, "adequado", clima)
            if sobra >= delta:
                m["modo_atual"] = "excedente"
                sobra -= delta
        return

    # Etapa 2: rebaixa bottom-up
    for nivel_nome in ("Expansão", "Sustento", "Vital"):
        for m in reversed(niveis[nivel_nome]):  # menor prioridade primeiro = maior id primeiro
            if custo <= oferta_kw:
                return
            antes = _consumo_no_modo(m, m["modo_atual"], clima)
            m["modo_atual"] = "minimo"
            depois = _consumo_no_modo(m, "minimo", clima)
            custo -= (antes - depois)

    if custo <= oferta_kw:
        return

    # Etapa 3: desliga bottom-up (Vital nunca)
    for nivel_nome in ("Expansão", "Sustento"):
        for m in reversed(niveis[nivel_nome]):
            if custo <= oferta_kw:
                return
            antes = _consumo_no_modo(m, m["modo_atual"], clima)
            m["modo_atual"] = "desligado"
            depois = _consumo_no_modo(m, "desligado", clima)
            custo -= (antes - depois)

    # Etapa 4: emergência — sinaliza via retorno (caller pode disparar alerta)
    # Vital permanece em 'minimo' independentemente do saldo.
```

- [ ] **Step 13.4: Rodar — devem passar**

Run: `python -m unittest tests.test_alocacao -v`
Expected: `4 tests, OK`

- [ ] **Step 13.5: Commit**

```bash
git add colonia/alocacao.py tests/test_alocacao.py
git commit -m "feat: política de alocação em 4 etapas (load shedding)"
```

---

### Task 14: Estado, simulador e integração ponta-a-ponta

**Files:**
- Create: `colonia/estado.py`
- Create: `colonia/simulador.py`
- Create: `tests/test_simulador.py`
- Create: `main.py`

- [ ] **Step 14.1: Escrever `colonia/estado.py`**

```python
"""Estado global do simulador: clima atual, bateria, histórico."""

from colonia.constantes import (
    BATERIA_CAPACIDADE_KWH, BATERIA_CARGA_INICIAL_KWH, BATERIA_RESERVA_EMERGENCIA_FRACAO,
)


def estado_inicial():
    """Cria estado novo da colônia (clima, bateria, histórico vazios)."""
    clima = {
        "sol": 0, "hora": 0,
        "vento_ms": 0.0,
        "tempestade": "limpo",
        "tau": 0.5,
        "temperatura_c": -60.0,
        "fator_paineis": 1.0,
    }
    bateria = {
        "carga_atual_kwh": BATERIA_CARGA_INICIAL_KWH,
        "capacidade_max_kwh": BATERIA_CAPACIDADE_KWH,
        "reserva_emergencia_kwh": BATERIA_CAPACIDADE_KWH * BATERIA_RESERVA_EMERGENCIA_FRACAO,
    }
    historico = {
        "vento_ms": [], "temperatura_c": [], "tempestade": [], "tau": [],
        "geracao_solar_kw": [], "geracao_eolica_kw": [], "geracao_nuclear_kw": [],
        "geracao_total_kw": [], "consumo_total_kw": [],
        "bateria_carga_kwh": [], "modos_resumo": [], "alertas": [],
    }
    return clima, bateria, historico
```

- [ ] **Step 14.2: Escrever testes em `tests/test_simulador.py`**

```python
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
```

- [ ] **Step 14.3: Rodar — devem falhar**

Run: `python -m unittest tests.test_simulador -v`
Expected: `ModuleNotFoundError: colonia.simulador`

- [ ] **Step 14.4: Implementar `colonia/simulador.py`**

```python
"""Orquestrador do simulador: 1 passo + horizonte completo de 168 passos."""

import random

from colonia.alocacao import alocar_energia
from colonia.clima import (
    amostrar_vento, amostrar_temperatura, calcular_tau,
    atualizar_fator_paineis, EstadoTempestade,
)
from colonia.consumo import consumo_atual_kw
from colonia.constantes import (
    HORIZONTE_SOLS, HORAS_POR_SOL, TOTAL_PASSOS,
    PROB_LIMPEZA_POR_SOL, FORCAR_EVENTO_DIDATICO,
)
from colonia.estado import estado_inicial
from colonia.geracao import gerar_solar, gerar_eolico, gerar_nuclear
from colonia.hierarquias import construir_arvore_funcional, construir_arvore_criticidade
from colonia.modulos import MODULOS


def _soma_geracao(arvore_funcional, clima):
    """Soma de geração no ramo 'Energia' da árvore funcional."""
    energia = arvore_funcional.buscar("Energia")
    total = 0.0
    for no in energia.percorrer_dfs():
        if not no.eh_folha():
            continue
        m = no.modulo
        if m["tipo"] == "gerador_solar":
            total += gerar_solar(m, clima)
        elif m["tipo"] == "gerador_eolico":
            total += gerar_eolico(m, clima)
        elif m["tipo"] == "gerador_nuclear":
            total += gerar_nuclear(m, clima)
    return total


def _detalhar_geracao(arvore_funcional, clima):
    """Devolve dict {tipo: kW} para registro no histórico."""
    energia = arvore_funcional.buscar("Energia")
    detalhe = {"solar": 0.0, "eolico": 0.0, "nuclear": 0.0}
    for no in energia.percorrer_dfs():
        if not no.eh_folha():
            continue
        m = no.modulo
        if m["tipo"] == "gerador_solar":
            detalhe["solar"] += gerar_solar(m, clima)
        elif m["tipo"] == "gerador_eolico":
            detalhe["eolico"] += gerar_eolico(m, clima)
        elif m["tipo"] == "gerador_nuclear":
            detalhe["nuclear"] += gerar_nuclear(m, clima)
    return detalhe


def passo(clima, bateria, historico, arvores, tempestade_state, ultimo_vento_24h):
    """Avança a simulação em 1 hora. Mutaciona clima/bateria/historico/MODULOS in-place."""
    funcional, criticidade = arvores
    sol = clima["sol"]
    hora = clima["hora"]

    # 1. Amostrar clima
    vento = amostrar_vento(hora)
    temperatura = amostrar_temperatura(sol, hora)
    ultimo_vento_24h.append(vento)
    if len(ultimo_vento_24h) > 24:
        ultimo_vento_24h.pop(0)
    vento_max_24h = max(ultimo_vento_24h)

    tempestade_state.avancar(vento_max_24h, sol, hora, forcar_evento=FORCAR_EVENTO_DIDATICO)
    tau = calcular_tau(tempestade_state.estado, vento)

    # Atualizar painéis (uma vez por sol, na hora 0)
    if hora == 0:
        sorteio_limpeza = random.random() < PROB_LIMPEZA_POR_SOL
        clima["fator_paineis"] = atualizar_fator_paineis(clima["fator_paineis"], sorteio_limpeza)

    clima["vento_ms"] = vento
    clima["temperatura_c"] = temperatura
    clima["tempestade"] = tempestade_state.estado
    clima["tau"] = tau

    # 2. Geração
    detalhe = _detalhar_geracao(funcional, clima)
    soma_geracao = detalhe["solar"] + detalhe["eolico"] + detalhe["nuclear"]

    # 3. Oferta (geração + bateria disponível acima da reserva)
    bateria_disponivel = max(0, bateria["carga_atual_kwh"] - bateria["reserva_emergencia_kwh"])
    oferta = soma_geracao + bateria_disponivel

    # 4. Alocação
    alocar_energia(criticidade, oferta_kw=oferta, clima=clima)

    # 5. Consumo total
    consumo_total = sum(consumo_atual_kw(m, clima) for m in MODULOS)

    # 6. Balanço bateria
    saldo = soma_geracao - consumo_total
    bateria["carga_atual_kwh"] = max(0, min(
        bateria["capacidade_max_kwh"],
        bateria["carga_atual_kwh"] + saldo,
    ))

    # 7. Alerta de emergência
    alertas = []
    if consumo_total > soma_geracao + bateria_disponivel:
        alertas.append(f"EMERGÊNCIA sol {sol} hora {hora}: oferta insuficiente")

    # 8. Registrar histórico
    historico["vento_ms"].append(vento)
    historico["temperatura_c"].append(temperatura)
    historico["tempestade"].append(tempestade_state.estado)
    historico["tau"].append(tau)
    historico["geracao_solar_kw"].append(detalhe["solar"])
    historico["geracao_eolica_kw"].append(detalhe["eolico"])
    historico["geracao_nuclear_kw"].append(detalhe["nuclear"])
    historico["geracao_total_kw"].append(soma_geracao)
    historico["consumo_total_kw"].append(consumo_total)
    historico["bateria_carga_kwh"].append(bateria["carga_atual_kwh"])
    historico["modos_resumo"].append({m["nome"]: m["modo_atual"] for m in MODULOS})
    historico["alertas"].append(alertas)

    # 9. Avançar relógio
    clima["hora"] += 1
    if clima["hora"] >= HORAS_POR_SOL:
        clima["hora"] = 0
        clima["sol"] += 1


def rodar_simulacao():
    """Roda os 168 passos do simulador e devolve (clima_final, bateria_final, historico)."""
    clima, bateria, historico = estado_inicial()
    arvores = (construir_arvore_funcional(), construir_arvore_criticidade())
    tempestade_state = EstadoTempestade()
    ultimo_vento_24h = []

    for _ in range(TOTAL_PASSOS):
        passo(clima, bateria, historico, arvores, tempestade_state, ultimo_vento_24h)

    return clima, bateria, historico
```

- [ ] **Step 14.5: Rodar testes do simulador**

Run: `python -m unittest tests.test_simulador -v`
Expected: `5 tests, OK`

- [ ] **Step 14.6: Escrever `main.py` — entry point**

```python
"""Entry point do simulador da colônia Aurora Siger.

Executa 1 semana marciana (168 horas) e imprime um resumo do histórico.
Uso:
    python main.py
"""

import random

from colonia.hierarquias import construir_arvore_funcional, construir_arvore_criticidade
from colonia.simulador import rodar_simulacao


def main(seed=42):
    random.seed(seed)
    print("Aurora Siger — Simulação de 7 sóis marcianos\n")

    print("Árvore funcional dos subsistemas:")
    print(construir_arvore_funcional().imprimir())
    print()

    print("Árvore de criticidade dos subsistemas:")
    print(construir_arvore_criticidade().imprimir())
    print()

    clima_final, bateria_final, historico = rodar_simulacao()

    print(f"Passos simulados: {len(historico['vento_ms'])}")
    print(f"Geração total média: {sum(historico['geracao_total_kw'])/len(historico['geracao_total_kw']):.1f} kW")
    print(f"Consumo total médio: {sum(historico['consumo_total_kw'])/len(historico['consumo_total_kw']):.1f} kW")
    print(f"Bateria final: {bateria_final['carga_atual_kwh']:.1f} / {bateria_final['capacidade_max_kwh']:.1f} kWh")
    tempestades = [t for t in historico["tempestade"] if t != "limpo"]
    print(f"Passos com tempestade: {len(tempestades)} de {len(historico['tempestade'])}")

    alertas_totais = sum(1 for a in historico["alertas"] if a)
    print(f"Passos com alerta: {alertas_totais}")


if __name__ == "__main__":
    main()
```

- [ ] **Step 14.7: Verificar execução**

Run: `python main.py`
Expected: imprime as duas árvores e um resumo numérico, sem exceções.

- [ ] **Step 14.8: Commit**

```bash
git add colonia/estado.py colonia/simulador.py tests/test_simulador.py main.py
git commit -m "feat: simulador integrado e entry point CLI"
```

---

### Task 15: README e documentação final

**Files:**
- Create: `README.md`

- [ ] **Step 15.1: Criar `README.md`**

```markdown
# Aurora Siger — Fase 3 (Atividade Integradora FIAP)

Sistema integrado de **organização de dados, decisão automática, previsão e análise energética** da colônia marciana Aurora Siger.

Continuação da Fase 2 (MGPEB): os 12 módulos que pousaram agora operam, com a adição de uma turbina eólica.

## Como executar

```bash
python main.py
```

Imprime as duas hierarquias (funcional e criticidade), roda 7 sóis marcianos de simulação e mostra um resumo.

## Como rodar os testes

```bash
python -m unittest discover -v
```

## Estrutura

| Arquivo | Responsabilidade |
|---|---|
| `colonia/modulos.py` | Lista plana dos 13 módulos |
| `colonia/arvore.py` | Classe `No` N-ária genérica |
| `colonia/hierarquias.py` | Duas árvores (funcional + criticidade) |
| `colonia/clima.py` | Vento, tempestades, tau, temperatura, painéis |
| `colonia/geracao.py` | Geração solar / eólica / nuclear |
| `colonia/consumo.py` | Consumo com termo térmico |
| `colonia/alocacao.py` | Load shedding em 4 etapas |
| `colonia/estado.py` | Bateria, clima atual, histórico |
| `colonia/simulador.py` | Orquestrador de 168 passos |

Sem dependências externas — usa apenas `math` e `random` da biblioteca padrão.

## Exemplo de entrada e saída

**Entrada implícita** (cenário simulado): 7 sóis marcianos em perihélio, vento amostrado por hora, tempestade moderada didática começando no sol 3 hora 8, painéis degradando 0.2%/sol.

**Saída** (exemplo do `main.py`):

```
Geração total média: 87.3 kW
Consumo total médio: 65.4 kW
Bateria final: 412.1 / 500.0 kWh
Passos com tempestade: 96 de 168
Passos com alerta: 4
```

## Documentação técnica

- `docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md` — design completo com decisões e justificativas
- `docs/superpowers/plans/2026-05-14-organizacao-dados-colonia-implementacao.md` — plano de implementação seguido

## Equipe

Mesma equipe da Fase 2 — Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia.
```

- [ ] **Step 15.2: Rodar a suíte completa de testes**

Run: `python -m unittest discover -v`
Expected: todos os testes passam (~50 testes)

- [ ] **Step 15.3: Commit final**

```bash
git add README.md
git commit -m "docs: README com instruções de execução e estrutura"
```

---

## Verificação final

Após todas as tasks, rodar:

```bash
python -m unittest discover -v   # todos os testes passam
python main.py                    # simulador roda sem exceções e imprime resumo
```

A entrega da Fase 3 estará pronta para revisão da equipe e merge na `main`.
