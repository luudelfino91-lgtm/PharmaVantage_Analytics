# Business Context — Farma Xperiun
### Fase 1 · Imersão no Negócio · Mapeamento das Dores da Diretoria

| Item | Detalhe |
|---|---|
| **Projeto** | Data Challenge — Farma Xperiun |
| **Fonte primária** | `Base e Materiais Auxiliares/Base/Datacast Xperiun.../Transcrição Video.txt` (23.938 bytes, 338 blocos, lidos integralmente) |
| **Fontes complementares** | `Duvidas do Desafio.docx` (perguntas escritas da diretoria) · `documentacao_farma_xperiun.docx` (dicionário de dados) |
| **Autor** | Engenharia de Analytics / BI |
| **Status** | Fase 1 concluída — aguardando aprovação para Fase 2 |

---

## 1. Por que este documento existe

O Datacast não é um briefing técnico. É uma conversa de **arqueologia de dados**: dois analistas recebem as tabelas brutas da Farma Xperiun *sem nenhum guia* e tentam reconstruir a história do negócio apenas pelos padrões. O valor dele para nós não está nas respostas que eles dão — está nas **perguntas que ficam abertas** e nas **hipóteses que eles não conseguiram provar**.

Cada dor abaixo foi extraída literalmente da transcrição e traduzida em pergunta analítica testável. Nenhuma query da Fase 2 será escrita sem estar ancorada em uma destas dores.

---

## 2. O retrato do negócio que o áudio revela

Antes das dores, o que o áudio estabelece como fato:

| Descoberta | Evidência na transcrição |
|---|---|
| **Setor**: farmácia / drogaria de varejo | *"essa lista não sussurra. Ela grita. Indústria farmacêutica"* — Eurofarma, EMS, Aché, Medley, Neo Química, Cimed, Hypera, Cristália |
| **Geografia**: Sudeste | 7 de 8 fornecedores em SP/MG; *"sugere que a nossa empresa mistério provavelmente ficava no sudeste, para aproveitar a proximidade"* |
| **Operação**: 14h/dia, 3 turnos assimétricos | Manhã 8–13 (5h), Tarde 13–18 (5h), Noite 18–22 (4h) |
| **Ambição**: expansão agressiva 2014→2019 | Meta de jan/2014 ≈ R$ 29 mil → jan/2019 ≈ R$ 59 mil. *"Basicamente duplicou"* |
| **Ruptura**: colapso no fim de 2019 | Out/19 despenca para ~R$ 10 mil; **nov/19 e dez/19 com meta de receita = 0 e quantidade = 0** |
| **Qualidade dos dados**: alta e confiável | Calendário trata 29/02/2016 corretamente — *"a gente pode confiar na qualidade geral da informação"* |

> **Nota de rigor analítico:** os apresentadores confirmam, ao final, que sua conclusão sobre o fim de 2019 é *"uma inferência lógica bem fundamentada"*, mas que *"os dados, por si sós, nos deixam na fronteira do mistério"*. Tratamos isso como **hipótese a testar**, não como fato.

---

## 3. As dores estratégicas mapeadas

### 🔴 DOR 1 — "O comportamento por turno é um mistério"

**O que foi dito:** *"Não são nem os 3 turnos em si, mas a duração deles. Os 2 primeiros têm 5 horas cada. Mas o da noite é mais curto, só 4 horas. Isso já é uma pista."* Levantam duas explicações concorrentes — **queda de fluxo de clientes** ou **custo da hora noturna** — e não resolvem qual é.

**A dor real:** a diretoria comparou turnos em números absolutos e concluiu que a noite "vende menos". Mas comparar um turno de 4h com um de 5h em receita bruta é uma **comparação injusta**. A decisão de encurtar (ou fechar, ou estender) a noite está sendo tomada sobre uma métrica enviesada.

**Pergunta analítica:** A noite vende menos porque é *pior* ou porque é *mais curta*? Normalizando por hora de operação, qual turno realmente tem a maior produtividade de receita, de lucro e de ticket médio? O mix de produtos muda entre os turnos?

