# AUDIT CLEANUP REPORT — Fase 0A

Data da auditoria: 2026-08-31  
Project root: `E:\APPSHOPLIST\shopping_list`  
Regra desta fase: análise apenas. Nenhum ficheiro foi apagado, movido, renomeado ou refatorado (excepto a criação deste relatório).

Critério de classificação:

- **KEEP** — usado pelo runtime actual, pelos testes actuais, ou documentação/deploy da stack actual.
- **REVIEW** — sem evidência suficiente, ou valor possível fora do runtime (branding, dados, docs).
- **PROBABLE DELETE** — código claramente da arquitectura anterior; não há import a partir do entrypoint actual; remoção deve ser validada.
- **SAFE DELETE** — artefacto gerado, dump, cache, ou cópia sem função de runtime.
- **ARCHIVE / NON-RUNTIME** — código antigo guardado de propósito; não entra no arranque.

Uma referência só conta como **runtime dependency** se for alcançável a partir de `main.py` → `supermarket_app.server`. Imports feitos apenas por módulos Kivy, pelo arquivo, ou por testes já marcados como legacy **não** tornam o destino activo.

---

## A. Runtime actual

A aplicação que realmente arranca é **Market Flow**: um servidor HTTP WSGI em Python stdlib, com frontend estático e SQLite.

### Como arranca

`main.py` não contém lógica de produto. Apenas importa e executa `supermarket_app.server.main`.

```python
from supermarket_app.server import main

if __name__ == "__main__":
    raise SystemExit(main())
```

`supermarket_app.server.main()`:

1. Lê `--host`, `--port`, `--db`, `--no-browser`.
2. Instancia `ShoppingApplication`.
3. Serve forever com `wsgiref.simple_server.make_server`.
4. Opcionalmente abre o browser em `http://{host}:{port}`.

Defaults (`supermarket_app/config.py`):

| Constante | Valor |
| --------- | ----- |
| `DEFAULT_HOST` | `127.0.0.1` |
| `DEFAULT_PORT` | `8000` |
| `STATIC_DIR` | `{repo}/web` |
| `DEFAULT_DB_PATH` | `{repo}/data/shopping_list.sqlite3` |
| `BASE_DIR` | raiz do repositório |

Docker/Render usam o mesmo entrypoint: `python main.py --host 0.0.0.0 --port 8000 --no-browser`.

### O que a app carrega

`ShoppingApplication`:

- `supermarket_app.database.Database` — SQLite em `data/shopping_list.sqlite3` (cria a pasta se faltar).
- `supermarket_app.services.ShoppingService` — domínio: listas, itens, duplicar, ciclar estado, sugestões, orçamento.
- `supermarket_app.seed.load_seed_data` — lê JSON em `assets/data/` e mistura com constantes internas.
- `supermarket_app.web.serve_static` — serve `web/index.html`, `web/styles.css`, `web/app.js` sob `/` e `/static/`.

Não há FastAPI, Flask, Django, nem Kivy neste caminho. Não há `requirements.txt`: a stack actual usa só biblioteca padrão (`wsgiref`, `sqlite3`, `argparse`, `json`, `pathlib`, `webbrowser`, `mimetypes`, `urllib.parse`).

### Schema SQLite activo

Confirmado em `data/shopping_list.sqlite3` (32768 bytes, já inicializada):

| Tabela | Linhas observadas | Função |
| ------ | ----------------- | ------ |
| `shopping_lists` | 1 | listas (nome, loja, orçamento, notas, estado) |
| `shopping_items` | 5 | itens da lista |
| `item_templates` | 171 | sugestões / frequência de uso |

Isto corresponde ao `CREATE TABLE` em `supermarket_app/database.py`. **Não** corresponde ao schema legado `users` / `lists` / `items` de `database/` e `migrations/`.

### Caminhos reais em runtime

| Caminho | Uso |
| ------- | --- |
| `main.py` | entrypoint |
| `supermarket_app/*.py` | servidor, serviço, DB, seed, HTTP helpers |
| `web/index.html` | UI |
| `web/styles.css` | estilos |
| `web/app.js` | cliente da API |
| `data/shopping_list.sqlite3` | persistência |
| `assets/data/categories.json` | lido no bootstrap (ver nota abaixo) |
| `assets/data/default_items.json` | lido no bootstrap e fundido nas templates |

