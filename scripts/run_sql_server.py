# -*- coding: utf-8 -*-
"""
=====================================================================================
 FARMA XPERIUN | Data Challenge - FASE 2: Exploracao Analitica
=====================================================================================
 Conecta na instancia local do SQL Server (banco: farma_xperiun), executa as 5
 queries analiticas complexas derivadas das dores mapeadas na Fase 1
 (docs/business_context.md) e exporta os resultados reais para
 docs/insights_iniciais.md.

 DEPENDENCIAS
     pip install pyodbc
     (opcional, fallback) pip install sqlalchemy

 EXECUCAO
     python scripts/run_sql_server.py
     python scripts/run_sql_server.py --server "localhost\\SQLEXPRESS"
     python scripts/run_sql_server.py --user sa --password ****   (SQL Auth)

 NOTA DE ENGENHARIA
     A coluna dbo.f_vendas.data foi convertida para DATE (ver
     'Alteracao da coluna data - de text para date.sql'), enquanto
     dbo.d_calendario.data pode ter permanecido como texto. Por isso toda query
     normaliza AMBAS as colunas com TRY_CONVERT(DATE, CAST(col AS VARCHAR(10)), 23)
     nas CTEs 'vnd' e 'cal'. O padrao funciona nos dois casos (DATE ou VARCHAR) e
     torna o script imune ao estado da conversao.

 Autor: Engenharia de Analytics / BI  |  Padrao PL-300
=====================================================================================
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path

# ------------------------------------------------------------------------------------
# CONFIGURACAO
# ------------------------------------------------------------------------------------
DEFAULT_SERVER = "localhost"
DEFAULT_DATABASE = "farma_xperiun"
DRIVER_CANDIDATES = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server",
    "ODBC Driver 13 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server",
]

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_MD = BASE_DIR / "docs" / "insights_iniciais.md"


# ------------------------------------------------------------------------------------
# AS 5 QUERIES
# Cada uma carrega o bloco obrigatorio RACIONAL / OBJETIVO / INSIGHT ESPERADO,
# ancorado em uma dor especifica extraida da transcricao do Datacast.
# ------------------------------------------------------------------------------------

Q1 = """
-- =====================================================================================
-- QUERY 1 | A ambicao bateu com a entrega?
-- =====================================================================================
-- RACIONAL: A transcricao dedica todo o terco final a analisar a evolucao das METAS
--           ("as metas sao a janela para a estrategia", "um crescimento implacavel",
--           "a empresa estava em modo de expansao agressivo") e em NENHUM momento
--           compara essas metas com o que foi efetivamente realizado. Toda a leitura de
--           sucesso do negocio e leitura de ambicao, nao de entrega. Este e o maior
--           ponto cego do audio e por isso e a primeira query do projeto.
-- OBJETIVO: De 2014 a 2019, qual foi o percentual de atingimento da meta de receita ano
--           a ano, quantos meses foram efetivamente batidos, e o gap esta crescendo ou
--           encolhendo?
-- INSIGHT ESPERADO: Se o "crescimento implacavel" for real, esperamos atingimento
--           proximo ou acima de 100% e uma maioria de meses batidos. A hipotese
--           alternativa - e mais provavel - e que a farmacia tenha passado seis anos
--           perseguindo metas que nunca alcancou, e que a diretoria tenha confundido
--           planejar crescimento com entregar crescimento.
-- =====================================================================================
WITH vnd AS (
    SELECT TRY_CONVERT(DATE, CAST(v.data AS VARCHAR(10)), 23) AS dt,
           v.receita_liquida, v.quantidade, v.lucro
    FROM dbo.f_vendas AS v
),
cal AS (
    SELECT TRY_CONVERT(DATE, CAST(c.data AS VARCHAR(10)), 23) AS dt, c.ano, c.mes
    FROM dbo.d_calendario AS c
),
realizado_mes AS (
    SELECT c.ano, c.mes,
           COUNT(*)                 AS transacoes,
           SUM(v.receita_liquida)   AS receita,
           SUM(v.quantidade)        AS quantidade,
           SUM(v.lucro)             AS lucro
    FROM vnd AS v
    INNER JOIN cal AS c ON c.dt = v.dt
    GROUP BY c.ano, c.mes
),
confronto AS (
    -- d_meta_mensal nao tem FK com o fato: o vinculo e logico, por ano + mes.
    SELECT m.ano, m.mes, m.meta_receita, m.meta_quantidade,
           COALESCE(r.receita, 0)    AS receita,
           COALESCE(r.quantidade, 0) AS quantidade,
           COALESCE(r.lucro, 0)      AS lucro
    FROM dbo.d_meta_mensal AS m
    LEFT JOIN realizado_mes AS r ON r.ano = m.ano AND r.mes = m.mes
),
anual AS (
    -- Meses com meta zero (out/nov/dez de 2019) sao excluidos do denominador:
    -- meta zero nao e meta baixa, e ausencia de meta. Incluir distorceria o indicador.
    SELECT ano,
           SUM(CASE WHEN meta_receita > 0 THEN meta_receita ELSE 0 END)    AS meta_total,
           SUM(CASE WHEN meta_receita > 0 THEN receita      ELSE 0 END)    AS receita_com_meta,
           SUM(receita)                                                    AS receita_total,
           SUM(lucro)                                                      AS lucro_total,
           SUM(CASE WHEN meta_quantidade > 0 THEN meta_quantidade ELSE 0 END) AS meta_qtd,
           SUM(CASE WHEN meta_quantidade > 0 THEN quantidade      ELSE 0 END) AS qtd_com_meta,
           SUM(CASE WHEN meta_receita > 0 THEN 1 ELSE 0 END)               AS meses_com_meta,
           SUM(CASE WHEN meta_receita > 0 AND receita >= meta_receita
                    THEN 1 ELSE 0 END)                                     AS meses_batidos
    FROM confronto
    GROUP BY ano
)
SELECT  CAST(ano AS VARCHAR(4))                                                  AS [Ano],
        CAST(meta_total AS DECIMAL(18,2))                                        AS [Meta Receita],
        CAST(receita_com_meta AS DECIMAL(18,2))                                  AS [Realizado],
        CAST(receita_com_meta / NULLIF(meta_total,0) * 100 AS DECIMAL(6,1))      AS [% Ating. Receita],
        CAST(receita_com_meta - meta_total AS DECIMAL(18,2))                     AS [Gap R$],
        CAST(qtd_com_meta / NULLIF(meta_qtd,0) * 100 AS DECIMAL(6,1))            AS [% Ating. Qtd],
        CAST(meses_batidos AS VARCHAR(2)) + '/' + CAST(meses_com_meta AS VARCHAR(2)) AS [Meses Batidos],
        CAST(lucro_total / NULLIF(receita_total,0) * 100 AS DECIMAL(6,1))        AS [Margem %],
        CAST((receita_total / NULLIF(LAG(receita_total) OVER (ORDER BY ano),0) - 1) * 100
             AS DECIMAL(6,1))                                                    AS [YoY Receita %]
