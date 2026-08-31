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

function renderCatalog() {
  const app = window.ShoppingApp;
  const container = document.getElementById("catalog");
  const search = document.getElementById("product-search");
  if (!app || !container) return;

  const term = (search?.value || "").trim().toLowerCase();
  const selected = app.selectedProductIds();
  const products = (app.shopState.products || []).filter((product) => matchesSearch(product, term));
  container.innerHTML = "";

  if (!products.length) {
    const empty = document.createElement("p");
    empty.className = "placeholder-copy";
    empty.textContent = term ? "Nenhum produto corresponde à pesquisa." : "Ainda não há produtos na Lista Geral.";
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
      section.appendChild(button);
    });
    container.appendChild(section);
  });
}

function setupCatalog() {
  const search = document.getElementById("product-search");
  const dialog = document.getElementById("product-dialog");
  const form = document.getElementById("product-form");
  if (!search || !dialog || !form) return;

  search.addEventListener("input", renderCatalog);

  document.getElementById("new-product-button").addEventListener("click", () => dialog.showModal());
  document.getElementById("cancel-product-button").addEventListener("click", () => dialog.close());

  form.addEventListener("submit", async (event) => {
    event.preventDefault();
    const formData = new FormData(form);
    const payload = Object.fromEntries(formData.entries());
    payload.default_quantity = Number(payload.default_quantity || 1);
    payload.default_estimated_price = Number(payload.default_estimated_price || 0);
    await window.ShoppingApp.api("/api/products", {
      method: "POST",
      body: JSON.stringify(payload),
    });
    dialog.close();
    form.reset();
    form.default_unit.value = "un";
    form.default_quantity.value = 1;
    form.default_estimated_price.value = 0;
    form.category.value = "Mercearia";
    await window.ShoppingApp.loadProducts();
  });
}

window.ShoppingCatalog = {
  render: renderCatalog,
  setup: setupCatalog,
};

setupCatalog();
