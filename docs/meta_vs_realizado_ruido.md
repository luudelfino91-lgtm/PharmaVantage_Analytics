# Por que a meta nunca acompanha o realizado

**Contexto.** A auditoria de hipóteses (`docs/auditoria_hipoteses.md`, H10) já havia
mostrado que a meta bate no agregado (~97–98% de atingimento acumulado) mas falha mês a mês
(apenas 31 de 69 meses com meta preenchida foram batidos individualmente), e que o ranking
dos meses por meta não corresponde ao ranking dos meses por realizado — a leitura registrada
foi "meta calibrada no mês errado". Esta nota investiga a causa estrutural por trás desse
padrão, testando diretamente contra `d_meta_mensal` e `f_vendas` em `farma_xperiun.db`.

## Três hipóteses testadas e descartadas

1. **Multiplicador fixo sobre o realizado do ano anterior.** A razão
   `meta(ano, mês) / realizado(ano-1, mês)` varia demais entre anos (desvio-padrão de até
   0,30) para sustentar um fator fixo de crescimento.
2. **Forma sazonal fixa repetida ano a ano.** O vetor mensal normalizado do realizado (a
   "forma" do ano) muda substancialmente de um ano para o outro — por exemplo, o índice de
   2017 (jan→dez: 157, 81, 76, 81, 91, 99, 77, 78, 108, 113, 107, 133) não se parece com o de
   2016 (94, 96, 106, 100, 91, 95, 71, 88, 93, 144, 82, 142). Não há uma curva sazonal fixa
   sendo copiada.
3. **Ticket médio implícito constante na meta.** `meta_receita / meta_quantidade` varia de
   12,72 a 22,04 — sem valor estável que sugira uma meta construída por volume × preço fixo.

## O que sustenta os dados: meta = realizado do mesmo mês × ruído aleatório

Nos 69 pares mês/ano com meta preenchida (exclui out/nov/dez de 2019, meta zerada):

```
fator = meta_receita(ano, mês) / receita_realizada(ano, mês)

média(fator)              = 1,026   (meta ~2,6% acima do realizado, em média)
desvio-padrão(fator)      = 0,105
mínimo / máximo           = 0,851 / 1,191
100% dos 69 meses caem dentro de ±19% do realizado do próprio mês
```

O ruído não mostra viés sistemático:

- **Por mês:** a média do fator varia de 0,946 a 1,092 entre os 12 meses — outubro (1,089)
  não se destaca dos demais.
- **Por ano:** a média varia de 0,994 a 1,082 — sem tendência de alta ou baixa ao longo dos
  6 anos.
- **Autocorrelação lag-1 (mês para o mês seguinte): 0,027** — estatisticamente
  indistinguível de zero, ou seja, o ruído de um mês não carrega informação sobre o ruído do
  mês seguinte.

Esse é o retrato estatístico de ruído aleatório aplicado sobre o resultado real do próprio
mês — não de um orçamento genuinamente prospectivo, baseado em crescimento planejado ou em
sazonalidade histórica.

## Por que isso explica os sintomas já documentados

- **97–98% de atingimento agregado com só 45% dos meses batidos:** se a meta é o próprio
  realizado do mês mais/menos um ruído de ~10,5% de desvio-padrão, o ruído tende a se
  cancelar no acumulado (por isso a meta somada ao longo do ano fica perto do realizado
  somado), mas mês a mês a "moeda" é sorteada de novo — em pouco mais da metade dos meses o
  sorteio empurra a meta para cima do realizado daquele mês específico.
- **Inversão de ranking entre janeiro/outubro/dezembro:** os três meses já são concorrentes
  próximos entre si em receita realizada. Um ruído de ~10% de desvio-padrão é suficiente
  para reembaralhar a ordem entre competidores próximos, sem que isso precise refletir um
  erro deliberado de julgamento sobre qual mês merece a meta mais ambiciosa.

## Como isso reformula (sem contradizer) a recomendação já feita

A leitura "meta calibrada no mês errado" continua descritivamente correta — a meta de fato
não segue a sazonalidade real do negócio. O que muda é a explicação provável: o padrão
observado é mais compatível com uma meta gerada a partir do próprio resultado do mês
(estrutural ao dataset) do que com um erro humano de leitura de mercado. A recomendação
prática permanece válida de qualquer forma: ancorar a meta na sazonalidade histórica real
(`Meta Ajustada por Dias Úteis`, já modelada em `powerbi/dax_measures.txt`) produziria uma
meta mais estável mês a mês e mais útil como ferramenta de gestão, independentemente de qual
das duas explicações for a verdadeira.

## Status

Investigação registrada como nota lateral, a pedido do usuário, em paralelo à auditoria de
hipóteses. Não alterou nenhum artefato do `.pbip` nem o relatório de auditoria já publicado —
fica documentada aqui para referência futura caso vire uma seção formal.