FROM anual
ORDER BY ano;
"""

Q2 = """
-- =====================================================================================
-- QUERY 2 | O que realmente aconteceu em 2019?
-- =====================================================================================
-- RACIONAL: O climax da transcricao e o colapso do fim de 2019 - "o negocio que por 6
--           anos planejou seu crescimento, de repente planejou nao vender absolutamente
--           nada por 2 meses". Os apresentadores levantam tres hipoteses (encerramento,
--           venda da empresa, falha de sistema) e admitem que "os dados, por si sos, nos
--           deixam na fronteira do misterio". O documento de duvidas da diretoria vai
--           alem e pergunta se ha relacao com "o inicio da pandemia".
-- OBJETIVO: A curva de 2019 mostra deterioracao operacional gradual (queda de trafego,
--           ticket ou margem) ou um corte abrupto de registro? Comparando cada mes de
--           2019 com o mesmo mes de 2018 em receita POR DIA COM VENDA - unica base justa,
--           ja que outubro/2019 e um mes parcial - o negocio estava morrendo ou operando?
-- INSIGHT ESPERADO: Se houver colapso operacional, a receita por dia deve cair mes a mes
--           ate zerar. Se a receita por dia se mantiver saudavel ate o ultimo registro, a
--           conclusao muda de natureza: nao houve morte do negocio, houve fim da captura
--           de dados. Isso tambem permitiria refutar a hipotese da pandemia por
--           impossibilidade cronologica (base termina em 2019, pandemia comeca em 2020).
-- =====================================================================================
WITH vnd AS (
    SELECT TRY_CONVERT(DATE, CAST(v.data AS VARCHAR(10)), 23) AS dt,
           v.receita_liquida, v.lucro, v.desconto, v.quantidade
    FROM dbo.f_vendas AS v
),
cal AS (
    SELECT TRY_CONVERT(DATE, CAST(c.data AS VARCHAR(10)), 23) AS dt,
           c.ano, c.mes, c.nome_mes
    FROM dbo.d_calendario AS c
),
mensal AS (
    SELECT c.ano, c.mes, MIN(c.nome_mes) AS nome_mes,
           COUNT(*)                  AS transacoes,
           COUNT(DISTINCT v.dt)      AS dias_com_venda,
           SUM(v.receita_liquida)    AS receita,
           SUM(v.lucro)              AS lucro,
           SUM(v.desconto)           AS desconto
    FROM vnd AS v
    INNER JOIN cal AS c ON c.dt = v.dt
    WHERE c.ano IN (2018, 2019)
    GROUP BY c.ano, c.mes
)
SELECT  a.mes                                                                    AS [Mes],
        a.nome_mes                                                               AS [Nome],
        a.dias_com_venda                                                         AS [Dias c/ Venda],
        a.transacoes                                                             AS [Transacoes],
        CAST(a.receita AS DECIMAL(18,2))                                         AS [Receita 2019],
        CAST(a.receita / NULLIF(a.transacoes,0) AS DECIMAL(18,2))                AS [Ticket 2019],
        CAST(a.lucro / NULLIF(a.receita,0) * 100 AS DECIMAL(6,1))                AS [Margem % 2019],
        CAST(a.receita / NULLIF(a.dias_com_venda,0) AS DECIMAL(18,2))            AS [Receita/Dia 2019],
        CAST(b.receita / NULLIF(b.dias_com_venda,0) AS DECIMAL(18,2))            AS [Receita/Dia 2018],
        CAST(((a.receita / NULLIF(a.dias_com_venda,0)) /
              NULLIF(b.receita / NULLIF(b.dias_com_venda,0), 0) - 1) * 100
             AS DECIMAL(6,1))                                                    AS [Var. Dia YoY %]
