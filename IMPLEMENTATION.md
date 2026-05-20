# Colônia Aurora — Guia de Implementação

> Arquivo de referência para implementação completa do sistema.  
> Linguagem: **Python 3**. Sem bibliotecas externas — apenas `heapq`, `math`, `random`, `time`, `csv`, `os`, `sys`, `functools` da stdlib.

---

## Estrutura de Arquivos

```
colonia_aurora/
├── main.py
├── core/
│   ├── __init__.py
│   ├── item.py          # classe base Item com @total_ordering
│   ├── manager.py       # GenericManager
│   └── storage.py       # DataStorage Singleton
├── sensors/
│   ├── __init__.py
│   ├── sensor.py        # Sensor base
│   └── sensors.py       # TemperatureSensor, WindSensor, SolarSensor, RainSensor, WindDirectionSensor, DayNightSensor
├── modules/
│   ├── __init__.py
│   ├── module.py        # Module base
│   └── modules.py       # todos os 14 módulos concretos
├── energy/
│   ├── __init__.py
│   ├── regression.py    # LinearRegression (implementação manual)
│   └── energy_manager.py
├── events/
│   ├── __init__.py
│   ├── event.py         # Event base
│   └── events.py        # ColdFront, Sandstorm, EquipmentFailure
├── crew/
│   ├── __init__.py
│   └── crew.py          # CrewMember + CrewManager
├── display/
│   ├── __init__.py
│   └── dashboard.py     # terminal dashboard com abas (← →)
└── logger.py            # Logger CSV + console
```

---

## Ordem de Implementação

Implemente **nesta sequência** — cada etapa depende da anterior:

1. `core/item.py`
2. `core/storage.py`
3. `core/manager.py`
4. `sensors/sensor.py` + `sensors/sensors.py`
5. `modules/module.py` + `modules/modules.py` (apenas P1 e P2 primeiro para testar)
6. `energy/regression.py`
7. `energy/energy_manager.py`
8. `events/event.py` + `events/events.py`
9. `crew/crew.py`
10. `logger.py`
11. `modules/modules.py` (completar P3–P14)
12. `main.py` (loop principal)
13. `display/dashboard.py`

---

## Especificações

### `core/item.py` — Classe Base

- Decorator `@functools.total_ordering` obrigatório.
- Subclasses **devem** implementar `__eq__` e `__lt__` com seu critério próprio.
- `@total_ordering` gera `__gt__`, `__le__`, `__ge__` automaticamente.
- Método `do()` é a ação principal — cada subclasse sobrescreve.

```python
from functools import total_ordering

@total_ordering
class Item:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other: "Item") -> bool:
        raise NotImplementedError

    def __lt__(self, other: "Item") -> bool:
        raise NotImplementedError

    # __gt__, __le__, __ge__ → gerados por @total_ordering

    def do(self):
        raise NotImplementedError

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self.name}>"
```

---

### `core/storage.py` — DataStorage Singleton

- Instância única via `__new__`.
- `_data: dict` → HashMap com valores atuais (acesso O(1)).
- `_history: dict` → HashMap com listas de valores passados por chave — usado pela regressão linear.
- Método `history(key, last_n=None)` retorna os últimos `last_n` valores da série.

**Chaves obrigatórias no HashMap:**

| Chave | Tipo | Quem escreve |
|---|---|---|
| `sensor.temperature` | float °C | SensorManager |
| `sensor.wind_speed` | float m/s | SensorManager |
| `sensor.solar_irradiance` | float W/m² | SensorManager |
| `sensor.day_phase` | float 0–1 | DayNightSensor |
| `sensor.dust` | float 0–1 | SensorManager |
| `energy.generated` | float kW | EnergyManager |
| `energy.consumed` | float kW | EnergyManager |
| `energy.battery` | float % 0–100 | EnergyManager |
| `energy.delta` | float kW | EnergyManager |
| `energy.predicted_delta` | float kW | EnergyManager |
| `energy.level` | str | EnergyManager |
| `event.active` | str \| None | EventManager |
| `tick` | int | GameLoop |
| `sol` | int | GameLoop |

