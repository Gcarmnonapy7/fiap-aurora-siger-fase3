# AURORA CORE — Port para inglês + módulos de decisão, previsão e análise

> **Para agentes:** USAR `superpowers:executing-plans` ou `superpowers:subagent-driven-development` para implementar este plano. Steps com `- [ ]` para tracking.

**Goal:** Reescrever o pacote `colonia/` (pt) para `colony/` (en), adicionar suporte a randomização não-determinística, e implementar 3 módulos novos (`decision.py`, `prediction.py`, `analysis.py`) que cobrem os itens 1.2, 1.3 e 1.4 do enunciado oficial.

**Architecture:** Port mecânico bottom-up por camada (constants → tree/modules → climate → ... → simulator → main), mantendo `colonia/` antigo vivo até cleanup final para preservar a suite. Depois, 3 módulos novos na camada 6 que consomem o `history` produzido pelo simulador. Documentação fica em pt; código em en.

**Tech Stack:** Python 3.12 stdlib apenas (`math`, `random`, `collections.deque`, `argparse`), `unittest` da stdlib. Sem dependências externas — restrição do enunciado.

---

## Decisões arquiteturais

- **Idioma do código:** todo em inglês (módulos, classes, funções, variáveis, chaves de dict, valores de string usados como dados, nomes de módulos exibidos).
- **Idioma da documentação:** pt-BR (README, comentários longos de explicação física, este plano, spec original).
- **Randomização:** `run_simulation(seed=42)` continua sendo o default. `run_simulation(seed=None)` pula `random.seed()` e usa entropia do sistema. Os testes existentes setam seed=42 explicitamente em `setUp`, então não quebram.
- **Loop "contínuo" da proposta AURORA CORE:** materializa-se como `--horizon N` no CLI (horizonte configurável de passos). Não há `time.sleep(300)` real — quebra UX em demo acadêmica e não atende avaliação.
- **`auto_module.py`:** **recusado**. Gerar arquivos `.py` vazios em runtime é decorativo e não atende nenhum dos 5 critérios de avaliação. Substituído pela camada de "evolução real": `prediction.py` aprende coeficientes do histórico (sistema reativo → preditivo, item 5 do enunciado).
- **Logs em arquivo:** opcional via `--log-file PATH`. Default: histórico só na memória.

## Glossário de tradução PT → EN

### Arquivos
| pt | en |
|---|---|
| `constantes.py` | `constants.py` |
| `modulos.py` | `modules.py` |
| `arvore.py` | `tree.py` |
| `hierarquias.py` | `hierarchies.py` |
| `estado.py` | `state.py` |
| `clima.py` | `climate.py` |
| `geracao.py` | `generation.py` |
| `consumo.py` | `consumption.py` |
| `alocacao.py` | `allocation.py` |
| `simulador.py` | `simulator.py` |

### Identificadores principais
| pt | en |
|---|---|
| `No` | `Node` |
| `adicionar_filho` | `add_child` |
| `eh_folha` | `is_leaf` |
| `folhas` | `leaves` |
| `percorrer_dfs` | `traverse_dfs` |
| `percorrer_bfs` | `traverse_bfs` |
| `buscar` | `find` |
| `imprimir` | `pretty_print` |
| `nome` (campo) | `name` |
| `filhos` | `children` |
| `modulo` (campo) | `module` |
| `MODULOS` | `MODULES` |
| `encontrar_modulo` | `find_module` |
| `construir_arvore_funcional` | `build_functional_tree` |
| `construir_arvore_criticidade` | `build_criticality_tree` |
| `EstadoTempestade` | `StormState` |
| `avancar` | `advance` |
| `amostrar_vento` | `sample_wind` |
| `amostrar_temperatura` | `sample_temperature` |
| `calcular_tau` | `compute_tau` |
| `transmissao_solar` | `solar_transmission` |
| `atualizar_fator_paineis` | `update_panel_factor` |
| `gerar_solar` | `generate_solar` |
| `gerar_eolico` | `generate_wind` |
| `gerar_nuclear` | `generate_nuclear` |
| `consumo_aquecimento_kw` | `heating_consumption_kw` |
| `consumo_atual_kw` | `current_consumption_kw` |
| `alocar_energia` | `allocate_energy` |
| `GERADORES` | `GENERATORS` |
| `estado_inicial` | `initial_state` |
| `rodar_simulacao` | `run_simulation` |
| `passo` | `step` |
| `curva_diurna_solar` | `solar_daytime_curve` |