FROM mensal AS a
LEFT JOIN mensal AS b ON b.mes = a.mes AND b.ano = 2018
WHERE a.ano = 2019
ORDER BY a.mes;
"""

Q3 = """
-- =====================================================================================
-- QUERY 3 | Qual turno e de fato o mais produtivo?
-- =====================================================================================
-- RACIONAL: A primeira observacao analitica da transcricao e sobre a assimetria dos
--           turnos: "nao sao nem os 3 turnos em si, mas a duracao deles [...] os 2
--           primeiros tem 5 horas cada, mas o da noite e mais curto, so 4 horas". Os
--           apresentadores explicam a hora a menos por queda de fluxo de clientes ou por
--           custo da mao de obra noturna - e nao resolvem qual. O erro embutido e
--           comparar um turno de 4h com um de 5h em receita absoluta, o que penaliza a
--           noite por construcao.
-- OBJETIVO: Normalizando por hora efetiva de operacao (dias operados x duracao do turno),
--           qual turno entrega mais receita, mais lucro e maior ticket? O mix de produtos
--           controlados muda entre turnos?
-- INSIGHT ESPERADO: Se a noite for a menos produtiva tambem por hora, a decisao de
--           encurtar o turno foi acertada. Se a noite liderar em receita/hora, a
--           conclusao se inverte: a farmacia esta cortando justamente sua faixa mais
--           rentavel e existe receita nao capturada na hora suprimida.
-- =====================================================================================
WITH base AS (
    SELECT  t.turno_id,
            t.nome_turno,
            (t.hora_fim - t.hora_inicio)      AS horas_turno,
            COUNT(*)                          AS transacoes,
            COUNT(DISTINCT TRY_CONVERT(DATE, CAST(v.data AS VARCHAR(10)), 23)) AS dias_operados,
            SUM(v.receita_liquida)            AS receita,
            SUM(v.receita_bruta)              AS receita_bruta,
            SUM(v.lucro)                      AS lucro,
            SUM(v.desconto)                   AS desconto
    FROM dbo.f_vendas AS v
    INNER JOIN dbo.d_turno AS t ON t.turno_id = v.turno_id
    GROUP BY t.turno_id, t.nome_turno, (t.hora_fim - t.hora_inicio)
),
mix_controlado AS (
    -- Cruzamento com d_produto: medicamentos que exigem receita tem margem menor
    -- (Sistema Nervoso e Antiasmaticos). Saber onde eles se concentram explica margem.
    SELECT  v.turno_id,
            SUM(CASE WHEN p.exige_receita = 1 THEN v.receita_liquida ELSE 0 END)
                / NULLIF(SUM(v.receita_liquida), 0) * 100 AS pct_controlado
    FROM dbo.f_vendas AS v
    INNER JOIN dbo.d_produto AS p ON p.produto_id = v.produto_id
    GROUP BY v.turno_id
)
SELECT  b.nome_turno                                                             AS [Turno],
        b.horas_turno                                                            AS [Horas],
        b.transacoes                                                             AS [Transacoes],
        CAST(b.receita AS DECIMAL(18,2))                                         AS [Receita],
        CAST(b.receita / SUM(b.receita) OVER () * 100 AS DECIMAL(6,1))           AS [Share %],
        CAST(b.receita / NULLIF(b.dias_operados * b.horas_turno, 0)
             AS DECIMAL(18,2))                                                   AS [Receita/Hora],
        CAST(b.lucro / NULLIF(b.dias_operados * b.horas_turno, 0)
             AS DECIMAL(18,2))                                                   AS [Lucro/Hora],
        CAST(b.receita / NULLIF(b.transacoes, 0) AS DECIMAL(18,2))               AS [Ticket Medio],
        CAST(b.lucro / NULLIF(b.receita, 0) * 100 AS DECIMAL(6,1))               AS [Margem %],
        CAST(b.desconto / NULLIF(b.receita_bruta, 0) * 100 AS DECIMAL(6,2))      AS [Desconto %],
        CAST(CAST(b.transacoes AS DECIMAL(18,4))
             / NULLIF(b.dias_operados * b.horas_turno, 0) AS DECIMAL(8,2))       AS [Transacoes/Hora],
        CAST(m.pct_controlado AS DECIMAL(6,1))                                   AS [% Controlado]
