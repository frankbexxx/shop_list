# PHASE 5 — HISTÓRICO DE COMPRAS

Compras concluídas passam a snapshots persistentes e imutáveis. Sem commit. Sem comparação de preços.

HEAD de partida: `2438d81` — `feat: add shopping list location context`

---

## Schema

### `purchase_history`

| Coluna | Papel |
| ------ | ----- |
| `id` | chave |
| `source_list_id` | lista de origem; **UNIQUE** |
| `name` | nome da lista no momento da conclusão |
| `completed_at` | instante da conclusão (UTC ISO) |
| `commerce_type_id` / `store_id` | referências opcionais para filtros |
| `commerce_type_name` / `store_name` | **snapshots** para apresentação |
| `estimated_total` | soma `quantity × estimated_price` |
| `actual_total` | soma só das linhas com preço real; `NULL` se nenhuma |
| `notes` | notas da lista |
| `created_at` | criação do snapshot |

`source_list_id` tem `ON DELETE SET NULL`. O histórico sobrevive se a lista for apagada.

### `purchase_history_items`

| Coluna | Papel |
| ------ | ----- |
| `product_id` | ligação opcional ao catálogo actual; **sem** `ON DELETE CASCADE` |
| `product_name`, `category`, `subcategory` | snapshot textual |
| `quantity`, `unit`, `estimated_price` | cópia da linha de trabalho |
| `actual_unit_price`, `actual_line_total` | preço observado; `NULL` se não registado |
| `status`, `aisle`, `note`, `position` | estado final da compra |

### `shopping_items.actual_unit_price`

Coluna `REAL`, default `NULL`, via `_ensure_column`. Não substitui `estimated_price`.

Índices: `completed_at DESC`, `product_id`, `purchase_history_id`.

---

## Complete purchase

`POST /api/lists/{id}/complete`

Uma transacção (`Database.connect()`): ou grava histórico + itens + arquivo, ou não grava nada.

1. Se já existe `purchase_history` com o mesmo `source_list_id`, devolve o existente (sem segundo insert).
2. Lista vazia → `400` «A lista está vazia».
3. Copia todos os itens (qualquer estado).
4. **Não** incrementa `times_used`.
5. Marca a lista `status = archived`.

### Idempotência

`source_list_id UNIQUE`. Clique repetido ou corrida: `IntegrityError` → devolve o histórico já criado. Uma lista de trabalho origina no máximo uma compra histórica.

### Lista após conclusão

- A lista fica `archived` e deixa de ser a compra activa.
- O dashboard escolhe a primeira lista `active` (não a mais recente arquivada).
- Se não houver lista activa: **não** se cria outra automaticamente. Comprar Hoje mostra «Compra concluída» + **Preparar nova compra**.
- «Preparar nova compra» cria uma lista vazia `Nova compra`, copiando o último contexto histórico se existir.

`duplicate` continua a clonar uma shopping list. «Usar novamente» parte só do snapshot.

---

## Snapshot

Preservados no histórico:

- nomes de loja e tipo
- nome / categoria / subcategoria do produto
- quantidade, unidade, preços, estado, corredor, nota

Alterar `Product.name` ou `Store.name` depois **não** muda o detalhe histórico. Os IDs servem só para filtros e reuse enquanto existirem.

---

## Prices

| Conceito | Fonte |
| -------- | ----- |
| Estimado | `estimated_price` (lista) / snapshot |
| Real | `actual_unit_price` observado nesta compra |

`actual_line_total = quantity × actual_unit_price` quando o preço real existe.

Total real = soma das linhas com preço conhecido. Não se inventam preços. A API devolve `priced_item_count` e `unpriced_item_count`.

Representação: `REAL` + `round(..., 2)`. Inputs aceitam vírgula portuguesa (`1,89`). Sem catálogo de preços por loja.

---

## History UI

### Lista

Cards: `31 AGO` / `Continente` / `5 produtos · 4,04 €`. Mais recente primeiro. Sem tabela desktop.

### Detalhe

Data longa, `Continente · Supermercado` (snapshots), notas, **Comprados** / **Não comprados**, total real, **Usar novamente**.

### Home

`1 compra · Última: 31 Ago` ou `Ainda sem compras concluídas`. O card em Mais usa o mesmo texto.

---

## Product insights

Derivados do histórico, sem colunas extra em `products`:

