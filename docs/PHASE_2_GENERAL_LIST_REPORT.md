# PHASE 2 — LISTA GERAL + COMPRAR HOJE

Catálogo persistente + compra actual. Sem commit. Sem comércio/lojas.

HEAD de partida: `e9a3b99` — `feat: add mobile shell and theme system`

---

## Schema

### Alterações

Nova tabela `products`:

| Coluna | Papel |
| ------ | ----- |
| `id` | PK |
| `name` | obrigatório; índice único `COLLATE NOCASE` |
| `category` | agrupamento (PT quando conhecido) |
| `subcategory` | reservado, UI simples |
| `default_unit` / `default_quantity` / `default_estimated_price` / `default_priority` | defaults da compra |
| `notes` | notas do catálogo |
| `is_active` | soft delete (`DELETE` API → `false`) |
| `created_at` / `updated_at` | auditoria |
| `last_used_at` / `times_used` | frequência (ex-`item_templates`) |

`shopping_items.product_id` adicionado por `ALTER TABLE` se em falta.

`shopping_lists` e colunas de compra dos itens **não** foram removidas.

Backup local (não no Git): `data/shopping_list.pre-phase2.sqlite3`  
Já coberto por `data/*.sqlite3` no `.gitignore`.

### Migração de `item_templates`

Opção preferida: **os templates passam a ser o catálogo `products`**.

No `bootstrap`:

1. criar schema + coluna `product_id`;
2. copiar cada `item_templates` para `products` (nome normalizado, `times_used` / `last_used_at` preservados);
3. inserir seeds em falta sem duplicar;
4. para cada `shopping_item` sem `product_id`, encontrar/criar produto pelo nome e associar;
5. alinhar `shopping_items.category` com o produto ligado.

A tabela `item_templates` **permanece** na DB (não há drop) mas **deixa de ser lida/escrita**. Fonte de verdade: `products`.

### Fase 2B — `item_templates`

| Pergunta | Resposta |
| -------- | -------- |
| A. Runtime depois da migração? | **Não.** Criar/editar/desactivar produto, adicionar a Hoje, frequência e Lista Geral usam só `products`. |
| B. Só migração inicial? | **Sim.** `SELECT` em `_migrate_catalog` + `CREATE TABLE IF NOT EXISTS` para DBs antigas. |
| C. Inserts/updates depois de `products` existir? | **Não.** Nenhum `INSERT`/`UPDATE` em `item_templates`. |
| D. Sugestões? | **Exclusivamente `products`.** |

Decisão: tabela **legacy no SQLite**, sem sincronização paralela. Não se apaga agora para não arriscar a migração. O bootstrap copia templates com `reactivate=False`, para um produto desactivado não voltar a activar-se só porque ainda está em `item_templates`.

Matching de nome: `strip` + comparação `lower()`. Sem fuzzy.

Categorias inglesas conhecidas (`Pantry`, `Dairy & Eggs`, `Groceries`, …) mapeiam para português (`Mercearia`, `Laticínios`, …). Nomes já em PT (incl. `Carne e Peixe`) mantêm-se.

### Relação Product → ShoppingItem

```text
products 1 ──< shopping_items (product_id)
```

O catálogo não desaparece ao terminar/remover a compra.  
Quantidade, preço, estado, corredor, prioridade e nota da viagem ficam em `shopping_items`.

---

## API

### Novos

| Método | Rota | Notas |
| ------ | ---- | ----- |
| GET | `/api/products` | query: `search`, `category`, `active` (`1` default, `0`, `all`) |
| POST | `/api/products` | 201 novo; 200 se o nome já existir (case-insensitive) |
| GET | `/api/products/{id}` | |
| PATCH | `/api/products/{id}` | |
| DELETE | `/api/products/{id}` | soft: `is_active = false` |
| POST | `/api/lists/{list_id}/products/{product_id}` | selecciona para a lista activa |

### Alterados (contrato preservado)

| Rota | Mudança interna |
| ---- | ---------------- |
| `POST /api/lists/{id}/items` | garante produto no catálogo; `product_id` no item; incrementa `times_used` |
| `GET /api/dashboard` | acrescenta `product_count` e `today` `{item_count, pending_count, in_cart_count, purchased_count}` |
| `GET /api/suggestions` | lê `products` (`times_used DESC, last_used_at DESC, name`) |

Rotas antigas de lists/items/cycle/health **mantidas**.

### Duplicados na compra actual

Se o produto já está na lista: **aumenta a quantidade** e devolve **200** com `"merged": true`.  
Não cria segunda linha.

---

## Lista Geral