**Tabelas:** `f_vendas` × `d_turno` × `d_produto` × `d_calendario`

---

### 🔴 DOR 2 — "A gestão de compras era um malabarismo constante"

**O que foi dito:** *"A distância vira tempo de espera."* Neo Química (Anápolis/GO, Centro-Oeste) tem o maior prazo — 5 dias — e é o único fornecedor fora do polo do Sudeste. EMS e Hypera entregam em 2 dias. E a consequência é explicitada: *"Precisava de um estoque maior para cobrir esses 5 dias de espera. O que imobiliza capital de giro."*

**A dor real:** ninguém quantificou **quanto custa** esse malabarismo. Se o fornecedor mais lento também é o que sustenta a maior fatia da receita, a farmácia está com capital de giro travado no pior lugar possível — e não sabe.

**Pergunta analítica:** Qual a relação entre prazo de entrega, participação na receita e margem por fornecedor? Existe um fornecedor que combine alto giro + prazo longo + margem baixa (o pior cenário de capital imobilizado)? A concentração regional é um risco ou uma vantagem?

**Tabelas:** `f_vendas` × `d_fornecedor` × `d_produto`

---

### 🔴 DOR 3 — "Tem meses que são sempre mais fortes?"

**O que foi dito:** *"Não é o crescimento ano a ano, é a maré subindo. Mas e as ondas dentro de cada ano?"* Identificam **outubro** como mês consistentemente forte (2014: R$ 41 mil → 2015: R$ 46 mil → 2016: R$ 53 mil) e levantam **duas teorias concorrentes não resolvidas**:
1. Pico de **alergias sazonais** da primavera no Sudeste → antialérgicos
2. **Outubro Rosa** → *"movimenta todo o ecossistema de saúde... pode gerar um tráfego indireto para as farmácias"*

**A dor real:** a diretoria planeja compras e escala de pessoal sobre uma sazonalidade que **intui mas nunca mediu**. Se a alta de outubro for de anti-histamínicos, é um problema de *compras*. Se for tráfego geral difuso, é um problema de *pessoal e caixa*. As duas hipóteses exigem ações opostas.

**Pergunta analítica:** Decompondo a receita de outubro por grupo terapêutico, o pico é concentrado em anti-histamínicos (tese alergia) ou distribuído por todas as categorias (tese Outubro Rosa)? E o inverno (mai–ago) eleva de fato o Sistema Respiratório?

**Tabelas:** `f_vendas` × `d_calendario` × `d_produto`

---

### 🔴 DOR 4 — "A ambição é tudo, mas a meta foi batida?"

**O que foi dito:** *"As metas são a janela para a estratégia, para a trajetória de crescimento."* O áudio analisa exaustivamente a **evolução das metas** — mas em nenhum momento compara meta com o que foi **efetivamente realizado**. Toda a leitura de "crescimento implacável" é leitura de *ambição*, não de *entrega*.

**A dor real:** este é o maior ponto cego do áudio. A diretoria confundiu **meta** com **resultado**. Pode ter havido 6 anos de metas crescentes e 6 anos de não-atingimento — e o áudio não saberia dizer. Não existe acompanhamento intra-mês: *quando percebem que não bateram, o mês já acabou*.

**Pergunta analítica:** Mês a mês, de 2014 a 2019: qual o % de atingimento da meta de receita e de quantidade? Quantos meses foram batidos? O gap está crescendo ou encolhendo? A meta estava calibrada com a realidade ou descolando dela?

**Tabelas:** `f_vendas` × `d_meta_mensal` × `d_calendario` (join lógico por ano+mês)

---

### 🔴 DOR 5 — "O mistério de 2019"

**O que foi dito:** *"O negócio que por 6 anos planejou seu crescimento, de repente planejou não vender absolutamente nada por 2 meses."* Outubro/19 cai para ~R$ 10 mil; novembro e dezembro zeram. Três hipóteses levantadas e **nenhuma confirmada**: encerramento da operação, venda da empresa, ou falha catastrófica de sistema — esta última considerada *"menos provável dado o cuidado que vimos antes"*.

