# Colônia Aurora — SIGER

**Sistema Integrado de Gerenciamento e Energia em Rede**

Simulação inteligente de uma colônia marciana desenvolvida em Python 3 puro (somente stdlib).
Projeto FIAP — Fase 3.

---

## Sumário

- [Colônia Aurora — SIGER](#colônia-aurora--siger)
  - [Sumário](#sumário)
  - [Como executar](#como-executar)
  - [Configuração](#configuração)
  - [Como funciona](#como-funciona)
    - [Loop de simulação](#loop-de-simulação)
    - [Sensores](#sensores)
    - [Módulos operacionais](#módulos-operacionais)
    - [Gerenciamento de energia](#gerenciamento-de-energia)
    - [Regressão linear](#regressão-linear)
    - [Gerador de números aleatórios (LCG)](#gerador-de-números-aleatórios-lcg)
    - [Eventos climáticos e falhas](#eventos-climáticos-e-falhas)
    - [Tripulação](#tripulação)
    - [Dashboard](#dashboard)
    - [Logger e CSV](#logger-e-csv)
  - [Estrutura do projeto](#estrutura-do-projeto)
  - [Estruturas de dados](#estruturas-de-dados)

---

## Como executar

**Pré-requisito:** Python 3.10+ (sem dependências externas).

```bash
python main.py
```

**Controles do dashboard:**

| Tecla | Ação |
|-------|------|
| `1` – `6` | Vai direto para a aba |
| `←` `→` | Navega entre abas |
| `P` | Pausa / retoma a simulação |
| `Q` | Encerra |

> Requer terminal com suporte a ANSI/cores de 24 bits e largura mínima de 100 colunas.
> O dashboard usa buffer de tela alternativo — ao sair, o terminal é restaurado automaticamente.

---

## Configuração

As três constantes no topo de `main.py` controlam o comportamento da simulação:

```python
TICK_RATE  = 0.001   # segundos por tick (0.001 = máximo, 0.5 = ~tempo real)
SPAWN_PROB = 0.02    # probabilidade de um novo módulo surgir a cada tick (2%)
SOL_TICKS  = 24      # quantos ticks formam um sol marciano completo
```

**Seed determinístico:** A simulação usa um LCG com seed fixo (padrão `42`). Para alterar:

```python
rng.set_seed(42)   # linha 12 de main.py — qualquer inteiro é válido
```

Com a mesma seed, dois runs produzem logs CSV bit-a-bit idênticos.

---

## Como funciona

### Loop de simulação

`SimulationLoop` roda em uma thread dedicada. A cada tick:

1. Incrementa o contador de tick e calcula o sol atual (`tick // SOL_TICKS`).
2. Todos os sensores leem e publicam valores no `DataStorage`.
3. Todos os módulos ativos executam `energy_logic()`, ajustando consumo conforme o nível de energia atual.
4. O `EnergyManager` recalcula geração, consumo, bateria, slope e nível de energia.
5. O `EventManager` processa eventos ativos e rola novos eventos/falhas.
6. A tripulação executa um tick (saúde + reparos em andamento).
7. O logger grava uma linha no CSV.

A thread do dashboard lê o `DataStorage` de forma independente — o singleton é o ponto de sincronização entre as duas threads.

```
tick
 ├── SensorManager.do_all()        → publica sensor.*
 ├── ModuleManager.run_all()       → atualiza consumption_kw de cada módulo
 ├── EnergyManager.calculate()     → publica energy.*
 ├── EventManager.check_and_roll() → publica event.*
 ├── CrewManager.do_all()          → atualiza saúde e reparos
 └── Logger.log()                  → grava linha no CSV
```

---

### Sensores

Sete sensores, todos derivados de `Sensor`, publicam em `DataStorage` a cada tick:

| Sensor | Chave | Faixa | Notas |
|--------|-------|-------|-------|
| `TemperatureSensor` | `sensor.temperature` | −140 a +30 °C | Variação aleatória ±2 °C/tick |
| `WindSpeedSensor` | `sensor.wind_speed` | 0 a 100 m/s | Variação ±2 m/s/tick |
| `DustSensor` | `sensor.dust` | 0,0 a 1,0 | Variação ±0,02/tick |
| `SolarIrradianceSensor` | `sensor.solar_irradiance` | 0 a 590 W/m² | Modulada pelo ciclo dia/noite e poeira |
| `DayNightSensor` | `sensor.day_phase` | 0,0 a 1,0 | Calculado deterministicamente por tick |
| `RainSensor` | `sensor.rain` | 0,0 a 1,0 | Sem uso ativo na v atual |
| `WindDirectionSensor` | `sensor.wind_direction` | 0 a 360° | Sem uso ativo na v atual |

**Ciclo dia/noite marciano:**

```
angle     = (tick % SOL_TICKS) / SOL_TICKS × 2π
day_phase = (cos(angle − π) + 1) / 2

tick =  0  → phase 0,00  (meia-noite)
tick =  6  → phase 0,50  (amanhecer)
tick = 12  → phase 1,00  (meio-dia — pico solar)
tick = 18  → phase 0,50  (entardecer)
```

**Modificadores de evento aplicados após leitura base:**

| Evento | Irradiância | Temperatura | Vento | Poeira |
|--------|-------------|-------------|-------|--------|
| `ColdFront` | × 0,50 | − 30 °C | — | — |
| `Sandstorm` | × 0,15 | — | + 40 m/s | + 0,50 |

---

### Módulos operacionais

O sistema opera com 14 tipos de módulos divididos em dois grupos:

**Geração de energia:**

| Módulo | Tipo | Comportamento |
|--------|------|---------------|
| `NuclearModule` | nuclear | 40 kW constante; −20% em SURPLUS |
| `SolarModule` | solar | `área × irradiância × 22%` ÷ 1000 |
| `WindModule` | wind | Curva cúbica `0,0003 × v³`; embandeirado 50–100 m/s; desliga ≥ 100 m/s |

**Consumo (por ordem de prioridade):**

| Módulo | P | CRITICAL | LOW | NOMINAL/HIGH | SURPLUS |
|--------|---|----------|-----|--------------|---------|
| Command | 1 | 3,0 kW mín | escala | 5,0 kW | 5,0 kW |
| ECLSS | 2 | 12 kW mín | escala | ~20 kW* | ~20 kW* |
| Habitat | 3 | escala | escala | 15 kW | 18 kW |
| Solar | 4 | 2 kW | 2 kW | 2 kW | 2 kW |
| Nuclear | 5 | 3 kW | 3 kW | 3 kW | 3 kW |
| Wind | 6 | 1 kW | 1 kW | 1 kW | 1 kW |
| Comms | 7 | escala | escala | 8 kW | 8 kW |
| Medical | 8 | escala | escala | 10 kW | 10 kW |
| Food | 9 | **desliga** | 4 kW | 12 kW | 12 kW |
| Logistics | 10 | **desliga** | 3 kW | 6 kW | 6 kW |
| ISRU | 11 | **desliga** | **desliga** | 18 kW | 21,6 kW |
| Workshop | 12 | 3 kW | 5 kW | 8 kW | 8 kW |
| Lab | 13 | **desliga** | **desliga** | 10 kW | 10 kW |
| Sensors | 14 | escala | escala | 3 kW | 3 kW |

*ECLSS escala também com temperatura ambiente e número de módulos ativos.*

**Power factor (escala contínua):** Os módulos marcados como "escala" aplicam um fator baseado na carga atual da bateria, tornando a resposta gradual em vez de binária:

```
bateria ≥ 50%  → factor = 1,00  (potência nominal)
bateria 30–50% → factor = 0,70 – 1,00 (interpolação linear)
bateria 10–30% → factor = 0,40 – 0,70 (interpolação linear)
bateria < 10%  → factor = 0,20  (mínimo absoluto)
```

**Spawn dinâmico:** A cada tick existe uma probabilidade `SPAWN_PROB` de um novo módulo ser adicionado. Usa shuffle-bag — todos os tipos passam antes de repetir, garantindo variedade. Quando o nível é `CRITICAL`, o sistema força o spawn de um módulo de geração.

---

### Gerenciamento de energia

`EnergyManager` calcula a cada tick:

1. **Geração total** = solar + nuclear + eólica (considerando estado dos módulos ativos)
2. **Consumo total** = soma de `consumption_kw` de todos os módulos ativos
3. **Delta** = geração − consumo
4. **Bateria** = clampada em [0, 1000 kWh]; exibida como percentual
5. **Slope** via regressão linear sobre os últimos 48 deltas
6. **Nível de energia** (veja tabela abaixo)
7. **Alerta** de texto publicado em `energy.alert`

**Tabela de níveis (combinação de bateria + slope preditivo):**

| Nível | Condição base | Escalonamento por slope |
|-------|---------------|------------------------|
| `CRITICAL` | bateria < 20% | slope ≤ −2,0 eleva LOW → CRITICAL |
| `LOW` | bateria < 40% | slope ≤ −0,5 eleva NOMINAL → LOW; slope ≤ −2,0 eleva HIGH/SURPLUS → LOW |
| `NOMINAL` | delta ≤ 0, bateria 40–90% | slope ≤ −0,5 rebaixa HIGH/SURPLUS → NOMINAL |
| `HIGH` | delta > 0, bateria 40–90% | — |
| `SURPLUS` | bateria > 90% | — |

O sistema é **preditivo**: uma bateria em 55% com tendência de −3,1 kW/tick já aciona `LOW`, antes de a bateria cair abaixo de 40%.

**Geração eólica — curva de potência:**

```
vento < 5 m/s      → 0 kW          (abaixo do cut-in)
5 ≤ vento < 50     → 0,0003 × v³   (curva cúbica)
50 ≤ vento < 100   → valor_furl × 0,3  (embandeirado — 70% de redução)
vento ≥ 100 m/s    → 0 kW          (parada de emergência)
```

---

### Regressão linear

Implementação manual de gradiente descendente — sem numpy ou scipy.

```
fit(X, y):
    para cada iteração:
        y_hat = w·X + b
        dw = Σ(erro × X) / n    (clampado em [-1, 1])
        db = Σerro / n           (clampado em [-1, 1])
        w -= lr × dw
        b -= lr × db
    se os pesos divergirem (NaN/inf): reset para zero
```

**Parâmetros:** `learning_rate=0.01`, `n_iterations=1000`. O clamp de gradiente previne overflow em séries de energia voláteis.

**Uso no sistema:** Treina sobre os últimos 48 valores de `energy.delta`. O slope resultante informa o nível de energia e o alerta textual.

A classe `Metrics` também expõe `mean_squared_error`, `r2_score` e `mean_absolute_error` para análise externa dos logs.

---

### Gerador de números aleatórios (LCG)

Toda aleatoriedade da simulação passa por `RandomLCG` — um gerador congruencial linear implementado do zero, sem usar o módulo `random` do Python.

**Fórmula:**

```
X_{n+1} = (a × X_n + c) mod m

a = 1_664_525     (Numerical Recipes)
c = 1_013_904_223
m = 2^32
```

**API disponível:**

| Método | Descrição |
|--------|-----------|
| `set_seed(n)` | Define a seed (reinicia sequência) |
| `random()` | Float em [0, 1) |
| `uniform(a, b)` | Float em [a, b] |
| `randint(low, high)` | Inteiro em [low, high] (inclusive) |
| `choice(seq)` | Elemento aleatório de uma sequência |
| `shuffle(array)` | Embaralha in-place (Fisher-Yates) |

**Singleton compartilhado:** `colonia_aurora/seed/__init__.py` exporta `rng`, uma única instância usada por todos os módulos da simulação. Definir a seed em `main.py` antes de qualquer import garante que toda a simulação seja determinística.

---

### Eventos climáticos e falhas

`EventManager` processa a cada tick:

**Eventos climáticos** (mutuamente exclusivos, um ativo por vez):

| Evento | Prob./tick | Duração | Efeito |
|--------|-----------|---------|--------|
| `ColdFront` | 3% | 12–48 ticks | Irradiância −50%, temperatura −30 °C |
| `Sandstorm` | 2% | 6–72 ticks | Irradiância −85%, vento +40 m/s, poeira +0,5 |

**Falhas de equipamento** (independentes por módulo):

- Probabilidade: 0,5% por módulo ativo por tick
- Duração do reparo: 2–12 ticks (aleatório)
- Ao ocorrer: módulo fica `broken=True`, `active=False`
- Sistema tenta alocar um engenheiro/técnico disponível automaticamente

---

### Tripulação

Quatro membros iniciais: Ana (engineer), Bruno (medic), Carla (scientist), Diego (commander).

| Estado | Condição |
|--------|----------|
| `idle` | Disponível |
| `repairing` | Executando reparo de módulo |
| `incapacitated` | Saúde chegou a 0 |

**Mecânica de saúde:**
- Nível `CRITICAL`: −5% de saúde por tick
- Qualquer outro nível: +5% de saúde por tick (recuperação)
- Somente `engineer` e `technician` podem ser designados para reparos

---

### Dashboard

Interface TUI de 6 abas, renderizada em buffer alternativo (não polui o histórico do terminal):

| Aba | Conteúdo |
|-----|----------|
| **1 — Visão Geral** | Nível de energia, bateria, delta atual, alerta, evento ativo |
| **2 — Energia** | Geração solar/eólica/nuclear, consumo, histórico sparkline |
| **3 — Sensores** | Temperatura, vento, irradiância, poeira, fase do dia |
| **4 — Módulos** | Lista de módulos com status, consumo e prioridade |
| **5 — Eventos** | Log dos últimos eventos climáticos e falhas |
| **6 — Tripulação** | Nome, função, saúde e status de cada membro |

O rodapé exibe tick atual, sol marciano e tick rate configurado.

---

### Logger e CSV

A cada tick, uma linha é acrescentada ao arquivo `logs/<timestamp>.csv`:

```
tick, sol, sensor.temperature, sensor.wind_speed, sensor.solar_irradiance,
sensor.day_phase, sensor.dust, energy.generated, energy.solar_gen,
energy.wind_gen, energy.nuclear_gen, energy.consumed, energy.delta,
energy.battery, energy.predicted_delta, energy.slope, energy.level,
event.active, energy.alert
```

**Comparar dois runs para verificar determinismo:**

```bash
python -c "
import csv
f1, f2 = 'logs/run_a.csv', 'logs/run_b.csv'
with open(f1) as a, open(f2) as b:
    r1, r2 = list(csv.reader(a)), list(csv.reader(b))
diffs = [i+1 for i,(a,b) in enumerate(zip(r1,r2)) if a!=b]
print('IDENTICAL' if not diffs else f'DIFFER at rows: {diffs[:20]}')
"
```

---

## Estrutura do projeto

```
colonia_aurora/
├── core/
│   ├── item.py          Base class para Sensor, Module, Event, CrewMember
│   ├── manager.py       GenericManager com lista interna
│   └── storage.py       DataStorage — singleton HashMap + histórico por chave
├── seed/
│   ├── linear_congruential_generator.py   Implementação do LCG
│   └── __init__.py      Exporta o singleton `rng`
├── sensors/
│   ├── sensor.py        Classe base Sensor
│   └── sensors.py       7 sensores concretos + SensorManager
├── modules/
│   ├── module.py        Classe base Module (com _power_factor())
│   └── modules.py       14 módulos concretos + ModuleManager (heap + shuffle-bag)
├── energy/
│   ├── regression.py    LinearRegression (gradiente descendente) + Metrics
│   └── energy_manager.py  Geração, consumo, bateria, nível, alerta
├── events/
│   ├── event.py         Classe base Event
│   └── events.py        ColdFront, Sandstorm, EquipmentFailure + EventManager
├── crew/
│   └── crew.py          CrewMember + CrewManager
├── display/
│   └── dashboard.py     TUI multi-aba com buffer alternativo
└── logger.py            Grava CSV em logs/

main.py                  Entry point — configura e inicia simulação + dashboard
```

---

## Estruturas de dados

| Estrutura | Onde | Para quê |
|-----------|------|----------|
| `dict` (HashMap) | `DataStorage` singleton | Acesso O(1) a todos os valores correntes: sensores, energia, eventos |
| Lista com histórico | `DataStorage._history` | Série temporal por chave — alimenta a regressão linear |
| Min-Heap (`heapq`) | `ModuleManager._heap` | Processa módulos em ordem de prioridade (P1 = mais crítico) |
| Shuffle-bag (lista embaralhada) | `ModuleManager._spawn_bag` | Spawn balanceado — todos os tipos antes de repetir |
| Herança polimórfica | `Item → Sensor / Module / Event / CrewMember` | `do()` especializado em cada subclasse |
| Singleton | `DataStorage`, `rng` | Compartilhados entre thread de simulação e thread do dashboard |
