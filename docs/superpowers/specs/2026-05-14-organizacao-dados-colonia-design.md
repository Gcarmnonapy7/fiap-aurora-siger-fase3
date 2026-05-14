# Spec — Organização dos dados da colônia (item 1.1)

**Data:** 2026-05-14
**Autor:** Iúri Leão (FIAP — Fase 3, Atividade Integradora)
**Escopo:** Item 1.1 do enunciado e infraestrutura para 1.2, 1.3, 1.4

---

## 1. Contexto e motivação

Na **Fase 2** a equipe modelou os 12 módulos da colônia Aurora Siger como entidades em órbita aguardando autorização de pouso (classe `Module` com `priority`, `fuel_level`, `sensors_ok`, etc.). O sistema usava estruturas lineares (`Vector`, `Queue`, `Stack`) e lógica booleana para escalonar pousos.

Na **Fase 3** os mesmos 12 módulos já pousaram e operam como **subsistemas da colônia**. O foco do enunciado muda de "ordenar fila de pouso" para "**organizar dados operacionais, decidir uso de energia, e prever comportamentos**". Esta evolução está explicitamente prevista no Objetivo Final do enunciado: "evoluir de sistemas reativos para sistemas preditivos".

O **item 1.1** exige três tipos de estruturação de dados:

1. **Listas / chave-valor** para energia, consumo e clima
2. **Hierarquia** de sistemas (exemplo do enunciado: `energético → solar / eólica`)
3. **Navegação** entre subsistemas

Este documento consolida as decisões de design que satisfazem esses requisitos e estabelecem a base para os itens 1.2 (decisão), 1.3 (regressão) e 1.4 (análise de energia).

---

## 2. Decisões de design

### 2.1 Continuidade com a Fase 2

**Decisão:** Reaproveitar a **identidade dos 12 módulos** (nomes, números, prioridades), mas **redesenhar a representação** com listas e dicionários simples — sem reutilizar a classe `Module` da Fase 2.

**Justificativa:**
- O critério "Estruturação de dados" da Fase 3 (peso 2) avalia uso de listas, dicts e hierarquias, não POO complexa.
- O enunciado explicita: "apenas conceitos trabalhados nos capítulos" e "não é necessário utilizar bibliotecas avançadas".
- Atributos da Fase 2 (`distance`, `speed`, `sensors_ok`, `fuel_level`) não fazem sentido para módulos já pousados em operação.

### 2.2 Hierarquia: duas árvores sobre uma lista plana de módulos

**Decisão:** Os 12 módulos vivem em **uma única lista** (estrutura principal). Sobre essa lista, construímos **duas árvores N-árias diferentes**, cada folha referenciando o mesmo módulo:

- **Árvore funcional** — agrupa por função (Energia, Suporte à Vida, Comando, Operações)
- **Árvore de criticidade** — agrupa por nível de criticidade (Vital, Sustento, Expansão)

**Justificativa:** A mesma informação ganha múltiplas estruturas de acesso, análogo a índices em bancos de dados. Cada árvore responde a uma pergunta diferente:

- **Funcional** → "qual a geração total?" (agregação no ramo Energia)
- **Criticidade** → "o que desligo se faltar energia?" (percurso BFS, do menos crítico ao mais crítico)

As duas árvores compartilham referências aos mesmos módulos. Alterar `consumo_atual` de um módulo se reflete automaticamente nas duas views (não há duplicação de dado).

### 2.3 Implementação: classe `No` N-ária única

**Decisão:** Uma única classe `No` reutilizada para construir as duas árvores.

```python
class No:
    def __init__(self, nome, modulo=None):
        self.nome = nome
        self.modulo = modulo      # None em nós internos; preenchido em folhas
        self.filhos = []          # lista de Nó

    def adicionar_filho(self, filho): ...
    def eh_folha(self): ...
    def percorrer_dfs(self): ...        # generator, pré-ordem
    def percorrer_bfs(self): ...        # generator, por nível
    def buscar(self, nome): ...
    def folhas(self): ...               # devolve só os módulos das folhas
    def profundidade(self): ...
    def imprimir(self, indent=0): ...   # pretty-print
```

