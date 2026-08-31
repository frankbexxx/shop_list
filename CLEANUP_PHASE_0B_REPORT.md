# CLEANUP PHASE 0B REPORT

Limpeza estrutural da arquitectura Kivy. Sem commit. Sem refactor funcional.

## Before

| Campo | Valor |
| ----- | ----- |
| Branch | `master` (`master...origin/master`) |
| HEAD | `2348954 Add product roadmap todo document` |
| Ficheiros no disco (excl. `.git`) | 794 |

### Git status pré-limpeza (resumo)

O working tree **já tinha um índice muito sujo** antes da Fase 0B, herdado de `git add` anteriores (não da Fase 0A):

| Estado | Paths |
| ------ | ----- |
| `A` | `.gitignore`, PDF, `data/shopping_list.sqlite3`, centenas de ficheiros em `.ignore_archive_code/`, vários `__pycache__/*.pyc` |
| `AD` | `.ignore` (no índice, ausente no disco) |
| `M` | `main.py` (uma linha em branco extra no topo, staged) |
| `??` | `AUDIT_CLEANUP_REPORT.md` |

**Alterações de trabalho anteriores à Fase 0A que não são o relatório de auditoria — não foram descartadas:**

- `main.py` staged (`M`): newline inicial. **Não tocado.**
- `Lista de Compras Super Organizada.pdf` staged (`A`): **mantido no disco e no índice.**
- `.gitignore` já estava staged como ficheiro novo vs HEAD. O conteúdo foi **substituído de propósito** nesta fase (pedido explícito da 0B), não revertido para o original partido.

### Testes baseline

```text
Ran 7 tests in 0.108s
OK (skipped=3)
```

- 4 passam (`tests/test_app.py`)
- 3 skip (stubs Kivy em `tests/managers|models|services`)
- 0 failures / 0 errors

### Smoke test baseline (`127.0.0.1:8765`)

| Pedido | Resultado |
| ------ | --------- |
| `GET /api/health` | `200` `{"status": "ok"}` |
| `GET /` | `200` `text/html` (Market Flow) |

Processo do servidor encerrado a seguir (porta ficou só em `TIME_WAIT`).

---

## Removed

Contagem aproximada: **771 ficheiros** saíram do disco (794 → 23 antes de criar este relatório).

### Pastas removidas

```text
.ignore_archive_code/
api/
app/
config/
controllers/
core/
database/
features/
integration/
migrations/
models/
screens/
services/
state/
storage/
ui/
utils/
views/
tests/managers/
tests/models/
tests/services/
assets/fonts/
assets/icons/
assets/images/
```

Mais todas as `__pycache__/` encontradas (raiz, `supermarket_app/`, `tests/`, `assets/`, arquivo).

### Ficheiros / entradas removidos

```text
combined_files.txt
shopping_list.db          (0 bytes; não era a DB activa)
__init__.py               (raiz, vazio)
assets/__init__.py
assets/data/__init__.py
.ignore                   (órfão no índice Git; já não existia no disco)
```

Bytecode: `*.pyc` / `__pycache__`, incluindo o órfão `supermarket_app/__pycache__/schemas.cpython-313.pyc`.

`.ignore_archive_code/` estava staged como `A` mas **não fazia parte de HEAD**. Foi apagado do disco e saiu do índice; por isso não aparece como `D` no diff contra `2348954`. O histórico Git (`924d3e4`) continua a ter a árvore Kivy original.

### Git (índice vs HEAD)

`git diff --cached --stat`: **265 files changed, 22 insertions(+), 11662 deletions(-)**  
Inclui 262 deletions staged das pastas Kivy / testes / assets / dumps que **estavam em HEAD**.

---

## Preserved

Mantido de propósito:

```text
main.py
supermarket_app/          (os 7 módulos da app actual)
web/                      (index.html, app.js, styles.css)
assets/data/categories.json
assets/data/default_items.json
data/shopping_list.sqlite3   (no disco; agora gitignored)
tests/test_app.py
tests/__init__.py
docs/TODO.md
README.md
Dockerfile
render.yaml
Lista de Compras Super Organizada.pdf
AUDIT_CLEANUP_REPORT.md
.gitignore                (conteúdo novo)
```

Conteúdo dos dois JSON de seed: **inalterado**. Schema e dados da SQLite: **inalterados**. API e UI: **inalteradas**.

`assets/images/` foi apagado depois da verificação textual pedida. Não há referências a `logo.png`, `splash*.png` ou `placeholder.png` em `web/`, `supermarket_app/`, `README.md`, `Dockerfile` ou `render.yaml`. `docs/TODO.md` menciona «Preparar splash» como ideia futura de Play Store, não como path de ficheiro — não justifica reter os PNG Kivy.

---

## Gitignore

Ficheiro reescrito. Removidos `pycache/` (incorrecto) e `opcional`. **Não** se adicionou `*.pdf`.

Conteúdo actual:

