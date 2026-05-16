# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Atividade Integradora da Fase 3 da disciplina de Ciência da Computação (FIAP, 2026). Continuação da Fase 2 (módulo de pouso MGPEB) — agora a colônia marciana **Aurora Siger** já pousou e o trabalho é simular sua operação por 7 sóis (168 horas).

O sistema integrado é chamado **AURORA CORE** e cobre os 4 itens do enunciado oficial:

- **1.1** Organização hierárquica dos dados — duas árvores N-árias (`functional`, `criticality`) sobre 13 módulos.
- **1.2** Regras de decisão — `colony/decision.py` (`evaluate_rules` retorna alertas estilo "ALERTA: reduzir consumo").
- **1.3** Regressão linear vento↔eólica — `colony/prediction.py` (`linear_regression` manual, sem numpy).
- **1.4** Análise consumo×geração — `colony/analysis.py` (`analyze_balance`, `summarize_history`, `write_log`).

Documentação técnica em:
- `docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md` — design original com justificativas físicas, referências NASA/ESA. **Identificadores nesse spec ainda estão em pt** (escrito antes da virada de idioma) — usar como referência de física, não de nomes.
- `docs/superpowers/plans/2026-05-14-organizacao-dados-colonia-implementacao.md` — plano TDD da Fase 1 (organização dos dados).
- `docs/superpowers/plans/2026-05-16-aurora-core-en-port.md` — plano TDD da migração pt→en + módulos novos.

## Tech stack

Python 3.12, **stdlib apenas** (`math`, `random`, `collections.deque`, `argparse`), `unittest` da stdlib para testes. Sem `pyproject.toml`, sem `requirements.txt`, sem virtualenv obrigatório. Restrição vem do enunciado: "Não é necessário utilizar bibliotecas avançadas".

## Convenção de idioma

**Código em inglês, documentação em português.**

- Módulos, classes, funções, variáveis, chaves de dicionário e valores de string usados como dados internos → **inglês** (`colony/`, `Node`, `evaluate_rules`, `"clear"`, `"adequate"`, `"Vital"`).
- README.md, CLAUDE.md, relatório PDF, comentários longos de docstring, este arquivo, specs em `docs/superpowers/` → **português BR**.
- Mensagens de saída para usuário (prints do `main.py`, alertas do `decision.py` tipo "ALERTA: reduzir consumo") ficam em **português** porque o enunciado pede exatamente esses textos.

Warnings cSpell para palavras como `Siger`, `Aurora`, `ECLSS`, `ISRU` são falsos positivos.

## Common commands

```bash
# Roda o simulador end-to-end (imprime árvores + resumo de 168 passos + alertas + previsão)
python3 main.py

# Modos não-determinísticos / horizonte curto
python3 main.py --random
python3 main.py --horizon 48
python3 main.py --seed 7

# Gravar log textual em arquivo
python3 main.py --log-file data/colony_log.txt

# Saída enxuta (sem árvores)
python3 main.py --quiet

# Suíte completa (119 testes, <1s)
python3 -m unittest discover -v

# Um arquivo de teste só
python3 -m unittest tests.test_climate -v

# Uma classe ou um método específico
python3 -m unittest tests.test_climate.TestStormState -v
python3 -m unittest tests.test_climate.TestStormState.test_force_didactic_event_at_sol_3 -v
```

Não há linter, formatter ou pre-commit configurados — o projeto se segura por testes.

## Architecture (the big picture)

O pacote `colony/` está organizado em **6 camadas**, com dependências apontando sempre para camadas inferiores:

```
Camada 6: decision.py, prediction.py, analysis.py    (analytics sobre history)
Camada 5: simulator.py, main.py                      (orquestração)
Camada 4: allocation.py                              (política — load shedding em 4 etapas)
Camada 3: generation.py, consumption.py              (física por módulo)
Camada 2: climate.py                                 (estocástico — vento, tempestade FSM, tau, painéis)
Camada 1: modules.py, tree.py, hierarchies.py, state.py   (dados e estruturas)
Camada 0: constants.py                               (parâmetros físicos — 30+ constantes)
```

A camada 6 é a contribuição AURORA CORE: consome o `history` produzido pelo simulador. Não há ciclo de dependência.