---

### `core/manager.py` — GenericManager

- Mantém uma lista interna de `Item`.
- Implementa: `add(item)`, `remove(item)`, `find(name)`, `find_by_index(i)`, `order_by(key_fn)`, `do_all()` (chama `do()` em cada item).
- `ModuleManager`, `SensorManager`, `EventManager`, `CrewManager` herdam de `GenericManager` e adicionam comportamentos específicos.

---

### `sensors/sensor.py` — Sensor Base

- Herda de `Item`.
- `__eq__`: compara `current_val`.
- `__lt__`: compara `current_val`.
- `do()`: aplica variação aleatória ao `current_val` limitado por `[min_val, max_val]`.
  - Fórmula: `current_val += random.uniform(-variation, +variation)` → clamp.
- Método `apply_modifier(factor)`: multiplica `current_val` por `factor` (usado por eventos climáticos).

---

### `sensors/sensors.py` — Sensores Concretos

| Classe | min_val | max_val | variation/tick | Unidade |
|---|---|---|---|---|
| `TemperatureSensor` | -70 | +20 | 0.5 | °C |
| `WindSpeedSensor` | 0 | 50 | 1.0 | m/s |
| `SolarIrradianceSensor` | 0 | 600 | 20 | W/m² |
| `RainSensor` | 0 | 1 | 0.05 | intensidade |
| `WindDirectionSensor` | 0 | 360 | 5.0 | graus |
| `DayNightSensor` | 0.0 | 1.0 | — | fase |

**DayNightSensor** não usa variação aleatória — é determinístico:

```python
def do(self):
    tick = DataStorage().get("tick", 0)
    angle = (tick % 24) / 24 * 2 * math.pi
    self.current_val = (math.cos(angle - math.pi) + 1) / 2
    # tick=0  → 0.0 (meia-noite)
    # tick=6  → 0.5 (amanhecer)
    # tick=12 → 1.0 (meio-dia)
    # tick=18 → 0.5 (entardecer)
    return self.current_val
```

**SensorManager** herda de `GenericManager`:
- `do_all()`: chama `do()` em cada sensor e grava no `DataStorage` pela chave correspondente.
- Deve aplicar modificadores de evento **depois** da leitura base se `event.active` estiver definido.

---

### `modules/module.py` — Module Base

- Herda de `Item`.
- `__eq__`: compara `priority`.
- `__lt__`: compara `priority` — **essencial para o heapq**.
- `do()`: lê `energy.level` do `DataStorage` e chama `energy_logic(level)`.
- `energy_logic(level: str)`: **abstract** — cada módulo concreto implementa.
- Atributos: `id`, `name`, `type`, `priority`, `consumption_kw`, `criticality` (1–5), `active`, `broken`.

```python
def do(self):
    storage = DataStorage()
    level = storage.get("energy.level", "NOMINAL")
    return self.energy_logic(level)

def energy_logic(self, level: str):
    raise NotImplementedError
```

---

### `modules/modules.py` — 14 Módulos Concretos

Cada módulo implementa `energy_logic(level)` com comportamento próprio por nível.

