const shopState = {
  lists: [],
  activeListId: null,
  activeList: null,
  suggestions: [],
  products: [],
  productCount: 0,
  today: null,
  commerceTypes: [],
  stores: [],
  catalogContext: { kind: "all" },
};

const currency = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
});

const CATEGORY_ORDER = [
  "Mercearia",
  "Fruta",
  "Legumes",
  "Laticínios",
  "Charcutaria",
  "Carne",
  "Peixe",
  "Carne e Peixe",
  "Congelados",
  "Padaria",
  "Bebidas",
  "Limpeza",
  "Higiene",
  "Vários",
];

function showError(message) {
  const banner = document.getElementById("error-banner");
  banner.hidden = false;
  banner.textContent = message;
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  const payload = await response.json();
  if (!response.ok) {
    throw new Error(payload.error || "API request failed");
  }
  return payload;
}

function selectedProductIds() {
  const items = shopState.activeList?.items || [];
  return new Set(items.map((item) => item.product_id).filter(Boolean));
}

function updateHomeHints() {
  const general = document.getElementById("home-general-hint");
  const today = document.getElementById("home-today-hint");
  if (general) {
    const count = shopState.productCount || 0;
    general.textContent = count === 1 ? "1 produto" : `${count} produtos`;
  }
  if (today) {
    const stats = shopState.today;
    if (!stats) {
      today.textContent = "Preparar ou continuar a compra actual";
      return;
    }
    const pending = stats.pending_count || 0;
    today.textContent = `${stats.item_count || 0} produtos · ${pending} por comprar`;
  }
  const locations = document.getElementById("home-locations-hint");
  if (locations && shopState.locations) {
    const types = shopState.locations.commerce_type_count || 0;
    const stores = shopState.locations.store_count || 0;
    locations.textContent = `${types} tipos · ${stores} lojas`;
  }
}

async function loadDashboard() {
  const dashboard = await api("/api/dashboard");
  shopState.lists = dashboard.lists;
  shopState.suggestions = dashboard.suggestions;
  shopState.activeListId = dashboard.active_list_id;
  shopState.productCount = dashboard.product_count || 0;
  shopState.today = dashboard.today;
  shopState.locations = dashboard.locations;
  renderLists();
  renderSuggestions();
  updateHomeHints();
  if (shopState.activeListId) {
    await loadList(shopState.activeListId);
  }
}

async function loadList(listId) {
  shopState.activeList = await api(`/api/lists/${listId}`);
  shopState.activeListId = listId;
  shopState.today = {
    item_count: shopState.activeList.items.length,
    pending_count: shopState.activeList.summary.pending_count,
    in_cart_count: shopState.activeList.summary.in_cart_count,
    purchased_count: shopState.activeList.summary.purchased_count,
  };
  renderLists();
  renderActiveList();
  updateHomeHints();
  if (window.ShoppingCatalog) {
    window.ShoppingCatalog.render();
  }
}

function catalogQuery() {
  const ctx = shopState.catalogContext || { kind: "all" };
  if (ctx.kind === "type" && ctx.id) return `?commerce_type_id=${ctx.id}`;
  if (ctx.kind === "store" && ctx.id) return `?store_id=${ctx.id}`;
  return "";
}

async function loadProducts() {
  const payload = await api(`/api/products${catalogQuery()}`);
  shopState.products = payload.products;
  updateHomeHints();
  if (window.ShoppingCatalog) {
    window.ShoppingCatalog.render();
  }
}

async function loadLocations() {
  const [types, stores] = await Promise.all([
    api("/api/commerce-types?active=all"),
    api("/api/stores?active=all"),
  ]);
  shopState.commerceTypes = types.commerce_types;
  shopState.stores = stores.stores;
  if (window.ShoppingLocations) {
    window.ShoppingLocations.render();
  }
  if (window.ShoppingCatalog) {
    window.ShoppingCatalog.renderTypes();
  }
}

function setCatalogContext(context) {
  shopState.catalogContext = context || { kind: "all" };
}

function applyGeneralHeader() {
  if (window.ShoppingNav.state.currentScreen !== "general") return;
  const ctx = shopState.catalogContext || { kind: "all" };
  const title = document.getElementById("screen-title");
  const subtitle = document.getElementById("screen-subtitle");
  const back = document.getElementById("header-back");
  if (ctx.kind === "store") {
    title.textContent = ctx.name;
    subtitle.textContent = ctx.typeName || "Loja";
    subtitle.hidden = false;
    back.hidden = false;
    back.dataset.navigate = "locations";
  } else if (ctx.kind === "type") {
    title.textContent = "Lista Geral";
    subtitle.textContent = ctx.name;
    subtitle.hidden = false;
    back.hidden = false;
    back.dataset.navigate = "locations";
  } else {
    title.textContent = "Lista Geral";
    subtitle.textContent = "Todos os produtos do utilizador";
    subtitle.hidden = false;
    back.hidden = true;
    delete back.dataset.navigate;
  }
}

