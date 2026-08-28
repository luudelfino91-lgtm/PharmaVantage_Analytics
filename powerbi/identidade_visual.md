# PharmaVantage Analytics — identidade visual

Especificação da identidade corporativa para o mercado de Life Sciences de Dublin/Cork,
aplicada ao artifact `PharmaVantage Executive Overview` e ao tema `pharmavantage_theme.json`
(pasta `powerbi/`). Este documento é a referência para replicar a identidade nos visuais reais
do Power BI Desktop.

**Atualização:** os visuais de relatório (PBIR `page.json`/`visual.json`) também podem ser
construídos por edição direta de arquivo — é JSON puro, como o TMDL do modelo. Os 4 cartões de
KPI abaixo já foram criados dessa forma (ver `PharmaVantage Analytics.Report/definition/pages/
834017b1147ca7af3a4d/visuals/`) e confirmados renderizando no Power BI Desktop. Não foi preciso
desenhar nada manualmente na tela — só um clique em "Apply external changes" no Desktop, que
detecta mudança externa nos arquivos do projeto e recarrega.

## Paleta

| Cor | Hex | Uso |
|---|---|---|
| Navy Slate | `#0B2545` | Primária institucional — títulos, cabeçalhos, texto de marca |
| Clinical Teal | `#139A8C` | Positivo/saudável — série principal, estado ativo |
| Muted Sage | `#8DAA9D` | Secundária — séries comparativas, tagline |
| Warm Amber | `#E08738` | Atenção — desvio moderado |
| Alert Crimson | `#C94A4A` | Crítico — meta não batida, margem negativa |
| Off-White / Soft Mist | `#F4F7F6` | Fundo de página |
| Graphite Dark | `#2D3748` | Texto de corpo, rótulos |

**Nota de validação:** rodei o validador de paleta categórica da skill de dataviz contra os
oito `dataColors` do tema. O par Navy/Teal passa CVD e contraste com folga (ΔE 36+, contraste
≥3:1) — a combinação usada de fato nos gráficos (Plano vs. Realizado). Isolado, o Navy Slate
falha os testes de "luminosidade" e "piso de croma" do validador, porque esses testes esperam
tons de meio-tom saturados para marcas de gráfico, e o Navy é deliberadamente quase-preto por
identidade institucional. Isso é uma escolha de marca, não um erro — mas por isso o Navy não
deve ser usado como uma cor categórica genérica em gráficos de muitas séries; funciona bem como
par binário (Plano/Realizado, institucional/ativo) ou como cor de texto e cabeçalho, que é como
foi aplicado no dashboard.

Amber e Crimson têm baixo contraste como **texto pequeno** direto sobre fundo claro (abaixo de
3:1). No dashboard, uso duas variantes: a cor de marca (`--amber` / `--crimson`) para preenchimentos
decorativos (barra lateral do KPI, ponto do pill), e uma variante mais escura (`--amber-ink` /
`--crimson-ink`) para texto de fato — números de variância, texto do pill. Ambas mantêm o mesmo
matiz, só ajustam a luminosidade para leitura.

## Logomarca

SVG vetorial, sem dependência de imagem: um "V" (de *Vantage*) construído em duas linhas finas
que se fundem, no vértice, com uma pequena cruz médica (marca do setor) e continuam como uma
linha de pulso ascendente (ECG estilizado) — o V não termina, ele *vira* a tendência de
crescimento. Gradiente linear Navy Slate → Clinical Teal ao longo do traço.

- **Pharma** — Segoe UI Semibold, `#0B2545`
- **Vantage** — Segoe UI Light, `#139A8C`
- Tagline — Segoe UI Bold, caixa alta, 7.5–8pt, `#8DAA9D`: **ANALYTICS & MARGIN GOVERNANCE**

Implementado como SVG inline no cabeçalho do dashboard (ver `<svg>` no topo do arquivo) —
reutilizável em qualquer página ou apresentação sem depender de arquivo de imagem externo.

## Layout

- Faixa superior fixa, 60px, fundo branco: logo à esquerda, data da última atualização ao
  centro, filtros globais à direita (Ano, Turno, Grupo Terapêutico).
- Quatro cartões de KPI no topo do corpo: fundo branco, cantos arredondados, sombra suave —
  Gross Revenue, Net Margin %, Total Transactions, Target Variance %.
- Formatos numéricos internacionais: separador de milhar por vírgula, decimal por ponto,
  percentuais com uma casa decimal.

## Tema do Power BI

`powerbi/pharmavantage_theme.json` já está na pasta do projeto. Para aplicar:
**Exibir → Temas → Procurar Temas** no Power BI Desktop, selecionar o arquivo.

## Cartões de KPI — já construídos no `.pbip` real

O tema JSON cobre cor/tipografia de visuais nativos automaticamente após a importação. Os 4
cartões de KPI foram construídos como visuais `cardVisual` reais (não mockup), cada um em seu
próprio `visual.json`, vinculados às medidas do modelo:

| Cartão | Medida (`_Medidas`) | Formato |
|---|---|---|
| Gross Revenue | `Receita Líquida` | `"R$" #,0.00` (moeda nativa BRL — não convertida para €) |
| Net Margin % | `Margem %` | `0.0%` |
| Total Transactions | `Transações` | `#,0` |
| Target Variance % | `% Desvio da Meta` *(nova)* | `+0.0%;-0.0%;0.0%` |

`% Desvio da Meta` é uma medida nova (`[% Atingimento Meta] - 1`), criada porque não existia
uma medida de variância percentual pronta no modelo — só o atingimento bruto e o gap em R$.