```gitignore
__pycache__/
*.py[cod]
*.pyo
*.pyd

.venv/
venv/
env/

.env
.env.*

*.log

.ignore_archive_code/

data/*.sqlite3
data/*.sqlite
data/*.db

combined_files.txt
```

### DB activa no Git

| | |
| --- | --- |
| Disco | `data/shopping_list.sqlite3` presente, 32768 bytes |
| Índice | `git rm --cached` — **já não tracked** |
| Ignore | `.gitignore:17:data/*.sqlite3` confirma `git check-ignore -v` |

Não foi apagada, não foi recriada, schema intacto.

---

## Validation

### Testes depois da limpeza

```text
Ran 4 tests in 0.108s
OK
```

- 4 passam (`test_app.py`)
- 0 skips (os stubs Kivy já não existem)
- 0 failures / 0 errors

### Smoke test (`127.0.0.1:8766`)

| Pedido | HTTP | Notas |
| ------ | ---- | ----- |
| `GET /api/health` | 200 | `{"status": "ok"}` |
| `GET /` | 200 | HTML Market Flow |
| `GET /api/dashboard` | 200 | 1 lista, 12 sugestões, `active_list_id=1` |
| `GET /api/lists` | 200 | 1 lista (`Weekly Essentials`) |

Servidor encerrado a seguir. Sem processos órfãos (só `TIME_WAIT`).

### Imports partidos

Pesquisa no código sobrevivente por `kivy` e imports das pastas raiz removidas.

Único hit: `docs/TODO.md` linha 25 — menção histórica («Testes legacy de Kivy…»). Não é import.

`supermarket_app.services` e `supermarket_app.database` mantêm-se; não colidem com as pastas raiz apagadas.

`web/app.js` continua a chamar só as rotas `/api/*` da app actual.

---

## Final tree

```text
shopping_list/
├── .gitignore
├── AUDIT_CLEANUP_REPORT.md
├── CLEANUP_PHASE_0B_REPORT.md
├── Dockerfile
├── Lista de Compras Super Organizada.pdf
├── README.md
├── main.py
├── render.yaml
├── assets/
│   └── data/
│       ├── categories.json
│       └── default_items.json
├── data/
│   └── shopping_list.sqlite3       # local / ignored
├── docs/
│   └── TODO.md
├── supermarket_app/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── seed.py
│   ├── server.py
│   ├── services.py
│   └── web.py
├── tests/
│   ├── __init__.py
│   └── test_app.py
└── web/
    ├── app.js
    ├── index.html
    └── styles.css
```

23 ficheiros de projecto no disco após limpeza (este relatório é o 24.º). `__pycache__` gerado pelos testes foi apagado outra vez; o `.gitignore` impede que volte a ser commitado.

---

## Git diff/status

**Não foi criado commit.**

### `git status -sb` (resumo)

```text
## master...origin/master
A  .gitignore
A  "Lista de Compras Super Organizada.pdf"
M  main.py
D  <262 paths Kivy / dumps / testes legacy / fonts / icons / images>
?? AUDIT_CLEANUP_REPORT.md
```

Mais este ficheiro, `CLEANUP_PHASE_0B_REPORT.md`, ficará untracked até um `git add` futuro.

Contagens do índice:

| | |
| --- | --- |
| `D` staged | 262 |
| `A` staged | 2 (`.gitignore`, PDF) |
| `M` staged | 1 (`main.py`) |
| `??` | `AUDIT_CLEANUP_REPORT.md` |

### `git diff --stat` (unstaged)

Vazio. Toda a limpeza está no **index** (`git add -u` + `git rm --cached`).

### `git diff --cached --stat`

```text
265 files changed, 22 insertions(+), 11662 deletions(-)
```

(O `+22` é o novo `.gitignore`.)

### `git diff -- .gitignore` (unstaged)

Vazio (já staged).

### `git diff --cached -- .gitignore`

HEAD **não tinha** `.gitignore` commitado; aparece como ficheiro novo com o conteúdo da secção Gitignore acima.

---

## Problems

- **Índice pré-existente:** a branch já tinha centenas de `git add` por commitar (arquivo, pyc, PDF, sqlite). A limpeza trabalhou por cima disso em vez de fazer reset. Nada desse trabalho alheio à 0B foi revertido, excepto o que a própria 0B pedia (untrack da sqlite, apagar arquivo, reescrever `.gitignore`).
- **`main.py` continua com um newline extra staged** — alteração anterior, deixada intacta.
- **PDF continua `A` no índice** — nunca esteve em HEAD; permanece staged porque a 0B o mantém no repo. Não foi introduzido agora.
- **`.ignore_archive_code/` não aparece como `D` vs HEAD** porque nunca esteve em HEAD, só no índice. Foi apagado do disco e do index.
- **Stdout do servidor** (`Shopping list app running at …`) não apareceu nos logs do processo em background (buffering do Python quando não há TTY). Os GETs HTTP responderam 200 na mesma.
- **Nenhuma excepção de `assets/images/`:** pasta removida na íntegra.