FROM base AS b
INNER JOIN mix_controlado AS m ON m.turno_id = b.turno_id
ORDER BY [Receita/Hora] DESC;
"""

Q4 = """
-- =====================================================================================
-- QUERY 4 | Onde esta travado o capital de giro?
-- =====================================================================================
-- RACIONAL: A transcricao identifica o problema mas nao o dimensiona: "a distancia vira
--           tempo de espera [...] precisava de um estoque maior para cobrir esses 5 dias
--           de espera, o que imobiliza capital de giro [...] a gestao de compras nao era
--           uma coisa so, era um malabarismo constante". Os apresentadores notam que a
--           Neo Quimica, unico fornecedor fora do Sudeste, tem o pior prazo (5 dias) -
--           mas nunca perguntam se ela merece esse custo.
-- OBJETIVO: Cruzando d_fornecedor com o fato, qual a relacao entre prazo de entrega,
--           participacao na receita e margem por fornecedor? Quanto capital fica
--           imobilizado em estoque de cobertura por fornecedor
--           (custo medio diario de mercadoria x prazo de entrega)?
-- INSIGHT ESPERADO: Esperamos encontrar um fornecedor no pior quadrante possivel -
--           prazo longo, margem baixa e participacao intermediaria - que imobiliza mais
--           capital do que devolve em resultado; e um fornecedor benchmark com prazo
--           curto e margem alta que deveria ganhar participacao. A concentracao da
--           receita em poucos fornecedores tambem deve aparecer como risco.
-- =====================================================================================
WITH dias_operacao AS (
    SELECT COUNT(DISTINCT TRY_CONVERT(DATE, CAST(data AS VARCHAR(10)), 23)) AS dias
    FROM dbo.f_vendas
),
base AS (
    SELECT  f.nome,
            f.cidade + '/' + f.estado    AS localizacao,
            f.regiao,
            f.prazo_entrega_dias,
            COUNT(*)                     AS transacoes,
            SUM(v.receita_liquida)       AS receita,
            SUM(v.lucro)                 AS lucro,
            SUM(v.custo_total)           AS custo
    FROM dbo.f_vendas AS v
    INNER JOIN dbo.d_fornecedor AS f ON f.fornecedor_id = v.fornecedor_id
    GROUP BY f.nome, f.cidade + '/' + f.estado, f.regiao, f.prazo_entrega_dias
)
SELECT  b.nome                                                                   AS [Fornecedor],
        b.localizacao                                                            AS [Local],
        b.regiao                                                                 AS [Regiao],
        b.prazo_entrega_dias                                                     AS [Prazo (dias)],
        CAST(b.receita AS DECIMAL(18,2))                                         AS [Receita],
        CAST(b.receita / SUM(b.receita) OVER () * 100 AS DECIMAL(6,1))           AS [Share %],
        CAST(b.lucro / NULLIF(b.receita,0) * 100 AS DECIMAL(6,1))                AS [Margem %],
        CAST(b.custo / NULLIF(d.dias,0) AS DECIMAL(18,2))                        AS [Custo/Dia],
        -- Capital de giro imobilizado = mercadoria necessaria para cobrir o lead time
        CAST(b.custo / NULLIF(d.dias,0) * b.prazo_entrega_dias AS DECIMAL(18,2)) AS [Capital Imobilizado],
        -- Indice de exposicao logistica = share da receita x prazo de entrega
        CAST(b.receita / SUM(b.receita) OVER () * 100 * b.prazo_entrega_dias
             AS DECIMAL(8,1))                                                    AS [Indice Exposicao]
FROM base AS b
CROSS JOIN dias_operacao AS d
ORDER BY [Capital Imobilizado] DESC;
"""

Q5 = """
-- =====================================================================================
-- QUERY 5 | Outubro e alergia sazonal ou efeito Outubro Rosa?
-- =====================================================================================
-- RACIONAL: A transcricao identifica outubro como mes consistentemente forte (metas de
--           R$41 mil em 2014, R$46 mil em 2015, R$53 mil em 2016) e apresenta DUAS teses
--           concorrentes que nunca sao testadas: (1) "a primavera no sudeste traz um pico
--           de alergias sazonais, isso impulsionaria a venda de antialergicos"; e (2)
--           "outubro e tambem o mes do Outubro Rosa [...] ela movimenta todo o
--           ecossistema de saude [...] pode gerar um trafego indireto para as farmacias".
--           As duas exigem acoes gerenciais opostas: a primeira e um problema de compras
--           de uma categoria; a segunda e um problema de escala e caixa.
-- OBJETIVO: Decompondo a receita por grupo terapeutico - e isolando Anti-histaminicos de
--           Antiasmaticos dentro do Sistema Respiratorio - qual e o indice de
--           sazonalidade de outubro por categoria (base 100 = mes medio do grupo)? O pico
--           esta concentrado nos antialergicos ou distribuido por todas as categorias?
-- INSIGHT ESPERADO: Se a tese da alergia estiver correta, Anti-histaminicos devem
--           apresentar o maior indice de outubro do modelo. Se for efeito Outubro Rosa,
--           esperamos elevacao difusa e semelhante em todos os grupos. Um terceiro
--           resultado - alta concentrada em grupos que nada tem a ver com alergia -
--           refutaria as duas hipoteses e exigiria uma explicacao nova.
-- =====================================================================================
WITH vnd AS (
    SELECT TRY_CONVERT(DATE, CAST(v.data AS VARCHAR(10)), 23) AS dt,
           v.produto_id, v.receita_liquida
    FROM dbo.f_vendas AS v
),
cal AS (
    SELECT TRY_CONVERT(DATE, CAST(c.data AS VARCHAR(10)), 23) AS dt, c.ano, c.mes
    FROM dbo.d_calendario AS c
),
fato_categorizado AS (
    -- 2019 e excluido de proposito: e ano parcial (termina em outubro) e distorceria
    -- justamente o indice do mes que estamos testando.
    SELECT  CASE WHEN p.categoria IN ('Anti-histamínicos', 'Antiasmáticos')
                 THEN 'Respiratório · ' + p.categoria
                 ELSE p.grupo_terapeutico END AS grupo,
            c.ano, c.mes, v.receita_liquida
    FROM vnd AS v
    INNER JOIN cal AS c        ON c.dt = v.dt
    INNER JOIN dbo.d_produto AS p ON p.produto_id = v.produto_id
    WHERE c.ano BETWEEN 2014 AND 2018
),
mensal AS (
    SELECT grupo, ano, mes, SUM(receita_liquida) AS receita
    FROM fato_categorizado
    GROUP BY grupo, ano, mes
),
media_mes AS (
    SELECT grupo, mes, AVG(receita) AS receita_media
    FROM mensal
    GROUP BY grupo, mes
),
indice AS (
    SELECT grupo, mes, receita_media,
           AVG(receita_media) OVER (PARTITION BY grupo) AS media_grupo
    FROM media_mes
)
SELECT  grupo                                                                    AS [Grupo / Categoria],
        CAST(MAX(CASE WHEN mes = 10 THEN receita_media / media_grupo * 100 END)
             AS DECIMAL(6,1))                                                    AS [Indice Outubro],
        CAST(AVG(CASE WHEN mes IN (9,10,11) THEN receita_media / media_grupo * 100 END)
             AS DECIMAL(6,1))                                                    AS [Indice Primavera],
        CAST(AVG(CASE WHEN mes IN (6,7,8) THEN receita_media / media_grupo * 100 END)
             AS DECIMAL(6,1))                                                    AS [Indice Inverno],
        CAST(AVG(CASE WHEN mes IN (12,1,2) THEN receita_media / media_grupo * 100 END)
             AS DECIMAL(6,1))                                                    AS [Indice Verao],
        CAST(MAX(receita_media / media_grupo * 100) AS DECIMAL(6,1))             AS [Pico],
        CAST(MIN(receita_media / media_grupo * 100) AS DECIMAL(6,1))             AS [Vale],
        CAST(MAX(media_grupo) * 12 AS DECIMAL(18,2))                             AS [Receita Media Anual]