function renderLists() {
  const container = document.getElementById("lists");
  container.innerHTML = "";
  shopState.lists.forEach((list) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `list-card ${list.id === shopState.activeListId ? "active" : ""}`;
    button.innerHTML = `
      <strong>${list.name}</strong>
      <span>${list.store_name || "Sem loja definida"}</span>
      <small>${list.purchased_count}/${list.item_count} comprados</small>
    `;
    button.addEventListener("click", () => loadList(list.id));
    container.appendChild(button);
  });
}

function renderSuggestions() {
  const container = document.getElementById("suggestions");
  container.innerHTML = "";
  shopState.suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "tag";
    button.textContent = suggestion.name;
    button.addEventListener("click", async () => {
      if (!shopState.activeListId) return;
      await api(`/api/lists/${shopState.activeListId}/items`, {
        method: "POST",
        body: JSON.stringify({
          name: suggestion.name,
          quantity: suggestion.default_quantity,
          unit: suggestion.unit,
          category: suggestion.category,
        }),
      });
      await refreshActiveList();
    });
    container.appendChild(button);
  });
}

function groupItemsByCategory(items) {
  const groups = new Map();
  items.forEach((item) => {
    const key = item.category || "Vários";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(item);
  });
  const ordered = [];
  CATEGORY_ORDER.forEach((name) => {
    if (groups.has(name)) {
      ordered.push([name, groups.get(name)]);
      groups.delete(name);
    }
  });
  [...groups.keys()].sort((a, b) => a.localeCompare(b, "pt")).forEach((name) => {
    ordered.push([name, groups.get(name)]);
  });
  return ordered;
}

function renderActiveList() {
  if (!shopState.activeList) return;
  const summary = shopState.activeList.summary;
  document.getElementById("active-list-name").textContent = shopState.activeList.name;
  document.getElementById("active-list-meta").textContent =
    `${shopState.activeList.store_name || "Sem supermercado definido"} • ${shopState.activeList.items.length} produtos`;
  document.getElementById("estimated-total").textContent = currency.format(summary.estimated_total);
  document.getElementById("budget-remaining").textContent = currency.format(summary.budget_remaining);
  document.getElementById("completion-rate").textContent = `${summary.completion_rate}%`;
  document.getElementById("aisle-count").textContent = String(summary.aisles.length);

  const todaySummary = document.getElementById("today-summary");
  todaySummary.hidden = false;
  todaySummary.textContent =
    `${shopState.activeList.items.length} produtos · ${summary.in_cart_count} no carrinho · ${summary.purchased_count} comprados`;

  const itemsContainer = document.getElementById("items");
  itemsContainer.innerHTML = "";
  groupItemsByCategory(shopState.activeList.items).forEach(([category, items]) => {
    const group = document.createElement("section");
    group.className = "item-group";
    group.innerHTML = `<h3 class="item-group-title">${category}</h3>`;
    items.forEach((item) => {
      group.appendChild(renderItemCard(item));
    });
    itemsContainer.appendChild(group);
  });
}

function renderItemCard(item) {
  const article = document.createElement("article");
  article.className = `item-card status-${item.status}`;
  article.innerHTML = `
    <div class="item-top">
      <div>
        <h3>${item.name}</h3>
        <p>${item.aisle || "Geral"}</p>
      </div>
      <button type="button" class="status-button">${labelForStatus(item.status)}</button>
    </div>
    <div class="item-meta">
      <span class="qty-stepper">
        <button type="button" class="ghost-button small qty-down" aria-label="Diminuir quantidade">−</button>
        <strong>${item.quantity} ${item.unit}</strong>
        <button type="button" class="ghost-button small qty-up" aria-label="Aumentar quantidade">+</button>
      </span>
      <span>${currency.format(item.line_total)}</span>
    </div>
    ${item.note ? `<p class="item-note">${item.note}</p>` : ""}
    <div class="item-actions">
      <button type="button" class="ghost-button small delete-button">Remover</button>
    </div>
  `;
  article.querySelector(".status-button").addEventListener("click", async () => {
    await api(`/api/items/${item.id}/cycle`, { method: "POST" });
    await refreshActiveList();
  });
  article.querySelector(".delete-button").addEventListener("click", async () => {
    await api(`/api/items/${item.id}`, { method: "DELETE" });
    await refreshActiveList();
  });
  article.querySelector(".qty-down").addEventListener("click", async () => {
    const next = Math.max(0.1, Math.round((item.quantity - 1) * 10) / 10);
    await api(`/api/items/${item.id}`, { method: "PATCH", body: JSON.stringify({ quantity: next }) });
    await refreshActiveList();
  });
  article.querySelector(".qty-up").addEventListener("click", async () => {
    await api(`/api/items/${item.id}`, {
      method: "PATCH",
      body: JSON.stringify({ quantity: Math.round((item.quantity + 1) * 10) / 10 }),
    });
    await refreshActiveList();
  });
  return article;
}

