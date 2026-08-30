# -*- coding: utf-8 -*-
"""
=====================================================================================
 FARMA XPERIUN | FASE 2 - Harness de validacao
=====================================================================================
 PARA QUE SERVE
     O entregavel oficial da Fase 2 e o run_sql_server.py, que roda em T-SQL contra a
     instancia local do SQL Server. Este script e a rede de seguranca: executa as MESMAS
     cinco analises, com a mesma logica, em dialeto SQLite contra o arquivo
     farma_xperiun.db distribuido no material do desafio.

     Ele existe por tres motivos:
       1. Provar que a logica das queries esta correta antes de rodar em producao.
       2. Reconciliar os totais contra os numeros publicados na documentacao oficial
          do desafio (documentacao_farma_xperiun.docx). Se os totais nao baterem, algo
          esta errado na query - nao no banco.
       3. Permitir gerar o docs/insights_iniciais.md mesmo sem SQL Server disponivel.

     A narrativa analitica (ANALISES) e importada de run_sql_server.py, e nao duplicada,
     para que exista uma unica fonte da verdade para o texto do documento.

 EXECUCAO
     python scripts/validate_sqlite.py
     python scripts/validate_sqlite.py --db "caminho/para/farma_xperiun.db"
     python scripts/validate_sqlite.py --no-output      (so valida, nao gera o .md)
=====================================================================================
"""

import argparse
import importlib.util
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DEFAULT_DB = (BASE_DIR / "Base e Materiais Auxiliares" / "Base"
              / "Base-20260210T235449Z-1-001" / "Base" / "farma_xperiun.db")
OUTPUT_MD = BASE_DIR / "docs" / "insights_iniciais.md"

# --- importa a narrativa e os utilitarios do script oficial (fonte unica da verdade) ---
_spec = importlib.util.spec_from_file_location("runner", Path(__file__).parent / "run_sql_server.py")
runner = importlib.util.module_from_spec(_spec)
sys.argv_backup, sys.argv = sys.argv, [sys.argv[0]]
_spec.loader.exec_module(runner)
sys.argv = sys.argv_backup

# ------------------------------------------------------------------------------------
# NUMEROS OFICIAIS (documentacao_farma_xperiun.docx, secao 1 - Visao Geral)
# ------------------------------------------------------------------------------------
GABARITO = {
    "transacoes":    (85407,        0),
    "receita_total": (2313807.90,   1.00),
    "lucro_total":   (671861.32,    1.00),
    "ticket_medio":  (27.09,        0.01),
    "produtos":      (33,           0),
    "fornecedores":  (8,            0),
}

# ------------------------------------------------------------------------------------
# AS MESMAS 5 QUERIES, EM DIALETO SQLITE
# Diferencas de dialeto tratadas: TRY_CONVERT->coluna ja em texto ISO; [col]->"col";
# CAST(... AS DECIMAL)->ROUND(); concatenacao +->||; CAST(x AS VARCHAR)->CAST(x AS TEXT).
# A logica algebrica e identica linha a linha.
# ------------------------------------------------------------------------------------
S1 = """
WITH realizado_mes AS (
    SELECT c.ano, c.mes, COUNT(*) transacoes, SUM(v.receita_liquida) receita,
           SUM(v.quantidade) quantidade, SUM(v.lucro) lucro
    FROM f_vendas v INNER JOIN d_calendario c ON c.data = v.data
    GROUP BY c.ano, c.mes),
confronto AS (
    SELECT m.ano, m.mes, m.meta_receita, m.meta_quantidade,
           COALESCE(r.receita,0) receita, COALESCE(r.quantidade,0) quantidade,
           COALESCE(r.lucro,0) lucro
    FROM d_meta_mensal m LEFT JOIN realizado_mes r ON r.ano=m.ano AND r.mes=m.mes),
anual AS (
    SELECT ano,
      SUM(CASE WHEN meta_receita>0 THEN meta_receita ELSE 0 END) meta_total,
      SUM(CASE WHEN meta_receita>0 THEN receita ELSE 0 END) receita_com_meta,
      SUM(receita) receita_total, SUM(lucro) lucro_total,
      SUM(CASE WHEN meta_quantidade>0 THEN meta_quantidade ELSE 0 END) meta_qtd,
      SUM(CASE WHEN meta_quantidade>0 THEN quantidade ELSE 0 END) qtd_com_meta,
      SUM(CASE WHEN meta_receita>0 THEN 1 ELSE 0 END) meses_com_meta,
      SUM(CASE WHEN meta_receita>0 AND receita>=meta_receita THEN 1 ELSE 0 END) meses_batidos
    FROM confronto GROUP BY ano)
SELECT CAST(ano AS TEXT) "Ano",
       ROUND(meta_total,2) "Meta Receita",
       ROUND(receita_com_meta,2) "Realizado",
       ROUND(receita_com_meta/NULLIF(meta_total,0)*100,1) "% Ating. Receita",
       ROUND(receita_com_meta-meta_total,2) "Gap R$",
       ROUND(qtd_com_meta/NULLIF(meta_qtd,0)*100,1) "% Ating. Qtd",
       CAST(meses_batidos AS TEXT)||'/'||CAST(meses_com_meta AS TEXT) "Meses Batidos",
       ROUND(lucro_total/NULLIF(receita_total,0)*100,1) "Margem %",
       ROUND((receita_total/NULLIF(LAG(receita_total) OVER (ORDER BY ano),0)-1)*100,1) "YoY Receita %"
FROM anual ORDER BY ano
"""

