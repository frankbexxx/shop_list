# PHASE 3 — LOCAIS + TIPOS DE COMÉRCIO

Tipos de comércio, marcas/lojas e filtro da Lista Geral por contexto. Sem commit. Sem preços, filiais ou histórico.

HEAD de partida: `1d5c1d9` — `feat: add persistent product catalog`

---

## Schema

Novas tabelas:

### `commerce_types`

| Coluna | Papel |
| ------ | ----- |
| `id` | PK |
| `name` | nome visível (PT-PT) |
| `slug` | UNIQUE; seed e lookup |
| `description` | texto curto |
| `icon` | chave simbólica (não é cor) |
| `position` | ordem no ecrã Locais |
| `is_active` | soft delete |
| `created_at` / `updated_at` | auditoria |

### `stores`

Marca/cadeia, **não** filial física.

| Coluna | Papel |
| ------ | ----- |
| `id` | PK |
| `name` | marca |
| `commerce_type_id` | tipo principal (FK `commerce_types`) |
| `slug` | UNIQUE |
| `notes` | livre |
| `is_active` | soft delete |
| `created_at` / `updated_at` | auditoria |

Uma store tem um tipo principal. Múltiplos tipos por loja ficam para depois.

### `product_commerce_types`

Many-to-many. UNIQUE/PK `(product_id, commerce_type_id)`. `priority` default `0`.

### `product_stores`

Many-to-many de preparação. UNIQUE/PK `(product_id, store_id)`. `priority` default `0`.

`products` continua a ser a única fonte de verdade para produtos. Sem nomes por loja, SKU, barcode ou preços.

```text
commerce_types 1 ──< stores
products ──< product_commerce_types >── commerce_types
products ──< product_stores >── stores
```

---

## Seed

Idempotente por `slug` (`INSERT OR IGNORE`).

### Commerce types (8)

Supermercado, Mercearia, Bricolage, Tecnologia, Farmácia, Papelaria, Casa, Outros.

### Stores (14)

| Tipo | Marcas |
| ---- | ------ |
| Supermercado | Continente, Auchan, Pingo Doce, Lidl, Aldi, Intermarché |
| Bricolage | Leroy Merlin, Bricomarché, MaxMat |
| Tecnologia | Worten, Rádio Popular, Fnac |
| Papelaria | Staples |
| Farmácia | Wells |

### Regras de migração dos produtos herdados

Corre **uma vez**, quando `product_commerce_types` está vazio:

1. todos os produtos existentes recebem **Supermercado**;
2. extras só com substrings conservadoras no nome:
   - `pilha` → Bricolage + Tecnologia
   - `lampad` / `lâmpad` → Bricolage + Casa
   - `caderno`, `caneta`, `lápis`/`lapis`, `marcador` → Papelaria

Não se usa `papel` isolado (apanharia papel higiénico).

Bootstrap seguinte **não** volta a inventar tipos. Produto criado em Comprar Hoje sem contexto fica sem tipos (não herda Supermercado no próximo arranque).

---

## API

### Commerce types

| Método | Rota | Notas |
| ------ | ---- | ----- |
| GET | `/api/commerce-types` | `active` default `1`; `all` inclui inactivos |
| POST | `/api/commerce-types` | cria; slug duplicado devolve o existente |
| GET | `/api/commerce-types/{id}` | |
| PATCH | `/api/commerce-types/{id}` | nome, descrição, posição, `is_active` |
| DELETE | `/api/commerce-types/{id}` | soft delete (`is_active = false`) |

### Stores

| Método | Rota | Notas |
| ------ | ---- | ----- |
| GET | `/api/stores` | `active`, `commerce_type_id`, `search` |
| POST | `/api/stores` | `name` + `commerce_type_id` |
| GET | `/api/stores/{id}` | inclui `commerce_type_name` / `_slug` |
| PATCH | `/api/stores/{id}` | nome, tipo, notas, `is_active` |
| DELETE | `/api/stores/{id}` | soft delete |

### Produtos por contexto

`GET /api/products` aceita:

| Query | Comportamento |
| ----- | ------------- |
| *(sem filtro)* | catálogo completo (Lista Geral / Todos) |
| `commerce_type_id` | só produtos ligados a esse tipo |
| `store_id` | **store-specific UNION produtos do commerce type da store**, sem duplicados |

Se ambos forem enviados, `store_id` ganha.

### Associações

| Método | Rota |
| ------ | ---- |
| POST | `/api/products/{id}/commerce-types/{type_id}` |
| DELETE | `/api/products/{id}/commerce-types/{type_id}` |
| POST | `/api/products/{id}/stores/{store_id}` |
| DELETE | `/api/products/{id}/stores/{store_id}` |

`POST /api/products` e `PATCH /api/products/{id}` aceitam `commerce_type_ids`. Create **adiciona**; update **substitui** se o campo vier no payload.

Dashboard: `locations.commerce_type_count` / `store_count` (activos).

---

## Product overlap

Um nome = uma row em `products` (`UNIQUE name COLLATE NOCASE`). Contextos são só junções.

**Pilhas AA** (id `175` na DB live):