### Constantes
| pt | en |
|---|---|
| `HORIZONTE_SOLS` | `HORIZON_SOLS` |
| `HORAS_POR_SOL` | `HOURS_PER_SOL` |
| `TOTAL_PASSOS` | `TOTAL_STEPS` |
| `FATOR_SAZONAL` | `SEASONAL_FACTOR` |
| `V_RUIDO_SIGMA` | `V_NOISE_SIGMA` |
| `PROB_BASE_POR_SOL` | `BASE_PROB_PER_SOL` |
| `DURACAO_HORAS` | `DURATION_HOURS` |
| `LIMIAR_VENTO_BONUS` | `WIND_BONUS_THRESHOLD` |
| `FATOR_PERIHELIO` | `PERIHELION_FACTOR` |
| `FORCAR_EVENTO_DIDATICO` | `FORCE_DIDACTIC_EVENT` |
| `SOL_EVENTO_DIDATICO` | `DIDACTIC_EVENT_SOL` |
| `HORA_EVENTO_DIDATICO` | `DIDACTIC_EVENT_HOUR` |
| `TAU_VENTO_FATOR` | `TAU_WIND_FACTOR` |
| `TAU_VENTO_LIMIAR` | `TAU_WIND_THRESHOLD` |
| `PERDA_PAINEIS_POR_SOL` | `PANEL_LOSS_PER_SOL` |
| `PROB_LIMPEZA_POR_SOL` | `CLEANING_PROB_PER_SOL` |
| `LIMPEZA_RECUPERACAO` | `CLEANING_RECOVERY` |
| `PISO_FATOR_PAINEIS` | `PANEL_FACTOR_FLOOR` |
| `T_MEDIA` | `T_MEAN` |
| `A_DIURNA` | `A_DAILY` |
| `A_SAZONAL` | `A_SEASONAL` |
| `PHI_DIURNO` | `PHI_DAILY` |
| `SOLS_POR_ANO_MARCIANO` | `SOLS_PER_MARS_YEAR` |
| `T_RUIDO_SIGMA` | `T_NOISE_SIGMA` |
| `U_ISOLAMENTO` | `U_INSULATION` |
| `T_ALVO_INTERNA` | `T_TARGET_INTERNAL` |
| `GANHO_INTERNO_W` | `INTERNAL_GAIN_W` |
| `ETA_AQUECEDOR` | `ETA_HEATER` |
| `BATERIA_CAPACIDADE_KWH` | `BATTERY_CAPACITY_KWH` |
| `BATERIA_CARGA_INICIAL_KWH` | `BATTERY_INITIAL_CHARGE_KWH` |
| `BATERIA_RESERVA_EMERGENCIA_FRACAO` | `BATTERY_EMERGENCY_RESERVE_FRACTION` |