**A dor real:** o negócio precisa saber se a queda foi **operacional** (perdeu clientes, perdeu mix, perdeu margem — algo que se corrige) ou **administrativa** (fim do registro de dados — algo que não se corrige, só se explica). São diagnósticos completamente diferentes.

**Pergunta analítica:** A curva de 2019 mostra deterioração gradual (declínio de ticket, de transações, de margem ao longo do ano) ou um corte abrupto? Qual foi a última data com venda registrada? A queda é de volume de transações ou de valor por transação?

> ⚠️ **Alerta de premissa a corrigir:** o `Duvidas do Desafio.docx` pergunta se há relação com *"o início da pandemia"*. A base termina em **out/2019** e a pandemia começa em **mar/2020** — cronologicamente incompatível. Este é um ponto onde a análise precisa **contrariar a hipótese da diretoria com dados**, não confirmá-la.

**Tabelas:** `f_vendas` × `d_calendario` × `d_meta_mensal`

---

### 🟡 DOR 6 — "Feriados e fins de semana: qual o impacto real?"

**O que foi dito:** *"Para uma máquina processando milhares de linhas de vendas, ter essa flag permite correlacionar picos ou quedas de receita com eventos específicos na hora. É a base de qualquer modelo de previsão de vendas decente."* O calendário foi construído com as flags `is_feriado` e `is_fim_semana` — e o áudio reconhece o valor delas, mas **nunca as usa**.

**A dor real:** a ferramenta existe e está parada. Metas são mensais e fixas, mas meses têm quantidades diferentes de dias úteis, fins de semana e feriados. Um mês com 3 feriados e uma meta idêntica à de um mês sem feriado nenhum é uma meta mal calibrada por construção.

**Pergunta analítica:** Qual a receita média por dia útil vs. fim de semana vs. feriado? A variação de dias úteis por mês explica parte do não-atingimento de meta?

**Tabelas:** `f_vendas` × `d_calendario` × `d_meta_mensal`

---

### 🟡 DOR 7 — "A forma de pagamento e a margem"

**O que foi dito:** o áudio trata isso como peça menor — *"uma peça minúscula, mas confirma nossa suspeita"* — usando `cartao_debito` apenas como prova de que é varejo B2C.

**A dor real:** a diretoria subestimou este eixo. Formas de pagamento carregam custos de adquirência e prazos de recebimento distintos, e o `Duvidas do Desafio.docx` pergunta diretamente se *"os descontos estão corroendo a margem ou atraindo volume"*. Ticket médio e desconto médio por forma de pagamento é análise de margem, não de curiosidade.

**Pergunta analítica:** O ticket médio e o desconto médio variam por forma de pagamento? Existe forma de pagamento que concentra desconto sem trazer volume proporcional?

**Tabelas:** `f_vendas` × `d_produto` × `d_turno`

---

### 🟡 DOR 8 — "Vendemos muito Paracetamol, mas ele dá margem?"

**O que foi dito (fonte complementar):** esta dor não está no Datacast — vem literal do `Duvidas do Desafio.docx`: *"Não sabem quais produtos realmente sustentam o lucro. Vendem muito Paracetamol, mas será que ele dá margem?"* e *"quais produtos dão margem e quais só giram estoque"*.

**A dor real:** clássico conflito volume × margem. A documentação já sinaliza a tensão estrutural: **produtos que exigem receita tendem a ter margens menores** (Sistema Nervoso 23,2% e Respiratório 23,9% vs. Analgésicos 38,9%) — e o Respiratório é justamente o maior gerador de *receita*. O maior faturador não é o maior lucrador.

**Pergunta analítica:** Construindo uma matriz volume × margem, quais produtos são âncoras de lucro, quais são âncoras de tráfego e quais são apenas ocupação de prateleira? Qual a diferença de perfil entre venda livre e controlado?

**Tabelas:** `f_vendas` × `d_produto`

---

## 4. Matriz de priorização