**Justificativa:** Torna explícitos os conceitos da disciplina (raiz, filho, folha, percurso, profundidade). Métodos são autodocumentação. Mesma classe serve as duas árvores — demonstra estrutura genérica reutilizada.

### 2.4 Simulador generativo (clima → geração → distribuição)

**Decisão:** O sistema é um **simulador**: amostra clima, calcula geração de cada fonte, distribui energia segundo política de criticidade, registra histórico. O **histórico de séries temporais não é input externo — é output da simulação**.

**Justificativa:**
- Resolve o problema "de onde vêm os dados históricos do item 1.3?": eles são gerados pelo próprio simulador.
- A regressão linear vento↔eólica do item 1.3 é ajustada sobre dados que **o próprio sistema produziu**.
- Permite previsão direta: "dado vento Y amanhã, o que acontece?" basta rodar o simulador com essa entrada.
- Cumpre o Objetivo Final do enunciado (reativo → preditivo).

### 2.5 Horizonte de 7 sóis marcianos (168 passos de 1 hora)

**Decisão:** Cada passo = 1 hora. Horizonte = 7 sóis × 24 h = **168 passos**.

**Justificativa:**
- 168 pontos é folgado para regressão linear robusta (item 1.3).
- 7 sóis permitem ver ciclos dia/noite repetidos, pelo menos 1 tempestade naturalmente, e degradação acumulada de painéis.
- Sol marciano = 24h37min — aproximação para 24h é simplificação aceitável.

---

## 3. Arquitetura

### 3.1 Camadas

```
┌──────────────────────────────────────────────────────────┐
│  Camada 5 — Histórico (dict de listas paralelas)         │
│  output da simulação, input para regressão (1.3) e       │
│  análise (1.4)                                            │
├──────────────────────────────────────────────────────────┤
│  Camada 4 — Política de alocação (load shedding)         │
│  percorre árvore de criticidade, decide modo de cada     │
│  módulo (item 1.2)                                        │
├──────────────────────────────────────────────────────────┤
│  Camada 3 — Modelo de geração                            │
│  funções físicas: solar(hora, tau), eólica(vento),       │
│  nuclear (constante)                                      │
├──────────────────────────────────────────────────────────┤
│  Camada 2 — Modelo climático (estocástico realista)      │
│  vento, tempestades graduadas, temperatura, deposição    │
│  de poeira                                                │
├──────────────────────────────────────────────────────────┤
│  Camada 1 — Modelo de dados (estruturas)                 │
│  lista de módulos, duas árvores, dict de estado          │
│  instantâneo, dict de histórico                           │
└──────────────────────────────────────────────────────────┘
```

Cada camada lê apenas as camadas abaixo. A simulação executa, a cada passo:

1. Camada 2 amostra novo clima
2. Camada 3 calcula geração por fonte
3. Camada 4 aplica política de alocação sobre a árvore de criticidade
4. Camada 5 registra resultados

### 3.2 Estruturas de dados — Camada 1

#### 3.2.1 Lista plana dos 12 módulos

```python
modulos = [
    {
        "id": 1, "nome": "Comando e Controle", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 2, "adequado": 8, "excedente": 8},
        "escalona_com_excedente": False,
        "fator_termico": 0.0,         # insensível a T_externa
        "modo_atual": "adequado",
    },
    {
        "id": 2, "nome": "Suporte de Vida (ECLSS)", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 4, "adequado": 12, "excedente": 12},
        "escalona_com_excedente": False,
        "fator_termico": 0.4,         # subsistema térmico do ECLSS sensível
        "modo_atual": "adequado",
    },
    {
        "id": 3, "nome": "Habitação", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 5, "adequado": 15, "excedente": 15},
        "escalona_com_excedente": False,
        "fator_termico": 1.0,         # absorve totalmente o modelo Q = U·A·ΔT
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
        "capacidade_max_kw": 80.0,    # baseload constante
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
        "escalona_com_excedente": True,     # estufa pode iluminar mais
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
        "escalona_com_excedente": True,     # extrai mais água/propelente
        "fator_termico": 0.0,
        "modo_atual": "adequado",
    },
    {
        "id": 11, "nome": "Oficina e Manutenção", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 0.5, "adequado": 3, "excedente": 3},
        "escalona_com_excedente": False,
        "fator_termico": 0.2,
        "modo_atual": "desligado",          # opera sob demanda
    },
    {
        "id": 12, "nome": "Laboratório Científico", "tipo": "consumidor",
        "consumo_por_modo": {"desligado": 0, "minimo": 1, "adequado": 5, "excedente": 12},
        "escalona_com_excedente": True,     # mais experimentos
        "fator_termico": 0.2,
        "modo_atual": "adequado",
    },
]
```

