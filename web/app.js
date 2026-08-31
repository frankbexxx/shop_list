const shopState = { lists: [], activeListId: null, activeList: null, suggestions: [] };

const currency = new Intl.NumberFormat("pt-PT", {
  style: "currency",
  currency: "EUR",
});

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

async function loadDashboard() {
  const dashboard = await api("/api/dashboard");
  shopState.lists = dashboard.lists;
  shopState.suggestions = dashboard.suggestions;
  shopState.activeListId = dashboard.active_list_id;
  renderLists();
  renderSuggestions();
  if (shopState.activeListId) {
    await loadList(shopState.activeListId);
  }
}

async function loadList(listId) {
  shopState.activeList = await api(`/api/lists/${listId}`);
  shopState.activeListId = listId;
  renderLists();
  renderActiveList();
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
          aisle: suggestion.aisle,
        }),
      });
      await refreshActiveList();
    });
    container.appendChild(button);
  });
}

function renderActiveList() {
  if (!shopState.activeList) return;
  document.getElementById("active-list-name").textContent = shopState.activeList.name;
  document.getElementById("active-list-meta").textContent =
    `${shopState.activeList.store_name || "Sem supermercado definido"} • ${shopState.activeList.items.length} produtos`;
  document.getElementById("estimated-total").textContent = currency.format(shopState.activeList.summary.estimated_total);
  document.getElementById("budget-remaining").textContent = currency.format(shopState.activeList.summary.budget_remaining);
  document.getElementById("completion-rate").textContent = `${shopState.activeList.summary.completion_rate}%`;
  document.getElementById("aisle-count").textContent = String(shopState.activeList.summary.aisles.length);

  const itemsContainer = document.getElementById("items");
  itemsContainer.innerHTML = "";
  shopState.activeList.items.forEach((item) => {
    const article = document.createElement("article");
    article.className = `item-card status-${item.status}`;
    article.innerHTML = `
      <div class="item-top">
        <div>
          <h3>${item.name}</h3>
          <p>${item.category} • ${item.aisle}</p>
        </div>
        <button type="button" class="status-button">${labelForStatus(item.status)}</button>
      </div>
      <div class="item-meta">
        <span>${item.quantity} ${item.unit}</span>
        <span>${currency.format(item.line_total)}</span>
        <span>Prioridade ${item.priority}</span>
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
    itemsContainer.appendChild(article);
  });
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
  renderLists();
  renderSuggestions();
  await loadList(shopState.activeListId || dashboard.active_list_id);
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
    itemForm.unit.value = "unit";
    itemForm.category.value = "Pantry";
    itemForm.aisle.value = "General";
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

window.ShoppingTheme.initTheme();
window.ShoppingNav.initNavigation();

loadDashboard().then(setupForms).catch((error) => {
  showError(error.message);
});