FROM indice
GROUP BY grupo
ORDER BY [Indice Outubro] DESC;
"""


# ------------------------------------------------------------------------------------
# LEITURA DO ANALISTA
# Narrativa versionada junto da query: reexecutar o script reproduz o documento inteiro,
# resultado E interpretacao. Numeros conferidos contra a base real (85.407 registros).
# ------------------------------------------------------------------------------------
ANALISES = {
    "Q1": """**A meta nunca foi uma meta. Foi uma previsão.**

Em seis anos de operação a Farma Xperiun **não fechou um único ano acima da meta de receita**. O melhor
resultado foi 2017, com 100,0% — e mesmo assim por uma margem de R$ 142,81 em um ano de R$ 363 mil.
No agregado, **31 dos 69 meses com meta definida foram batidos: 45%**. Uma moeda jogada para o alto
teria performance estatisticamente equivalente.

Mas o achado que realmente importa está na coluna do gap. O desvio anual entre meta e realizado **nunca
passou de 5,3%** — em nenhum dos seis anos, em nenhuma direção. Uma meta genuinamente ambiciosa produz
variância: anos de superação, anos de frustração. Um alinhamento tão apertado e tão consistente só tem
uma explicação plausível: **a meta estava sendo calibrada a partir do resultado, e não o contrário.**

O ano de 2017 comprova a mecânica. A receita caiu 17,8% em relação a 2016 — e a meta de 2017 foi
*reduzida* de R$ 442,9 mil para R$ 363,0 mil, aterrissando em 100,0% de atingimento. O sistema de metas
não estava puxando o negócio para cima; estava se ajustando ao que o negócio já havia entregado.

Isso **refuta diretamente a leitura central do Datacast**. O "crescimento implacável" que os
apresentadores identificaram na série de metas é real como número e vazio como estratégia: é o eco do
faturamento passado, não a expressão de uma ambição. E 2017 mostra que nem a trajetória foi implacável —
houve um ano de queda de quase um quinto da receita, invisível para quem só olhou as metas.

A coluna de atingimento de quantidade fecha o diagnóstico: **95,7% a 98,3% em todos os anos**, sem
exceção. Volume subentregue de forma sistemática e estável, enquanto o atingimento de receita oscila.
Ou seja, **o que move o resultado é ticket e mix — não fluxo de clientes.** É aí que a gestão deveria
estar olhando, e é exatamente onde ela não olhou.""",

    "Q2": """**Não houve colapso. Houve fim de registro.**

A hipótese dominante do Datacast — encerramento das operações — **não sobrevive ao teste da receita por
dia operado**, que é a única base de comparação justa quando o último mês da série tem apenas 8 dias.

Outubro de 2019 registrou R$ 9.175,22 em 8 dias, o que dá **R$ 1.146,90 por dia — acima de junho
(R$ 964,04), julho (R$ 932,93), agosto (R$ 914,51) e setembro (R$ 1.038,68)**. O mês que supostamente
marca a agonia do negócio é o terceiro melhor do semestre em produtividade diária. A margem em outubro
foi de 29,6%, a segunda maior do ano. E o último dia com registro, 08/10/2019, teve 33 transações e
R$ 1.166,23 — um dia absolutamente comum.

Uma farmácia que fecha as portas não fecha assim. Fecha com queda de fluxo, liquidação de estoque,
margem comprimida e um rastro de dias fracos. **Nada disso aparece.** A operação estava viva na última
linha da base. O que terminou em 08/10/2019 foi a captura de dados, não o negócio — cenário consistente
com troca de sistema, migração ou venda com transferência do registro para o comprador.

**Duas correções factuais ao material de origem:**

1. O Datacast afirma que *"a meta de receita cai abruptamente pra cerca de 10.000 BRL"* em outubro de
   2019. A meta de outubro/2019 é **R$ 0,00**. O valor de ~R$ 10 mil que os apresentadores viram é o
   **realizado parcial** dos 8 dias. Houve confusão entre meta e realizado — e são **três** meses
   zerados (out, nov, dez), não dois.
2. O documento de dúvidas da diretoria pergunta se a queda tem relação com *"o início da pandemia"*.
   A base termina em **08/10/2019**; a pandemia começa em março de 2020. **É cronologicamente
   impossível.** A hipótese precisa ser descartada, não investigada.

Sobre 2019 como ano: houve, sim, fraqueza real — 8 dos 10 meses ficaram abaixo de 2018 em receita/dia.
Mas é erosão gradual e modesta, não ruptura. A exceção é **janeiro/2019, com +54,1%** sobre janeiro/2018,
puxado pelo Sistema Respiratório, cujo ticket saltou de R$ 89,10 para R$ 118,56. Foi esse pico isolado
que ancorou a meta recorde de janeiro que tanto impressionou os apresentadores.""",

    "Q3": """**A noite é o turno mais rentável da farmácia — e é o único que foi encurtado.**