| # | Dor | Impacto na decisão | Complexidade SQL | Prioridade Fase 2 |
|---|---|---|---|---|
| 4 | Meta vs. Realizado | 🔴 Alto — ponto cego total | Alta (join lógico ano+mês) | **1** |
| 5 | Mistério de 2019 | 🔴 Alto — define narrativa | Alta (janelas, MoM) | **2** |
| 1 | Turno normalizado/hora | 🔴 Alto — decisão de escala | Média | **3** |
| 2 | Fornecedor × prazo × capital | 🔴 Alto — capital de giro | Média-alta | **4** |
| 3 | Sazonalidade (outubro/inverno) | 🔴 Alto — plano de compras | Alta (pivot por grupo) | **5** |
| 8 | Volume × margem por produto | 🟡 Médio | Média | Fase 3 (DAX/visual) |
| 6 | Feriado / fim de semana | 🟡 Médio | Média | Fase 3 (DAX/visual) |
| 7 | Pagamento × desconto | 🟡 Médio | Baixa | Fase 3 (DAX/visual) |

As **5 dores prioritárias (4, 5, 1, 2, 3)** viram as 5 queries complexas da Fase 2. As dores 6, 7 e 8 são endereçadas por medidas DAX e telas do dashboard na Fase 3 — não porque sejam menos importantes, mas porque são melhor respondidas de forma interativa do que por uma query estática.

---

## 5. Lacunas e riscos que a Fase 2 precisa carregar

| # | Risco | Tratamento |
|---|---|---|
| 1 | **Meta ≠ Realizado.** O áudio inteiro analisa metas achando que analisa desempenho. | Toda análise de "crescimento" deve reportar as duas séries lado a lado. |
| 2 | **Assimetria de turno.** 4h vs. 5h invalida comparação absoluta. | Métrica obrigatória: receita/hora e lucro/hora. |
| 3 | **Nov–dez/19 zerados.** Meta zero não é meta baixa. | Excluir da análise de atingimento; tratar como marco, não como desempenho. Séries de tendência devem cortar em out/2019. |
| 4 | **Hipótese da pandemia é cronologicamente impossível.** | Refutar explicitamente com a data da última venda registrada. |
| 5 | **`d_meta_mensal` sem FK direta.** Relação é lógica (ano+mês). | Join via `d_calendario`; no Power BI exige chave de período dedicada (tratado na Fase 3). |
| 6 | **Feriados móveis ausentes** (Carnaval, Sexta-Feira Santa, Corpus Christi). | Documentar como limitação; não atribuir quedas nessas datas a comportamento do consumidor. |
| 7 | **`quantidade` é fracionada** e `preco_unitario` da venda varia ±5% vs. tabela. | Nunca recalcular receita a partir de `d_produto`; usar sempre os campos de `f_vendas`. |
| 8 | **Arquitetura de dados a confirmar.** O material entregue traz um banco **SQLite** (`farma_xperiun.db`); a Fase 2 pede **SQL Server local**. | ⚠️ Ponto de decisão levantado ao stakeholder antes de executar a Fase 2. |

---

## 6. As 5 perguntas de negócio da Fase 2 (proposta para aprovação)

1. **A ambição bateu com a entrega?** Atingimento de meta mês a mês (2014–out/2019), gap absoluto e percentual, contagem de meses batidos e tendência do gap.
2. **O que realmente aconteceu em 2019?** Decomposição da queda: transações, ticket médio, margem e última data com venda — corte abrupto ou deterioração gradual?
3. **Qual turno é de fato o mais produtivo?** Receita, lucro, ticket e mix por turno, normalizados por hora de operação.
4. **Onde está travado o capital de giro?** Fornecedor × prazo de entrega × participação na receita × margem, com índice de exposição logística.
5. **Outubro é alergia ou Outubro Rosa?** Decomposição da sazonalidade por grupo terapêutico, testando a concentração em anti-histamínicos contra a alta difusa.

---

*Documento gerado na Fase 1. Nenhuma query foi escrita antes deste mapeamento — por desenho.*