### Chaves de dict
| pt | en |
|---|---|
| `nome` (em módulo) | `name` |
| `tipo` | `type` |
| `consumo_por_modo` | `consumption_by_mode` |
| `escalona_com_excedente` | `scales_with_surplus` |
| `fator_termico` | `thermal_factor` |
| `modo_atual` | `current_mode` |
| `capacidade_max_kw` | `max_capacity_kw` |
| `vento_ms` | `wind_ms` |
| `temperatura_c` | `temperature_c` |
| `tempestade` | `storm` |
| `tau` | `tau` |
| `fator_paineis` | `panel_factor` |
| `sol` | `sol` |
| `hora` | `hour` |
| `carga_atual_kwh` | `current_charge_kwh` |
| `capacidade_max_kwh` | `max_capacity_kwh` |
| `reserva_emergencia_kwh` | `emergency_reserve_kwh` |
| `geracao_solar_kw` | `solar_generation_kw` |
| `geracao_eolica_kw` | `wind_generation_kw` |
| `geracao_nuclear_kw` | `nuclear_generation_kw` |
| `geracao_total_kw` | `total_generation_kw` |
| `consumo_total_kw` | `total_consumption_kw` |
| `bateria_carga_kwh` | `battery_charge_kwh` |
| `modos_resumo` | `modes_summary` |
| `alertas` | `alerts` |

### Valores literais
| pt | en |
|---|---|
| `"adequado"` | `"adequate"` |
| `"minimo"` | `"minimum"` |
| `"excedente"` | `"surplus"` |
| `"desligado"` | `"off"` |
| `"consumidor"` | `"consumer"` |
| `"gerador_solar"` | `"solar_generator"` |
| `"gerador_eolico"` | `"wind_generator"` |
| `"gerador_nuclear"` | `"nuclear_generator"` |
| `"limpo"` | `"clear"` |
| `"leve"` | `"light"` |
| `"moderada"` | `"moderate"` |
| `"grave"` | `"severe"` |
| `"Vital"` | `"Vital"` |
| `"Sustento"` | `"Sustenance"` |
| `"Expansão"` | `"Expansion"` |
| `"Colônia Aurora Siger"` | `"Aurora Siger Colony"` |
| `"Energia"` | `"Energy"` |
| `"Suporte à Vida"` | `"Life Support"` |
| `"Comando"` | `"Command"` |
| `"Operações"` | `"Operations"` |
| `"Comando e Controle"` | `"Command and Control"` |
| `"Suporte de Vida (ECLSS)"` | `"Life Support (ECLSS)"` |
| `"Habitação"` | `"Habitat"` |
| `"Energia Solar"` | `"Solar Power"` |
| `"Energia Nuclear"` | `"Nuclear Power"` |
| `"Energia Eólica"` | `"Wind Power"` |
| `"Comunicações"` | `"Communications"` |
| `"Suporte Médico"` | `"Medical Support"` |
| `"Produção de Alimentos"` | `"Food Production"` |
| `"Logística e Armazenamento"` | `"Logistics and Storage"` |
| `"ISRU (Recursos Locais)"` | `"ISRU (Local Resources)"` |
| `"Oficina e Manutenção"` | `"Workshop and Maintenance"` |
| `"Laboratório Científico"` | `"Science Lab"` |

---

## Fase 1: Port `colonia/` → `colony/`

Estratégia: bottom-up, manter `colonia/` vivo até o cleanup, sobrescrever `tests/test_<nome>.py` em pt deletando-os e criando arquivos novos em en. A cada task: criar módulo + testes em en, validar suite inteira, commitar.

### Task 1: Port `constants.py`

**Arquivos:**
- Criar: `colony/__init__.py` (vazio)
- Criar: `colony/constants.py`
- Criar: `tests/test_constants.py`

- [ ] Implementar `colony/constants.py` traduzindo `colonia/constantes.py` integralmente conforme glossário.
- [ ] Implementar `tests/test_constants.py` (espelhando `tests/test_modulos.py` no espírito — testar `solar_daytime_curve(hour)` em valores-chave).
- [ ] Rodar `python3 -m unittest discover -v` → 69 (pt) + N (en) verdes.
- [ ] Commitar: `feat(en): port constants.py to English`.

### Task 2: Port `tree.py` (classe `Node`)

**Arquivos:**
- Criar: `colony/tree.py`
- Criar: `tests/test_tree.py`