**Observação sobre energia eólica:** a Fase 2 contava com Solar e Nuclear. Para a Fase 3 vamos **introduzir um 13º elemento — gerador eólico** — como filho do nó "Energia" da árvore funcional. Justificativa: o enunciado (item 1.3) dá como exemplo a previsão de energia eólica. Tratamos esse acréscimo como **expansão narrativa da colônia** ("nova turbina instalada após o pouso bem-sucedido da Fase 2"), não como contradição.

```python
modulo_eolico = {
    "id": 13, "nome": "Energia Eólica", "tipo": "gerador_eolico",
    "capacidade_max_kw": 30.0,
    "consumo_por_modo": {"desligado": 0, "minimo": 0.3, "adequado": 0.5, "excedente": 0.5},
    "escalona_com_excedente": False,
    "fator_termico": 0.0,
    "modo_atual": "adequado",
}
```

#### 3.2.2 Árvore funcional

```
Colônia Aurora Siger
├── Energia
│   ├── Solar (id 4)
│   ├── Nuclear (id 5)
│   └── Eólica (id 13)
├── Suporte à Vida
│   ├── ECLSS (id 2)
│   ├── Habitação (id 3)
│   ├── Médico (id 7)
│   └── Alimentos (id 8)
├── Comando
│   ├── Comando e Controle (id 1)
│   └── Comunicações (id 6)
└── Operações
    ├── Logística (id 9)
    ├── ISRU (id 10)
    ├── Oficina (id 11)
    └── Laboratório (id 12)
```

#### 3.2.3 Árvore de criticidade

```
Colônia
├── Vital
│   ├── Comando e Controle (id 1)
│   ├── ECLSS (id 2)
│   ├── Médico (id 7)
│   ├── Habitação (id 3)
│   └── [Energia é tratada à parte — não consome, gera]
├── Sustento
│   ├── Energia Solar (id 4)
│   ├── Energia Nuclear (id 5)
│   ├── Energia Eólica (id 13)
│   ├── Alimentos (id 8)
│   ├── Comunicações (id 6)
│   └── ISRU (id 10)
└── Expansão
    ├── Logística (id 9)
    ├── Oficina (id 11)
    └── Laboratório (id 12)
```

**Nota:** geradores aparecem em "Sustento" porque seu próprio consumo (ventiladores, controle) é não-vital — se faltar energia, primeiro desligamos coisa não-essencial; geradores em si não precisam ser "alocados" pela política, eles **fornecem** energia.

#### 3.2.4 Estado instantâneo (chave-valor global)

```python
clima_atual = {
    "sol": 0,                     # 0..6
    "hora": 0,                    # 0..23
    "vento_ms": 0.0,
    "tempestade": "limpo",        # "limpo" | "leve" | "moderada" | "grave"
    "tau": 0.5,                   # derivado de tempestade + vento
    "temperatura_c": -60.0,
    "fator_paineis": 1.0,         # eficiência por deposição/limpeza acumulada
}

bateria = {
    "carga_atual_kwh": 250.0,
    "capacidade_max_kwh": 500.0,
    "reserva_emergencia_kwh": 100.0,   # 20% da capacidade — intocável exceto emergência
}
```

#### 3.2.5 Histórico (chave-valor de listas paralelas)