S2 = """
WITH mensal AS (
    SELECT c.ano, c.mes, MIN(c.nome_mes) nome_mes, COUNT(*) transacoes,
           COUNT(DISTINCT v.data) dias_com_venda, SUM(v.receita_liquida) receita,
           SUM(v.lucro) lucro, SUM(v.desconto) desconto
    FROM f_vendas v INNER JOIN d_calendario c ON c.data=v.data
    WHERE c.ano IN (2018,2019) GROUP BY c.ano, c.mes)
SELECT a.mes "Mes", a.nome_mes "Nome", a.dias_com_venda "Dias c/ Venda",
       a.transacoes "Transacoes", ROUND(a.receita,2) "Receita 2019",
       ROUND(a.receita/NULLIF(a.transacoes,0),2) "Ticket 2019",
       ROUND(a.lucro/NULLIF(a.receita,0)*100,1) "Margem % 2019",
       ROUND(a.receita/NULLIF(a.dias_com_venda,0),2) "Receita/Dia 2019",
       ROUND(b.receita/NULLIF(b.dias_com_venda,0),2) "Receita/Dia 2018",
       ROUND(((a.receita/NULLIF(a.dias_com_venda,0))/
              NULLIF(b.receita/NULLIF(b.dias_com_venda,0),0)-1)*100,1) "Var. Dia YoY %"
FROM mensal a LEFT JOIN mensal b ON b.mes=a.mes AND b.ano=2018
WHERE a.ano=2019 ORDER BY a.mes
"""

S3 = """
WITH base AS (
    SELECT t.turno_id, t.nome_turno, (t.hora_fim-t.hora_inicio) horas_turno,
           COUNT(*) transacoes, COUNT(DISTINCT v.data) dias_operados,
           SUM(v.receita_liquida) receita, SUM(v.receita_bruta) receita_bruta,
           SUM(v.lucro) lucro, SUM(v.desconto) desconto
    FROM f_vendas v INNER JOIN d_turno t ON t.turno_id=v.turno_id
    GROUP BY t.turno_id, t.nome_turno, (t.hora_fim-t.hora_inicio)),
mix_controlado AS (
    SELECT v.turno_id,
      SUM(CASE WHEN p.exige_receita=1 THEN v.receita_liquida ELSE 0 END)
        /NULLIF(SUM(v.receita_liquida),0)*100 pct_controlado
    FROM f_vendas v INNER JOIN d_produto p ON p.produto_id=v.produto_id
    GROUP BY v.turno_id)
SELECT b.nome_turno "Turno", b.horas_turno "Horas", b.transacoes "Transacoes",
       ROUND(b.receita,2) "Receita",
       ROUND(b.receita/SUM(b.receita) OVER ()*100,1) "Share %",
       ROUND(b.receita/NULLIF(b.dias_operados*b.horas_turno,0),2) "Receita/Hora",
       ROUND(b.lucro/NULLIF(b.dias_operados*b.horas_turno,0),2) "Lucro/Hora",
       ROUND(b.receita/NULLIF(b.transacoes,0),2) "Ticket Medio",
       ROUND(b.lucro/NULLIF(b.receita,0)*100,1) "Margem %",
       ROUND(b.desconto/NULLIF(b.receita_bruta,0)*100,2) "Desconto %",
       ROUND(b.transacoes*1.0/NULLIF(b.dias_operados*b.horas_turno,0),2) "Transacoes/Hora",
       ROUND(m.pct_controlado,1) "% Controlado"
FROM base b INNER JOIN mix_controlado m ON m.turno_id=b.turno_id
ORDER BY "Receita/Hora" DESC
"""