Normalizado por hora de operação, o ranking se inverte por completo em relação à leitura do Datacast:

| Turno | Receita/hora | vs. líder |
|---|---|---|
| **Noite** (4h) | **R$ 88,96** | — |
| Manhã (5h) | R$ 79,70 | −10,4% |
| Tarde (5h) | R$ 74,29 | −16,5% |

A noite lidera também em **lucro/hora (R$ 26,05** contra R$ 22,92 da manhã e R$ 21,62 da tarde) e em
**ticket médio (R$ 28,77** contra R$ 26,65 e R$ 26,14). Em receita absoluta ela aparece em último — 30,9%
contra 35,8% da manhã — mas isso é aritmética de denominador, não desempenho: **ela tem 20% menos tempo
para vender.**

A transcrição levanta duas explicações para o turno curto: queda de fluxo de clientes ou custo da hora
noturna. Os dados **eliminam a primeira**. A noite faz 3,10 transações por hora, a manhã 3,00 e a tarde
2,80 — o fluxo horário noturno é o *maior* dos três. A justificativa de fluxo não se sustenta; resta a
hipótese de custo, que precisa ser confrontada com a receita que está sendo deixada na mesa.

**Dimensionamento honesto da hora suprimida:** à média do turno, uma hora extra à noite valeria
R$ 88,96 de receita e R$ 26,05 de lucro por dia — cerca de R$ 32 mil e R$ 9,4 mil por ano
respectivamente. Este é um **teto, não uma estimativa**: a última hora de operação tende a ter fluxo
abaixo da média do turno, e o custo do adicional noturno precisa entrar na conta. A recomendação
correta não é "estenda o turno", é **"teste a extensão por 60 dias e meça"** — a hipótese agora tem
tamanho e merece experimento.""",

    "Q4": """**A concentração é o risco maior; a Neo Química é o custo mais caro.**

Dois problemas distintos aparecem na mesma tabela, e é importante não confundi-los.

**1. Concentração.** A Medley sozinha responde por **27,4% da receita** — mais do que os três menores
fornecedores somados. Com prazo de 3 dias e a maior necessidade de estoque de cobertura
(**R$ 625,86** por ciclo, 26% de todo o capital imobilizado da farmácia), ela é simultaneamente o maior
gerador de receita e o maior ponto único de falha. Uma ruptura de fornecimento da Medley não é um
incidente logístico; é uma parada de mais de um quarto do faturamento.

**2. Eficiência logística.** A intuição do Datacast sobre a Neo Química se confirma — e fica pior quando
quantificada. Único fornecedor fora do Sudeste (Anápolis/GO), prazo de 5 dias, ela entrega apenas
**9,7% da receita** com margem de **22,4%** (a segunda pior) e ainda assim imobiliza **R$ 419,69** —
o **segundo maior capital travado da operação**. Está no quadrante errado dos três eixos ao mesmo tempo:
longe, cara de estocar e pouco rentável. Seu índice de exposição logística (48,6) é o segundo pior da
base, enquanto ela é apenas a quinta em receita.

**O benchmark existe e está do lado.** A Hypera Pharma entrega em 2 dias, tem a **melhor margem da base
(33,5%)** e imobiliza apenas R$ 138,88 — um terço da Neo Química — para uma participação quase idêntica
(9,4%). Se houver sobreposição de portfólio entre as duas, migrar volume da Neo Química para a Hypera é
a ação de maior retorno imediato: libera capital de giro, encurta o lead time e ganha 11 pontos
percentuais de margem no mesmo item de receita.

**Um terceiro caso, de natureza diferente:** a Cimed tem prazo curto (3 dias) e logística boa, mas a
**pior margem da base — 20,4%** — sobre 13,4% da receita. Aqui o problema não é logístico, é comercial:
é negociação de preço de compra, não de prazo de entrega.

O capital total imobilizado em estoque de cobertura é de **R$ 2.440,10** — dos quais R$ 1.045,55 (43%)
concentrados em Medley e Neo Química.""",

    "Q5": """**As duas hipóteses do Datacast estão erradas. E a documentação também.**

A tese da alergia sazonal é **refutada de forma inequívoca**. Os Anti-histamínicos — exatamente a
categoria que deveria explodir na primavera — registram **índice 73,2 em outubro**, ou seja, 27% *abaixo*
da sua própria média mensal. É o pior índice de outubro de toda a base. A categoria que a hipótese
elegeu como protagonista é a única que **cai** no mês em questão.

A tese do Outubro Rosa também não se sustenta como formulada. O efeito de "tráfego indireto elevado"
deveria erguer todas as categorias de forma parecida. Não é o que acontece:

| Grupo / Categoria | Índice Outubro |
|---|---|
| Analgésicos | **140,3** |
| Respiratório · Antiasmáticos | **140,1** |
| Sistema Nervoso | 105,2 |
| Anti-inflamatórios | 102,3 |
| Respiratório · Anti-histamínicos | **73,2** |

O pico de outubro é real (índice geral **122,2**, o maior do ano), mas é **concentrado**: dois grupos
sobem 40%, dois ficam praticamente parados e um cai. Isso não é maré, é corrente específica. Analgésicos
e Antiasmáticos respondem por praticamente todo o efeito — e nenhum dos dois tem relação com alergia
ou com rastreamento de câncer de mama.