```python
historico = {
    # Entradas climáticas
    "vento_ms":           [],
    "temperatura_c":      [],
    "tempestade":         [],
    "tau":                [],
    # Saídas do simulador
    "geracao_solar_kw":   [],
    "geracao_eolica_kw":  [],
    "geracao_nuclear_kw": [],
    "geracao_total_kw":   [],
    "consumo_total_kw":   [],
    "bateria_carga_kwh":  [],
    "modos_resumo":       [],     # dict {nome_modulo: modo} a cada passo
    "alertas":            [],     # lista de strings, vazia se passo sem alertas
}
```

### 3.3 Modelo climático realista — Camada 2

Todos os valores citados a seguir vêm de literatura científica (NASA, ESA, papers revisados) — fontes na Seção 6.

#### Vento marciano

```python
V_BASE = 2.5            # m/s
V_AMPLITUDE = 7.0       # m/s
FATOR_SAZONAL = 1.2     # perihélio (verão sul) — semana simulada nessa estação

def amostrar_vento(hora):
    componente_diurno = V_AMPLITUDE * max(0, math.sin(math.pi * (hora - 6) / 12))
    ruido = random.gauss(0, 1.5)
    return max(0, (V_BASE + componente_diurno) * FATOR_SAZONAL + ruido)
```

Pico ~14h local, mínimo de madrugada — InSight, Curiosity. Rajadas até ~20 m/s.

#### Tempestades de poeira — máquina de estados 4 níveis

```python
PROB_BASE_POR_SOL = {
    "leve":     0.40,    # Cantor: centenas de locais por ano marciano
    "moderada": 0.04,    # ~10-30 regionais por ano marciano
    "grave":    0.002,   # ~1 GDS a cada 3-4 anos marcianos
}

DURACAO_HORAS = {
    "leve":     (12, 72),
    "moderada": (72, 168),
    "grave":    (168, 720),
}

# Forçar evento didático: tempestade moderada começa no sol 3, hora 8
FORCAR_EVENTO_DIDATICO = True
```

Probabilidade modulada por vento alto (bônus linear acima de 15 m/s) e estação (perihélio dobra a base).

#### Opacidade (tau) e atenuação solar (Beer-Lambert)

```python
TAU_BASE = {
    "limpo":    0.5,
    "leve":     1.5,
    "moderada": 3.0,
    "grave":    8.0,
}

def calcular_tau(tempestade, vento):
    tau_extra = 0.05 * max(0, vento - 5)
    return TAU_BASE[tempestade] + tau_extra

def transmissao(tau):
    return math.exp(-tau)   # zenith simplificado (equador)
```

#### Deposição e limpeza dos painéis

```python
PERDA_POR_SOL = 0.002
PROB_LIMPEZA_POR_SOL = 0.005
PISO_FATOR_PAINEIS = 0.3   # limpeza manual da equipe humana (não modelada explicitamente)
```

#### Temperatura

```python
T_MEDIA = -60.0
A_DIURNA = 35.0
A_SAZONAL = 18.0
PHI_DIURNO = 9             # pico ~15h

def amostrar_temperatura(sol, hora):
    diurno = A_DIURNA * math.sin(2*math.pi * (hora - PHI_DIURNO) / 24)
    sazonal = A_SAZONAL * math.sin(2*math.pi * sol / 668)
    return T_MEDIA + diurno + sazonal + random.gauss(0, 2)
```

Munguira et al. 2024 (MEDA/Jezero), Martínez et al. 2017 (REMS/Gale).

### 3.4 Modelo de geração — Camada 3

```python
def gerar_solar(modulo, clima):
    curva_diurna = max(0, math.sin(math.pi * (clima["hora"] - 6) / 12))
    return modulo["capacidade_max_kw"] * curva_diurna * transmissao(clima["tau"]) * clima["fator_paineis"]

def gerar_eolico(modulo, clima):
    # Modelo linear com cut-in (v < 3 m/s não gera) e cut-out (satura na capacidade nominal).
    # Linear é deliberado: o item 1.3 pede regressão linear, e o ajuste captura bem este sinal.
    v = clima["vento_ms"]
    A_LINEAR = 2.5    # kW por m/s — coeficiente angular
    B_LINEAR = 7.5    # cut-in: P(v=3) = 0
    potencia_teorica = A_LINEAR * v - B_LINEAR
    return max(0, min(modulo["capacidade_max_kw"], potencia_teorica))
# P(3) = 0, P(10) = 17.5 kW, P(15) = 30 kW (saturação)

def gerar_nuclear(modulo, clima):
    return modulo["capacidade_max_kw"]   # baseload constante
```

