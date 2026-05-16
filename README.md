# Aurora Siger — Fase 3: Sistema Inteligente Integrado (AURORA CORE)

Simulador em Python da colônia marciana **Aurora Siger** após o pouso bem-sucedido dos 12 módulos da Fase 2. Os módulos agora **operam** sob clima estocástico realista (7 sóis marcianos), produzindo séries temporais de geração, consumo e estado de bateria. Sobre essas séries, o sistema **AURORA CORE** aplica três camadas analíticas: regras de decisão automáticas, previsão de geração eólica via regressão linear e análise de balanço energético.

Atividade Integradora da Fase 3 — Ciência da Computação, FIAP (2026).

## Objetivo

Cobrir os 4 itens do enunciado oficial em um único sistema funcional:

| Item | Descrição | Implementação |
|------|-----------|---------------|
| **1.1** | Organização hierárquica dos dados | `colony/modules.py` + `colony/hierarchies.py` (duas árvores N-árias) |
| **1.2** | Regras de decisão automáticas | `colony/decision.py` (`evaluate_rules`) |
| **1.3** | Regressão linear (vento → energia) | `colony/prediction.py` (sem numpy/sklearn) |
| **1.4** | Análise consumo × geração | `colony/analysis.py` (`analyze_balance`) |

## Estrutura do repositório

```
.
├── README.md
├── LICENSE
├── enunciado.md                   # enunciado original da atividade
├── main.py                        # entry point CLI (com argparse)
├── colony/                        # pacote em inglês (código)
│   ├── __init__.py
│   ├── constants.py               # parâmetros físicos (clima, painéis, bateria, térmico)
│   ├── modules.py                 # lista plana dos 13 módulos (MODULES)
│   ├── tree.py                    # classe Node (árvore N-ária genérica)
│   ├── hierarchies.py             # build_functional_tree, build_criticality_tree
│   ├── climate.py                 # vento, temperatura, tempestades (FSM), tau, painéis
│   ├── generation.py              # generate_solar / generate_wind / generate_nuclear
│   ├── consumption.py             # consumo base + termo térmico Q = U·A·ΔT
│   ├── allocation.py              # política de load shedding em 4 etapas
│   ├── state.py                   # bateria, clima atual, histórico
│   ├── simulator.py               # orquestrador (run_simulation, step)
│   ├── decision.py                # NOVO — regras de decisão (item 1.2)
│   ├── prediction.py              # NOVO — regressão linear manual (item 1.3)
│   └── analysis.py                # NOVO — balanço energético + log (item 1.4)
├── tests/                         # 119 testes unitários e de integração
└── docs/superpowers/
    ├── specs/                     # design e justificativas físicas
    └── plans/                     # planos TDD executados
```

## Como executar o simulador

```bash
python3 main.py
```

O programa abre um **menu interativo** com 9 opções:

```
=========================================================
  Configuração: seed=42 | horizonte=168
  Estado: (sem simulação ainda)
---------------------------------------------------------
  [1] Rodar simulação
  [2] Configurar seed (determinístico/aleatório)
  [3] Configurar horizonte (em horas)
  [4] Mostrar hierarquias da colônia (item 1.1)
  [5] Resumo numérico da simulação
  [6] Regras de decisão (item 1.2)
  [7] Previsão eólica via regressão linear (item 1.3)
  [8] Análise de balanço energético (item 1.4)
  [9] Salvar log da simulação em arquivo
  [0] Sair
=========================================================
Escolha uma opção:
```

**Fluxo típico:** configurar seed/horizonte (opções 2 e 3 — opcionais, defaults já cobrem o enunciado), rodar a simulação (1), depois navegar pelos itens 4–9 para explorar os resultados sem precisar rodar de novo.

**Dependências:** nenhuma externa — apenas `math`, `random` e `collections.deque` da biblioteca padrão. Sem `argparse`, sem CLI flags, dentro do espírito do enunciado ("Não é necessário utilizar bibliotecas avançadas").

### Saída de exemplo (após rodar a simulação)

```
Rodando simulação (seed=42, horizonte=168 passos)...
[OK] 168 passos simulados.
     Geração média: 92.6 kW
     Consumo médio: 93.4 kW
     Bateria final: 103.6/500.0 kWh
```

