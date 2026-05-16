# Aurora Siger — Fase 3: Organização, decisão e análise de dados

Simulador em Python da colônia marciana **Aurora Siger** após o pouso bem-sucedido dos 12 módulos da Fase 2. Os módulos agora **operam** sob clima estocástico realista (7 sóis marcianos), produzindo séries temporais de geração, consumo e estado de bateria que servirão de base para os itens de previsão (regressão linear) e decisão automática da entrega final.

Atividade Integradora da Fase 3 — Ciência da Computação, FIAP (2026).

## Entregáveis

| Arquivo | Descrição |
|---------|-----------|
| `main.py` | Entry point do simulador (imprime árvores e resumo de 168 passos) |
| `colonia/` | Pacote Python — 9 módulos organizados em 5 camadas (dados → clima → geração → política → histórico) |
| `tests/` | Suíte de 68 testes unitários e de integração (`unittest`) |
| `docs/superpowers/specs/` | Documento de design com decisões arquiteturais e referências científicas |
| `docs/superpowers/plans/` | Plano de implementação em 15 tasks (TDD) |

## Estrutura do repositório

```
.
├── README.md
├── LICENSE
├── enunciado.md                   # enunciado original da atividade
├── main.py                        # entry point CLI do simulador
├── colonia/
│   ├── __init__.py
│   ├── constantes.py              # parâmetros físicos (clima, painéis, bateria, térmico)
│   ├── modulos.py                 # lista plana dos 13 módulos
│   ├── arvore.py                  # classe No N-ária genérica (DFS, BFS, busca, agregação)
│   ├── hierarquias.py             # duas árvores: funcional e criticidade
│   ├── clima.py                   # vento, temperatura, tempestades (FSM), tau, painéis
│   ├── geracao.py                 # geração solar, eólica e nuclear
│   ├── consumo.py                 # consumo base + termo térmico Q=U·A·ΔT
│   ├── alocacao.py                # política de load shedding em 4 etapas
│   ├── estado.py                  # bateria, clima atual, histórico
│   └── simulador.py               # orquestrador (passo + horizonte de 168 passos)
├── tests/                         # testes unitários espelhando os módulos de colonia/
└── docs/superpowers/
    ├── specs/                     # design e justificativas
    └── plans/                     # plano de implementação seguido (TDD)
```

## Como executar o simulador

```bash
python3 main.py
```

Sem dependências externas — usa apenas `math`, `random` e `collections.deque` da biblioteca padrão.

O programa imprime as duas hierarquias (funcional e criticidade), roda 7 sóis marcianos (168 horas) e mostra um resumo numérico do histórico.

**Saída de exemplo** (`seed=42`):

```
Passos simulados: 168
Geração total média: 92.6 kW
Consumo total médio: 94.1 kW
Bateria final: 0.0 / 500.0 kWh
Passos com tempestade: 142 de 168
Passos com alerta: 98
```

## Como rodar os testes

```bash
python3 -m unittest discover -v
```

Os testes são determinísticos via `random.seed(42)` e validam:

- Estrutura da árvore N-ária e percursos (DFS pré-ordem, BFS por nível).
- Construção das duas hierarquias e compartilhamento de referências entre elas.
- Modelo climático (vento, temperatura, tempestades, opacidade tau, fator de painéis).
- Geração de cada fonte (solar com Beer-Lambert, eólica com cut-in e saturação, nuclear constante).
- Consumo com termo térmico em diferentes temperaturas externas.
- Política de alocação em 4 etapas (load shedding).
- Integração ponta-a-ponta do simulador (histórico íntegro, bateria dentro dos limites, evento didático registrado).

## Equipe

| Nome | RM | E-mail |
|------|----|--------|
| Gabriel Carmona Bittencourt | RM569239 | gabrielcarmabittencourtpy@gmail.com |
| Marcio Francisco dos Santos Junior | RM570758 | marciofsantos65@gmail.com |
| Iúri Leão de Almeida | RM570215 | iurileao@gmail.com |
| Maria Sophia Domingues dos Santos | RM571209 | maria.sophia.domingues@gmail.com |

## Licença

[MIT](LICENSE)