### 3.5 Consumo com temperatura ativa — Camada 3

Modelo Q = U·A·ΔT calibrado para habitat 100 m² (envelope 250 m², aerogel + MLI):

```python
A_ENVELOPE = 250.0           # m²
U = 0.15                     # W/m²·K
T_ALVO = 20.0                # °C
GANHO_INTERNO_W = 4000.0
ETA_AQUECEDOR = 0.95
# k_termico ≈ 39.5 W/K

def consumo_aquecimento_kw(temperatura_externa, fator_termico):
    if fator_termico == 0:
        return 0
    perda_W = U * A_ENVELOPE * max(0, T_ALVO - temperatura_externa)
    liquido_W = max(0, perda_W - GANHO_INTERNO_W * fator_termico)
    return (liquido_W / ETA_AQUECEDOR / 1000) * fator_termico

def consumo_atual_kw(modulo, clima):
    base = modulo["consumo_por_modo"][modulo["modo_atual"]]
    extra_termico = consumo_aquecimento_kw(clima["temperatura_c"], modulo["fator_termico"])
    return base + extra_termico
```

### 3.6 Política de alocação (load shedding) — Camada 4

Quatro etapas em cascata sobre a árvore de criticidade. Detalhamento completo em Seção 4 (sequência operacional). Resumo:

1. Tentativa otimista: tudo em "adequado". Se cabe, distribui excedente.
2. Rebaixamento bottom-up: Expansão → Sustento → Vital descem para "mínimo" um a um.
3. Desligamento bottom-up: Expansão → Sustento desligam (Vital nunca).
4. Emergência: libera reserva intocável da bateria, registra alerta.

Critério de desempate dentro de um nível: atributo `id` original (1–13), menor = mais prioritário.

**Geradores são imunes ao rebaixamento.** Solar (id 4), Nuclear (id 5) e Eólica (id 13) ficam sempre em modo `adequado`. Razões: (a) consumo próprio é pequeno (0.5–3 kW) frente à geração que entregam; (b) rebaixar um gerador é fisicamente absurdo — sua **geração** é determinada pelo clima, não pela política; o que a política controla é o **consumo** próprio (controle, ventilação, instrumentação), que deve continuar para que a geração seja monitorada e ajustada. A política simplesmente os **ignora** ao iterar as folhas para alocação.

**Aquecimento persiste mesmo com módulo "desligado".** Para módulos pressurizados com `fator_termico > 0` (Habitação, ECLSS, Médico, Laboratório, Oficina), o `extra_termico` calculado por `consumo_aquecimento_kw` é adicionado independentemente do modo de operação — não dá para deixar o habitat congelar. Implica que o piso de consumo de Habitação numa madrugada de -70 °C pode ser ~3.4 kW de aquecimento mesmo que o módulo esteja "desligado". Se nem isso couber, a Etapa 4 (emergência) é acionada.

---

## 4. Sequência operacional (1 passo da simulação)

```
1. amostrar_clima(sol, hora) → atualiza clima_atual
2. Para cada gerador na árvore funcional:
     calcular geração atual via Camada 3
3. soma_geracao = agregação recursiva no ramo "Energia" da árvore funcional
4. oferta = soma_geracao + (bateria.carga_atual − bateria.reserva_emergencia)
5. Aplicar política de alocação (4 etapas) na árvore de criticidade:
     define modulo["modo_atual"] de cada folha
6. consumo_total = soma de consumo_atual_kw(modulo, clima) para todos os módulos
7. saldo = soma_geracao − consumo_total
8. Se saldo > 0: carregar bateria (até capacidade_max)
   Se saldo < 0: descarregar bateria
9. Atualizar fator_paineis (deposição contínua + evento estocástico de limpeza)
10. Registrar tudo no histórico
11. Avançar para próxima hora
```

