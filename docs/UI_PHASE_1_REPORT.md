# UI PHASE 1 REPORT

Shell visual + sistema de temas. Sem commit. Sem Fase 2.

HEAD de partida: `bf83490 — chore: remove legacy Kivy application`

---

## Referência SUECÃO

Repo: `https://github.com/frankbexxx/sueca` · branch `v2-main`

### Ficheiros analisados

| Ficheiro | O que foi extraído |
| -------- | ------------------- |
| `frontend/src/styles/design-tokens.css` | Tokens de cor, raio, espaço, sombra, touch mínimo; paleta conceptual, não nomenclatura de jogo |
| `frontend/src/styles/themes.css` | Temas que redefinem o conjunto completo de tokens (fundo, superfície, texto, acento, bordas) |
| `frontend/src/styles/app-shell.css` | Coluna única, max-width tipo telemóvel, header compacto, conteúdo com padding para a nav |
| `frontend/src/styles/shell-screens.css` | Ecrãs empilhados, um activo de cada vez, hub list |
| `frontend/src/components/navigation/BottomNav.*` | Barra fixa inferior, ícone + label, estado activo, `aria-current`, safe-area |
| `frontend/src/components/navigation/ShellHeader.*` | Título + subtítulo + acção secundária (voltar) |
| `frontend/src/components/navigation/ShellHubList.*` | Lista de caixas grandes tocáveis |
| `frontend/src/components/screens/HomeDashboard.*` | Landing operacional com cards, não dashboard técnico |
| `frontend/src/components/screens/ThemesScreen.*` | Grelha de previews; aplicar ao toque |
| `frontend/src/services/preferences.ts` | Camada `getPreference` / `setPreference` sobre `localStorage` |

Lidos também, quando necessário para contexto: tokens de fonte, estados activos da nav, e a forma como `data-theme` é aplicado no shell.

### Princípios reutilizados

* Shell em coluna, mobile-first, largura máxima ~480 px no conteúdo (hoje vai até ~720 px).
* Header curto: título forte + subtítulo discreto.
* Bottom nav fixa, touch ~48 px, label visível, activo por cor **e** barra/inset (não só cor).
* Padding inferior do conteúdo para a nav não tapar a lista.
* `env(safe-area-inset-bottom)` / top no header.
* Hub cards sólidos: título + hint, contraste alto, pouco texto.
* Tokens globais + ficheiro de temas que substitui o conjunto, não só `--color-primary`.
* Preferência isolada (`getPreference` / `setPreference`), chave própria da app.
* Preview de tema com fundo / superfície / acento / texto.
* Aplicação imediata + persistência após refresh.

**Não copiado:** React, TypeScript, nomenclatura de jogo (felt, nós/eles, etc.), editor de temas, 30+ paletas.

---

## Estrutura criada

### Shell

`#app-shell.app-shell` em `web/index.html`:

1. `.shell-header` — título, subtítulo, botão voltar (ecrãs nested)
2. `#error-banner` — erros de API sem destruir o `body`
3. `main.app-shell-content` — ecrãs
4. `nav.bottom-nav` — Início / Geral / Hoje / Locais / Mais

`data-theme` em `html` e `.app-shell`. Script no `<head>` lê `localStorage` antes do CSS pintar, para reduzir FOUC.

### Navegação

`web/navigation.js`:

* `navState.currentScreen`
* `navigate(screenId)` — `is-active` + `hidden` + `aria-hidden`, `aria-current="page"` no tab
* Tabs: `home`, `general`, `today`, `locations`, `more`
* Nested (tab Mais + voltar): `themes`, `history`, `settings`, `about`

Histórico **não** é um sexto tab: entra pela Home e por Mais.

### Ecrãs

| Ecrã | Conteúdo nesta fase |
| ---- | ------------------- |
| Home | Quatro hub cards: Lista Geral, Comprar Hoje, Locais, Histórico |
| Lista Geral | Placeholder |
| Comprar Hoje | UI existente (listas, itens, orçamento, sugestões, dialog nova lista) |
| Locais | Placeholder |
| Mais | Histórico, Temas, Definições, Sobre |
| Temas | Selector com previews (funcional) |
| Histórico / Definições / Sobre | Placeholders |

Ícones da nav: SVG stroke, sem emoji.

---

## Temas

### Lista (8)

| ID | Nome | Família |
| -- | ---- | ------- |
| `classic` | Clássico | Pergaminho quente + verde-loja |
| `forest` | Floresta | **Default** — musgo escuro, não branco |
| `midnight` | Meia-noite | Índigo |
| `ocean` | Oceano | Petróleo / água-marinha |
| `sand` | Areia | Deserto / ouro |
| `plum` | Ameixa | Vinho |
| `slate` | Ardósia | Cinza-azulado |
| `contrast` | Alto contraste | Preto / branco / amarelo |

Cada tema redefine fundo, superfícies, primary, hover, accent, texto, muted, bordas, sucesso/aviso/perigo, fundo da nav, estados de item (pending / cart / purchased) e sombras.

### Tokens principais