| P. | Classe | Tipo | Crit. | kW | CRITICAL | LOW | NOMINAL | HIGH | SURPLUS |
|---|---|---|---|---|---|---|---|---|---|
| 1 | `CommandModule` | command | 5 | 5 | modo reduzido (3 kW) | normal | normal | normal | normal |
| 2 | `LifeSupportModule` | life_support | 5 | 20 | mínimo vital (12 kW) | normal | normal | normal | normal |
| 3 | `HabitatModule` | habitat | 4 | 15 | aquec. mín. (8 kW) | reduzido (10 kW) | normal | normal | conforto extra |
| 4 | `SolarModule` | solar | 5 | 2 | opera | opera | opera | opera | opera |
| 5 | `NuclearModule` | nuclear | 5 | 3 | potência máx. | potência máx. | normal | normal | reduz 20% |
| 6 | `WindModule` | wind | 5 | 1 | opera* | opera* | opera* | opera* | opera* |
| 7 | `CommsModule` | comms | 4 | 8 | só SOS (2 kW) | emergência (4 kW) | normal | normal | normal |
| 8 | `MedicalModule` | medical | 4 | 10 | básico (6 kW) | reduzido (8 kW) | normal | normal | normal |
| 9 | `FoodModule` | food | 3 | 12 | desliga | manutenção (4 kW) | normal | normal | normal |
| 10 | `LogisticsModule` | logistics | 3 | 6 | desliga | reduzido (3 kW) | normal | normal | normal |
| 11 | `ISRUModule` | isru | 2 | 18 | desliga | desliga | normal | normal | extra (+20%) |
| 12 | `WorkshopModule` | workshop | 2 | 8 | só reparos críticos (3 kW) | reduzido (5 kW) | normal | normal | normal |
| 13 | `LabModule` | lab | 2 | 10 | desliga | desliga | normal | normal | normal |
| 14 | `SensorsModule` | sensors | 4 | 3 | básico (1 kW) | reduzido (2 kW) | normal | normal | normal |

> *`WindModule`: lógica de embandeiramento independente do energy_level — ver seção de Geração Eólica.

**Padrão de implementação:**

```python
class FoodModule(Module):
    def __init__(self):
        super().__init__(id=9, name="Produção de Alimentos", type="food",
                         priority=9, consumption_kw=12, criticality=3)

    def energy_logic(self, level: str):
        if level == "CRITICAL":
            self.active = False
            self.consumption_kw = 0
            print("[Food] DESLIGADO — energia crítica")
        elif level == "LOW":
            self.active = True
            self.consumption_kw = 4
            print("[Food] Modo manutenção — mantém apenas culturas vivas")
        else:
            self.active = True
            self.consumption_kw = 12
        return self.consumption_kw
```

---

### `modules/modules.py` — ModuleManager

Herda de `GenericManager`. Substitui a lista interna por um **min-heap**.

```python
import heapq

class ModuleManager(GenericManager):
    def __init__(self):
        self._heap = []      # min-heap de Module
        self._map  = {}      # HashMap id → Module

    def add(self, module: Module):
        heapq.heappush(self._heap, module)  # usa module.__lt__ (priority)
        self._map[module.id] = module

    def remove(self, module_id: int):
        if module_id in self._map:
            self._map[module_id].active = False
            del self._map[module_id]

    def find(self, module_id: int) -> Module:
        return self._map.get(module_id)

    def run_all(self):
        # Itera em ordem de prioridade SEM destruir a heap
        # (heapq não suporta iteração ordenada não-destrutiva nativamente)
        snapshot = sorted(self._heap)   # cria cópia ordenada (usa __lt__)
        for module in snapshot:
            if module.active and not module.broken:
                module.do()

    def do_all(self):
        self.run_all()

    def spawn_random(self, available_types: list):
        """Instancia um módulo aleatório da lista e adiciona à heap."""
        ModuleClass = random.choice(available_types)
        new_module  = ModuleClass()
        self.add(new_module)
        print(f"[ModuleManager] Novo módulo chegou: {new_module.name}")
        return new_module
```

---

### `energy/regression.py` — Regressão Linear Manual

Implementação dos mínimos quadrados. Sem numpy.

