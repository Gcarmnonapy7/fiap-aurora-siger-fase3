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

**Saída** (exemplo do `main.py` com `seed=42`):

```
Passos simulados: 168
Geração total média: 92.6 kW
Consumo total médio: 94.1 kW
Bateria final: 0.0 / 500.0 kWh
Passos com tempestade: 142 de 168
Passos com alerta: 98
```

A colônia opera em déficit modesto durante a tempestade didática — situação realista que dará material rico para os itens 1.4 (decisão automática) e 1.5 (análise) da entrega final.

## Documentação técnica

- `docs/superpowers/specs/2026-05-14-organizacao-dados-colonia-design.md` — design completo com decisões e justificativas
- `docs/superpowers/plans/2026-05-14-organizacao-dados-colonia-implementacao.md` — plano de implementação seguido

## Equipe

Mesma equipe da Fase 2 — Gabriel Carmona, Carlos Eugênio, Marcio Francisco, Iúri Leão, Maria Sophia.
