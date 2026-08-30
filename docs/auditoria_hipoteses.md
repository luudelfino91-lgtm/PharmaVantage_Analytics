# Farma Xperiun — auditoria das hipóteses e cenários

Documento de referência da auditoria completa: as hipóteses do Datacast julgadas contra os
dados, as análises formalmente solicitadas respondidas, as hipóteses próprias testadas, o
ranking de impacto e as recomendações.

**Entregável:** artifact *Farma Xperiun sob Auditoria*
(https://claude.ai/code/artifact/3c747f2d-8622-4694-bf4e-c47c5257a889).

**Fontes primárias lidas nesta rodada** (nunca lidas antes no projeto):
- `Base e Materiais Auxiliares/Base/Datacast Xperiun-.../Transcrição Video.txt` — a transcrição
  completa do vídeo (SRT, ~12k caracteres de texto limpo).
- `.../Solicitação.txt` — o briefing formal do desafio.

Todos os números saem de `farma_xperiun.db` via SQL direto (não pelo modelo semântico) e foram
reconciliados com o gabarito oficial: 85.407 transações, R$ 2.313.807,90 de receita,
R$ 671.861,32 de lucro, ticket R$ 27,09, 33 produtos, 8 fornecedores. **Todos conferem.**

## Veredito das 19 hipóteses do Datacast

| # | Afirmação do vídeo | Veredito | Dado que decide |
|---|---|---|---|
| H1 | Turno da noite é curto porque o movimento cai depois das 21h | **Refutada em dia útil** | 21h rende R$ 84,69/dia vs. 8h R$ 69,16/dia (+22,5%). No FDS confirma-se: venda às 21h em 38 de 593 dias |
| H2 | Ou é por custo de hora noturna / segurança | Não testável | Base não tem folha nem ocorrências |
| H3 | 14h/dia é típico de varejo com público direto | Confirmada | Amplitude real 8h–21h, 14 horas distintas |
| H4 | Dá para confiar na qualidade dos dados (bissexto) | **Confirmada, e mais forte** | 45 vendas em 29/02/2016; **zero** inconsistências aritméticas em receita e lucro nas 85.407 linhas; zero órfãs |
| H5 | Operação no Brasil | Confirmada | 48 feriados brasileiros, 2014-01-01 a 2019-12-25 |
| H6 | É farmácia/drogaria | Confirmada | 8 laboratórios, 33 medicamentos com código ATC |
| H7 | A farmácia ficava no Sudeste | Não verificável | Sem endereço na base. 7 de 8 fornecedores no Sudeste = 90,3% da receita |
| H8 | Neo Química, única fora do Sudeste, tem o maior prazo | **Confirmada exatamente** | Neo Química (Anápolis/GO) 5 dias; EMS e Hypera (SP) 2 dias. Todos os detalhes do vídeo conferem |
| H9 | Prazos variados imobilizam capital de giro | Confirmada | Neo Química: pior prazo (5d) + margem 22,4% |
| H10 | "Crescimento implacável, consistente, claríssimo" | **Parcial** | Janeiro dobrou (29.355→58.879) e jan–set +37,5%, mas a meta **anual** de 2017 (363.000) ficou abaixo de 2014 (364.348) e 18% abaixo de 2016. Serrilhado, não linha |
| H11 | Outubro é sempre um dos meses de meta mais alta | Confirmada | Meta média out (2014-18) = R$ 44.074, a maior; top-3 em todos os anos |
| H12 | Outubro forte por alergia de primavera → antialérgicos | **Refutada e invertida** | Anti-histamínicos em outubro: índice 0,62, o **4º pior mês**. Pico real abr/mai/jun = 1,58/1,78/1,72 — outono |
| H13 | Outubro Rosa gera tráfego indireto | Sem evidência | Quem puxa outubro é Paracetamol e Derivados (1,21), analgésico comum |
| H14 | Meta de out/2019 cai para ~10.000 BRL | **Erro factual** | Meta out/2019 = R$ 0,00. Os ~R$ 9.175 são o **realizado** parcial de 8 dias. E são **três** meses zerados, não dois |
| H15 | Metas zeradas = a operação cessou | **Refutada** | Jan–set/2019 = R$ 1.195,97/dia, o **melhor da série** (2016: 1.174,96; 2018: 1.156,50), com os mesmos ~269 dias operados |
| H16/H17 | Falha de sistema / venda da empresa | Compatíveis | Terminou a captura, não o negócio. Esta base não distingue as duas |
| H18 | Cartão de débito confirma varejo | Confirmada | 5 meios, todos de varejo |
| H19 | Relação com o início da pandemia (dúvidas da diretoria) | **Impossível** | Base termina em 08/10/2019; pandemia em março/2020 |

**Placar: 8 confirmadas · 4 refutadas · 3 parciais/corrigidas · 4 não testáveis.**

## Achado adjacente a H11 — a meta está calibrada no mês errado

Índice mensal (100 = média do ano):

| | Jan | Out | Dez |
|---|---|---|---|
| **Meta** | 110,6 | **131,1** | 124,6 |
| **Realizado** | **123,7** | 116,3 | 120,3 |

A ordem da meta (Out > Dez > Jan) é o inverso exato da ordem do realizado (Jan > Dez > Out).
São ~15 pontos de ambição sobrando em outubro e ~13 faltando em janeiro — explica parte dos 38
meses não batidos sem que nada estivesse errado na operação.

## Respostas ao briefing (Solicitação.txt)

**Descritivas.** Receita 2014–2019 = R$ 2.313.807,90 (por ano: 353.879 / 386.163 / 441.765 /
363.143 / 437.965 / 330.892). Ticket médio R$ 27,09. Top volume: Paracetamol 750mg (10.718),
Dipirona 500mg (10.582). Top receita: Formoterol 12mcg (238.950), Budesonida 200mcg (180.607).
Pagamento: PIX 30,6%, Crédito 24,9%, Débito 19,5%, Dinheiro 15,3%, Convênio 9,8%. Turnos:
Manhã 828.533 / Tarde 769.649 / Noite 715.626.

**Diagnósticas.**
- Categorias abaixo da média (29,04%): Deriv. Ác. Acético 27,2%, Ansiolíticos 23,7%,
  Antiasmáticos 22,4%, Sedativos 18,8% — **as três piores são as três de venda controlada**.
- *"Inverno aumenta respiratórios?"* → **NÃO.** Antiasmáticos têm a sazonalidade mais fraca do
  catálogo (amplitude 0,25) e ficam abaixo da média em jul (0,97) e ago (0,90). Quem sobe no
  inverno é Deriv. Ác. Acético (ago 1,38), Ansiolíticos (ago 1,27) e Sedativos (jul 1,26).
- *"Turnos concentram desconto?"* → **NÃO.** Manhã 1,043% / Noite 1,007% / Tarde 0,964%.
- *"Batendo metas?"* → 97,5% de atingimento agregado nos 69 meses com meta real; **31 de 69
  meses batidos (44,9%)**; gap R$ 59.698. (Os 3 meses de 2019 com meta zerada ficam fora.)

**Comparativas.** Meta vs. realizado por ano: 97,1 / 94,7 / 99,7 / 100,0 / 99,6 / 95,5.
Grupo terapêutico 2014→2019: Respiratório **+56,6%**, Anti-inflamatórios −3,2%,
Analgésicos −18,1%, Sistema Nervoso −41,6%. Ticket por turno: Noite +26,7% (24,78→31,40),
Manhã +3,8%, Tarde +4,6%.

**Perguntas da introdução.** A noite vende 13,6% menos em absoluto mas **11,6% mais por hora**,
com ticket 8% maior e a melhor margem. O PIX domina e **não** afeta o desconto (amplitude
0,11pp). Quem sustenta receita (Formoterol, Budesonida — margem 19–21%) não é quem sustenta
lucro (Paracetamol, Dipirona — 39–44%).

## Hipóteses próprias (12 testadas)

**Confirmadas (7):** P1 margem caiu por mix, não por preço (mix explica 67%); P2 Sistema
Respiratório é motor de crescimento e dreno de margem (+56,6% num negócio que caiu 6,5%);
P3 os 2 maiores em receita são os piores em margem; P4 Cimed puxa a margem para baixo (20,44%
vs. 32,49% do top-3); P5 concentração de fornecedor (Medley 27,4%, dois maiores 42,6%);
P6 a curva por hora difere entre dia útil e FDS; P7 o FDS é mais rentável por dia
(R$ 1.127,16 vs. R$ 1.106,53; margem 29,59% vs. 28,81%).

**Refutadas (5):** P8 desconto agressivo (máximo 15,8%, nenhuma transação ≥30%); P9 migração de
meio de pagamento (PIX 30–31% em todos os anos); P10 Pareto de produtos (precisa de 19 dos 33);
P11 efeito feriado (real mas fraco, 37 dias na base); P12 erosão de preço/custo dentro de
categoria (±0,3pp em 6 anos — é esta refutação que **obriga** a explicação de mix).

## Decomposição da margem (o achado central)

Margem 29,08% (2014) → 28,47% (2019), delta −0,61pp.
**Efeito mix −0,41pp · efeito taxa −0,20pp → o mix explica 67%.**
Sistema Respiratório saiu de 22,0% para 36,9% da receita; Sistema Nervoso caiu de 31,3% para
19,6%. A alavanca é a mesa de compras, não a política de preço.

## Ranking de impacto

| Cenário | Impacto | Prioridade |
|---|---|---|
| Margem abaixo da média em 15 produtos | R$ 75.359 (11,2% do lucro) | Alta |
| Formoterol + Budesonida | R$ 37.507 | Alta |
| Cimed vs. média da casa | R$ 26.661 (R$ 37.373 vs. top-3) | Alta |
| Meta calibrada no mês errado | ~15 pontos de índice | Alta |
| Hora das 21h em dia útil | R$ 34.347 de lucro já realizado | Média |
| Concentração Medley + EMS | 42,6% (risco, não perda) | Média |
| Desconto · meio de pagamento · feriado · Pareto | nulo ou marginal | **Arquivar** |

## Oito recomendações aplicáveis

1. Renegociar Formoterol 12mcg com a Cimed — **R$ 23.219** em jogo.
2. Renegociar Budesonida 200mcg com a Medley — **R$ 14.288**; a Medley já concentra 27,4% da
   receita, o poder de barganha existe e não está sendo usado.
3. Redistribuir a meta anual entre os meses, sem mexer no total.
4. Antecipar a compra de anti-histamínicos para março (pico é abr–jun, +78% em maio).
5. Rever o horário de **abertura**, não o de fechamento (8h rende 22,5% menos que 21h).
6. Reescalar a equipe de FDS para o pico de 10h–13h e liberar após as 20h.
7. Qualificar segunda fonte para os itens da Medley (nenhum produto tem fornecedor alternativo).
8. Encerrar formalmente as frentes de desconto e meio de pagamento — sem alavanca comprovada.

## Alterações no Power BI

**4 medidas novas** em `_Medidas.tmdl` (por edição direta de TMDL, Desktop fechado):
`% da Receita Total` e `Margem Média da Casa` (02 · KPIs); `Lucro Perdido vs. Média da Casa` e
`Lucro Perdido Total (produtos)` (07 · Produto). A última usa `SUMX(VALUES(...))` porque a
versão linha a linha colapsa para zero no total.

**2 páginas novas** (PBIR, `visual.json` escrito direto em disco):
- `a4d1c7e0b93f5628ac10` — **04 · Hipóteses do Datacast** (8 visuais): receita/dia por hora,
  meta vs. realizado por ano, índice sazonal com slicer de categoria, e o veredito escrito ao
  lado de cada gráfico.
- `b7e2f4a1c85d3690fe27` — **05 · Cenários & Impacto** (9 visuais): 4 cartões, receita por grupo
  terapêutico com legenda por série, margem por fornecedor ordenada, tabela de lucro renunciado.

`pageOrder` atualizado para 6 páginas.

**Preservado:** as alterações que o usuário havia feito no Desktop desde o último commit
(`d_turno[nome_turno]` com `sortByColumn: turno_id`, e ajustes nos visuais das páginas 01 e 02)
não foram tocadas — só arquivos distintos foram escritos.

**Verificação pendente:** as duas páginas foram validadas como JSON mas nunca vistas na tela.
Ao abrir o `.pbip`, conferir primeiro (a) a legenda por série do gráfico de grupo terapêutico
na página 05 e (b) o slicer de categoria ligado ao índice sazonal na página 04 — são os dois
padrões novos nesta entrega.

## Auditoria dos números

Um subagente independente recalculou 32 afirmações do relatório direto contra o banco.
30 confirmadas; 2 divergências encontradas e **corrigidas** antes da publicação:

1. **Anti-histamínicos em outubro** — o texto dizia "um dos dois piores meses"; os dois piores
   são dezembro (0,487) e janeiro (0,501), com novembro (0,615) também abaixo. Outubro é o
   **4º pior** (0,623). Corrigido; o argumento contra H12 não muda.
2. **Meta vs. realizado** — o relatório misturava duas bases: "97,9% e R$ 50.523" vinham de
   incluir os 3 meses de meta zerada (que contam como batidos, dando 34/72), enquanto
   "31 de 69" vinha de excluí-los. Padronizado na base de **69 meses com meta real**:
   atingimento **97,5%**, 31 batidos, gap **R$ 59.698**, com nota metodológica no rodapé.

## Limitações declaradas

- Localização da farmácia, custo de folha, escala de pessoal, dados de campanha e origem do
  cliente não existem na base — H2, H7 e H13 não são resolvíveis com este material.
- H16 e H17 (falha de sistema vs. venda da empresa) são indistinguíveis: ambas produzem o mesmo
  corte limpo em uma operação saudável.
- O efeito feriado tem apenas 37 dias de amostra — insuficiente para decisão.