- [ ] Implementar `colony/tree.py` com `class Node` (`add_child`, `is_leaf`, `leaves`, `traverse_dfs`, `traverse_bfs`, `find`, `pretty_print`, atributos `name`, `children`, `module`).
- [ ] Implementar `tests/test_tree.py` reproduzindo os testes de `tests/test_arvore.py`.
- [ ] Validar suite.
- [ ] Commit: `feat(en): port tree.py with Node class`.

### Task 3: Port `modules.py`

**Arquivos:**
- Criar: `colony/modules.py`
- Criar: `tests/test_modules.py`

- [ ] Traduzir `MODULES` (lista plana de 13 módulos) e função `find_module(id_)`.
- [ ] Validar suite.
- [ ] Commit: `feat(en): port modules.py with MODULES list`.

### Task 4: Port `state.py`

**Arquivos:**
- Criar: `colony/state.py`
- Criar: `tests/test_state.py`

- [ ] Implementar `initial_state()` retornando `(climate, battery, history)`.
- [ ] Testes: validar estruturas iniciais + chaves do `history`.
- [ ] Validar suite.
- [ ] Commit: `feat(en): port state.py`.

### Task 5: Port `climate.py`

**Arquivos:**
- Criar: `colony/climate.py`
- Criar: `tests/test_climate.py`

- [ ] Implementar `compute_tau`, `solar_transmission`, `update_panel_factor`, `sample_wind`, `sample_temperature`, `class StormState`.
- [ ] Testes (com `random.seed(42)` em `setUp`).
- [ ] Validar.
- [ ] Commit: `feat(en): port climate.py with StormState FSM`.

### Task 6: Port `hierarchies.py`

**Arquivos:**
- Criar: `colony/hierarchies.py`
- Criar: `tests/test_hierarchies.py`

- [ ] `build_functional_tree`, `build_criticality_tree`.
- [ ] Testes: estrutura, contagem de folhas, compartilhamento de referência entre as duas árvores.
- [ ] Validar.
- [ ] Commit: `feat(en): port hierarchies.py`.

### Task 7: Port `generation.py`

**Arquivos:** `colony/generation.py`, `tests/test_generation.py`.

- [ ] `generate_solar`, `generate_wind`, `generate_nuclear`.
- [ ] Validar.
- [ ] Commit: `feat(en): port generation.py`.

### Task 8: Port `consumption.py`

**Arquivos:** `colony/consumption.py`, `tests/test_consumption.py`.

- [ ] `heating_consumption_kw`, `current_consumption_kw`.
- [ ] **Atenção:** preservar fórmula térmica corrigida do commit `f732386` (ambos `perda_W` e `ganho_interno` escalam por `thermal_factor`).
- [ ] Validar.
- [ ] Commit: `feat(en): port consumption.py with thermal model`.

### Task 9: Port `allocation.py`

**Arquivos:** `colony/allocation.py`, `tests/test_allocation.py`.

- [ ] `allocate_energy(criticality_tree, supply_kw, climate)` com 4 etapas.
- [ ] Constante `GENERATORS = ("solar_generator", "wind_generator", "nuclear_generator")`.
- [ ] Testes resetam `current_mode` em `setUp` para evitar leakage.
- [ ] Validar.
- [ ] Commit: `feat(en): port allocation.py with 4-stage load shedding`.

### Task 10: Port `simulator.py` + suporte a `seed=None`

**Arquivos:** `colony/simulator.py`, `tests/test_simulator.py`.

- [ ] `step(climate, battery, history, trees, storm_state, last_wind_24h)`.
- [ ] `run_simulation(seed=42)` — se `seed is not None`, chama `random.seed(seed)`. Se `None`, pula.
- [ ] Testes: `seed=42` continua determinístico (compara um valor exato do history); `seed=None` produz outputs diferentes em runs consecutivas.
- [ ] Validar.
- [ ] Commit: `feat(en): port simulator.py and add seed=None for non-deterministic runs`.