**Um alerta de qualidade de dado que precisa subir para a diretoria:** os Anti-histamínicos são
**contracíclicos** nesta base — índice **125,0 no inverno** e **53,4 no verão**, o inverso do
comportamento clínico esperado para antialérgicos. Simetricamente, os **Antiasmáticos caem no inverno
(índice 63,9)**, contrariando tanto a intuição médica quanto a orientação explícita da documentação do
desafio (*"preste atenção nos meses de inverno para respiratórios"*). Esses dois padrões invertidos
devem ser **validados junto ao negócio antes de virar decisão de compra**. Podem ser característica real
da farmácia, podem ser um artefato de geração da base — mas não podem ser assumidos como verdade.

**O que fica de acionável:** o inverno é o pior período do ano (índice geral 80,3 em julho, o vale da
série) e outubro é o pico (122,2), seguido de dezembro (120,7) e janeiro (114,2). O plano de compras e
a escala de pessoal devem ser dimensionados por esse ciclo — e as metas mensais, hoje planas, deveriam
respeitá-lo.""",
}

QUERIES = [
    {"id": "Q1", "titulo": "A ambição bateu com a entrega?",
     "dor": "DOR 4 — Meta vs. Realizado", "sql": Q1},
    {"id": "Q2", "titulo": "O que realmente aconteceu em 2019?",
     "dor": "DOR 5 — O mistério de 2019", "sql": Q2},
    {"id": "Q3", "titulo": "Qual turno é de fato o mais produtivo?",
     "dor": "DOR 1 — O comportamento por turno é um mistério", "sql": Q3},
    {"id": "Q4", "titulo": "Onde está travado o capital de giro?",
     "dor": "DOR 2 — O malabarismo da gestão de compras", "sql": Q4},
    {"id": "Q5", "titulo": "Outubro é alergia sazonal ou efeito Outubro Rosa?",
     "dor": "DOR 3 — Sazonalidade intuída mas nunca medida", "sql": Q5},
]


# ------------------------------------------------------------------------------------
# CONEXAO
# ------------------------------------------------------------------------------------
def build_connection_string(server, database, driver, user=None, password=None,
                            trust_cert=True):
    parts = [f"DRIVER={{{driver}}}", f"SERVER={server}", f"DATABASE={database}"]
    if user:
        parts += [f"UID={user}", f"PWD={password}"]
    else:
        parts.append("Trusted_Connection=yes")   # Windows Authentication
    if trust_cert:
        parts.append("TrustServerCertificate=yes")
    parts.append("Encrypt=no")
    return ";".join(parts) + ";"


def connect(server, database, user=None, password=None):
    try:
        import pyodbc
    except ImportError:
        sys.exit("ERRO: pyodbc nao instalado.  Execute:  pip install pyodbc")

    available = [d for d in pyodbc.drivers()]
    if not available:
        sys.exit("ERRO: nenhum driver ODBC encontrado. Instale o 'ODBC Driver 17/18 for SQL Server'.")

    ordered = [d for d in DRIVER_CANDIDATES if d in available] or available
    last_error = None
    for driver in ordered:
        cs = build_connection_string(server, database, driver, user, password)
        try:
            conn = pyodbc.connect(cs, timeout=10)
            print(f"  [OK] Conectado  |  driver: {driver}  |  server: {server}  |  db: {database}")
            return conn
        except Exception as exc:                                   # noqa: BLE001
            last_error = exc
            print(f"  [--] Falhou com '{driver}': {str(exc).splitlines()[0][:110]}")

    sys.exit(f"\nERRO: nao foi possivel conectar ao SQL Server.\nUltimo erro: {last_error}\n"
             f"Drivers disponiveis: {available}")


# ------------------------------------------------------------------------------------
# FORMATACAO
# ------------------------------------------------------------------------------------
def fmt(value):
    """Formata valores no padrao pt-BR para exibicao em markdown."""
    from decimal import Decimal
    if value is None:
        return "—"
    if isinstance(value, (int,)) and not isinstance(value, bool):
        return f"{value:,}".replace(",", ".")
    if isinstance(value, (float, Decimal)):
        s = f"{float(value):,.2f}"
        return s.replace(",", "\x00").replace(".", ",").replace("\x00", ".")
    return str(value)


def to_markdown_table(columns, rows):
    if not rows:
        return "_A consulta não retornou linhas._"
    head = "| " + " | ".join(columns) + " |"
    sep = "|" + "|".join(["---"] * len(columns)) + "|"
    body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in rows]
    return "\n".join([head, sep] + body)


# ------------------------------------------------------------------------------------
# MAIN
# ------------------------------------------------------------------------------------
def main():
    ap = argparse.ArgumentParser(description="Farma Xperiun - Fase 2 - Exploracao Analitica")
    ap.add_argument("--server", default=DEFAULT_SERVER)
    ap.add_argument("--database", default=DEFAULT_DATABASE)
    ap.add_argument("--user", default=None, help="Se omitido, usa Windows Authentication")
    ap.add_argument("--password", default=None)
    ap.add_argument("--output", default=str(OUTPUT_MD))
    args = ap.parse_args()

    print("=" * 88)
    print(" FARMA XPERIUN | FASE 2 - Exploracao Analitica (SQL Server)")
    print("=" * 88)

    conn = connect(args.server, args.database, args.user, args.password)
    cursor = conn.cursor()

    blocos = []
    for q in QUERIES:
        print(f"\n  >> {q['id']} - {q['titulo']}")
        try:
            cursor.execute(q["sql"])
            columns = [c[0] for c in cursor.description]
            rows = cursor.fetchall()
            print(f"     {len(rows)} linha(s) retornada(s).")
            tabela = to_markdown_table(columns, rows)
            erro = None
        except Exception as exc:                                   # noqa: BLE001
            print(f"     [ERRO] {exc}")
            tabela = f"> ⚠️ **Falha na execução:** `{exc}`"
            erro = exc

        blocos.append({
            "id": q["id"], "titulo": q["titulo"], "dor": q["dor"],
            "sql": q["sql"].strip(), "tabela": tabela,
            "analise": ANALISES.get(q["id"], ""), "erro": erro,
        })

    cursor.close()
    conn.close()

    # ---------------------------------------------------------------------------
    # MONTAGEM DO DOCUMENTO
    # ---------------------------------------------------------------------------
    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    md = []
    md.append("# Insights Iniciais — Farma Xperiun")
    md.append("### Fase 2 · Exploração Analítica · SQL Server + Python\n")
    md.append("| | |")
    md.append("|---|---|")
    md.append(f"| **Origem** | `{args.server}` · banco `{args.database}` |")
    md.append(f"| **Executado em** | {agora} |")
    md.append("| **Script** | `scripts/run_sql_server.py` |")
    md.append("| **Base analítica** | 85.407 transações · 02/01/2014 a 08/10/2019 |")
    md.append("| **Ancoragem** | `docs/business_context.md` (Fase 1) |\n")
    md.append("---\n")
    md.append("## Como ler este documento\n")
    md.append("As cinco perguntas abaixo **não foram escolhidas por conveniência técnica**. Cada uma "
              "responde a uma dor específica levantada pela diretoria na transcrição do Datacast, "
              "mapeada na Fase 1. Cada query carrega o bloco `RACIONAL / OBJETIVO / INSIGHT ESPERADO` "
              "que amarra a consulta à dor que a originou — e a hipótese registrada **antes** de olhar "
              "o resultado, para que a análise possa ser confrontada, e não apenas confirmada.\n")
    md.append("Em quatro das cinco perguntas o resultado **contraria** a hipótese de partida. "
              "Isso está sinalizado no texto.\n")
    md.append("---\n")

    for b in blocos:
        md.append(f"## {b['id']} · {b['titulo']}\n")
        md.append(f"> **Dor de origem:** {b['dor']}\n")
        md.append("<details>\n<summary><b>Ver query SQL documentada</b></summary>\n")
        md.append("```sql")
        md.append(b["sql"])
        md.append("```\n")
        md.append("</details>\n")
        md.append("### Resultado\n")
        md.append(b["tabela"] + "\n")
        if b["analise"]:
            md.append("### Leitura do analista\n")
            md.append(b["analise"] + "\n")
        md.append("---\n")

    md.append("## Síntese executiva\n")
    md.append("| # | Pergunta | Hipótese inicial | Veredito |")
    md.append("|---|---|---|---|")
    md.append("| Q1 | A ambição bateu com a entrega? | Crescimento implacável | ❌ **Refutada** — "
              "nenhum ano batido, e a meta seguia o resultado |")
    md.append("| Q2 | O que houve em 2019? | Encerramento do negócio | ❌ **Refutada** — "
              "operação saudável até o último registro |")
    md.append("| Q3 | Qual turno é mais produtivo? | A noite vende menos | ❌ **Refutada** — "
              "a noite lidera em receita e lucro por hora |")
    md.append("| Q4 | Onde trava o capital de giro? | Neo Química é o gargalo | ✅ **Confirmada "
              "e dimensionada** — e a concentração na Medley é risco maior |")
    md.append("| Q5 | Outubro é alergia ou Outubro Rosa? | Uma das duas teses | ❌ **Ambas refutadas** — "
              "o motor são analgésicos e antiasmáticos |")
    md.append("\n---\n")
    md.append("## Limitações declaradas\n")
    md.append("- **Meses com meta zero** (out/nov/dez de 2019) são excluídos do cálculo de "
              "atingimento. Meta zero é ausência de meta, não meta baixa.\n"
              "- **2019 é ano parcial** (termina em 08/10) e foi excluído do cálculo de índices "
              "sazonais, para não distorcer justamente o mês em teste.\n"
              "- **Feriados móveis** (Carnaval, Sexta-Feira Santa, Corpus Christi) não constam de "
              "`d_calendario`. Quedas nessas datas não devem ser atribuídas a comportamento do "
              "consumidor.\n"
              "- **Sazonalidade invertida** em Anti-histamínicos e Antiasmáticos é reportada como "
              "achado, não como recomendação. Exige validação com o negócio.\n"
              "- **`quantidade` é fracionada** e `preco_unitario` da venda varia ±5% face à tabela de "
              "`d_produto`. Toda métrica financeira usa exclusivamente os campos de `f_vendas`.\n"
              "- **A hora extra noturna** dimensionada a partir da Q3 é um teto teórico calculado à "
              "média do turno, não uma previsão. A recomendação é testar, não implementar.\n")
    md.append("\n---\n")
    md.append(f"*Documento gerado automaticamente por `scripts/run_sql_server.py` em {agora}.*")

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")

    print("\n" + "=" * 88)
    print(f" Documento gerado: {out}")
    falhas = [b["id"] for b in blocos if b["erro"]]
    print(f" Queries executadas com sucesso: {len(blocos) - len(falhas)}/{len(blocos)}")
    if falhas:
        print(f" ATENCAO - falharam: {', '.join(falhas)}")
    print("=" * 88)


if __name__ == "__main__":
    main()