```python
class LinearRegression:
    def __init__(self):
        self.slope     = 0.0
        self.intercept = 0.0

    def fit(self, xs: list, ys: list):
        """Ajusta a reta y = slope*x + intercept aos dados."""
        n = len(xs)
        if n < 2:
            self.slope     = 0.0
            self.intercept = ys[0] if n == 1 else 0.0
            return

        x_mean = sum(xs) / n
        y_mean = sum(ys) / n

        numerator   = sum((x - x_mean) * (y - y_mean) for x, y in zip(xs, ys))
        denominator = sum((x - x_mean) ** 2           for x in xs)

        self.slope     = numerator / denominator if denominator != 0 else 0.0
        self.intercept = y_mean - self.slope * x_mean

    def predict(self, x: float) -> float:
        return self.slope * x + self.intercept
```

---

### `energy/energy_manager.py` — Gerenciador de Energia

> **Especificação principal:** o nível de energia é **preditivo**, não apenas reativo.  
> A regressão linear roda sobre o histórico de `delta = geração - consumo` por tick.  
> Um slope negativo significa que a tendência é de consumo crescendo sobre geração → escalona o nível antes da bateria cair.

#### Constantes

```python
BATTERY_MAX      = 1000.0   # kWh
SOLAR_AREA       = 200.0    # m²
SOLAR_EFFICIENCY = 0.22     # 22%
NUCLEAR_RATED    = 40.0     # kW constante
WIND_K           = 0.002    # coeficiente curva potência
WIND_CUT_IN      = 3.0      # m/s
WIND_FURL        = 25.0     # m/s → embandeiramento
WIND_CUTOUT      = 35.0     # m/s → parada total
HISTORY_WINDOW   = 48       # últimos N ticks para a regressão
SLOPE_CRITICAL   = -2.0     # kW/tick → tendência muito negativa
SLOPE_LOW        = -0.5     # kW/tick → tendência negativa moderada
```

#### Cálculo de Geração

```python
def _calculate_generation(self, storage) -> float:
    phase = storage.get("sensor.day_phase", 0)
    irrad = storage.get("sensor.solar_irradiance", 0)
    wind  = storage.get("sensor.wind_speed", 0)

    # Solar: proporcional à fase do dia e irradiância
    solar_gen = SOLAR_AREA * irrad * SOLAR_EFFICIENCY * phase / 1000  # kW

    # Eólico: curva de potência cúbica com embandeiramento
    if wind < WIND_CUT_IN:
        wind_gen = 0.0
    elif wind < WIND_FURL:
        wind_gen = WIND_K * wind ** 3
    elif wind < WIND_CUTOUT:
        wind_gen = WIND_K * WIND_FURL ** 3 * 0.3   # reduz 70%
    else:
        wind_gen = 0.0                               # parada total

    nuclear_gen = NUCLEAR_RATED   # constante, independe do clima

    return round(solar_gen + wind_gen + nuclear_gen, 2)
```

#### Cálculo do Consumo

```python
def _calculate_consumption(self, module_manager) -> float:
    total = sum(
        mod.consumption_kw
        for mod in module_manager._heap
        if mod.active and not mod.broken
    )
    return round(total, 2)
```

#### Determinação do Nível de Energia — Lógica Preditiva

```
A decisão usa DOIS fatores combinados:
  1. Estado atual da bateria (%)
  2. Slope da regressão linear sobre o histórico de deltas

Isso torna o sistema PREDITIVO:
  → bateria em 60% mas slope muito negativo → já entra em LOW
  → bateria em 35% mas slope positivo (geração crescendo) → mantém LOW, não escalona
```

```python
def _determine_level(self, battery_pct: float, predicted_delta: float, slope: float) -> str:
    # Nível base pela bateria
    if battery_pct < 20:
        base = "CRITICAL"
    elif battery_pct < 40:
        base = "LOW"
    elif battery_pct > 90:
        base = "SURPLUS"
    elif predicted_delta > 0:
        base = "HIGH"
    else:
        base = "NOMINAL"

    # Ajuste pela tendência (slope da regressão)
    # slope < 0 → consumo crescendo sobre geração ao longo do tempo
    if slope <= SLOPE_CRITICAL:
        # Tendência muito negativa → escala para pelo menos LOW
        if base in ("NOMINAL", "HIGH", "SURPLUS"):
            return "LOW"
        if base == "LOW":
            return "CRITICAL"

    elif slope <= SLOPE_LOW:
        # Tendência negativa moderada → escala um nível
        if base in ("HIGH", "SURPLUS"):
            return "NOMINAL"
        if base == "NOMINAL":
            return "LOW"

    # slope >= 0 → tendência estável ou positiva → mantém base
    return base
```