### Decisões arquiteturais que não são óbvias por arquivo

**Os 13 módulos compartilham referência entre as duas árvores.**
`modules.MODULES` é uma lista plana global. As duas árvores construídas em `hierarchies.py` (funcional e criticidade) usam `find_module(id)` e referenciam **o mesmo dict** em ambas — testado em `tests/test_hierarchies.py::TestSharedReferences`. Consequência: mutar `module["current_mode"]` em qualquer ponto afeta as duas árvores automaticamente. É por isso que `allocation.py` muta os modos in-place sem se preocupar com sincronização.

**Estado mutável global causa leakage entre testes.**
`MODULES` é importado por vários módulos. Testes que mudam `current_mode` (especialmente `test_allocation.py`) precisam resetar antes de rodar, ou o teste seguinte herda estado contaminado. `test_consumption.py::TestCurrentConsumption` declara `current_mode` explicitamente para se proteger disso. **Ao escrever novo teste que dependa de `current_mode` padrão, sempre o setar explicitamente.**

**Determinismo via `random.seed(42)` no `run_simulation`.**
`run_simulation(seed=42)` (default) chama `random.seed(seed)` no início. Testes que envolvem `climate.py` diretamente chamam `random.seed(42)` no `setUp` deles. **`run_simulation(seed=None)` pula o `random.seed()` — usado pela flag `--random` do CLI para demos não-determinísticas.** A reprodutibilidade dos testes não é afetada porque eles passam `seed=42` ou setam seed manualmente.

**Evento didático forçado.**
`constants.FORCE_DIDACTIC_EVENT = True` faz uma tempestade `moderate` começar no sol 3 hora 8 (`DIDACTIC_EVENT_SOL`, `DIDACTIC_EVENT_HOUR`). Isso garante que toda execução do `main.py` mostra a colônia lidando com crise climática — comportamento esperado e testado, não acidente. Para simular cenário sem evento, setar `FORCE_DIDACTIC_EVENT = False`.

**Geradores são imunes ao load shedding.**
`allocation.GENERATORS = ("solar_generator", "wind_generator", "nuclear_generator")`. A política decide consumo dos módulos consumidores, mas não rebaixa geradores — ver justificativa em `colony/allocation.py` (docstring) e no spec original (seção sobre política).

**Termo térmico desvia do plano original.**
A fórmula em `consumption.heating_consumption_kw` escala **tanto `loss_W` quanto `internal_gain`** por `thermal_factor` (envelope menor → perde menos). O plano original só escalava ganho e resultado, mas isso falhava o teste `workshop@-50°C` e era fisicamente inconsistente. **Não reverter sem entender o teste.**

**Histórico = listas paralelas indexadas por passo.**
`history["wind_ms"][k]` e `history["wind_generation_kw"][k]` referem-se ao mesmo passo `k` da simulação. Esse formato é deliberado: `prediction.py` (regressão item 1.3) e `analysis.py` (item 1.4) consomem essas listas paralelas diretamente. Não trocar para lista de dicts.

**Regressão linear no `prediction.py` recupera os coeficientes verdadeiros.**
O modelo físico em `generation.generate_wind` é `P = max(0, min(cap, 2.5·v - 7.5))`. Como `fit_wind_power_model` filtra pontos com `wind_generation_kw > 0` (ignora cut-in), a regressão sobre os dados simulados recupera quase exatamente `a=2.5, b=-7.5`. Isso é proposital — mostra a regressão funcionando corretamente e dá um output reproduzível para a demo.

## Workflow para adicionar features

Seguir o padrão TDD usado nas tasks já executadas:

1. Escrever teste em `tests/test_<module>.py` referenciando a função/classe que ainda não existe.
2. Rodar e confirmar RED (`ModuleNotFoundError` ou `AttributeError`).
3. Implementar o mínimo para passar.
4. Rodar suite **completa** (`python3 -m unittest discover`) — não só o teste novo, por causa do leakage de estado descrito acima.
5. Commit granular com mensagem em inglês iniciando por `feat:`, `fix:`, `docs:`, `test:`, `chore:`, `refactor:`.

Idioma das mensagens de commit: **inglês** (segue convenção do código). Conteúdo das mensagens descritivas pode mesclar inglês e português livremente.
