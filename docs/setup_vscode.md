# Como rodar no VS Code

Guia de execução do pipeline da Fase 2. Dois scripts, nesta ordem — o primeiro não precisa de nada instalado e prova que a lógica está certa antes de você tocar no SQL Server.

---

## 0 · Abrir a pasta certa

No VS Code: **Arquivo → Abrir Pasta** e selecione

```
C:\Users\lucas\Desktop\Xperiun\MBA\3- Data Challenge -
```

> ⚠️ O nome da pasta tem espaços e termina com hífen. Sempre que digitar esse caminho no terminal, **coloque entre aspas**. Abrindo a pasta como workspace, o VS Code cuida disso sozinho.

Extensão necessária: **Python** (`ms-python.python`). O `.vscode/` do projeto já traz `settings.json` e `launch.json` configurados.

---

## 1 · Criar o ambiente virtual

No terminal integrado (**Ctrl + `**), com PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Se o PowerShell bloquear o script de ativação:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
```

Ou, no terminal `cmd`, use `.\.venv\Scripts\activate.bat`.

Com o ambiente ativo o prompt mostra `(.venv)`. Depois disso, **Ctrl+Shift+P → Python: Select Interpreter** e escolha o `.venv` do projeto.

---

## 2 · Instalar as dependências

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Só há uma dependência real: `pyodbc`. O `validate_sqlite.py` roda com a biblioteca padrão.

---

## 3 · Validar a lógica antes de tocar no SQL Server

```powershell
python scripts\validate_sqlite.py
```

Este script executa as mesmas cinco análises contra o `farma_xperiun.db` que veio no material do desafio e confere os totais contra a documentação oficial. Saída esperada:

```
  [OK] transacoes       esperado=     85,407.00   obtido=     85,407.00
  [OK] receita_total    esperado=  2,313,807.90   obtido=  2,313,807.90
  [OK] lucro_total      esperado=    671,861.32   obtido=    671,861.32
  [OK] ticket_medio     esperado=         27.09   obtido=         27.09
  [OK] produtos         esperado=         33.00   obtido=         33.00
  [OK] fornecedores     esperado=          8.00   obtido=          8.00
  --------------------------------------------------------------------------
  TODOS OS TOTAIS RECONCILIAM.
```

Se isso passar, `docs/insights_iniciais.md` é gerado. **Se falhar aqui, não adianta ir para o SQL Server** — o problema está na query ou no arquivo do banco, não na conexão.

---

## 4 · Pré-requisitos do SQL Server

Antes de rodar o script oficial, três coisas precisam estar de pé:

**a) O serviço rodando.** No PowerShell:

```powershell
Get-Service | Where-Object { $_.Name -like "MSSQL*" }
```

**b) O driver ODBC instalado.** Verifique com:

```powershell
Get-OdbcDriver | Select-Object -ExpandProperty Name
```

Precisa aparecer `ODBC Driver 18 for SQL Server` (ou 17). Se não aparecer, baixe o *Microsoft ODBC Driver for SQL Server* no site da Microsoft e instale.

**c) O banco `farma_xperiun` restaurado**, com as tabelas no esquema `dbo`: `f_vendas`, `d_calendario`, `d_produto`, `d_fornecedor`, `d_turno`, `d_meta_mensal`.

---

## 5 · Executar contra o SQL Server

```powershell
python scripts\run_sql_server.py
```

Instância nomeada:

```powershell
python scripts\run_sql_server.py --server "localhost\SQLEXPRESS"
```

Autenticação SQL em vez de Windows:

```powershell
python scripts\run_sql_server.py --user sa --password "SuaSenha"
```

O script testa os drivers ODBC disponíveis em ordem de preferência e informa qual funcionou. Ao terminar, regrava `docs/insights_iniciais.md` com os resultados vindos do SQL Server.

---

## 6 · Rodar pelo painel de depuração

O `launch.json` já traz três configurações prontas. **Ctrl+Shift+D**, escolha no menu suspenso e **F5**:

| Configuração | O que faz |
|---|---|
| `1 · Validar lógica (SQLite — sem dependências)` | Roda o harness de validação |
| `2 · Executar no SQL Server (Windows Auth)` | Execução oficial |
| `3 · SQL Server — instância nomeada` | Igual, apontando para `localhost\SQLEXPRESS` |

---

## Problemas comuns

| Sintoma | Causa provável | Solução |
|---|---|---|
| `ModuleNotFoundError: No module named 'pyodbc'` | Ambiente virtual não ativado, ou interpretador errado selecionado no VS Code | Ative o `.venv` e refaça **Python: Select Interpreter** |
| `ERRO: nenhum driver ODBC encontrado` | Driver da Microsoft não instalado | Instale o *ODBC Driver 18 for SQL Server* |
| `Login failed for user` | Windows Auth sem permissão no banco | Conceda acesso ao seu usuário no SQL Server, ou use `--user` / `--password` |
| `SSL Provider: certificate chain... not trusted` | Driver 18 exige criptografia por padrão | Já tratado: a string de conexão manda `TrustServerCertificate=yes` e `Encrypt=no` |
| `Cannot open database "farma_xperiun"` | Banco não restaurado ou nome diferente | Confira no SSMS e passe `--database` se o nome divergir |
| `Invalid object name 'dbo.f_vendas'` | Tabelas em outro esquema | Ajuste o prefixo `dbo.` nas queries, ou mova as tabelas para `dbo` |
| Acentos quebrados no terminal | Console em code page antiga | `chcp 65001` antes de rodar. Os arquivos `.md` são gravados em UTF-8 e não são afetados |
| `ERRO: banco nao encontrado` no validate | Pasta aberta não é a raiz do projeto | Rode a partir da raiz, ou passe `--db "caminho\para\farma_xperiun.db"` |

---

## O que confirma que deu certo

`docs/insights_iniciais.md` regravado, com **cinco tabelas de resultados preenchidas** e nenhum bloco de erro. Os números precisam continuar batendo com o gabarito:

| Indicador | Valor |
|---|---|
| Transações | 85.407 |
| Receita líquida | R$ 2.313.807,90 |
| Lucro | R$ 671.861,32 |
| Ticket médio | R$ 27,09 |
| Meses com meta batida | 31 de 69 |

Se algum divergir entre o SQLite e o SQL Server, a carga do banco está diferente da base original — e é isso que precisa ser investigado, não as queries.