#### Método `calculate()` — Chamado a Cada Tick

```python
def calculate(self, module_manager):
    storage = DataStorage()

    generated = self._calculate_generation(storage)
    consumed  = self._calculate_consumption(module_manager)
    delta     = generated - consumed

    # Atualiza bateria
    battery_kwh = storage.get("energy.battery", BATTERY_MAX * 0.65)
    battery_kwh = max(0, min(BATTERY_MAX, battery_kwh + delta))
    battery_pct = (battery_kwh / BATTERY_MAX) * 100

    # Acumula histórico de deltas (janela deslizante)
    delta_history = storage.history("energy.delta", last_n=HISTORY_WINDOW)

    # Ajusta regressão linear
    xs = list(range(len(delta_history)))
    ys = delta_history
    self._regression.fit(xs, ys)

    # Prediz o próximo delta
    predicted_delta = self._regression.predict(len(xs))
    slope           = self._regression.slope

    # Determina nível
    level = self._determine_level(battery_pct, predicted_delta, slope)

    # Gera alerta textual
    alert = self._generate_alert(level, generated, consumed, slope)

    # Grava tudo no DataStorage
    storage.set("energy.generated",       generated)
    storage.set("energy.consumed",        consumed)
    storage.set("energy.delta",           delta)
    storage.set("energy.battery",         battery_pct)
    storage.set("energy.predicted_delta", predicted_delta)
    storage.set("energy.level",           level)
    storage.set("energy.alert",           alert)

def _generate_alert(self, level, generated, consumed, slope) -> str:
    if level == "CRITICAL":
        return f"ALERTA: consumo maior que geração (slope={slope:+.2f} kW/tick)"
    elif level == "LOW":
        return f"ALERTA: reduzir consumo — tendência negativa detectada"
    elif level == "SURPLUS":
        return "SUGESTÃO: armazenar energia excedente"
    elif generated > consumed:
        return f"Geração: {generated:.1f} kW  Consumo: {consumed:.1f} kW  Saldo: {generated-consumed:+.1f} kW"
    else:
        return "Operação nominal"
```

---

### `events/event.py` — Event Base

- Herda de `Item`.
- `__eq__`: compara `type`.
- `__lt__`: compara `severity`.
- `do()`: chama `tick()` — decrementa `duration_ticks`.
- `apply(storage)`: aplica modificadores no `DataStorage`.
- `revert(storage)`: reverte modificadores.

---

### `events/events.py` — Eventos Concretos

#### ColdFront — Frente Fria

- Probabilidade: **3% por tick** (`random.random() < 0.03`)
- Duração: `random.randint(12, 48)` ticks
- Efeitos em `apply()`:
  - `sensor.solar_irradiance` → multiplica por **0.6**
  - `sensor.temperature` → subtrai **10°C**
  - `HabitatModule.consumption_kw` → multiplica por **1.4** (mais aquecimento)
- Reverte em `revert()`.

#### Sandstorm — Tempestade de Areia

- Probabilidade: **2% por tick**
- Duração: `random.randint(6, 72)` ticks
- Efeitos em `apply()`:
  - `sensor.solar_irradiance` → multiplica por **0.2**
  - `sensor.wind_speed` → soma **+15 m/s** (pode ativar embandeiramento)
- A lógica de embandeiramento é do `WindModule` — ele lê `sensor.wind_speed` do storage.

#### EquipmentFailure — Falha de Equipamento

