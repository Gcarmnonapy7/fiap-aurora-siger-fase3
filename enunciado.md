# 1. Atividade Detalhada

Sua equipe deverá desenvolver um sistema integrado que represente o funcionamento inteligente da colônia. Esse sistema deve reunir, de forma organizada, tudo o que foi trabalhado ao longo dessa fase.

O sistema deve ser capaz de:

## 1.1 Organizar os dados da colônia

- Armazenar energia, consumo e clima em estruturas como **listas** ou **chave-valor**;
- Representar os sistemas da colônia de forma **hierárquica** (ex.: sistema energético → solar / eólico);
- Navegar entre subsistemas usando listas, tabelas chave-valor e organização hierárquica, conforme práticas trabalhadas na disciplina de **estruturas de dados**.

## 1.2 Tomar decisões automaticamente — Regras de decisão (lógica do sistema)

De forma simples, seu sistema deve:

- **Criar regras básicas.** Exemplo: `se energia < 50 → reduzir consumo`;
- **Combinar condições** quando necessário. Exemplo: `se energia < 50 E consumo alto → ativar modo economia`;
- **Priorizar o que é mais importante.** Exemplo: manter suporte à vida ligado e desligar sistemas não essenciais;
- **Gerar uma ação clara (saída).** Exemplo:
  - Entrada: `energia = 40`, `consumo = 70`
  - Saída: `"ALERTA: reduzir consumo"`

> **Objetivo:** transformar dados em uma decisão simples e clara, como foi feito nos exercícios de lógica e programação.

## 1.3 Prever comportamentos simples (usando regressão)

**Exemplo (colônia):** usar dados de vento para estimar quanta energia eólica será gerada.

### Como fazer

1. Organize os dados em listas (ex.: `vento = [8, 10, 12]`, `energia = [20, 25, 30]`);
2. Ajuste uma relação simples entre as variáveis (uma "reta");
3. Use essa relação para estimar valores futuros.

### Resultado esperado

- **Entrada:** `vento = 11`
- **Saída:** previsão de energia ≈ `27`

> **Objetivo:** transformar dados históricos em uma estimativa simples, como foi feito nos exercícios de regressão.

## 1.4 Analisar o uso de energia

**O que fazer:** comparar geração, consumo e (se houver) reserva de energia.

- Organize os dados em variáveis/listas (ex.: `geração = 45`, `consumo = 60`);
- Verifique situações simples:
  - `consumo > geração` → **risco**
  - `geração > consumo` → **possível desperdício**

### Exemplos

**Exemplo 1 (colônia):**

- Entrada: `geração = 40`, `consumo = 70`
- Saída: `"ALERTA: consumo maior que geração"`

**Exemplo 2 (colônia):**

- Entrada: `geração = 80`, `consumo = 30`
- Saída: `"SUGESTÃO: armazenar energia excedente"`

> **Objetivo:** analisar os dados de energia e gerar uma ação simples, como foi feito nas atividades envolvendo energia solar e eólica.

---

# 2. Entregáveis Obrigatórios

## 2.1 Repositório GitHub (Público)

A equipe deverá entregar um único sistema funcionando, contendo:

- **Código em Python** organizado em funções;
- **Estrutura clara** — separação de lógica, dados e decisões.

  > Por exemplo, o sistema recebe os dados como `energia = 40` e `consumo = 70`. Em seguida aplica uma regra simples, como "se energia < 50 então reduzir consumo". Por fim, gera uma decisão objetiva, exibindo a saída `"ALERTA: reduzir consumo"`.

- `README.md` com:
  - Explicação simples do funcionamento;
  - Exemplo de entrada e saída.

## 2.2 Relatório em PDF

O relatório deve explicar o sistema de forma objetiva:

- Como os dados foram organizados;
- Quais regras de decisão foram utilizadas;
- Qual foi o modelo de previsão aplicado;
- Como o sistema ajuda a melhorar o uso de energia na colônia;
- Link do repositório GitHub (público) para acesso ao sistema desenvolvido.

> Explicação simples e direta, com foco em mostrar entendimento, **não volume**.

---

# 3. Critérios de Avaliação

| Critério                      | Peso |
| ----------------------------- | :--: |
| Estruturação de dados         |  2   |
| Lógica de decisão             |  2   |
| Modelagem e previsão          |  2   |
| Implementação em Python       |  2   |
| Documentação e organização    |  2   |

*Tabela 1 — Critérios de avaliação. Fonte: Elaborada pelo autor (2026).*

---

# 4. Observações Importantes

- O projeto deve utilizar **apenas conceitos trabalhados nos capítulos**;
- Não é necessário utilizar bibliotecas avançadas;
- O foco está na **lógica, organização e interpretação**.

---

# 5. Objetivo Final

Ao final dessa atividade, espera-se que a equipe seja capaz de:

- Organizar dados de forma eficiente;
- Criar sistemas de decisão baseados em lógica;
- Aplicar modelos matemáticos para previsão;
- Desenvolver soluções computacionais integradas;
- **Evoluir de sistemas reativos para sistemas preditivos.**
