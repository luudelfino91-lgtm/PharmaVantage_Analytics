# Prompt para o Claude no VS Code

Copie o bloco abaixo inteiro e cole na primeira mensagem do Claude, com a pasta
`3- Data Challenge -` já aberta como workspace.

---

```
Você é um Engenheiro de Analytics trabalhando neste repositório. A pasta aberta é a raiz
de um Data Challenge de BI já concluído — a análise está pronta e validada. Sua tarefa é
APENAS colocar o pipeline Python para rodar nesta máquina Windows e executá-lo contra o
SQL Server local.

CONTEXTO
Banco: SQL Server local, database `farma_xperiun`, esquema `dbo`, modelo estrela com
f_vendas (fato) + d_calendario, d_produto, d_fornecedor, d_turno, d_meta_mensal.

Dois scripts em /scripts:
  • validate_sqlite.py — roda as mesmas 5 análises contra o farma_xperiun.db do material
    do desafio e reconcilia os totais contra a documentação oficial. Só usa a stdlib.
  • run_sql_server.py — o entregável oficial. T-SQL via pyodbc com Windows Authentication.
    Ambos geram docs/insights_iniciais.md.

Há um guia completo em docs/setup_vscode.md — leia antes de começar.

EXECUTE NESTA ORDEM

1. Criar e ativar o venv:
     py -m venv .venv
     .\.venv\Scripts\Activate.ps1
   Se o PowerShell bloquear, rode antes:
     Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   Depois selecione esse interpretador no VS Code.

2. pip install -r requirements.txt

3. python scripts\validate_sqlite.py
   Este passo é o portão. Ele DEVE imprimir "TODOS OS TOTAIS RECONCILIAM." com seis [OK].
   Se falhar, PARE e me diga o erro — não siga para o SQL Server.

4. Conferir os pré-requisitos do SQL Server antes de conectar:
     Get-Service | Where-Object { $_.Name -like "MSSQL*" }
     Get-OdbcDriver | Select-Object -ExpandProperty Name
   Reporte o que encontrou. Se faltar o ODBC Driver 18 (ou 17) for SQL Server, me avise —
   não tente contornar com outra biblioteca.

5. python scripts\run_sql_server.py
   Se a instância for nomeada, tente:
     python scripts\run_sql_server.py --server "localhost\SQLEXPRESS"

VERIFICAÇÃO FINAL
Abra docs/insights_iniciais.md e confirme que as CINCO tabelas de resultados estão
preenchidas, sem nenhum bloco "Falha na execução". Os números têm de bater com o gabarito:

  Transações ......... 85.407
  Receita líquida .... R$ 2.313.807,90
  Lucro .............. R$ 671.861,32
  Ticket médio ....... R$ 27,09
  Dias operados ...... 2.080
  Meses batidos ...... 31 de 69

REGRAS
• NÃO altere a lógica SQL das queries nem os blocos de comentário
  RACIONAL / OBJETIVO / INSIGHT ESPERADO. Eles são parte da entrega avaliada.
• NÃO altere os textos da seção ANALISES em run_sql_server.py.
• Se uma query falhar, reporte o erro exato do SQL Server e a query afetada.
  Não reescreva a consulta para "fazer passar".
• Se um número divergir do gabarito, NÃO ajuste o código. Divergência significa que a
  carga do banco está diferente da base original — investigue a carga e me reporte.
• Nada de dados inventados ou de exemplo. Se não conseguir conectar, diga que não conseguiu.

AO TERMINAR, me reporte:
  1. Qual driver ODBC foi usado e em qual servidor/instância conectou.
  2. Se os seis números do gabarito bateram (sim/não, e quais divergiram).
  3. Qualquer erro que tenha aparecido, com o texto original.
```