**Nota sobre seed:** `load_seed_data()` devolve `(categories, templates)`, mas `ShoppingService.bootstrap()` **não usa** o argumento `categories`. Só insere `item_templates` e, se a lista default estiver vazia, os primeiros templates. O JSON de categorias é lido, mas não alimenta nenhuma tabela. Continua a ser um ficheiro de runtime (é aberto), não um módulo importado.

### O que o runtime **não** carrega

Confirmado por leitura de todos os `import` em `supermarket_app/`: zero imports de `api`, `app`, `controllers`, `core`, `database`, `features`, `integration`, `models`, `screens`, `services` (o pacote raiz), `state`, `storage`, `ui`, `utils`, `views`, `config/` (JSON), ou `migrations/`.

Os únicos consumidores de `supermarket_app` no repositório são:

- `main.py` — **runtime dependency**
- `tests/test_app.py` — **test dependency da stack actual**

---

## B. Dependency map

Árvore confirmada no código. Nenhuma aresta inventada.

```text
main.py
└── supermarket_app.server.main
    ├── argparse / wsgiref.simple_server / webbrowser   (stdlib)
    ├── supermarket_app.config
    │   ├── BASE_DIR            → raiz do repo
    │   ├── DATA_DIR            → ./data
    │   ├── STATIC_DIR          → ./web
    │   └── DEFAULT_DB_PATH     → ./data/shopping_list.sqlite3
    ├── supermarket_app.database.Database
    │   └── sqlite3             → data/shopping_list.sqlite3
    ├── supermarket_app.seed.load_seed_data
    │   ├── constantes internas (DEFAULT_CATEGORIES, DEFAULT_TEMPLATES)
    │   ├── assets/data/categories.json
    │   └── assets/data/default_items.json
    ├── supermarket_app.services.ShoppingService
    │   └── supermarket_app.database.Database
    └── supermarket_app.web
        ├── JSON helpers (parse body, query, path)
        └── serve_static
            └── web/index.html
            └── web/styles.css
            └── web/app.js

tests/test_app.py
└── supermarket_app.server.ShoppingApplication
    └── (mesmo grafo, com DB temporária em data/test-*.sqlite3)
```

Rotas HTTP reais (`supermarket_app/server.py`):

```text
GET  /
GET  /static/*
GET  /api/health
GET  /api/dashboard
GET  /api/lists
POST /api/lists
GET  /api/suggestions
GET|PATCH|DELETE /api/lists/{id}
POST /api/lists/{id}/duplicate
POST /api/lists/{id}/items
PATCH|DELETE /api/items/{id}
POST /api/items/{id}/cycle
```

O frontend (`web/app.js`) fala só com estas rotas via `fetch`.

---

## C. Directory classification

Contagens de `.py` (excluindo `__pycache__`) nas pastas Kivy: cerca de **223 ficheiros Python** vs **7** em `supermarket_app/` + `main.py`.

