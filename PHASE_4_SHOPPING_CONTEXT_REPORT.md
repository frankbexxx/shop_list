# PHASE 4 — COMPRAR HOJE LIGADO A UM LOCAL

Contexto opcional na compra actual. Sem commit. Sem preços, filiais ou GPS.

HEAD de partida: `2032ce9` — `feat: add shopping location contexts`

---

## Schema

`shopping_lists` passa a ter:

| Coluna | Papel |
| ------ | ----- |
| `commerce_type_id` | opcional; tipo da compra |
| `store_id` | opcional; marca/cadeia |

Colunas adicionadas com `_ensure_column` (INTEGER, NULL). Listas existentes ficam `NULL`/`NULL`.

Não há FK física no `ALTER TABLE` (SQLite). A coerência é validada no serviço.

Se existir `store_id`, o tipo efectivo é o da store e é gravado em `commerce_type_id`.

---

## API

`POST /api/lists`, `PATCH /api/lists/{id}`, `GET /api/lists`, `GET /api/lists/{id}` e `GET /api/dashboard` incluem:

```text
commerce_type_id
store_id
commerce_type_name
location_store_name
location_label    → "Continente · Supermercado" | "Bricolage" | "Todos os locais"
location_short    → "Continente" | "Bricolage" | "Todos"
```

Payloads antigos (só `name` / `store_name` / `budget`) continuam válidos.

### Validação

- Store tem de existir e estar activa.
- Commerce type tem de existir e estar activo.
- Se `store_id` e `commerce_type_id` vêm os dois: o tipo tem de ser o da store. `Worten` + `Supermercado` → 400.
- Só `store_id`: o tipo é derivado da store (mudar Continente → Leroy não exige enviar o tipo).
- `null` limpa o contexto.

`POST /api/lists/{id}/duplicate` copia `commerce_type_id` e `store_id`.

Dashboard `today` inclui o mesmo contexto da lista activa.

---

## Comprar Hoje

Header:

```text
Comprar Hoje
Continente · Supermercado
```

ou `Bricolage` ou `Todos os locais`.

Acções:

- **Alterar local** — dialog com Todos, tipos e lojas (hub-cards / list-cards).
- **Adicionar da Lista Geral** — abre o catálogo no contexto da compra.

Formulário de nova lista: tipo e loja opcionais. Escolher loja assume o tipo.

Cards de listas mostram `Continente` / `Bricolage` / `Todos`.

Itens fora do contexto actual: nota discreta `Fora do contexto`. Não se removem.

---

## Lista Geral contextual

A partir de Hoje, a Lista Geral herda Store ou Commerce Type.

**Mostrar todos** no chip: vê o catálogo completo sem perder o contexto da compra (aprendizagem continua a usar a lista). É possível voltar ao filtro.

Marcações da Fase 2 (seleccionado / não seleccionado) mantêm-se.

---

## Learning

Ao criar ou adicionar um produto a uma lista com contexto:

| Compra | Efeito |
| ------ | ------ |
| Store (ex. Leroy Merlin) | Product ↔ tipo da store + Product ↔ store |
| Só Commerce Type | Product ↔ tipo; sem store |
| Todos os locais | nenhuma associação comercial |

`INSERT OR IGNORE`. Sem clones. `product_id` único.

---

## Product uniqueness

`Pilhas AA` em lista Continente e lista Worten: 1 row em `products`, só ganha relações. Coberto por teste.

---

## Duplicate list

O clone recebe o mesmo `commerce_type_id` / `store_id` e os mesmos itens (quantidades/estados como antes).

---

## Migration

Listas pré-Fase 4: contexto `NULL`. `_ensure_column` é idempotente. Bootstrap ×3 não altera relações nem inventa contexto.

---

## Tests

`python -m unittest discover -s tests -v`

**26 testes, OK.**

Novos: listas NULL; criar/alterar/limpar contexto; rejeitar mismatch; duplicate; learning A–D; Pilhas AA em duas lojas; mudança de local sem perder itens.

---

## Browser validation

Contra `http://127.0.0.1:8010/` (servidor Fase 4; o :8000 antigo estava stale):

| # | Passo | Resultado |
| - | ----- | --------- |
| 1–3 | Hoje → Continente | Header `Comprar Hoje` / `Continente · Supermercado` |
| 4–5 | Adicionar da Lista Geral | `Continente` / `Supermercado`; 175 produtos |
| 6 | Mostrar todos | 178 produtos |
| 7–8 | Adicionar Fita isoladora | 1 `product_id` (176) |
| 9–10 | Novo em Hoje: Manteiga extra | tipos `[Supermercado]`, store Continente |
| 11–12 | → Leroy Merlin | itens antigos iguais |
| 13–14 | Cavilha 8mm | Bricolage + Leroy Merlin |
| 15–16 | → Todos | 3 itens mantidos |
| 17–18 | Duplicar | contexto copiado (`Todos`, o estado actual) |
| 19–20 | Refresh | persistido |

Smoke: `/`, `/api/health`, `/api/dashboard`, `/api/lists`, `/api/products`, `/api/commerce-types`, `/api/stores` → 200.

---

## Files changed

- `supermarket_app/database.py`
- `supermarket_app/services.py`
- `web/index.html`
- `web/app.js`
- `web/catalog.js`
- `web/styles.css`
- `tests/test_app.py`
- `PHASE_4_SHOPPING_CONTEXT_REPORT.md`

`main.py` **não** foi alterado.

---

## Problems / compromises

- FKs de `commerce_type_id` / `store_id` só na validação da API, não no `ALTER TABLE`.
- `store_name` livre da lista antiga mantém-se como nota; o contexto real é `store_id`.
- Aviso «Fora do contexto» é só visual; não há correcção obrigatória.
- A primeira tentativa de browser no `:8000` falou com um processo antigo; a validação correu no `:8010`.

---

## Next logical step

Preços por loja (ou histórico simples de preço) sobre o `store_id` da compra — sem filiais físicas nem GPS.