S4 = """
WITH dias_operacao AS (SELECT COUNT(DISTINCT data) dias FROM f_vendas),
base AS (
    SELECT f.nome, f.cidade||'/'||f.estado localizacao, f.regiao, f.prazo_entrega_dias,
           COUNT(*) transacoes, SUM(v.receita_liquida) receita, SUM(v.lucro) lucro,
           SUM(v.custo_total) custo
    FROM f_vendas v INNER JOIN d_fornecedor f ON f.fornecedor_id=v.fornecedor_id
    GROUP BY f.nome, f.cidade||'/'||f.estado, f.regiao, f.prazo_entrega_dias)
SELECT b.nome "Fornecedor", b.localizacao "Local", b.regiao "Regiao",
       b.prazo_entrega_dias "Prazo (dias)", ROUND(b.receita,2) "Receita",
       ROUND(b.receita/SUM(b.receita) OVER ()*100,1) "Share %",
       ROUND(b.lucro/NULLIF(b.receita,0)*100,1) "Margem %",
       ROUND(b.custo/NULLIF(d.dias,0),2) "Custo/Dia",
       ROUND(b.custo/NULLIF(d.dias,0)*b.prazo_entrega_dias,2) "Capital Imobilizado",
       ROUND(b.receita/SUM(b.receita) OVER ()*100*b.prazo_entrega_dias,1) "Indice Exposicao"
FROM base b CROSS JOIN dias_operacao d ORDER BY "Capital Imobilizado" DESC
"""

S5 = """
WITH fato_categorizado AS (
    SELECT CASE WHEN p.categoria IN ('Anti-histamínicos','Antiasmáticos')
                THEN 'Respiratório · '||p.categoria ELSE p.grupo_terapeutico END grupo,
           c.ano, c.mes, v.receita_liquida
    FROM f_vendas v INNER JOIN d_calendario c ON c.data=v.data
                    INNER JOIN d_produto p ON p.produto_id=v.produto_id
    WHERE c.ano BETWEEN 2014 AND 2018),
mensal AS (SELECT grupo, ano, mes, SUM(receita_liquida) receita
           FROM fato_categorizado GROUP BY grupo, ano, mes),
media_mes AS (SELECT grupo, mes, AVG(receita) receita_media FROM mensal GROUP BY grupo, mes),
indice AS (SELECT grupo, mes, receita_media,
                  AVG(receita_media) OVER (PARTITION BY grupo) media_grupo FROM media_mes)
SELECT grupo "Grupo / Categoria",
       ROUND(MAX(CASE WHEN mes=10 THEN receita_media/media_grupo*100 END),1) "Indice Outubro",
       ROUND(AVG(CASE WHEN mes IN (9,10,11) THEN receita_media/media_grupo*100 END),1) "Indice Primavera",
       ROUND(AVG(CASE WHEN mes IN (6,7,8) THEN receita_media/media_grupo*100 END),1) "Indice Inverno",
       ROUND(AVG(CASE WHEN mes IN (12,1,2) THEN receita_media/media_grupo*100 END),1) "Indice Verao",
       ROUND(MAX(receita_media/media_grupo*100),1) "Pico",
       ROUND(MIN(receita_media/media_grupo*100),1) "Vale",
       ROUND(MAX(media_grupo)*12,2) "Receita Media Anual"
FROM indice GROUP BY grupo ORDER BY "Indice Outubro" DESC
"""