| Path | Estado | Runtime? | Motivo |
| ---- | ------ | -------- | ------ |
| `supermarket_app/` | KEEP | Sim | Pacote da app actual. Servidor WSGI, serviço, schema SQLite, seed. |
| `web/` | KEEP | Sim | Frontend servido por `STATIC_DIR`. Único UI activo. |
| `data/` | KEEP | Sim | Directório da DB actual. Criado em runtime se faltar. |
| `assets/data/` | KEEP | Sim (leitura) | `seed.py` abre `categories.json` e `default_items.json`. |
| `assets/images/` | PROBABLE DELETE | Não | PNGs de logo/splash da era Kivy/Android. `web/` e `supermarket_app/` não referenciam nenhum. |
| `assets/fonts/` | PROBABLE DELETE | Não | TTF Roboto; só fariam sentido numa UI Kivy. Sem referência no frontend actual. |
| `assets/icons/` | PROBABLE DELETE | Não | Ícones PNG (`add`, `home`, `list`, …). Sem referência em `web/` ou no servidor. |
| `assets/__init__.py` e `__pycache__` | SAFE DELETE | Não | Pacote vazio + bytecode. O seed usa paths de ficheiro, não o pacote Python. |
| `tests/test_app.py` | KEEP | Testes actuais | Única suíte que exercita `ShoppingApplication`. |
| `tests/managers/`, `tests/models/`, `tests/services/` | PROBABLE DELETE | Não | Stubs `@unittest.skip` da suíte Kivy. Não importam código de produto. |
| `docs/` | KEEP | Não (docs) | Só `TODO.md`; descreve a stack actual e o roadmap. |
| `api/` | PROBABLE DELETE | Não | Cliente Kivy `UrlRequest` para `https://api.shoppinglist.com/v1`. Sem consumidor no runtime. |
| `app/` | PROBABLE DELETE | Não | Antigo `kivy.app.App` (`ShoppingApp`). Era o entrypoint no dump antigo; `main.py` já não o importa. |
| `config/` | PROBABLE DELETE | Não | JSON de rotas/tema/settings da app Kivy (`Shopping List Pro`). O runtime usa `supermarket_app/config.py`. |
| `controllers/` | PROBABLE DELETE | Não | Controllers Kivy. Sem import a partir de `supermarket_app`. |
| `core/` | PROBABLE DELETE | Não | App/cache/logger/settings managers Kivy. |
| `database/` | PROBABLE DELETE | Não | Camada SQLite Kivy apontando a `shopping_list.db`. Schema `users`/`lists` diferente do actual. |
| `features/` | PROBABLE DELETE | Não | Features Kivy (listas, itens, categorias). |
| `integration/` | PROBABLE DELETE | Não | Binding, sync, animações Kivy. |
| `migrations/` | PROBABLE DELETE | Não | Migrações `users`/`lists`/`items`. Schema incompatível com `shopping_lists`/`shopping_items`. |
| `models/` | PROBABLE DELETE | Não | Dois conjuntos de modelos Kivy no mesmo pacote (`item.py` e `item_model.py`). Não usados pelo serviço actual. |
| `screens/` | PROBABLE DELETE | Não | Screens MVC Kivy (`main`, `shopping_list`, `categories`, `settings`). |
| `services/` | PROBABLE DELETE | Não | Auth/sync/analytics/notification Kivy. Distinto de `supermarket_app/services.py`. |
| `state/` | PROBABLE DELETE | Não | Store/observer/dispatcher Kivy. |
| `storage/` | PROBABLE DELETE | Não | `JsonStore` Kivy (`shopping_list_data.json`). Persistência concorrente abandonada. |
| `ui/` | PROBABLE DELETE | Não | Kit de widgets/estilos Kivy. |
| `utils/` | PROBABLE DELETE | Não | Helpers Kivy + `AppConstants`. Nenhum import desde o runtime. |
| `views/` | PROBABLE DELETE | Não | Maior pasta morta (~71 `.py`): screens, widgets, navigation Kivy. Segunda UI completa, paralela a `screens/` e a `web/`. |
| `.ignore_archive_code/` | ARCHIVE / NON-RUNTIME | Não | Cópia local da árvore Kivy + dumps. Gitignore declara a pasta, mas os ficheiros **já estão tracked**. |
| `__pycache__/` (raiz e subpastas) | SAFE DELETE | Não | Bytecode. `.gitignore` actual (`pycache/` sem underscores) **não** ignora `__pycache__/`. |

---

## D. Suspected legacy architecture

Há **duas aplicações no mesmo repositório**, e vestígios de uma terceira camada de modelos. O rebuild em `4ed420e` (*Rebuild app as deployable supermarket shopping list*) **adicionou** `supermarket_app/` + `web/` e **não removeu** a árvore Kivy.

### 1. Actual — Market Flow (web + WSGI)

- Entrada: `main.py` → `supermarket_app.server`
- UI: `web/`
- Dados: `data/shopping_list.sqlite3`
- Testes: `tests/test_app.py`
- Commit: `4ed420e` (2026-04-30)

Documentado em `README.md` e `docs/TODO.md`. `docs/TODO.md` afirma explicitamente: «Refatoração total da base anterior para uma app web funcional» e «Testes legacy de Kivy retirados de circulação».

### 2. Anterior — app Kivy (completamente abandonada no runtime)

