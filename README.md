# Colônia Aurora — SIGER (Sistema Integrado de Gerenciamento e Energia em Rede)

Sistema de simulação inteligente de uma colônia marciana desenvolvido em Python 3 (somente stdlib).  
Projeto FIAP — Fase 3.

---

## Funcionamento

O sistema simula o gerenciamento energético de uma base em Marte, integrando:

- **Sensores ambientais** (temperatura, vento, irradiância solar, ciclo dia/noite)
- **14 módulos** operacionais com prioridade e comportamento adaptativo por nível de energia
- **Regressão linear manual** para prever tendências de consumo/geração
- **Sistema preditivo de nível de energia** (não apenas reativo — antecipa crises)
- **Eventos climáticos** (frente fria, tempestade de areia, falhas de equipamento)
- **Tripulação** com saúde variável e capacidade de reparo

O loop roda a 0,5 s/tick. Um **sol marciano** equivale a 24 ticks.

---

## Como executar

```bash
python main.py
```

**Navegação do dashboard:**

| Tecla | Ação |
|-------|------|
| `1` – `6` | Salta para a aba diretamente |
| `←` `→` | Navega entre abas |
| `P` | Pausa / retoma a simulação |
| `Q` | Encerra |

> Requer terminal com suporte a ANSI/cores de 24 bits e largura mínima de 100 colunas.

---

## Estrutura do Projeto

```
colonia_aurora/
├── core/        item.py · storage.py · manager.py
├── sensors/     sensor.py · sensors.py (6 sensores + SensorManager)
├── modules/     module.py · modules.py (14 módulos + ModuleManager/heap)
├── energy/      regression.py · energy_manager.py
├── events/      event.py · events.py (ColdFront, Sandstorm, EquipmentFailure)
├── crew/        crew.py (CrewMember + CrewManager)
├── display/     dashboard.py (terminal UI multi-aba)
└── logger.py
main.py          ← entry point
simulation_log.csv ← gerado em runtime
```

---

## Como os dados foram organizados

| Estrutura | Onde | Para quê |
|-----------|------|----------|
| **HashMap** (`dict`) | `DataStorage` singleton | Acesso O(1) a todos os valores correntes: sensores, energia, eventos |
| **Lista com histórico** | `DataStorage._history` | Série temporal de cada chave — alimenta a regressão linear |
| **Min-Heap** (`heapq`) | `ModuleManager` | Processa módulos em ordem de prioridade (P1 = mais crítico) |
| **Hierarquia de herança** | `Item → Sensor / Module / Event / CrewMember` | Polimorfismo via `do()` — cada subclasse especializa o comportamento |
| **Singleton** | `DataStorage` | Compartilhado entre simulação e dashboard (threads distintos) |

---

## Regras de decisão

O sistema determina o **nível de energia** com base em dois fatores combinados:

```
1. Estado atual da bateria (%)
2. Slope da regressão linear sobre o histórico de deltas (geração − consumo)

→ bateria OK mas tendência muito negativa → já entra em LOW (preditivo)
→ bateria baixa mas tendência positiva → mantém LOW, não escalona para CRITICAL
```

### Tabela de níveis

| Nível | Condição |
|-------|----------|
| CRITICAL | bateria < 20 % ou slope ≤ −2 kW/tick com bateria já em LOW |
| LOW | bateria < 40 % ou slope ≤ −0,5 kW/tick com bateria em NOMINAL |
| NOMINAL | geração ≤ consumo, bateria 40–90 % |
| HIGH | geração > consumo, bateria 40–90 % |
| SURPLUS | bateria > 90 % |

### Comportamento dos módulos por nível

| Módulo | CRITICAL | LOW | NOMINAL/HIGH | SURPLUS |
|--------|----------|-----|--------------|---------|
| Command (P1) | 3 kW (modo reduzido) | 5 kW | 5 kW | 5 kW |
| ECLSS (P2) | 12 kW (mínimo vital) | 20 kW | 20 kW | 20 kW |
| Food (P9) | **desliga** | 4 kW | 12 kW | 12 kW |
| ISRU (P11) | **desliga** | **desliga** | 18 kW | 21,6 kW (+20%) |

---

## Modelo de previsão (regressão linear)

Implementação manual dos mínimos quadrados — sem numpy.

```python
# slope = Σ(xi − x̄)(yi − ȳ) / Σ(xi − x̄)²
# intercept = ȳ − slope · x̄
```

### Exemplo de entrada e saída

**Entrada:** velocidade do vento nos últimos 5 ticks = `[8, 10, 12, 14, 16]` m/s  
**Saída:** previsão para o próximo tick = `18,0` m/s  
*(regressão ajusta reta perfeita com slope = 2,0 e intercept = 8,0)*

---

## Análise de energia — exemplos

**Exemplo 1 — consumo maior que geração:**

```
Entrada:  geração = 40 kW,  consumo = 70 kW
Saída:    "ALERTA: consumo maior que geração (slope=-X.XX kW/tick)"
Nível:    CRITICAL
```

**Exemplo 2 — energia excedente:**

```
Entrada:  bateria = 92 %
Saída:    "SUGESTÃO: armazenar energia excedente"
Nível:    SURPLUS
```

**Exemplo 3 — sistema preditivo antecipa crise:**

```
Entrada:  bateria = 55 %,  slope = −3,1 kW/tick
Saída:    energy.level = "LOW"  →  escalona de NOMINAL para LOW pela tendência
```

**Exemplo 4 — tendência positiva segura a bateria:**

```
Entrada:  bateria = 25 %,  slope = +0,8 kW/tick
Saída:    energy.level = "LOW"  →  mantém LOW (não escalona, tendência positiva)
```

---

## Geração eólica — embandeiramento

```
vento < 3 m/s    → geração = 0           (abaixo do cut-in)
3 ≤ vento < 25   → geração = 0,002 · v³  (curva cúbica)
25 ≤ vento < 35  → geração *= 0,3        (embandeiramento — 70% de redução)
vento ≥ 35       → geração = 0           (parada de emergência)
```

---

## Ciclo dia/noite marciano

```
angle     = (tick % 24) / 24 × 2π
day_phase = (cos(angle − π) + 1) / 2

tick =  0  → phase 0,00  (meia-noite)
tick =  6  → phase 0,50  (amanhecer)
tick = 12  → phase 1,00  (meio-dia — pico solar)
tick = 18  → phase 0,50  (entardecer)
```

---

## Log gerado (`simulation_log.csv`)

Cada tick gera uma linha com todas as colunas do `DataStorage`:  
`tick, sol, sensor.temperature, sensor.wind_speed, sensor.solar_irradiance, sensor.day_phase, sensor.dust, energy.generated, energy.solar_gen, energy.wind_gen, energy.nuclear_gen, energy.consumed, energy.delta, energy.battery, energy.predicted_delta, energy.slope, energy.level, event.active, energy.alert`