| Campo | Regra |
| ----- | ----- |
| `last_purchased_at` | `MAX(completed_at)` onde o item tem `status = purchased` |
| `last_actual_price` | `actual_unit_price` da compra mais recente em que o preço não é `NULL` |
| `purchase_count` | linhas históricas com `status = purchased` |

No diálogo do produto: «Última compra», «Último preço», «Comprado: N vezes».

`times_used` **não** é este número.

Semântica final:

| Acção | `times_used` |
| ----- | ------------ |
| Adicionar produto a uma lista (`create_item` / add from catalog) | +1 |
| Concluir compra | não altera |
| Segundo `POST /complete` | não altera |
| Usar novamente | +1 por item, porque os produtos são seleccionados para a nova lista |

`times_used` = número de selecções para listas de trabalho. `purchase_count` = vezes `purchased` no histórico.

---

## Reuse

`POST /api/history/{id}/reuse` cria uma **nova** `shopping_list` e novos `shopping_items`.

- Copia `commerce_type_id` / `store_id`.
- Reutiliza o mesmo `product_id`; não duplica Products.
- Itens começam `pending`; `actual_unit_price = NULL`.
- `estimated_price` vem do snapshot estimado.
- Product inactivo → **reactiva** automaticamente.
- `product_id` inexistente → procura nome normalizado → senão cria a partir do snapshot.
- O histórico original não é editado.

---

## Migration

`CREATE TABLE IF NOT EXISTS` + `_ensure_column` para `actual_unit_price`. Bootstrap repetido não duplica tabelas nem linhas. Listas antigas continuam válidas (`actual_unit_price` a `NULL`).

---

## Tests

Suite alargada na Fase 5B (rename/deactivate, reuse defensivo, arredondamento, `times_used`, histórico read-only).

```text
python -m unittest discover -s tests -v
Ran 44 tests
OK
```

Cobertura: schema/coluna; complete A/B/C/D; snapshot vs rename e deactivate; reuse; reactivate; product inexistente; insights; filtros; lista vazia; ordem; preços parciais 2×1.50; `3 × 1.10 = 3.30`; histórico sem PATCH/DELETE.

---

## Browser validation

Servidor Phase 5 em `http://127.0.0.1:8012` (DB de validação). O porto 8010 tinha um processo antigo sem `POST /complete`.

Fluxo percorrido:

1. Início → Hoje (Weekly Essentials, 5 produtos).
2. Local → Continente · Supermercado.
3. Milk e Bananas → `purchased`; resto `pending`.
4. Preços reais `1,89` e `2,15` (vírgula).
5. **Concluir compra** → «2 comprados / 3 por comprar / Total real 4,04 € / 3 produtos sem preço».
6. Confirmar → lista arquivada; Hoje: «Compra concluída» + Preparar nova compra.
7. Histórico no topo: `31 AGO · Continente · 5 produtos · 4,04 €`.
8. Detalhe: snapshots, comprados/não comprados, preços, notas da lista.
9. Lista Geral → Milk: «Última compra: 31 Ago 2026 · Último preço: 1,89 € · Comprado: 1 vez».
10. Usar novamente → lista `id=2`, mesmos `product_id`, todos `pending`, `actual_unit_price` vazio, contexto Continente.
11. Refresh: Home «1 compra · Última: 31 Ago»; Hoje «5 produtos · 5 por comprar · Continente»; 1 histórico.

---

## Files changed

- `supermarket_app/database.py`
- `supermarket_app/services.py`
- `supermarket_app/server.py`
- `web/index.html`
- `web/navigation.js`
- `web/app.js`
- `web/catalog.js`
- `web/history.js` (novo)
- `web/styles.css`
- `tests/test_app.py`
- `PHASE_5_PURCHASE_HISTORY_REPORT.md`

`main.py` não foi tocado.

---

## Problems / compromises

- Dinheiro continua em `REAL` + arredondamento a 2 casas; sem migração para cêntimos.
- `times_used` mantém-se como contagem de selecção; `purchase_count` é que vem do histórico.
- Product inactivo é reactivado no reuse, sem diálogo.
- Depois de concluir, se existir outra lista activa o dashboard salta para essa; só mostra o ecrã «Compra concluída» quando não há nenhuma activa.
- Um servidor antigo em `:8010` servia estáticos novos e API velha (`complete` → 404). A validação usou `:8012` com o código desta fase.

---

## Next logical step

Preços observados por loja (`product_prices` a partir do histórico), sem charts nem promoções.