Era o entrypoint antigo, ainda visível no dump `combined_files.txt`:

```text
import kivy
kivy.require('2.1.0')
from app.shopping_app import ShoppingApp
...
shopping_app.run()
```

Essa árvore continua na raiz: `app/`, `screens/`, `views/`, `ui/`, `controllers/`, `core/`, `database/`, `models/`, `features/`, `integration/`, `state/`, `storage/`, `services/`, `api/`, `utils/`, `config/`.

Quase todos esses ficheiros começam com `from kivy...`. Não há `kivy` no caminho de execução actual. Não há `requirements.txt` a instalá-lo.

Dentro da própria era Kivy já havia **sobreposição interna**:

| Camada | Pasta A | Pasta B | Observação |
| ------ | ------- | ------- | ---------- |
| UI screens | `screens/` (MVC: screen/view/controller) | `views/screens/` + `views/widgets/` | Dois `MainScreen`, duas navegações. |
| Modelos | `models/item.py` (classe `Item`) | `models/item_model.py` (Kivy Property) | Dois modelos de item no mesmo pacote. |
| Modelos + DB | `models/` | `database/models/` | Terceiro `ItemModel` / `BaseModel`. |
| Persistência | `database/` → `shopping_list.db` | `storage/` → `JsonStore` | Dois backends. |
| Config | `config/*.json` | `app/config.py` + `app/app_config.py` + `utils/config.py` | Quatro sítios. |

Isto não é reutilização parcial pela app actual. É código morto que se importa **entre si**. Cadeias Kivy → Kivy não contam como runtime.

### 3. Arquivo local incompleto (2026-04-30)

`.ignore_archive_code/phase-2-legacy-python/README.md` diz que essas pastas foram «removed from the active application tree». **Não foram.** Os originais continuam na raiz, com o mesmo conteúdo (hashes SHA256 iguais em amostras: `app/shopping_app.py`, `views/main_view.py`, `database/db_config.py`).

`.ignore_archive_code/support-review-legacy-files/README.md` diz que `combined_files.txt`, `shopping_list.db`, `migrations/` e os testes legacy foram removidos da árvore activa. **Também não foram.** Continuam na raiz.

Conclusão: houve uma tentativa de limpeza que copiou para `.ignore_archive_code/` e parou antes de apagar os originais.

### 4. Referência inexistente

O README do arquivo aponta para `docs/refactor-plan.md`. Esse ficheiro **não existe**. Só existe `docs/TODO.md`.

### 5. Bytecode órfão

`supermarket_app/__pycache__/schemas.cpython-313.pyc` existe, mas **não há** `supermarket_app/schemas.py` nem qualquer import `schemas` no código-fonte. Vestígio de um módulo já apagado.

---

## E. Duplicações

### Persistência (3 sistemas)

| Sistema | Path | Schema / store | Estado |
| ------- | ---- | -------------- | ------ |
| Actual | `supermarket_app/database.py` + `data/shopping_list.sqlite3` | `shopping_lists`, `shopping_items`, `item_templates` | **activo** |
| Legado SQLite Kivy | `database/` + `shopping_list.db` | `users`, `lists` (e migrações `items`) | abandonado; o `.db` da raiz tem **0 bytes** |
| Legado JSON Kivy | `storage/local_storage.py` | `shopping_list_data.json` | abandonado; o JSON nem está na raiz |

### Modelos de domínio (3 famílias)

| Família | Exemplos | Usado por |
| ------- | -------- | --------- |
| Dicts + SQL | `supermarket_app/services.py` (`ListPayload`, `ItemPayload`) | runtime |
| `models/item.py`, `models/shopping_list.py`, `models/user.py` | classes Python simples sobre `BaseModel` Kivy | ninguém no runtime |
| `models/*_model.py` e `database/models/*_model.py` | Kivy Properties | ninguém no runtime |

### UI (3 famílias)

| Família | Path | Tecnologia | Estado |
| ------- | ---- | ---------- | ------ |
| Actual | `web/` | HTML/CSS/JS | **activo** |
| Screens MVC | `screens/` | Kivy Screen | abandonado |
| Views + widgets | `views/` (~71 ficheiros) | Kivy widgets | abandonado |
| Design system | `ui/` | Kivy buttons/modals/layouts | abandonado |