### Task 11: Port `main.py` + CLI

**Arquivos:** `main.py` (sobrescreve).

- [ ] `argparse` com flags `--seed N` (default 42), `--random` (seta seed=None), `--horizon N` (default `TOTAL_STEPS=168`), `--log-file PATH`, `--quiet`.
- [ ] Importar de `colony.*`.
- [ ] Continuar imprimindo as duas árvores e o resumo do histórico.
- [ ] Validar `python3 main.py` e `python3 main.py --random`.
- [ ] Commit: `feat(en): port main.py with CLI flags --seed --random --horizon --log-file`.

---

## Fase 2: Módulos novos (decisão, previsão, análise)

### Task 12: `decision.py` — regras simples do enunciado (item 1.2)

**Arquivos:** `colony/decision.py`, `tests/test_decision.py`.

Objetivo: expor regras lógicas no formato exato do enunciado (`se energia < 50 → reduzir consumo`), separadas da política mais complexa de `allocation.py`. Permite o relatório acadêmico mostrar entrada/saída triviais.

**API:**
```python
def evaluate_rules(snapshot: dict) -> list[str]:
    """Recebe {'energy_kw': float, 'consumption_kw': float, 'storm': str, ...}
    e retorna lista de ações textuais."""

def priority_order() -> list[str]:
    """Retorna ordem de prioridade dos sistemas (Vital → Sustenance → Expansion)."""
```

**Regras a implementar:**
1. `energy_kw < 50` → `"ALERTA: reduzir consumo"`
2. `energy_kw < 50 and consumption_kw > 70` → `"ATIVAR MODO ECONOMIA"`
3. `storm in ("moderate", "severe")` → `"ALERTA CLIMÁTICO: priorizar Vital e Sustento"`
4. `consumption_kw > energy_kw` (sem bateria) → `"EMERGÊNCIA ENERGÉTICA"`

- [ ] Testes para cada regra individualmente + combinações.
- [ ] Validar.
- [ ] Commit: `feat: add decision.py with rule-based evaluations`.

### Task 13: `prediction.py` — regressão linear manual (item 1.3)

**Arquivos:** `colony/prediction.py`, `tests/test_prediction.py`.

Objetivo: implementar y = ax + b manualmente sem numpy/sklearn. Treinar sobre `history["wind_ms"]` × `history["wind_generation_kw"]` e prever potência eólica futura.

**API:**
```python
def linear_regression(xs: list[float], ys: list[float]) -> tuple[float, float]:
    """Devolve (a, b) tal que y ≈ a*x + b minimizando SSE.
    Fórmula: a = Σ((x-x̄)(y-ȳ)) / Σ((x-x̄)²), b = ȳ - a*x̄.
    Levanta ValueError se len(xs) < 2 ou Σ((x-x̄)²) == 0."""

def predict(a: float, b: float, x: float) -> float:
    return a * x + b

def fit_wind_power_model(history: dict) -> tuple[float, float]:
    """Filtra pontos onde wind_generation_kw > 0 (cut-in) e treina."""

def predict_next_wind_power(history: dict, wind_forecast_ms: float) -> float:
    """Treina e prevê em uma chamada."""
```

- [ ] Testes do exemplo do enunciado: `vento=[8,10,12]`, `energia=[20,25,30]`, `predict(11) ≈ 27.5`.
- [ ] Teste com dados reais simulados (rodar simulação 7 sóis, treinar, validar R² razoável).
- [ ] Edge cases: lista vazia, lista de 1 ponto, vento constante.
- [ ] Validar.
- [ ] Commit: `feat: add prediction.py with manual linear regression for wind power`.

### Task 14: `analysis.py` — comparação geração×consumo + log (item 1.4)

**Arquivos:** `colony/analysis.py`, `tests/test_analysis.py`.