- 1 row em `products`
- tipos: Supermercado + Bricolage + Tecnologia
- store explícita: Worten
- aparece nas três vistas de tipo e em Worten
- adicionar a Hoje usa o mesmo `product_id` (`175`); frequência fica no mesmo produto
- `GET /api/products?search=Pilhas%20AA` devolve 1 row

---

## Lista Geral contextual

| Contexto | Header | Dados |
| -------- | ------ | ----- |
| Todos | Lista Geral / Todos os produtos do utilizador | catálogo completo |
| Commerce type | Lista Geral / *tipo* | produtos da junção |
| Store | *marca* / *tipo da store* | UNION store + tipo |

Chip `[contexto] [Todos ×]` quando há filtro. Limpar volta a Todos. Escolher um local **não** esconde produtos de forma permanente.

Criar produto **dentro de um tipo** pré-marca esse tipo em «Onde costumas comprar?». Criar em Hoje **não** inventa contexto.

---

## Locais

Ecrã `Locais` deixa de ser placeholder:

- card **Todos**
- secção **Tipos** (hub-cards)
- secção **Lojas** (list-cards com tipo)

Home: `8 tipos · 14 lojas`.

Mais → **Gerir locais**: criar/editar nome/activar-desactivar tipos e lojas. Soft delete. Sem ecrã administrativo pesado. Sem morada/GPS/horário.

Tokens de tema; os 8 temas mantêm-se.

---

## Migration

DB live `data/shopping_list.sqlite3`:

| | Antes | Depois (após seed + validação) |
| - | ----- | ------------------------------ |
| products | 174 | 176 (`Pilhas AA`, `Fita isoladora` criados na validação) |
| commerce_types | 0 | 8 |
| stores | 0 | 14 |
| product_commerce_types | 0 | 183 |
| product_stores | 0 | 1 (Pilhas AA → Worten) |

Herdados: 174 × Supermercado; `pilhas` e `Pilhas CR2032` também Bricolage + Tecnologia.

Idempotência: `INSERT OR IGNORE` por slug; migração de produtos só se a junção estiver vazia. Teste de bootstrap ×3: tipos, lojas e relações estáveis.

---

## Tests

`python -m unittest discover -s tests -v`

**17 testes, OK.**

Cobertura nova: seed 8+14; bootstrap idempotente inclui tipos/lojas/relações; overlap Pilhas AA; filtro store UNION; soft delete sem destruir products; item de Hoje sem tipos inventados.

---

## Browser validation

Fluxo pedido, contra `http://127.0.0.1:8000/`:

| # | Passo | Resultado |
| - | ----- | --------- |
| 1 | Abrir Locais | Tipos + 14 lojas + Todos |
| 2–3 | Supermercado | Lista Geral / Supermercado; ~175 produtos |
| 4 | Voltar | Locais |
| 5–6 | Bricolage | Conteúdo diferente: `pilhas`, `Pilhas AA`, `Pilhas CR2032` |
| 7–8 | Pesquisar Pilhas AA | 1 resultado |
| 9–10 | Tecnologia | o mesmo `Pilhas AA` (id 175) |
| 11–12 | Adicionar a Hoje | 1 item, `product_id` 175 |
| 13–14 | Worten | header Worten / Tecnologia; inclui Pilhas AA |
| 15–16 | Todos | catálogo completo; chip escondido |
| 17–18 | Novo produto em Bricolage | `Fita isoladora` id 176, só tipo Bricolage |
| 19–20 | Editar + Tecnologia | aparece em Bricolage e Tecnologia; 1 row |

Smoke: `GET /`, `/api/health`, `/api/dashboard`, `/api/products`, `/api/commerce-types`, `/api/stores` → 200.

---

## Files changed

- `supermarket_app/database.py`
- `supermarket_app/locations.py` *(novo)*
- `supermarket_app/services.py`
- `supermarket_app/server.py`
- `web/index.html`
- `web/app.js`
- `web/catalog.js`
- `web/locations.js` *(novo)*
- `web/navigation.js`
- `web/styles.css`
- `tests/test_app.py`
- `PHASE_3_LOCATIONS_REPORT.md`

`main.py` **não** foi alterado nesta fase.

---

## Problems / compromises

- Store filter inclui **todos** os produtos do tipo da loja, não só os ligados à marca. Simples e documentado; associação explícita `product_stores` já existe para o caso Worten ∩ Bricolage.
- Migração extra só por substring no **nome**. Categorias domésticas (Mercearia, Fruta, …) vão todas para Supermercado. Conservador de propósito.
- UI de lojas: editar nome e activar/desactivar; mudar o tipo principal faz-se na API, não num formulário rico.
- `DELETE` de tipo/store não bloqueia «em uso»: é sempre soft delete, os products ficam.
- Validação no browser criou `Pilhas AA` e `Fita isoladora` na DB live (176 products).

---

## Next logical step

Ligar a compra actual (Comprar Hoje) a um local seleccionado — herdar Commerce Type/Store ao adicionar produtos — **sem** ainda modelar filiais, GPS ou preços por loja.