`screens/` e `views/screens/` duplicam ecrãs (`main`, `settings`, `shopping_list`, `categories`, etc.).

### Serviços / API (2 famílias)

| Actual | Legado |
| ------ | ------ |
| Rotas em `supermarket_app/server.py` | `api/client.py` + `api/endpoints/*` contra um host fictício |
| `supermarket_app/services.py` | `services/data_service.py`, `sync_service.py`, `auth_service.py`, … |

### Configuração (várias)

- `supermarket_app/config.py` — **activa**
- `config/settings.json`, `routes.json`, `theme.json` — Kivy «Shopping List Pro»
- `app/config.py`, `app/app_config.py`, `utils/config.py`

### Bases de dados em disco (2 ficheiros)

| Ficheiro | Tamanho | Uso |
| -------- | ------- | --- |
| `data/shopping_list.sqlite3` | 32768 bytes | **DB activa** |
| `shopping_list.db` (raiz) | 0 bytes | placeholder legado; `database/db_config.py` e `database/managers/sqlite_manager.py` ainda apontam para este nome, mas esses módulos não correm |

### Código vs arquivo

A pasta `.ignore_archive_code/phase-2-legacy-python/` é um **clone** das pastas Kivy da raiz. Duplicação byte-a-byte nas amostras verificadas. O dump `combined_files.txt` existe **duas vezes** (raiz e arquivo), hash idêntico.

---

## F. Root files

| Ficheiro | Classificação | Notas |
| -------- | ------------- | ----- |
| `main.py` | **Runtime** KEEP | 5 linhas. Único entrypoint. |
| `README.md` | **Documentação** KEEP | Documenta `python main.py` e a stack actual. |
| `Dockerfile` | **Deploy** KEEP | `CMD python main.py --host 0.0.0.0 --port 8000 --no-browser`. Mesma app. `COPY . .` copia também todo o legado (imagem inchada, não é outro entrypoint). |
| `render.yaml` | **Deploy** KEEP | Serviço Docker `market-flow`. Sem `startCommand`; usa o `CMD` do Dockerfile. Mesma app. |
| `.gitignore` | **Repo** KEEP | Ver secção H/Git. Precisa de correcção futura (`__pycache__/`, sqlite, PDF já tracked). |
| `__init__.py` | **Provavelmente eliminável** SAFE DELETE | Ficheiro vazio na raiz, 0 bytes, de 2024. Não torna o repo um pacote usado pelo runtime. |
| `combined_files.txt` | **Dump/agregação temporária** SAFE DELETE | 179 555 bytes. Cabeçalho `## Caminho: ./main.py` com o **main.py Kivy antigo**, não o actual. Cópia idêntica no arquivo. |
| `shopping_list.db` | **Artefacto vazio legado** SAFE DELETE | 0 bytes. Não é a DB do runtime. Criada/referenciada só pelo código Kivy. A DB activa é criada em `data/` por `Database.__init__`. Apagar este ficheiro **não** impede o arranque actual. |
| `Lista de Compras Super Organizada.pdf` | **Referência / documentação** KEEP (não apagar nesta fase) | 271 586 bytes, data 2017-03-09. Não é lido pelo código. `.gitignore` tem `*.pdf`, mas o ficheiro **já está tracked**. |
| `.ignore` | **Índice git órfão** SAFE DELETE (já ausente no disco) | `git status` mostra `AD .ignore`: adicionado ao index e apagado do working tree. Não existe no filesystem. |

`docs/TODO.md` (não está na raiz, mas é o único doc de produto): KEEP.

---

## G. Tests

Comando documentado: `python -m unittest discover -s tests -v`.

| Ficheiro | Arquitectura | Tipo de dependência |
| -------- | ------------ | ------------------- |
| `tests/test_app.py` | Market Flow actual | **runtime/test dependency** — importa `ShoppingApplication`, faz pedidos WSGI a `/api/dashboard`, `/`, CRUD de listas/itens, ciclo de estado. |
| `tests/services/test_services.py` | Kivy, retirada | **dead** — classe skipped; `assertTrue(True)`; **não importa** `services/`. |
| `tests/models/test_models.py` | Kivy, retirada | **dead** — idem; **não importa** `models/`. |
| `tests/managers/test_managers.py` | Kivy, retirada | **dead** — idem; **não importa** managers. |
| `tests/__init__.py` | vazio | irrelevante |