- Probabilidade: **0.5% por tick por módulo ativo** (rola separado para cada um)
- Efeito: `module.broken = True`, `module.active = False`
- `repair_ticks`: `random.randint(2, 12)`
- Aloca um `CrewMember` com `role == "engineer"` ou `"technician"` para o reparo.
- Após `repair_ticks` ticks: `module.broken = False`, `module.active = True`.

---

### `crew/crew.py` — Tripulantes

#### CrewMember

Herda de `Item`. `__eq__` e `__lt__` comparam por `health`.

```python
class CrewMember(Item):
    ROLES = ["commander", "engineer", "medic", "scientist", "technician"]

    def __init__(self, name: str, role: str):
        super().__init__(name)
        self.role               = role      # str
        self.health             = 1.0       # float 0–1
        self.status             = "idle"    # idle | working | repairing | resting
        self.assigned_module    = None      # Module | None
        self.repair_ticks_left  = 0         # int

    def __eq__(self, other): return self.health == other.health
    def __lt__(self, other): return self.health  < other.health

    def do(self):
        self._update_health()
        self._update_repair()

    def _update_health(self):
        storage = DataStorage()
        level   = storage.get("energy.level", "NOMINAL")
        if level == "CRITICAL":
            self.health = max(0.0, self.health - 0.05)
        elif level in ("HIGH", "SURPLUS"):
            self.health = min(1.0, self.health + 0.01)

    def _update_repair(self):
        if self.status == "repairing" and self.repair_ticks_left > 0:
            self.repair_ticks_left -= 1
            if self.repair_ticks_left == 0:
                if self.assigned_module:
                    self.assigned_module.broken = False
                    self.assigned_module.active = True
                self.status          = "idle"
                self.assigned_module = None

    def assign_repair(self, module, ticks: int):
        self.status             = "repairing"
        self.assigned_module    = module
        self.repair_ticks_left  = ticks
```

#### CrewManager

Herda de `GenericManager`. Adiciona:
- `assign_repair(module, ticks)`: encontra tripulante idle com role técnico e atribui reparo.
- `available_engineers()`: retorna lista de membros idle com role em `["engineer", "technician"]`.

---

### `main.py` — Loop Principal

```python
TICK_RATE     = 0.5     # segundos reais por tick (ajustável)
SPAWN_PROB    = 0.02    # 2% de chance por tick de spawnar módulo novo
SOL_TICKS     = 24      # ticks por sol marciano

def game_loop():
    storage         = DataStorage()
    sensor_manager  = SensorManager()
    module_manager  = ModuleManager()
    event_manager   = EventManager()
    energy_manager  = EnergyManager()
    crew_manager    = CrewManager()
    logger          = Logger()

    # Módulos iniciais instalados na colônia (P1 a P6 no mínimo)
    for ModClass in [CommandModule, LifeSupportModule, HabitatModule,
                     SolarModule, NuclearModule, WindModule]:
        module_manager.add(ModClass())

    # Tripulação inicial
    for name, role in [("Ana", "engineer"), ("Bruno", "medic"),
                       ("Carla", "scientist"), ("Diego", "commander")]:
        crew_manager.add(CrewMember(name, role))

    tick = 0
    while True:
        tick += 1
        storage.set("tick", tick)
        storage.set("sol",  tick // SOL_TICKS)

        # 1. Atualiza sensores (incluindo ciclo dia/noite)
        sensor_manager.do_all()

        # 2. Processa eventos climáticos e falhas
        event_manager.check_and_roll(module_manager, crew_manager, storage)

        # 3. Calcula geração, consumo, regressão linear e determina energy.level
        energy_manager.calculate(module_manager)

        # 4. Executa módulos em ordem de prioridade (heap)
        #    Cada módulo lê energy.level do DataStorage internamente
        module_manager.run_all()

        # 5. Atualiza tripulantes (saúde, reparos em andamento)
        crew_manager.do_all()

        # 6. Grava log do tick atual
        logger.log(tick, storage)

        # 7. Chance de novo módulo/tripulante chegar da Terra
        if random.random() < SPAWN_PROB:
            available = [FoodModule, LogisticsModule, ISRUModule,
                         WorkshopModule, LabModule, SensorsModule]
            module_manager.spawn_random(available)
            # Novo tripulante junto
            crew_manager.add(CrewMember(f"Tripulante_{tick}", random.choice(CrewMember.ROLES)))

        time.sleep(TICK_RATE)
```

