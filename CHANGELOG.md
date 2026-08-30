# Changelog

Todas as mudanças relevantes do projeto Farma Xperiun / PharmaVantage Analytics, por fase de
entrega. Formato livre, em português, alinhado ao histórico real de commits.

## [Fase 3] — 2026-08-30

### Adicionado
- `docs/auditoria_hipoteses.md` — auditoria completa das 19 hipóteses levantadas de viva voz
  pela diretoria no áudio do Datacast, cruzadas uma a uma contra o banco, com veredito
  Confirmada / Refutada / Parcial / Não verificável; respostas às perguntas do briefing
  (`Solicitação.txt`); 12 hipóteses próprias adicionais (7 confirmadas, 5 refutadas); ranking
  de impacto financeiro; 8 recomendações aplicáveis.
- `docs/cenarios_ocultos.md` — três cenários novos encontrados numa análise sem roteiro
  prévio: efeito-mix na queda de margem (r = −0,93 entre % receita controlada e margem),
  curva de vendas por hora dependente do dia da semana (o turno "Noite" fixo não existe aos
  fins de semana), e concentração de 42,6% da receita em dois fornecedores.
- `docs/meta_vs_realizado_ruido.md` — investigação da lógica estatística por trás do
  desalinhamento crônico entre meta e realizado: o padrão observado é consistente com
  `meta ≈ realizado do mesmo mês × ruído aleatório` (média 1,026, desvio 0,105, sem viés por
  mês/ano, autocorrelação lag-1 ≈ 0), o que explica a coexistência de ~97% de atingimento
  agregado com apenas 45% dos meses batidos individualmente.
- Página **04 · Hipóteses do Datacast** no `.pbip` — veredito visual das hipóteses com maior
  carga de dado (venda por hora, meta vs. receita por ano, índice sazonal por categoria).
- Página **05 · Cenários & Impacto** no `.pbip` — efeito-mix de margem por grupo terapêutico,
  gap de margem por fornecedor, tabela de lucro perdido por produto abaixo da margem média da
  casa.
- 4 medidas DAX novas em `_Medidas.tmdl`: `% da Receita Total`, `Margem Média da Casa`,
  `Lucro Perdido vs. Média da Casa` (linha a linha) e `Lucro Perdido Total (produtos)`
  (agregável via `SUMX` sobre `VALUES`, usada nos cartões da página 05 — R$ 75.359 de lucro
  potencial concentrado em 15 dos 33 produtos).
- `CHANGELOG.md` (este arquivo).

### Corrigido
- Relatório de auditoria: ranking de outubro entre os antialérgicos corrigido de "um dos
  dois piores meses" para o real 4º pior (dez/jan/nov ficam abaixo).
- Relatório de auditoria: estatísticas de meta vs. realizado padronizadas para uma única
  base de 69 meses (97,5% / 31–69 / R$ 59.698), eliminando uma inconsistência de denominador
  entre duas frases do texto.

### Verificado
- Todos os números do relatório de auditoria recomputados por um agente independente direto
  no banco, sem confiar no texto já escrito — processo descrito em
  `docs/auditoria_hipoteses.md`, seção "Auditoria dos números" (30 de 32 afirmações batiam de
  primeira; as 2 divergências viraram as correções acima).
- Mudanças no `.pbip` verificadas com o Power BI Desktop fechado
  (`ListLocalInstances` = 0 instâncias) antes e depois da edição direta dos arquivos PBIR/TMDL,
  para não colidir com edições concorrentes feitas na ferramenta.

## [Fase 2.5] — 2026-08-29

### Adicionado
- Análise independente pós-entrega, sem roteiro do usuário, catalogada em
  `docs/cenarios_ocultos.md` — precursora dos cenários formalizados na Fase 3.

## [Fase 1–2] — commit inicial

### Adicionado
- `docs/business_context.md` — 8 dores da diretoria extraídas do áudio do Datacast.
- `docs/insights_iniciais.md` — 5 queries T-SQL com resultado e leitura analítica.
- `scripts/run_sql_server.py` e `scripts/validate_sqlite.py` — pipeline de exploração e
  harness de validação contra o gabarito oficial.
- `powerbi/` — modelo dimensional (`star_schema.md`), 50 medidas DAX (`dax_measures.txt`),
  mockup navegável (`mockup_dashboard.html`) e o projeto Power BI completo em PBIP (4
  páginas: Descritiva, Diagnóstica, Comparativa, What-If).
- `presentation/executive_summary.md` — roteiro de 6 slides para a apresentação executiva.
- `README.md` — narrativa completa do projeto, decisões de engenharia e limitações
  declaradas.