### Distinção pedida

| Módulo | Runtime dependency | Test-only dependency | Dead dependency |
| ------ | ------------------ | -------------------- | --------------- |
| `supermarket_app/*` | sim (`main.py`) | também testado por `test_app.py` | não |
| `web/*` | sim (ficheiros estáticos) | `test_app.py` verifica que `/` contém `Market Flow` | não |
| `assets/data/*.json` | sim (leitura no seed) | indirecta via bootstrap do teste | não |
| `app/`, `views/`, `screens/`, `database/`, … | não | **não** (os testes legacy já não os importam) | **sim** |
| Stubs em `tests/models|services|managers` | não | placeholders skipped | dead test files |

Ponto importante: **os testes antigos já não são a única coisa a importar módulos legacy**, porque deixaram de os importar. Os módulos Kivy estão mortos mesmo sem a suíte antiga. Remover os stubs skipped não “desenterra” Kivy; apenas limpa ruído no `discover`.

---

## H. Candidate deletions

### SAFE DELETE

Risco de runtime praticamente zero. Nenhum destes caminhos é importado ou aberto por `supermarket_app`.

- Todas as pastas `__pycache__/` (raiz, `supermarket_app/`, `tests/`, `assets/`, árvore Kivy, arquivo). Inclui o órfão `supermarket_app/__pycache__/schemas.cpython-313.pyc`.
- `combined_files.txt` na raiz (dump; duplicado no arquivo).
- `shopping_list.db` na raiz (0 bytes, schema legado, path não usado pelo config actual).
- `__init__.py` vazio na raiz.
- `.ignore` no índice git (já não existe no disco).
- `.ignore_archive_code/` **como working copy** — é arquivo local + `__pycache__` + duplicado da árvore Kivy que ainda está na raiz. O histórico Git (`924d3e4`) já contém essa versão. `.gitignore` já tenta ignorar a pasta, mas os ficheiros foram commitados na mesma: 486 paths tracked só nesta pasta, muitos `.pyc`.

Não classificar como SAFE DELETE: `assets/data/*.json`, `data/shopping_list.sqlite3`, o PDF.

### PROBABLE DELETE

Código da app Kivy, ainda na raiz, sem qualquer aresta desde `main.py`. Remoção deve ser validada com um arranque + `python -m unittest discover -s tests -v` depois de apagar.

Pastas inteiras:

```text
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
```

Também:

- `tests/managers/`, `tests/models/`, `tests/services/` (stubs skipped)
- `assets/fonts/`, `assets/icons/`, `assets/images/` (binários da UI Kivy / splash; `web/` não os usa)
- `assets/__init__.py` e os `__init__.py` vazios em `assets/fonts|icons|images|data` (o JSON pode ficar sem ser um pacote Python)

Estimativa: ~223 ficheiros `.py` mortos na raiz, mais widgets, JSON de tema Kivy, e vários MB de splash (`splash.png` ~2.5 MB, `splash2.png` ~3.1 MB, etc.).

### REVIEW

Não há evidência de uso no runtime, mas há motivo para não apagar no piloto automático:

| Item | Porquê REVIEW |
| ---- | ------------- |
| `Lista de Compras Super Organizada.pdf` | Referência de produto de 2017. Fora do runtime; o utilizador pediu para não apagar. |
| `docs/TODO.md` | Roadmap da stack actual. Manter. |
| `data/shopping_list.sqlite3` | **É a DB activa.** Não apagar. Decisão de git: está tracked e contém dados de bootstrap/uso local (1 lista, 5 itens, 171 templates). Candidato a passar a gitignore, não a delete. |
| `assets/data/categories.json` | É lido, mas o conteúdo **não é persistido**. Pode-se mais tarde deixar de o ler; isso já seria refactor. |
| `assets/images/` (logo/splash) | Sem referência no web actual; `docs/TODO.md` menciona PWA/Play Store e splash. Valor de branding incerto. |
| `Dockerfile` / `render.yaml` | São da stack actual, mas `COPY . .` arrasta o legado. Limpar o contexto Docker é consequência da limpeza, não um delete isolado. |
| `.gitignore` | Manter o ficheiro; corrigir padrões numa fase posterior (`__pycache__/`, `*.sqlite3`, deixar de trackar PDF/arquivo). |