Explorando o item 1.3 (previsão eólica):

```
--- Previsão eólica (item 1.3) ---
  reta ajustada: y = 2.500·v - 7.500
  vento (m/s) para prever [11]: 11
  -> para v = 11 m/s, energia eólica prevista ≈ 20.0 kW
```

> A reta `y = 2.5·v - 7.5` recupera quase exatamente o modelo físico interno da geração eólica. Isso é proposital — demonstra que a regressão linear manual funciona corretamente sobre os dados reais do simulador.

## Exemplos do enunciado (entrada → saída)

### Item 1.2 — Regras de decisão

```python
from colony.decision import evaluate_rules

evaluate_rules({"energy_kw": 40, "consumption_kw": 70, "storm": "clear"})
# → ['ALERTA: reduzir consumo', 'EMERGÊNCIA ENERGÉTICA']

evaluate_rules({"energy_kw": 40, "consumption_kw": 80, "storm": "clear"})
# → ['ALERTA: reduzir consumo', 'ATIVAR MODO ECONOMIA', 'EMERGÊNCIA ENERGÉTICA']
```

### Item 1.3 — Regressão linear

```python
from colony.prediction import linear_regression, predict

a, b = linear_regression([8, 10, 12], [20, 25, 30])
# a = 2.5, b = 0
predict(a, b, 11)
# → 27.5
```

### Item 1.4 — Análise de balanço

```python
from colony.analysis import analyze_balance

analyze_balance(generation_kw=40, consumption_kw=70)
# → {'status': 'risk', 'message': 'ALERTA: consumo maior que geração', 'delta_kw': -30}

analyze_balance(generation_kw=80, consumption_kw=30)
# → {'status': 'surplus', 'message': 'SUGESTÃO: armazenar energia excedente', 'delta_kw': 50}
```

## Como rodar os testes

```bash
python3 -m unittest discover -v
```

**119 testes** determinísticos via `random.seed(42)`, todos passam em <100ms. Validam:

- Estrutura da árvore N-ária e percursos (DFS pré-ordem, BFS por nível).
- Construção das duas hierarquias e compartilhamento de referências entre elas.
- Modelo climático (vento, temperatura, tempestades, opacidade tau, fator de painéis).
- Geração de cada fonte (solar com Beer-Lambert, eólica com cut-in e saturação, nuclear constante).
- Consumo com termo térmico em diferentes temperaturas externas.
- Política de alocação em 4 etapas (load shedding).
- Integração ponta-a-ponta do simulador (histórico íntegro, bateria dentro dos limites, evento didático registrado).
- **Determinismo** vs. **não-determinismo** (`seed=42` reprodutível; `seed=None` varia entre runs).
- Regras de decisão, regressão linear manual e análise de balanço.

## Convenções

- **Código**: identificadores em **inglês** (`colony/`, `Node`, `evaluate_rules`, `"adequate"`, `"Vital"`).
- **Documentação** (este README, CLAUDE.md, relatório PDF, specs): **português BR**.
- **Mensagens de alerta** voltadas ao usuário (saída do programa, valores literais retornados por `evaluate_rules`): **português**, pois o enunciado pede esses textos exatos.

## Evolução: reativo → preditivo

A Fase 2 entregou um sistema **reativo**: 12 módulos sabiam pousar mas não sabiam operar. A Fase 3 adiciona:

1. **Operação contínua sob clima estocástico** (168 passos com ruído gaussiano, FSM de tempestades, deposição de poeira).
2. **Decisão automática** baseada em regras (`decision.py`) e política de load shedding (`allocation.py`).
3. **Previsão** via regressão linear manual (`prediction.py`) — sistema agora **aprende** dos próprios dados.
4. **Análise crítica** do balanço energético (`analysis.py`) — fechando o ciclo: dado → análise → ação.

O sistema final cumpre o objetivo declarado no enunciado: evoluir de **reativo** para **preditivo**.

## Equipe

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmabittencourtpy@gmail.com |
| Marcio Francisco dos Santos Junior | RM570758 | marciofsantos65@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Maria Sophia Domingues dos Santos | RM571209 | maria.sophia.domingues@gmail.com |

## Licença

[MIT](LICENSE)