SQLITE_SQL = {"Q1": S1, "Q2": S2, "Q3": S3, "Q4": S4, "Q5": S5}


def reconciliar(conn):
    """Confere os totais da base contra a documentacao oficial do desafio."""
    print("\n  RECONCILIACAO COM A DOCUMENTACAO OFICIAL")
    print("  " + "-" * 74)
    medido = dict(zip(
        ["transacoes", "receita_total", "lucro_total", "ticket_medio"],
        conn.execute("""SELECT COUNT(*), ROUND(SUM(receita_liquida),2), ROUND(SUM(lucro),2),
                               ROUND(SUM(receita_liquida)/COUNT(*),2) FROM f_vendas""").fetchone()))
    medido["produtos"] = conn.execute("SELECT COUNT(*) FROM d_produto").fetchone()[0]
    medido["fornecedores"] = conn.execute("SELECT COUNT(*) FROM d_fornecedor").fetchone()[0]

    ok = True
    for chave, (esperado, tol) in GABARITO.items():
        obtido = medido[chave]
        passou = abs(obtido - esperado) <= tol
        ok &= passou
        print(f"  {'[OK]' if passou else '[XX]'} {chave:<16} esperado={esperado:>14,.2f}   "
              f"obtido={obtido:>14,.2f}")
    print("  " + "-" * 74)
    print(f"  {'TODOS OS TOTAIS RECONCILIAM.' if ok else 'DIVERGENCIA DETECTADA - INVESTIGAR.'}")
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default=str(DEFAULT_DB))
    ap.add_argument("--output", default=str(OUTPUT_MD))
    ap.add_argument("--no-output", action="store_true")
    args = ap.parse_args()

    print("=" * 88)
    print(" FARMA XPERIUN | FASE 2 - Harness de validacao (SQLite)")
    print("=" * 88)

    db = Path(args.db)
    if not db.exists():
        sys.exit(f"ERRO: banco nao encontrado em {db}")
    conn = sqlite3.connect(db)
    print(f"  Base: {db.name}")

    if not reconciliar(conn):
        sys.exit(1)

    blocos = []
    for q in runner.QUERIES:
        print(f"\n  >> {q['id']} - {q['titulo']}")
        cur = conn.execute(SQLITE_SQL[q["id"]])
        columns = [d[0] for d in cur.description]
        rows = cur.fetchall()
        print(f"     {len(rows)} linha(s).")
        blocos.append({
            "id": q["id"], "titulo": q["titulo"], "dor": q["dor"],
            "sql": q["sql"].strip(),
            "tabela": runner.to_markdown_table(columns, rows),
            "analise": runner.ANALISES.get(q["id"], ""), "erro": None,
        })

    if args.no_output:
        print("\n  Validacao concluida (--no-output: documento nao gerado).")
        return

    agora = datetime.now().strftime("%d/%m/%Y às %H:%M")
    md = ["# Insights Iniciais — Farma Xperiun",
          "### Fase 2 · Exploração Analítica · SQL Server + Python\n",
          "| | |", "|---|---|",
          "| **Modelo** | `farma_xperiun` · esquema `dbo` · star schema |",
          f"| **Gerado em** | {agora} |",
          "| **Script oficial** | `scripts/run_sql_server.py` (T-SQL / pyodbc / Windows Auth) |",
          "| **Harness de validação** | `scripts/validate_sqlite.py` |",
          "| **Base analítica** | 85.407 transações · 02/01/2014 a 08/10/2019 |",
          "| **Ancoragem** | `docs/business_context.md` (Fase 1) |\n",
          "> **Nota de procedência.** As queries exibidas abaixo são as de produção, em **T-SQL**, "
          "prontas para rodar contra o SQL Server local. Os resultados foram validados executando "
          "a mesma álgebra sobre a base oficial do desafio, com **reconciliação automática** contra "
          "os totais publicados na documentação (85.407 transações · R$ 2.313.807,90 de receita · "
          "R$ 671.861,32 de lucro · ticket de R$ 27,09). Todos os totais conferem.\n",
          "---\n", "## Como ler este documento\n",
          "As cinco perguntas abaixo **não foram escolhidas por conveniência técnica**. Cada uma "
          "responde a uma dor específica levantada pela diretoria na transcrição do Datacast, mapeada "
          "na Fase 1. Cada query carrega o bloco `RACIONAL / OBJETIVO / INSIGHT ESPERADO` que amarra "
          "a consulta à dor que a originou — e registra a hipótese **antes** de olhar o resultado, "
          "para que a análise possa ser confrontada, e não apenas confirmada.\n",
          "Em quatro das cinco perguntas o resultado **contraria** a hipótese de partida. "
          "Isso está sinalizado no texto.\n", "---\n"]

    for b in blocos:
        md += [f"## {b['id']} · {b['titulo']}\n",
               f"> **Dor de origem:** {b['dor']}\n",
               "<details>\n<summary><b>Ver query SQL documentada (T-SQL)</b></summary>\n",
               "```sql", b["sql"], "```\n", "</details>\n",
               "### Resultado\n", b["tabela"] + "\n"]
        if b["analise"]:
            md += ["### Leitura do analista\n", b["analise"] + "\n"]
        md.append("---\n")

    md += ["## Síntese executiva\n",
           "| # | Pergunta | Hipótese de partida | Veredito |",
           "|---|---|---|---|",
           "| Q1 | A ambição bateu com a entrega? | Crescimento implacável | ❌ **Refutada** — nenhum "
           "ano batido; a meta seguia o resultado, não o contrário |",
           "| Q2 | O que houve em 2019? | Encerramento do negócio | ❌ **Refutada** — operação saudável "
           "até o último registro; foi fim de captura de dados |",
           "| Q3 | Qual turno é mais produtivo? | A noite vende menos | ❌ **Refutada** — a noite lidera "
           "em receita e lucro por hora |",
           "| Q4 | Onde trava o capital de giro? | Neo Química é o gargalo | ✅ **Confirmada e "
           "dimensionada** — mas a concentração na Medley é o risco maior |",
           "| Q5 | Outubro é alergia ou Outubro Rosa? | Uma das duas teses | ❌ **Ambas refutadas** — "
           "o motor são analgésicos e antiasmáticos |",
           "\n---\n", "## Limitações declaradas\n",
           "- **Meses com meta zero** (out/nov/dez de 2019) são excluídos do cálculo de atingimento. "
           "Meta zero é ausência de meta, não meta baixa.",
           "- **2019 é ano parcial** (termina em 08/10) e foi excluído do cálculo de índices sazonais, "
           "para não distorcer justamente o mês em teste.",
           "- **Feriados móveis** (Carnaval, Sexta-Feira Santa, Corpus Christi) não constam de "
           "`d_calendario`. Quedas nessas datas não devem ser atribuídas a comportamento do consumidor.",
           "- **Sazonalidade invertida** em Anti-histamínicos e Antiasmáticos é reportada como achado, "
           "não como recomendação. Exige validação com o negócio antes de virar decisão de compra.",
           "- **`quantidade` é fracionada** e `preco_unitario` da venda varia ±5% face à tabela de "
           "`d_produto`. Toda métrica financeira usa exclusivamente os campos de `f_vendas`.",
           "- **A hora extra noturna (Q3)** é um teto teórico calculado à média do turno, não uma "
           "previsão. A recomendação é testar, não implementar.\n", "\n---\n",
           f"*Gerado por `scripts/validate_sqlite.py` em {agora}. "
           f"Para reproduzir contra o SQL Server: `python scripts/run_sql_server.py`.*"]

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(md), encoding="utf-8")
    print("\n" + "=" * 88)
    print(f" Documento gerado: {out}")
    print(f" Queries validadas: {len(blocos)}/{len(runner.QUERIES)}")
    print("=" * 88)


if __name__ == "__main__":
    main()
