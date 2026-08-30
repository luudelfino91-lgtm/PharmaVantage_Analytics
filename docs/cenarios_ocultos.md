# Cenários ocultos · análise independente pós-entrega

**Contexto.** Depois da entrega inicial (Fases 1–2, 4 páginas do `.pbip`), foi pedida uma
segunda passada sobre a base sem nenhum roteiro — "como se você precisasse entender sem
ter recebido nenhuma outra instrução". Este documento registra os quatro achados que essa
passada trouxe, nenhum deles coberto pelas páginas existentes ou pelas 5 perguntas já
respondidas em `docs/insights_iniciais.md`.

**Entregável visual:** artifact publicado — [Cenários Ocultos](https://claude.ai/code/artifact/9f0a39b6-b30f-4b78-bc6a-38218ffa4670) — com os 4 gráficos (linha, barras) em SVG nativo,
paleta PharmaVantage (Navy/Teal/Amber/Crimson, ver `powerbi/identidade_visual.md`), tabela
de dados acessível atrás de cada gráfico e tooltip on hover.

## Método

Reconexão direta em `farma_xperiun.db` (SQLite — a mesma base que `scripts/validate_sqlite.py`
usa para reconciliar a Fase 2 contra o gabarito oficial), via Python + `sqlite3` puro, sem
passar pelo modelo semântico do Power BI. Totais conferem com o gabarito: 85.407 transações,
receita R$ 2.313.807,90. Catorze hipóteses testadas; quatro confirmadas com dado forte, quatro
descartadas por honestidade metodológica (registradas abaixo).

## Cenário 1 — A margem não caiu por desconto. Caiu por mix.

- Margem global: 29,08% (2014) → pico 29,99% (2015) → 28,36% (2018) → 28,47% (2019).
- Desconto médio sobre receita bruta: ~1,0% em todos os 6 anos, sem tendência — descarta
  desconto como causa.
- Margem *dentro* de cada categoria: variação de no máximo ±0,3pp entre 2014 e 2019 —
  descarta erosão de preço/custo como causa.
- % da receita vinda de produtos de venda controlada (`d_produto.exige_receita = 1`): 40,7%
  (2015, mínimo) → 50,8% (2018, máximo) → 49,5% (2019).
- **Correlação entre % receita controlada e margem global, 2014–2019: r = −0,93.**
- Causa raiz: categorias controladas têm margem estruturalmente menor — Ansiolíticos 23,7%,
  Antiasmáticos 22,4%, Sedativos/Hipnóticos 18,8% — contra 27,2–38,9% nas categorias de
  venda livre (Paracetamol 38,9%, Salicilatos 38,8%, Anti-histamínicos 30,6%, Derivados Ác.
  Propiônico 30,1%, Derivados Ác. Acético 27,2%). Quando o mix migra para controlados, a
  margem da empresa cai matematicamente, mesmo com toda categoria individualmente estável.
- **Achado dentro do achado:** a razão receita-livre/receita-controlada por dia da semana é
  ~1,01–1,12× em dias úteis, sobe para 1,32× no sábado e 1,55× no domingo — controlados
  dependem de prescrição médica recente, e clínicas fecham no fim de semana. O fim de semana
  da farmácia é estruturalmente mais dependente de OTC e mais rentável por real vendido do
  que a segunda-feira.

## Cenário 2 — O turno da noite não é o mesmo turno nos 7 dias da semana

Cruzamento `f_vendas.hora × d_calendario.dia_semana`, nunca feito nas páginas existentes
(que só têm granularidade de turno). Participação de cada hora na receita diária do seu
grupo (dia útil vs. fim de semana, normalizado para comparar forma de curva):

- Às 21h: dias úteis ainda respondem por 7,04% da receita do dia; fim de semana cai para
  0,26% — colapso quase total.
- Pico do fim de semana: meio-dia (12h, 10,3% da receita do dia). Pico de dia útil: 19h–20h
  (~9,2% cada).
- `d_turno` define "Noite" como bloco fixo 18h–22h para qualquer dia da semana — a curva real
  mostra que essa definição não se sustenta aos sábados/domingos.

**Implicação sobre o simulador já entregue:** o What-If "Hora Extra" (medidas `Receita
Potencial Hora Extra` / `Lucro Potencial Hora Extra` / `Fechamento Simulado`) aplica o mesmo
fator de atenuação (0,7) independente do dia selecionado no filtro. Com esta curva, hora
extra no fim de semana captura receita marginal próxima de zero — o ganho real do simulador
está concentrado em dias úteis. Recomendação de produto: documentar essa limitação ou
restringir a projeção a dias úteis.

## Cenário 3 — 42,6% da receita depende de dois fornecedores

Ângulo diferente do que já existe na página Diagnóstica (prazo de entrega × margem × capital
de giro por fornecedor): aqui a pergunta é concentração de receita — risco de continuidade de
negócio, não capital imobilizado.

| Fornecedor | % da receita total |
|---|---|
| Medley | 27,4% |
| EMS | 15,2% |
| Eurofarma | 14,0% |
| Cimed | 13,4% |
| Neo Química | 9,7% |
| Hypera Pharma | 9,4% |
| Aché | 8,5% |
| Cristália | 2,4% |

Medley sozinho responde por 27,4% da receita (prazo médio de entrega de 3 dias — mitigante
para ruptura de estoque, mas não para risco comercial/negociação). Medley + EMS = 42,6%.
Nenhum produto da base tem mais de um fornecedor cadastrado simultaneamente: hoje não existe
fornecedor alternativo pré-qualificado para os itens da Medley.

## Hipóteses descartadas (testadas, sem sinal)

- **Desconto agressivo:** desconto médio uniforme (~1%) em todas as formas de pagamento,
  dias da semana e anos. Maior desconto individual encontrado: 15,8% (transação de R$0,19).
  Sem padrão de abuso.
- **Migração de forma de pagamento:** participação de PIX/Cartão Crédito/Débito/Dinheiro/
  Convênio praticamente idêntica de 2014 a 2019 (PIX sempre ~30–31%). Sem mudança de
  comportamento do consumidor na janela.
- **Concentração de produto (Pareto clássico):** não há 80/20 aqui — são necessários 19 dos
  33 produtos ativos (58%) para atingir 80% do lucro acumulado. Portfólio maduro e
  diversificado; o risco de concentração está no fornecedor (Cenário 3), não no catálogo.
- **Efeito feriado:** receita/dia cai ~9% em feriados, ticket médio sobe ~3,6%, leve desvio
  de mix para Ansiolíticos/Sedativos — sinal real mas estatisticamente fraco (1.338
  transações em feriados na base toda); não elevado a cenário principal.

## Status

Os três cenários confirmados foram levados adiante como entrega formal na auditoria de
hipóteses seguinte (ver `docs/auditoria_hipoteses.md`): o Cenário 1 (mix de controlados)
virou a página "05 · Cenários & Impacto" do `.pbip`, com medidas dedicadas de lucro perdido
por produto abaixo da margem média da casa.