---

### `logger.py` — Logger

- Imprime linha no console a cada tick com o estado atual.
- Grava linha em `simulation_log.csv` com todas as colunas do DataStorage.
- Formato de alerta no console:
  - `"ALERTA: ..."` → prefixo `⚠`
  - `"SUGESTÃO: ..."` → prefixo `✓`

---

### `display/dashboard.py` — Terminal Dashboard

Dashboard interativo com abas navegáveis pelas teclas `←` `→`. Usa ANSI escape codes. Sem dependências externas.

**Abas:**

| Aba | Conteúdo |
|---|---|
| Overview | Gráfico de bateria (sparkline), barras de geração por fonte, predição |
| Energia | Waveform geração vs consumo, slope da regressão, nível atual |
| Módulos | Tabela completa: prioridade, consumo, status, risco por nível |
| Sensores | Leituras atuais, mini gráficos de vento e solar, ciclo dia/noite |
| Eventos | Evento ativo com countdown, log de eventos |
| Crew | Tabela de tripulantes: saúde, status, módulo em reparo |

**Captura de teclas:**
- Linux/macOS: `termios` + `tty` em modo raw, `select` para leitura não-bloqueante.
- Windows: `msvcrt.kbhit()` + `msvcrt.getch()`.

---

## Regras de Negócio Importantes

### Embandeiramento Eólico (`WindModule`)

```
vento < 3 m/s    → geração = 0           (abaixo do cut-in)
3 ≤ vento < 25   → geração = 0.002 * v³  (curva cúbica)
25 ≤ vento < 35  → geração *= 0.3        (embandeiramento parcial)
vento ≥ 35       → geração = 0           (parada de emergência)
```

### Ciclo Dia/Noite

```python
angle     = (tick % 24) / 24 * 2 * math.pi
day_phase = (math.cos(angle - math.pi) + 1) / 2
# Fase 0.0 = meia-noite, 1.0 = meio-dia
# Geração solar = 0 quando day_phase próximo de 0
```

### Saúde da Tripulação

```
energy.level == "CRITICAL" → health -= 0.05 por tick para todos
energy.level in HIGH/SURPLUS → health += 0.01 por tick
health == 0 → tripulante incapacitado, status = "incapacitated"
```

### Spawn de Módulos

- Probabilidade: `SPAWN_PROB = 0.02` (2% por tick)
- Só spawna módulos que **ainda não estão instalados** (verificar pelo tipo)
- Sempre acompanhado de 1 novo tripulante
- Módulos iniciais garantidos: P1 (Command), P2 (ECLSS), P4 (Solar), P5 (Nuclear)

---

## Saídas Esperadas (Exemplos para README)

```
Entrada:  wind_speed=11 m/s, solar_irradiance=0 (noite), nuclear=40 kW
Saída:    Geração total ≈ 42.7 kW  |  Predição próx. tick: 43.1 kW

Entrada:  battery=38%, slope=-1.2 kW/tick
Saída:    energy.level = "LOW"  →  "ALERTA: reduzir consumo — tendência negativa detectada"

Entrada:  battery=55%, slope=-3.1 kW/tick
Saída:    energy.level = "LOW"  →  escalona de NOMINAL para LOW pela tendência

Entrada:  battery=25%, slope=+0.8 kW/tick
Saída:    energy.level = "LOW"  →  mantém LOW (não escalona, tendência positiva)

Entrada:  battery=92%
Saída:    energy.level = "SURPLUS"  →  "SUGESTÃO: armazenar energia excedente"
```