* Pesquisa client-side em nome / categoria / subcategoria (catálogo carregado de uma vez; ~170 itens).
* Grupos por categoria; toque adiciona/remove da lista activa (sem diálogo).
* Estado seleccionado: `aria-pressed` + check + estilo (não só cor).
* `+ Novo produto`: nome + categoria obrigatórios; resto opcional.

---

## Comprar Hoje

* Resumo: N produtos · no carrinho · comprados.
* Itens agrupados por categoria.
* Form de adicionar mantido: se o nome já existe no catálogo, reutiliza; senão cria produto + item.
* Stepper de quantidade; ciclo pending → in_cart → purchased; remover tira só da compra.
* Sugestões passam a vir de `products`.
* Múltiplas `shopping_lists` continuam; uma lista activa.

---

## Migration

### Antes (DB activa)

| Tabela | Contagem |
| ------ | -------- |
| `shopping_lists` | 1 |
| `shopping_items` | 6 |
| `item_templates` | 172 |

Backup: `data/shopping_list.pre-phase2.sqlite3`

### Depois do bootstrap (antes da validação browser)

| Tabela | Contagem |
| ------ | -------- |
| `products` | **172** (todos activos) |
| `shopping_items` com `product_id` | **6 / 6** |
| `item_templates` | 172 (legado, não usado) |

Segundo `ShoppingApplication` no mesmo ficheiro: **172 products** (sem duplicar).

### Depois da validação browser

Criados `Pilhas CR2032` e `Farinha 00` → **174** produtos.  
Arroz ficou na compra; Pilhas removidas da compra e **mantidas no catálogo**.

---

## Tests

```text
python -m unittest discover -s tests -v
Ran 12 tests in 0.352s
OK
```

Inclui bootstrap ×3 sem duplicar products (ids, nomes, `times_used`, `product_id`) e `"Arroz"` / `" arroz "` / `"ARROZ"` / `"ArRoZ"` → o mesmo Product.

Cópia da DB activa (174 products): bootstrap 1/2/3 → mesma contagem, ids, nomes, frequências e ligações. `item_templates` ficou em 172, sem escrita.

---

## Browser validation

Servidor em `127.0.0.1:8000` (depois encerrado).

| Passo | Resultado |
| ----- | --------- |
| Home | `172 produtos` / `6 produtos · 4 por comprar` (depois `174` / `7`) |
| Lista Geral | categorias PT; pesquisa `arroz` → um resultado |
| Seleccionar arroz | passa a Comprar Hoje; marcado na Geral |
| Comprar Hoje | arroz presente |
| Quantidade | 1 → 2 |
| Ciclo estado | `in_cart` |
| Adicionar `Pilhas CR2032` em Hoje | item + produto no catálogo |
| Remover das Hoje | some da compra; **continua na Geral** |
| `Farinha 00` pela Geral | aparece no catálogo |
| Refresh | arroz e 7 itens persistem; 174 produtos |

Smoke: `GET /`, `/api/health`, `/api/dashboard`, `/api/lists`, `/api/products` → **200**.

Temas/shell da Fase 1 intactos (tokens, 8 temas, bottom nav).

---

## Files changed

* `supermarket_app/database.py` — tabela `products`, `product_id`
* `supermarket_app/services.py` — migração, catálogo, merge, sugestões
* `supermarket_app/server.py` — rotas products
* `web/index.html` — Geral, form Hoje, diálogo produto, hints Home
* `web/app.js` — Hoje agrupado, quantidade, dashboard
* `web/catalog.js` — Lista Geral
* `web/styles.css` — catálogo / grupos / stepper
* `web/navigation.js` — `onScreen`
* `tests/test_app.py` — 6 testes novos + `catalog.js`
* `PHASE_2_GENERAL_LIST_REPORT.md`

Não tocado: `main.py`, schema conceptual de lojas, `item_templates` drop.

---

## Problems / compromises

* `item_templates` não foi apagada (migração reversível / DBs antigas). Deixou de ser usada.
* Há pares redundantes no catálogo legado (`banana` / `Bananas`, `leite` / `Milk`) — não foram fundidos (sem fuzzy).
* `Carne e Peixe` permanece como categoria existente; o selector de novos produtos usa Carne e Peixe em separado.
* Duplicado na mesma lista **aumenta quantidade** em vez de aviso modal.
* `times_used` incrementa ao **adicionar** à compra, não ao marcar comprado.
* Soft delete: produto some da Geral (`active=1`) mas os itens antigos ficam válidos.
* Vários processos antigos na porta 8000 atrasaram o primeiro smoke de `/api/products` (404 no servidor velho); após limpar a porta, 200.

---

## Next logical step

Fase 3 natural: **locais / tipos de comércio** (Continente, bricolage, tecnologia) e a relação produto ↔ local, sem misturar ainda histórico completo nem PWA.

Fase 2 + verificação 2B. Sem lojas.
