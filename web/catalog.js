function matchesSearch(product, term) {
  if (!term) return true;
  const haystack = `${product.name} ${product.category} ${product.subcategory || ""}`.toLowerCase();
  return haystack.includes(term);
}

function groupProducts(products) {
  const groups = new Map();
  products.forEach((product) => {
    const key = product.category || "Vários";
    if (!groups.has(key)) groups.set(key, []);
    groups.get(key).push(product);
  });
  const order = window.ShoppingApp?.CATEGORY_ORDER || [];
  const ordered = [];
  order.forEach((name) => {
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

function renderContextChip() {
  const chip = document.getElementById("catalog-context");
  const app = window.ShoppingApp;
  if (!chip || !app) return;
  const ctx = app.shopState.catalogContext || { kind: "all" };
  if (ctx.kind === "all" && !ctx.source) {
    chip.hidden = true;
    chip.textContent = "";
    return;
  }
  if (ctx.kind === "all" && !ctx.showAll) {
    chip.hidden = true;
    chip.textContent = "";
    return;
  }
  chip.hidden = false;
  chip.innerHTML = "";
  const label = document.createElement("span");
  const action = document.createElement("button");
  action.type = "button";
  action.className = "ghost-button small";
  if (ctx.showAll && ctx.kind !== "all") {
    label.textContent = "Todos os produtos";
    action.textContent = ctx.kind === "store" ? ctx.name : ctx.name;
    action.addEventListener("click", async () => {
      app.setCatalogContext({ ...ctx, showAll: false });
      await app.loadProducts();
      app.applyGeneralHeader();
    });
  } else if (ctx.kind === "all") {
    chip.hidden = true;
    chip.textContent = "";
    return;
  } else {
    label.textContent = ctx.kind === "store" ? `${ctx.name} · ${ctx.typeName || ""}` : ctx.name;
    action.textContent = "Mostrar todos";
    action.addEventListener("click", async () => {
      app.setCatalogContext({ ...ctx, showAll: true });
      await app.loadProducts();
      app.applyGeneralHeader();
    });
  }
  chip.append(label, action);
}

function renderCatalog() {
  const app = window.ShoppingApp;
  const container = document.getElementById("catalog");
  const search = document.getElementById("product-search");
  if (!app || !container) return;
  renderContextChip();

  const term = (search?.value || "").trim().toLowerCase();
  const selected = app.selectedProductIds();
  const products = (app.shopState.products || []).filter((product) => matchesSearch(product, term));
  container.innerHTML = "";

  if (!products.length) {
    const empty = document.createElement("p");
    empty.className = "placeholder-copy";
    empty.textContent = term ? "Nenhum produto corresponde à pesquisa." : "Ainda não há produtos neste contexto.";
    container.appendChild(empty);
    return;
  }

  groupProducts(products).forEach(([category, items]) => {
    const section = document.createElement("section");
    section.className = "catalog-group";
    const heading = document.createElement("h2");
    heading.className = "catalog-group-title";
    heading.textContent = category;
    section.appendChild(heading);

    items.forEach((product) => {
      const onToday = selected.has(product.id);
      const row = document.createElement("div");
      row.className = "catalog-row";
      const button = document.createElement("button");
      button.type = "button";
      button.className = `catalog-item${onToday ? " is-selected" : ""}`;
      button.setAttribute("aria-pressed", onToday ? "true" : "false");
      button.innerHTML = `
        <span class="catalog-check" aria-hidden="true">${onToday ? "✓" : ""}</span>
        <span class="catalog-item-copy">
          <strong>${product.name}</strong>
          <small>${product.subcategory || product.default_unit || "un"}</small>
        </span>
      `;
      button.addEventListener("click", () => app.toggleProductOnToday(product.id));
      const edit = document.createElement("button");
      edit.type = "button";
      edit.className = "ghost-button small";
      edit.textContent = "Editar";
      edit.addEventListener("click", (event) => {
        event.stopPropagation();
        openProductDialog(product);
      });
      row.append(button, edit);
      section.appendChild(row);
    });
    container.appendChild(section);
  });
}

function selectedTypeIds() {
  return [...document.querySelectorAll("#product-commerce-types input:checked")].map((input) => Number(input.value));
}

function renderTypeCheckboxes(selectedIds) {
  const container = document.getElementById("product-commerce-types");
  const app = window.ShoppingApp;
  if (!container || !app) return;
  const selected = new Set((selectedIds || []).map(Number));
  const ctx = app.shopState.catalogContext || { kind: "all" };
  if (ctx.kind === "type" && ctx.id) selected.add(Number(ctx.id));
  if (ctx.kind === "store" && ctx.typeId) selected.add(Number(ctx.typeId));
  container.innerHTML = "";
  (app.shopState.commerceTypes || []).filter((type) => type.is_active || selected.has(type.id)).forEach((type) => {
    const label = document.createElement("label");
    label.className = "check-option";
    label.innerHTML = `
      <input type="checkbox" value="${type.id}" ${selected.has(type.id) ? "checked" : ""}>
      <span>${type.name}</span>
    `;
    container.appendChild(label);
  });
}

function resetProductForm() {
  const form = document.getElementById("product-form");
  form.reset();
  form.id.value = "";
  form.default_unit.value = "un";
  form.default_quantity.value = 1;
  form.default_estimated_price.value = 0;
  form.category.value = "Mercearia";
  document.getElementById("product-dialog-title").textContent = "Novo produto";
  const ctx = window.ShoppingApp.shopState.catalogContext;
  renderTypeCheckboxes(ctx?.kind === "type" && ctx.id ? [ctx.id] : []);
}

function openProductDialog(product) {
  const form = document.getElementById("product-form");
  const dialog = document.getElementById("product-dialog");
  resetProductForm();
  if (product) {
    document.getElementById("product-dialog-title").textContent = "Editar produto";
    form.id.value = product.id;
    form.name.value = product.name;
    form.category.value = product.category;
    form.subcategory.value = product.subcategory || "";
    form.default_unit.value = product.default_unit || "un";
    form.default_quantity.value = product.default_quantity || 1;
    form.default_estimated_price.value = product.default_estimated_price || 0;
    renderTypeCheckboxes(product.commerce_type_ids || []);
  }
  dialog.showModal();
}

function setupCatalog() {
  const search = document.getElementById("product-search");
  const dialog = document.getElementById("product-dialog");
  const form = document.getElementById("product-form");
  if (!search || !dialog || !form) return;

  search.addEventListener("input", renderCatalog);
  document.getElementById("new-product-button").addEventListener("click", () => openProductDialog(null));
  document.getElementById("cancel-product-button").addEventListener("click", () => dialog.close());

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    const productId = payload.id;
    delete payload.id;
    payload.default_quantity = Number(payload.default_quantity || 1);
    payload.default_estimated_price = Number(payload.default_estimated_price || 0);
    payload.commerce_type_ids = selectedTypeIds();
    const ctx = window.ShoppingApp.shopState.catalogContext || {};
    if (!productId && ctx.kind === "store" && ctx.id) {
      payload.store_ids = [ctx.id];
    }
    if (productId) {
      await window.ShoppingApp.api(`/api/products/${productId}`, {
        method: "PATCH",
        body: JSON.stringify(payload),
      });
    } else {
      await window.ShoppingApp.api("/api/products", {
        method: "POST",
        body: JSON.stringify(payload),
      });
    }
    dialog.close();
    resetProductForm();
    await window.ShoppingApp.loadProducts();
  });
}

window.ShoppingCatalog = {
  render: renderCatalog,
  renderTypes: renderTypeCheckboxes,
  setup: setupCatalog,
  openProductDialog,
};

setupCatalog();
