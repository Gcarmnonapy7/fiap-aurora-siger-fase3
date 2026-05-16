# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project context

Atividade Integradora da Fase 3 da disciplina de Ciência da Computação (FIAP, 2026). Continuação da Fase 2 (módulo de pouso MGPEB) — agora a colônia marciana **Aurora Siger** já pousou e o trabalho é simular sua operação por 7 sóis (168 horas).

Lê `enunciado.md` para o escopo oficial da atividade. Itens **1.1** (organização hierárquica dos dados) e a infraestrutura do simulador estão prontos. Itens **1.2** (regras de decisão), **1.3** (regressão linear vento↔eólica) e **1.4** (análise consumo×geração) ainda serão construídos sobre o histórico que `rodar_simulacao()` produz.

Documentação técnica completa em:
- `docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md` — design, justificativas físicas, referências NASA/ESA
- `docs/superpowers/plans/2026-05-14-organizacao-dados-colonia-implementacao.md` — plano TDD em 15 tasks (já executado)

## Tech stack

Python 3.12, **stdlib apenas** (`math`, `random`, `collections.deque`), `unittest` da stdlib para testes. Sem `pyproject.toml`, sem `requirements.txt`, sem virtualenv obrigatório. Restrição vem do enunciado: "Não é necessário utilizar bibliotecas avançadas".

Identificadores de código em **português** intencionalmente (módulos: `clima`, `geracao`, `consumo`, `alocacao`; classes: `No`, `EstadoTempestade`). Não normalizar para inglês. Warnings cSpell para palavras como `Siger`, `geracao`, `historico` são falsos positivos.

## Common commands

```bash
# Roda o simulador end-to-end (imprime árvores + resumo de 168 passos)
python3 main.py

# Suíte completa (68 testes, deve passar em <1s)
python3 -m unittest discover -v

# Um arquivo de teste só
python3 -m unittest tests.test_clima -v

# Uma classe ou um método específico
python3 -m unittest tests.test_clima.TestTempestade -v
python3 -m unittest tests.test_clima.TestTempestade.test_forcar_evento_didatico_no_sol_3 -v
```

Não há linter, formatter ou pre-commit configurados — o projeto se segura por testes.

## Architecture (the big picture)

O pacote `colonia/` está organizado em **5 camadas**, com dependências apontando sempre para camadas inferiores:

```
Camada 5: simulador.py, main.py          (orquestração)
Camada 4: alocacao.py                    (política — load shedding em 4 etapas)
Camada 3: geracao.py, consumo.py         (física por módulo)
Camada 2: clima.py                       (estocástico — vento, tempestade FSM, tau, painéis)
Camada 1: modulos.py, arvore.py,         (dados e estruturas)
          hierarquias.py, estado.py
Camada 0: constantes.py                  (parâmetros físicos — todas as 30+ constantes)
```

### Decisões arquiteturais que não são óbvias por arquivo

**Os 13 módulos compartilham referência entre as duas árvores.**
`modulos.MODULOS` é uma lista plana global. As duas árvores construídas em `hierarquias.py` (funcional e criticidade) usam `encontrar_modulo(id)` e referenciam **o mesmo dict** em ambas — testado em `tests/test_hierarquias.py::TestCompartilhamentoDeReferencias`. Consequência: mutar `modulo["modo_atual"]` em qualquer ponto afeta as duas árvores automaticamente. É por isso que `alocacao.py` muta os modos in-place sem se preocupar com sincronização.

**Estado mutável global causa leakage entre testes.**
`MODULOS` é importado por vários módulos. Testes que mudam `modo_atual` (especialmente `test_alocacao.py`) precisam resetar antes de rodar, ou o teste seguinte herda estado contaminado. `test_consumo.py::TestConsumoAtual` declara `modo_atual` explicitamente para se proteger disso. **Ao escrever novo teste que dependa de `modo_atual` padrão, sempre o setar explicitamente.**

**Determinismo via `random.seed(42)`.**
Todos os testes que envolvem `clima.py` ou `simulador.py` chamam `random.seed(42)` no `setUp`. O simulador é stochástico (`random.gauss`, `random.uniform`), mas reprodutível. Não tirar a seed — quebra a reprodutibilidade dos testes e da apresentação acadêmica.

**Evento didático forçado.**
`constantes.FORCAR_EVENTO_DIDATICO = True` faz uma tempestade `moderada` começar no sol 3 hora 8 (`SOL_EVENTO_DIDATICO`, `HORA_EVENTO_DIDATICO`). Isso garante que toda execução do `main.py` mostra a colônia lidando com crise climática — comportamento esperado e testado, não acidente. Para simular cenário sem evento, setar `FORCAR_EVENTO_DIDATICO = False`.

**Geradores são imunes ao load shedding.**
`alocacao.GERADORES = ("gerador_solar", "gerador_eolico", "gerador_nuclear")`. A política decide consumo dos módulos consumidores, mas não rebaixa geradores — ver justificativa em `colonia/alocacao.py` (docstring) e `docs/superpowers/specs/...md` (seção sobre política).

**Termo térmico desvia do plano original.**
A fórmula em `consumo.consumo_aquecimento_kw` escala **tanto `perda_W` quanto `ganho_interno`** por `fator_termico` (envelope menor → perde menos). O plano original só escalava ganho e resultado, mas isso falhava o teste `oficina@-50°C` e era fisicamente inconsistente. A correção está documentada no commit `f732386`. **Não reverter sem entender o teste.**

**Histórico = listas paralelas indexadas por passo.**
`historico["vento_ms"][k]` e `historico["geracao_eolica_kw"][k]` referem-se ao mesmo passo `k` da simulação. Esse formato é deliberado: os itens 1.3 (regressão) e 1.4 (análise) do enunciado vão consumir essas listas paralelas diretamente. Não trocar para lista de dicts.

## Workflow para adicionar features

Seguir o padrão TDD usado nas 15 tasks já executadas:

1. Escrever teste em `tests/test_<modulo>.py` referenciando a função/classe que ainda não existe.
2. Rodar e confirmar RED (`ModuleNotFoundError` ou `AttributeError`).
3. Implementar o mínimo para passar.
4. Rodar suite **completa** (`python3 -m unittest discover`) — não só o teste novo, por causa do leakage de estado descrito acima.
5. Commit granular com mensagem em português iniciando por `feat:`, `fix:`, `docs:`, `test:`.

Para os próximos itens do enunciado (1.2, 1.3, 1.4), prefira criar novos módulos em `colonia/` (ex: `decisao.py`, `previsao.py`, `analise.py`) que consomem `historico` em vez de modificar o simulador.