function labelForStatus(status) {
  if (status === "pending") return "Por comprar";
  if (status === "in_cart") return "No carrinho";
  return "Comprado";
}

async function refreshActiveList() {
  const dashboard = await api("/api/dashboard");
  shopState.lists = dashboard.lists;
  shopState.suggestions = dashboard.suggestions;
  shopState.productCount = dashboard.product_count || shopState.productCount;
  shopState.today = dashboard.today;
  renderLists();
  renderSuggestions();
  updateHomeHints();
  await loadList(shopState.activeListId || dashboard.active_list_id);
  await loadProducts();
}

async function toggleProductOnToday(productId) {
  if (!shopState.activeListId) return;
  const existing = (shopState.activeList?.items || []).find((item) => item.product_id === productId);
  if (existing) {
    await api(`/api/items/${existing.id}`, { method: "DELETE" });
  } else {
    await api(`/api/lists/${shopState.activeListId}/products/${productId}`, { method: "POST" });
  }
  await refreshActiveList();
}

function setupForms() {
  const itemForm = document.getElementById("item-form");
  itemForm.addEventListener("submit", async (event) => {
    event.preventDefault();
    if (!shopState.activeListId) return;
    const formData = new FormData(itemForm);
    const payload = Object.fromEntries(formData.entries());
    payload.quantity = Number(payload.quantity);
    payload.estimated_price = Number(payload.estimated_price);
    payload.priority = Number(payload.priority);
    await api(`/api/lists/${shopState.activeListId}/items`, {
      method: "POST",
      body: JSON.stringify(payload),
    });
    itemForm.reset();
    itemForm.quantity.value = 1;
    itemForm.unit.value = "un";
    itemForm.category.value = "Mercearia";
    itemForm.aisle.value = "Geral";
    itemForm.estimated_price.value = 0;
    itemForm.priority.value = 2;
    await refreshActiveList();
  });

  const dialog = document.getElementById("list-dialog");
  document.getElementById("new-list-button").addEventListener("click", () => dialog.showModal());
  document.getElementById("cancel-list-button").addEventListener("click", () => dialog.close());
  document.getElementById("list-form").addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(event.target);
    const payload = Object.fromEntries(formData.entries());
    payload.budget = Number(payload.budget);
    const created = await api("/api/lists", { method: "POST", body: JSON.stringify(payload) });
    dialog.close();
    event.target.reset();
    await refreshActiveList();
    await loadList(created.id);
  });

  document.getElementById("duplicate-list-button").addEventListener("click", async () => {
    if (!shopState.activeListId) return;
    const clone = await api(`/api/lists/${shopState.activeListId}/duplicate`, { method: "POST" });
    await refreshActiveList();
    await loadList(clone.id);
  });

  document.getElementById("archive-list-button").addEventListener("click", async () => {
    if (!shopState.activeListId) return;
    await api(`/api/lists/${shopState.activeListId}`, {
      method: "PATCH",
      body: JSON.stringify({ status: "archived" }),
    });
    await loadDashboard();
  });
}

window.ShoppingApp = {
  shopState,
  api,
  CATEGORY_ORDER,
  selectedProductIds,
  loadProducts,
  loadLocations,
  loadDashboard,
  refreshActiveList,
  toggleProductOnToday,
  updateHomeHints,
  setCatalogContext,
  applyGeneralHeader,
};

window.ShoppingTheme.initTheme();
window.ShoppingNav.initNavigation();
window.ShoppingNav.onScreen = (screenId) => {
  if (screenId === "general") {
    applyGeneralHeader();
    window.ShoppingCatalog?.render();
  }
  if (screenId === "home") {
    updateHomeHints();
  }
  if (screenId === "locations" || screenId === "manage-locations") {
    window.ShoppingLocations?.render();
  }
};

loadDashboard()
  .then(loadLocations)
  .then(loadProducts)
  .then(setupForms)
  .catch((error) => {
    showError(error.message);
  });