## Cabeçalho e gráficos de apoio — já escritos, ainda não verificados na tela

Escritos diretamente em disco (sem abrir o Power BI Desktop, a pedido do usuário — os arquivos
ficam prontos e o Desktop só precisa ser aberto/recarregado quando for conveniente):

| Visual | Tipo | Conteúdo |
|---|---|---|
| Cabeçalho de marca | `textbox` | "Pharma" (Navy, Semibold) + "Vantage" (Teal, Light) + tagline "ANALYTICS & MARGIN GOVERNANCE" (Sage, Bold, caixa alta) |
| Filtro Ano | `slicer` (Dropdown) | `d_calendario[ano]` |
| Filtro Turno | `slicer` (Dropdown) | `d_turno[nome_turno]` |
| Filtro Grupo Terapêutico | `slicer` (Dropdown) | `d_produto[grupo_terapeutico]` |
| Revenue Trend by Year | `lineChart` | Categoria `d_calendario[ano]`, valor `Receita Líquida`, linha Teal |
| Plan vs. Actual by Therapeutic Group | `clusteredColumnChart` | Categoria `d_produto[grupo_terapeutico]`, `Receita Líquida` (Teal) vs. `Meta Receita` (Navy) |
| Shift Performance | `tableEx` | `d_turno[nome_turno]`, `Receita por Hora`, `Transações por Hora`, `Índice de Produtividade do Turno` |

Como o Power BI Desktop não foi aberto nesta etapa, essas 7 visões ainda não foram conferidas
visualmente (só a validação de JSON). Na próxima vez que o `.pbip` for aberto (ou recarregado
com "Apply external changes"), valem a pena conferir: clipping de texto nos cartões/slicers,
overlap entre o cabeçalho e a linha de KPIs, e se as cores dos gráficos saíram como esperado.

## Nota sobre moeda

O tema/artifact usa `€` para o pitch de portfólio (mercado Dublin/Cork). Os cartões reais no
`.pbip`, porém, mantêm `R$` — os dados de origem são BRL de verdade, e mudar o símbolo no
modelo real apresentaria os números como se fossem Euros. A narrativa "mercado irlandês" fica
no artifact/tema (contexto de apresentação), não na formatação numérica do dado real.

## As 3 telas do mockup — agora também como páginas reais

O `mockups.html` original ("Farma Xperiun") é um sistema de 3 telas (Descritiva/Diagnóstica/
Comparativa). Essas 3 telas foram construídas como páginas reais no `.pbip` (mesmo método:
`visual.json` escrito direto em disco, sem abrir o Power BI Desktop — ele está fechado desde
que você pediu para eu não abrir). **Nada disso foi visto na tela ainda** — só validado como
JSON sintaticamente correto. Abra o `.pbip` quando for conveniente para conferir.

Mudanças no modelo (por edição de TMDL, já que o Desktop estava fechado e não dava para usar o
TOM ao vivo):
- 2 medidas novas em `_Medidas` (pasta "04 · Turno"): `Lucro Potencial Hora Extra` e
  `Fechamento Simulado` (mesma lógica de `Receita Potencial Hora Extra`, para completar o
  simulador What-If da Tela 3).
- 1 coluna calculada nova em `d_fornecedor`: `'Local' = [cidade] & "/" & [estado]`.
- 1 ajuste em `d_calendario`: `sortByColumn: mes` na coluna `nome_mes`, para o heatmap da
  Tela 2 ordenar jan→dez em vez de alfabético.

**Página "01 · Descritiva"** (11 visuais): 5 cartões de KPI com tarja colorida (Receita
Líquida/Lucro em teal, Ticket Médio em amber, Transações em navy, Quantidade Vendida em sage),
gráfico de linha de receita mês a mês, gráfico de barras de receita por grupo terapêutico
(margem como tooltip), tabela de forma de pagamento, tabela de top produtos por receita, e
gráfico de receita por turno.

**Página "02 · Diagnóstica"** (5 visuais): matriz-heatmap (categoria × mês, valor = Índice
Sazonal vs. Categoria, gradiente Teal→Off-White→Amber), gráfico de receita média por tipo de
dia, gráfico de dispersão de fornecedores (prazo × margem, tamanho = receita) e tabela de
capital de giro por fornecedor. **Atenção**: o heatmap (conditional formatting `FillRule` numa
matriz) e o gráfico de dispersão (`scatterChart`, sem referência oficial confirmada para os
nomes exatos dos papéis de dados) são os dois pontos de maior risco desta entrega — vale a
pena conferir esses dois primeiro.

**Página "03 · Comparativa"** (14 visuais): 5 cartões de KPI (Meses Batidos, Taxa de Sucesso
Mensal, Aderência da Meta ao Realizado, Gap da Meta, Atingimento de Receita), gráfico de Meta
vs. Realizado por ano, caixa de texto com o achado central, os dois gráficos de turno
(absoluto vs. por hora) lado a lado, e o simulador What-If completo: slicer ligado a
`'Cenário Hora Extra'[Horas]` (0–3h) + 3 cartões (Receita Potencial, Lucro Potencial,
Fechamento Simulado).

**Simplificações assumidas** (documentadas para não parecerem esquecimento): sem filtro Top N
na tabela de produtos (lista completa ordenada); sem o gráfico "2019 vs. 2018 por dia
operado" (comparação dia a dia entre dois anos, mais complexa que os demais visuais); sem a
métrica "atingimento de quantidade" do mockup (não existe medida pronta equivalente no
modelo).