---

## I. Minimal surviving project

Árvore conceptual **depois de remover apenas o comprovadamente morto** (SAFE DELETE + PROBABLE DELETE da secção H). **Não foi feita esta remoção.**

```text
shopping_list/
├── .gitignore
├── Dockerfile
├── README.md
├── render.yaml
├── main.py
├── AUDIT_CLEANUP_REPORT.md          # este relatório (fase 0A)
├── Lista de Compras Super Organizada.pdf   # referência; fora do runtime
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
├── web/
│   ├── index.html
│   ├── app.js
│   └── styles.css
├── assets/
│   └── data/
│       ├── categories.json
│       └── default_items.json
├── data/
│   └── shopping_list.sqlite3        # gerada em runtime; preferível gitignore
└── tests/
    ├── __init__.py                  # opcional
    └── test_app.py
```

O que desapareceria desta vista: toda a árvore Kivy da raiz, `.ignore_archive_code/`, `combined_files.txt`, `shopping_list.db`, caches, stubs de testes legacy, e (se se confirmar PROBABLE DELETE) fontes/ícones/splashes em `assets/`.

Deploy continuaria igual: `python main.py` localmente; Docker/Render com o mesmo `CMD`.

---

## Git / Deploy (secção 8)

### Histórico relevante

| Commit | Mensagem | Efeito |
| ------ | -------- | ------ |
| `924d3e4` | Primeiro commit: Estrutura inicial do projeto | Árvore Kivy |
| `4ed420e` | Rebuild app as deployable supermarket shopping list | Acrescenta `supermarket_app/`, `web/`, Docker, README, `tests/test_app.py`; transforma testes Kivy em skip. **Não apaga** Kivy. |
| `2348954` | Add product roadmap todo document | `docs/TODO.md` |

### `.gitignore` (conteúdo actual)

```
pycache/
*.pyc
*.pyo
*.pyd
.venv/
env/
venv/
.env
*.log
.ignore_archive_code/
opcional
*.pdf
```

Problemas confirmados:

1. `pycache/` **não** corresponde a `__pycache__/`. Há `__pycache__` tracked na raiz, `assets/`, `supermarket_app/`, `tests/` e em todo o arquivo.
2. `.ignore_archive_code/` está no gitignore, mas **486 ficheiros** dessa pasta estão tracked (gitignore não destarckea o que já foi commitado).
3. `*.pdf` está no gitignore, mas o PDF está tracked.
4. Linha `opcional` não ignora nada de útil.
5. `data/*.sqlite3` **não** está ignorado; a DB de runtime está no Git.
6. Não há regra para `combined_files.txt`.

### Docker vs `main.py`

São a mesma aplicação. O Dockerfile não instala dependências (correcto: só stdlib). O problema é o contexto: `COPY . .` inclui centenas de ficheiros Kivy, o arquivo, dumps e `__pycache__`.

### Render vs `main.py`

`render.yaml` define um serviço web Docker chamado `market-flow`, plano free, `autoDeploy: true`. Sem comando extra → usa o `CMD` do Dockerfile → `main.py`. Mesma app.

Não há segundo servidor escondido no deploy.

---

## Síntese

A aplicação executada hoje é pequena e coerente: `main.py` → `supermarket_app` → `web/` + `data/shopping_list.sqlite3` + dois JSON de seed.

O restante da raiz é, com evidência de imports e de hashes, a app Kivy de `924d3e4`, ainda presente porque o rebuild não a removeu, e de novo copiada para `.ignore_archive_code/` numa limpeza que não chegou a apagar os originais.

Próximo passo (fase posterior, não esta): apagar primeiro o conjunto SAFE DELETE, correr `python main.py` e `python -m unittest discover -s tests -v`, depois o conjunto PROBABLE DELETE com a mesma verificação.
