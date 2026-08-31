function renderLocations() {
  const app = window.ShoppingApp;
  if (!app) return;
  const types = document.getElementById("commerce-type-list");
  const stores = document.getElementById("store-list");
  if (!types || !stores) return;

  types.innerHTML = "";
  (app.shopState.commerceTypes || []).filter((type) => type.is_active).forEach((type) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "hub-card";
    button.innerHTML = `
      <span class="hub-card-label">${type.name}</span>
      <span class="hub-card-hint">${type.description || "Ver produtos deste contexto"}</span>
    `;
    button.addEventListener("click", () => openTypeContext(type));
    types.appendChild(button);
  });

  stores.innerHTML = "";
  (app.shopState.stores || []).filter((store) => store.is_active).forEach((store) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "list-card";
    button.innerHTML = `
      <strong>${store.name}</strong>
      <span>${store.commerce_type_name}</span>
    `;
    button.addEventListener("click", () => openStoreContext(store));
    stores.appendChild(button);
  });

  renderManageLocations();
}

async function openTypeContext(type) {
  const app = window.ShoppingApp;
  app.setCatalogContext({ kind: "type", id: type.id, name: type.name });
  await app.loadProducts();
  window.ShoppingNav.navigate("general");
  app.applyGeneralHeader();
}

async function openStoreContext(store) {
  const app = window.ShoppingApp;
  app.setCatalogContext({
    kind: "store",
    id: store.id,
    name: store.name,
    typeName: store.commerce_type_name,
  });
  await app.loadProducts();
  window.ShoppingNav.navigate("general");
  app.applyGeneralHeader();
}

async function openAllContext() {
  const app = window.ShoppingApp;
  app.setCatalogContext({ kind: "all" });
  await app.loadProducts();
  window.ShoppingNav.navigate("general");
  app.applyGeneralHeader();
}

function renderManageLocations() {
  const app = window.ShoppingApp;
  const typesBox = document.getElementById("manage-types");
  const storesBox = document.getElementById("manage-stores");
  const typeSelect = document.getElementById("store-type-select");
  if (!app || !typesBox || !storesBox || !typeSelect) return;

  typeSelect.innerHTML = "";
  (app.shopState.commerceTypes || []).filter((type) => type.is_active).forEach((type) => {
    const option = document.createElement("option");
    option.value = type.id;
    option.textContent = type.name;
    typeSelect.appendChild(option);
  });

  typesBox.innerHTML = "";
  (app.shopState.commerceTypes || []).forEach((type) => {
    const row = document.createElement("div");
    row.className = "manage-row";
    row.innerHTML = `
      <input class="manage-name" value="${type.name}" aria-label="Nome do tipo">
      <button type="button" class="ghost-button small">${type.is_active ? "Desactivar" : "Activar"}</button>
    `;
    row.querySelector(".manage-name").addEventListener("change", async (event) => {
      await app.api(`/api/commerce-types/${type.id}`, {
        method: "PATCH",
        body: JSON.stringify({ name: event.target.value }),
      });
      await app.loadLocations();
    });
    row.querySelector("button").addEventListener("click", async () => {
      await app.api(`/api/commerce-types/${type.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !type.is_active }),
      });
      await app.loadLocations();
    });
    typesBox.appendChild(row);
  });

  storesBox.innerHTML = "";
  (app.shopState.stores || []).forEach((store) => {
    const row = document.createElement("div");
    row.className = "manage-row";
    row.innerHTML = `
      <div>
        <input class="manage-name" value="${store.name}" aria-label="Nome da loja">
        <span>${store.commerce_type_name}</span>
      </div>
      <button type="button" class="ghost-button small">${store.is_active ? "Desactivar" : "Activar"}</button>
    `;
    row.querySelector(".manage-name").addEventListener("change", async (event) => {
      await app.api(`/api/stores/${store.id}`, {
        method: "PATCH",
        body: JSON.stringify({ name: event.target.value }),
      });
      await app.loadLocations();
    });
    row.querySelector("button").addEventListener("click", async () => {
      await app.api(`/api/stores/${store.id}`, {
        method: "PATCH",
        body: JSON.stringify({ is_active: !store.is_active }),
      });
      await app.loadLocations();
    });
    storesBox.appendChild(row);
  });
}

function setupLocations() {
  const all = document.getElementById("locations-all");
  const typeForm = document.getElementById("commerce-type-form");
  const storeForm = document.getElementById("store-form");
  if (all) all.addEventListener("click", openAllContext);

  typeForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(typeForm);
    await window.ShoppingApp.api("/api/commerce-types", {
      method: "POST",
      body: JSON.stringify({ name: formData.get("name") }),
    });
    typeForm.reset();
    await window.ShoppingApp.loadLocations();
  });

  storeForm?.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(storeForm);
    await window.ShoppingApp.api("/api/stores", {
      method: "POST",
      body: JSON.stringify({
        name: formData.get("name"),
        commerce_type_id: Number(formData.get("commerce_type_id")),
      }),
    });
    storeForm.reset();
    await window.ShoppingApp.loadLocations();
  });
}

window.ShoppingLocations = {
  render: renderLocations,
  openTypeContext,
  openStoreContext,
  openAllContext,
};

setupLocations();