Definidos em `web/design-tokens.css` (`:root` = Floresta):

`--color-bg`, `--color-bg-alt`, `--color-surface`, `--color-surface-alt`, `--color-primary`, `--color-primary-hover`, `--color-accent`, `--color-text`, `--color-text-muted`, `--color-border`, `--color-success`, `--color-warning`, `--color-danger`, `--radius-sm|md|lg`, `--space-xs…xl`, `--shadow-sm|md`, `--touch-min`.

Extras de implementação: `--color-on-primary`, `--color-nav-bg`, `--color-pending|cart|purchased`, `--bottom-nav-height`, `--font-sans`.

Fonte: Plus Jakarta Sans (Google Fonts) com fallback `"Segoe UI", system-ui, sans-serif`. Inputs a **16 px**.

### Persistência

`web/theme.js`:

* `THEME_KEY = "shopping-list.theme"`
* `getPreference` / `setPreference`
* `getTheme` / `setTheme` / `applyTheme`
* Default `forest` se valor inválido ou ausente
* Picker: `aria-pressed`, badge «Activo»

---

## Funcionalidade preservada

Nada de API, payloads, schema SQLite ou `supermarket_app/database.py` foi alterado.

Continua operacional (reorganizado em **Comprar Hoje**):

* Dashboard API / bootstrap da lista por omissão
* Criar e seleccionar listas
* Adicionar itens, sugestões, orçamento / stats
* Ciclar estado do produto (pendente → carrinho → comprado)
* Dialog «Nova lista»

O dashboard técnico deixou de ser a landing; a lógica vive no ecrã Hoje.

---

## Files changed

### Novos

* `web/design-tokens.css`
* `web/themes.css`
* `web/theme.js`
* `web/navigation.js`
* `UI_PHASE_1_REPORT.md`

### Reescritos / actualizados

* `web/index.html` — shell, ecrãs, nav SVG, scripts
* `web/styles.css` — tokens, shell, hub, nav, forms/itens restyled
* `web/app.js` — mesmo contrato API; `shopState`; banner de erro
* `tests/test_app.py` — asserts de shell; teste extra de assets estáticos

### Sem alteração de propósito

* `supermarket_app/**` (rotas, DB, serviços)
* Schema SQLite

`main.py` pode continuar com uma newline extra não relacionada (pré-existente).

---

## Validation

### Testes

```text
python -m unittest discover -s tests -v
Ran 5 tests in 0.121s
OK
```

Os 4 testes originais passam. Foi adicionado `test_shell_assets_respond` (`/static/design-tokens.css`, `themes.css`, `styles.css`, `theme.js`, `navigation.js`, `app.js` → 200).

### Smoke tests

Servidor `python main.py --host 127.0.0.1 --port 8000 --no-browser` (depois encerrado).

| Pedido | Resultado |
| ------ | --------- |
| `GET /` | 200 `text/html` |
| `GET /api/health` | 200 |
| `GET /api/dashboard` | 200 |
| `GET /api/lists` | 200 |

### Checks responsive

`scrollWidth === clientWidth` (sem overflow horizontal) em:

* 360×800
* 390×844
* 430×932
* 768×1024
* 1280×900 (desktop)

Nav utilizável; cards em coluna; inputs ≥16 px.

### Persistência de tema

No browser de verificação:

1. Temas → 8 previews, Floresta default
2. Tocar **Oceano** → paleta aplicada de imediato
3. `localStorage['shopping-list.theme'] === 'ocean'`
4. Refresh → Oceano mantido

### Fluxo manual (browser)

* Navegação pelos 5 destinos (Início, Geral, Hoje, Locais, Mais)
* Locais: heading + copy placeholder
* Comprar Hoje: listas, sugestões, form, itens
* Ciclo de estado num item existente
* Adicionar produto **Tomates** (lista passou a 6)
* Temas + persistência (acima)

---

## Problems / compromises

* **Histórico** não tem tab próprio; está na Home e em Mais, conforme o briefing.
* **Lista Geral / Locais / Histórico / Definições / Sobre** são shells placeholder — conteúdo real fica para fases seguintes.
* A UI antiga de listas/itens **não foi apagada**; foi movida para Comprar Hoje. Pode parecer «mais densa» do que os outros ecrãs.
* `color-mix()` no estado activo da nav: browsers modernos; o inset da barra continua a marcar o activo sem depender só da mistura.
* Plus Jakarta Sans vem da Google; se a rede falhar, o fallback do sistema aplica-se.
* O snapshot de acessibilidade do browser ainda lista nós `hidden` (caminha o DOM completo). No CSS, `.shell-screen[hidden] { display: none !important }` e `aria-hidden` são aplicados no `navigate()`.
* Default **Floresta** (escuro). Quem nunca escolheu tema não vê branco puro.
* A sessão de verificação deixou `ocean` no `localStorage` **desse** browser; máquinas novas começam em `forest`.
* Não há Theme Editor, PWA, Capacitor, login, scanner, nem modelo Lista Geral real — fora de âmbito.

Fase 1 concluída. Fase 2 não implementada.
