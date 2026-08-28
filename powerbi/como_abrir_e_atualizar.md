# Como abrir e atualizar o modelo

O modelo semântico **já está construído**. Os arquivos TMDL em
`PharmaVantage Analytics.SemanticModel/definition/` contêm tabelas, colunas, relações,
hierarquia de datas e as 50 medidas DAX. Falta apenas carregar os dados.

---

## 1 · Abrir o projeto certo

Abra o **`PharmaVantage Analytics.pbip`** — não o `.pbix`.

> ⚠️ Existe um `PharmaVantage Analytics.pbix` na mesma pasta. Ele é o arquivo antigo, com o
> modelo vazio. Abrir o `.pbix` por engano faz parecer que nada foi feito. O modelo construído
> está no formato PBIP, e só o `.pbip` o enxerga.

Se o Power BI Desktop reclamar do formato, ative **Arquivo → Opções → Recursos de visualização →
Power BI Project (.pbip) save option** e reinicie.

## 2 · Autenticar no SQL Server

Na primeira abertura o Power BI vai pedir credenciais da origem:

1. Aparece o aviso de conteúdo nativo/fonte de dados → **Editar credenciais**
2. Aba **Windows** → *Usar minhas credenciais atuais*
3. Nível de privacidade: **Organizacional** (ou *Nenhum*, se preferir evitar avisos)

## 3 · Atualizar

**Página Inicial → Atualizar.** São 85.407 linhas — leva poucos segundos.

Depois do refresh, `d_periodo` é carregada via Power Query (deriva de `f_meta_mensal`) e
`Cenário Hora Extra` se materializa (tabela calculada em DAX) — todas as medidas passam a
devolver número.

## 4 · Conferir contra o gabarito

Jogue um visual de cartão na tela com estas medidas. Sem nenhum filtro, o modelo tem de
reproduzir exatamente:

| Medida | Valor esperado |
|---|---|
| `Transações` | 85.407 |
| `Receita Líquida` | R$ 2.313.807,90 |
| `Lucro` | R$ 671.861,32 |
| `Ticket Médio` | R$ 27,09 |
| `Dias Operados` | 2.080 |
| `Meses Batidos` | 31 |
| `Receita por Hora` (turno Noite) | R$ 88,96 |

**Se algum divergir, o problema está na carga do banco — não no modelo.** Os mesmos números
já foram validados em SQL puro na Fase 2.

---

## Trocar de servidor

O modelo usa dois parâmetros do Power Query. **Página Inicial → Transformar dados →
Gerenciar Parâmetros:**

| Parâmetro | Valor atual |
|---|---|
| `Servidor` | `localhost` |
| `Banco` | `farma_xperiun` |

Para uma instância nomeada, mude `Servidor` para `localhost\SQLEXPRESS`. Todas as seis tabelas
seguem o parâmetro — não há string de conexão espalhada pelas consultas.

---

## O que já está pronto no modelo

**9 tabelas**

| Tabela | Tipo | Origem |
|---|---|---|
| `f_vendas` | Fato diário | `dbo.f_vendas` |
| `f_meta_mensal` | Fato de orçamento mensal | `dbo.d_meta_mensal` (renomeada) |
| `d_calendario` | Dimensão · **marcada como Tabela de Datas** | `dbo.d_calendario` |
| `d_produto` | Dimensão | `dbo.d_produto` |
| `d_fornecedor` | Dimensão | `dbo.d_fornecedor` |
| `d_turno` | Dimensão | `dbo.d_turno` |
| `d_periodo` | **Dimensão conformada** | Power Query (M) · `Table.Distinct` sobre `f_meta_mensal[ano,mes]` |
| `_Medidas` | Tabela de medidas | Calculada (DAX) |
| `Cenário Hora Extra` | Parâmetro What-If (0–3 h) | Calculada (DAX) |

**6 relações**, todas 1:N com filtro cruzado **Simples**. Nenhuma bidirecional, nenhuma inativa.

**5 colunas calculadas**

- `d_calendario[PeriodoKey]` e `f_meta_mensal[PeriodoKey]` — a ligação lógica ano+mês
- `d_calendario[Tipo de Dia]` — Dia Útil / Fim de Semana / Feriado
- `d_turno[Duração do Turno (h)]` — base das medidas normalizadas por hora
- `d_produto[Tipo de Venda]` — Controlado / Venda Livre

**50 medidas** em 8 pastas de exibição, com `VAR` em todo cálculo de múltiplas etapas e
descrição de negócio em cada uma (aparece como tooltip no painel de campos).

**Colunas ocultas:** todas as chaves estrangeiras, e preço/custo/margem de `d_produto` — que são
valores de tabela, não os praticados. O preço real está em `f_vendas` e varia ±5%.

---

## Detalhes de modelagem que valem conhecer

**`d_meta_mensal` virou `f_meta_mensal`.** Ela contém medidas aditivas e descreve um evento de
planejamento: é um fato de orçamento, não uma dimensão. Foi tratá-la como dimensão que levou à
busca por uma chave estrangeira que nunca poderia existir.

**`d_periodo` resolve a granularidade.** O fato é diário, a meta é mensal — não existe relação
1:N possível entre eles. A dimensão conformada fica acima do calendário e filtra os dois lados
a partir de um ponto só.

**`d_periodo` é tabela Power Query, não calculada em DAX.** A primeira versão construída usava uma tabela calculada (`SUMMARIZE`/`ADDCOLUMNS`), mas o Power BI Desktop falha ao reabrir um `.pbip` quando uma relação aponta para a coluna de uma tabela calculada por `SUMMARIZE`/`DISTINCT` — erro `invalid column ID`, um problema conhecido do motor TOM (reproduzido também fora deste projeto: github.com/TabularEditor/TabularEditor/issues/891). A correção foi reconstruir `d_periodo` como tabela importada via Power Query, derivada de `f_meta_mensal` (a mesma fonte e a mesma lógica já previstas em `star_schema.md`), eliminando a classe do bug por completo.

**Ao filtrar por dia, a meta não responde.** É proposital. A medida `% Atingimento Meta` usa
`ISINSCOPE` e devolve vazio em contexto diário, em vez de exibir um percentual que não existe.

**Meta zero ≠ meta baixa.** Outubro, novembro e dezembro de 2019 têm meta zerada por
característica da base. Esses meses saem do cálculo de atingimento.

---

## Backup

O estado anterior do modelo (vazio) está em `_backup_SemanticModel_antes/`, na mesma pasta.
Para voltar atrás, substitua a pasta `PharmaVantage Analytics.SemanticModel` por ele.