168 passos no total. No final, o `historico` contém séries paralelas de 168 pontos cada — input direto para itens 1.3 e 1.4.

---

## 5. Conexão com os demais itens da Fase 3

| Item | Conexão com esta arquitetura |
|---|---|
| **1.1** (organização) | Listas (`modulos`, séries em `historico`), dicts (`clima_atual`, `bateria`, módulos individuais, `historico`), árvore N-ária (duas instâncias). Cumprido integralmente. |
| **1.2** (decisão automática) | Política de alocação da Camada 4 É a regra de decisão. Combina condições (oferta vs demanda em vários modos), prioriza Vital, gera saídas claras (modos, alertas). |
| **1.3** (regressão) | Após simulação, `historico["vento_ms"]` e `historico["geracao_eolica_kw"]` são listas paralelas prontas para ajuste linear por mínimos quadrados. O modelo cúbico do simulador será aproximado por uma reta — exatamente o que o enunciado pede. |
| **1.4** (análise de energia) | `historico["geracao_total_kw"]` vs `historico["consumo_total_kw"]` permite identificar passos com `risco` (consumo > geração) e `desperdício` (geração > consumo + capacidade da bateria). Os alertas/sugestões do enunciado caem direto. |

---

## 6. Fontes científicas (modelo climático)

**Vento e tempestades:**
- Modern Near-Surface Martian Climate (Springer, 2017)
- InSight wind data (EGU 2020)
- Martian dust storm distribution and annual cycle (Icarus 2023)
- Fluid Threshold of Windblown Sand on Mars (JGR Planets 2026)
- MSL Observations of 2018/MY34 Global Dust Storm (Guzewich 2019)

**Opacidade e atenuação solar:**
- MSL optical depth via solar imaging (Icarus 2023)
- MER 5-Mars-year optical depth record (NASA NTRS)
- The Mars Global Dust Storm of 2018 (NASA NTRS)

**Deposição em painéis:**
- Solar Panel Clearing Events on Mars (PMC)
- Seasonal Deposition and Lifting of Dust — Curiosity (Nature Sci Rep 2018)

**Temperatura:**
- Munguira et al. 2024 — One Martian Year of Near-Surface Temperatures at Jezero (MEDA)
- NASA — Seasonal Cycles in Curiosity's First Two Martian Years (REMS/Gale)

**Demanda térmica de habitats:**
- Cataldo & Borowski — Power Requirements for NASA DRA 5.0 (NTRS)
- Rucker — Surface Power for Mars (NASA NTRS 2016)
- ICES-2023-265 — ECLSS Options for Mars Transit and Surface (NTRS)
- Marspedia — Insulation (tabela de condutividades)

---

## 7. Fora de escopo (YAGNI)

Decisões deliberadas de **não** incluir, para manter o escopo coerente com a Fase 3:

- **Não** modelamos pressão atmosférica, umidade ou radiação ionizante (irrelevantes para o cálculo energético).
- **Não** modelamos falhas mecânicas, manutenção corretiva ou degradação por idade dos equipamentos.
- **Não** modelamos comunicação com a Terra (latência, janelas) — Comunicações é um módulo consumidor, mas não há "tráfego" simulado.
- **Não** há interação manual do operador via menu (a Fase 2 já tinha; aqui o foco é simulação automática).
- **Tempestades graves** (GDS) têm probabilidade tão baixa (~1.4% em 1 semana) que **não vão aparecer naturalmente** no horizonte simulado. O modelo as comporta, mas a expectativa é que apareça apenas a moderada didática + leves estocásticas.
- **Não** modelamos outras tripulações ou módulos além dos 12 originais + a turbina eólica de Fase 3.

---

## 8. Próximos passos

1. Após aprovação deste spec, a skill `writing-plans` será invocada para gerar um plano de implementação com etapas verificáveis.
2. A implementação seguirá uma camada por vez (bottom-up: Camada 1 primeiro, Camada 5 por último).
3. Cada camada terá testes que verificam invariantes (ex.: "soma de gerações nunca negativa", "Vital nunca desligado em condições normais").