**API:**
```python
def analyze_balance(generation_kw: float, consumption_kw: float) -> dict:
    """Retorna {'status': 'risk'|'surplus'|'balanced', 'message': str, 'delta_kw': float}."""

def summarize_history(history: dict) -> dict:
    """Métricas agregadas: avg_generation, avg_consumption, total_alerts, storm_hours, etc."""

def write_log(history: dict, path: str) -> None:
    """Serializa o histórico passo-a-passo em texto legível em data/colony_log.txt."""
```

Regras de `analyze_balance`:
- `generation > consumption * 1.1` → `"SUGESTÃO: armazenar energia excedente"` (`status="surplus"`)
- `generation < consumption` → `"ALERTA: consumo maior que geração"` (`status="risk"`)
- caso contrário → `"BALANCEADO"` (`status="balanced"`)

- [ ] Testes dos 3 estados.
- [ ] Teste de `write_log` com `tempfile.TemporaryDirectory`.
- [ ] Validar.
- [ ] Commit: `feat: add analysis.py with balance evaluation and log writer`.

### Task 15: Integrar os 3 módulos novos em `main.py`

- [ ] Ao final da simulação, `main.py` chama:
  - `analysis.summarize_history(history)` e imprime as métricas.
  - `prediction.fit_wind_power_model(history)` e imprime a reta + previsão para `wind=11 m/s` (exemplo do enunciado).
  - `decision.evaluate_rules({"energy_kw": last_generation, "consumption_kw": last_consumption, "storm": last_storm})` e imprime alertas.
  - Se `--log-file PATH`, chama `analysis.write_log(history, path)`.
- [ ] Validar visualmente `python3 main.py` produz saída coerente.
- [ ] Commit: `feat: integrate decision/prediction/analysis into main.py`.

---

## Fase 3: Cleanup e documentação

### Task 16: Deletar pacote antigo

- [ ] `rm -r colonia/`
- [ ] `rm tests/test_alocacao.py tests/test_arvore.py tests/test_clima.py tests/test_consumo.py tests/test_geracao.py tests/test_hierarquias.py tests/test_modulos.py tests/test_simulador.py`
- [ ] Rodar suite EN → todos passam.
- [ ] Rodar `python3 main.py` → saída coerente.
- [ ] Commit: `chore: remove legacy colonia/ package and pt test files`.

### Task 17: Atualizar `CLAUDE.md` (pt)

- [ ] Reescrever seção sobre "Identificadores em português intencionalmente" para nova convenção: **código em inglês**, **docs em pt-BR**.
- [ ] Atualizar exemplos de paths (`colonia/` → `colony/`).
- [ ] Atualizar exemplos de testes.
- [ ] Adicionar referência aos 3 módulos novos.
- [ ] Commit: `docs: update CLAUDE.md to reflect EN code convention`.

### Task 18: Atualizar `README.md` (pt)

- [ ] Atualizar estrutura do repositório.
- [ ] Documentar novas flags do CLI.
- [ ] Adicionar seção sobre os 3 módulos novos (decisão, previsão, análise) com exemplos de entrada/saída conforme enunciado oficial.
- [ ] Atualizar exemplo de saída.
- [ ] Commit: `docs: update README with new modules and CLI flags`.

---

## Critérios de aceitação

1. `python3 -m unittest discover -v` passa com 100% verde, sem nenhum import de `colonia.*`.
2. `python3 main.py` imprime: árvores em EN, resumo da simulação, alertas de decisão, previsão eólica, balanço de energia.
3. `python3 main.py --random` produz outputs diferentes em runs sucessivas.
4. `python3 main.py --log-file data/colony_log.txt` cria arquivo legível.
5. `enunciado.md` itens 1.1, 1.2, 1.3, 1.4 todos demonstráveis no programa rodando.
6. `CLAUDE.md` e `README.md` atualizados e coerentes com o estado novo.
