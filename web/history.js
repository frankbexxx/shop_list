function historyPlace(row) {
  return row.store_name || row.commerce_type_name || "Todos os locais";
}

function historyTotalLine(row) {
  const count = row.item_count === 1 ? "1 produto" : `${row.item_count} produtos`;
  if (row.actual_total == null) return count;
  return `${count} · ${window.ShoppingApp.currency.format(row.actual_total)}`;
}

function renderHistoryList(rows) {
  const container = document.getElementById("history-list");
  if (!container) return;
  container.innerHTML = "";
  if (!rows.length) {
    const empty = document.createElement("p");
    empty.className = "placeholder-copy";
    empty.textContent = "Ainda sem compras concluídas";
    container.appendChild(empty);
    return;
  }
  rows.forEach((row) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = "hub-card history-card";
    button.innerHTML = `
      <span class="hub-card-label">${window.ShoppingApp.formatHistoryDay(row.completed_at)}</span>
      <span class="hub-card-hint">${historyPlace(row)}</span>
      <span class="hub-card-hint">${historyTotalLine(row)}</span>
    `;
    button.addEventListener("click", () => openHistoryDetail(row.id));
    container.appendChild(button);
  });
}

function historyItemLine(item) {
  const qty = item.unit && item.unit !== "un"
    ? `${item.quantity} ${item.unit}`
    : `${item.quantity} ×`;
  if (item.actual_unit_price == null) {
    return item.unit && item.unit !== "un" ? `${item.quantity} ${item.unit}` : "";
  }
  const unitPrice = window.ShoppingApp.currency.format(item.actual_unit_price);
  if (item.actual_line_total != null && item.quantity !== 1) {
    return `${item.quantity} × ${unitPrice} = ${window.ShoppingApp.currency.format(item.actual_line_total)}`;
  }
  if (item.unit && item.unit !== "un") {
    return `${qty} · ${unitPrice}`;
  }
  return `${item.quantity} × ${unitPrice}`;
}

function renderHistoryGroup(title, items) {
  const section = document.createElement("section");
  section.className = "history-group";
  const heading = document.createElement("h2");
  heading.className = "catalog-group-title";
  heading.textContent = title;
  section.appendChild(heading);
  if (!items.length) {
    const empty = document.createElement("p");
    empty.className = "item-note";
    empty.textContent = "Nenhum";
    section.appendChild(empty);
    return section;
  }
  items.forEach((item) => {
    const article = document.createElement("article");
    article.className = "item-card history-item-card";
    const extra = historyItemLine(item);
    article.innerHTML = `
      <h3>${item.product_name}</h3>
      ${extra ? `<p class="item-note">${extra}</p>` : ""}
      ${item.note ? `<p class="item-note">${item.note}</p>` : ""}
    `;
    section.appendChild(article);
  });
  return section;
}

function renderHistoryDetail(purchase) {
  const container = document.getElementById("history-detail");
  if (!container) return;
  const place = [purchase.store_name, purchase.commerce_type_name].filter(Boolean).join(" · ") || "Todos os locais";
  const purchased = purchase.items.filter((item) => item.status === "purchased");
  const leftover = purchase.items.filter((item) => item.status !== "purchased");
  const actual = purchase.actual_total == null
    ? "sem preços registados"
    : window.ShoppingApp.currency.format(purchase.actual_total);

  container.innerHTML = "";
  const header = document.createElement("header");
  header.className = "history-detail-header";
  header.innerHTML = `
    <h2>${window.ShoppingApp.formatLongDate(purchase.completed_at)}</h2>
    <p class="screen-subtitle">${place}</p>
    ${purchase.notes ? `<p class="item-note">${purchase.notes}</p>` : ""}
  `;
  container.appendChild(header);
  container.appendChild(renderHistoryGroup("Comprados", purchased));
  container.appendChild(renderHistoryGroup("Não comprados", leftover));

  const totals = document.createElement("p");
  totals.className = "today-summary";
  totals.textContent = `Total real: ${actual}`;
  container.appendChild(totals);

  const actions = document.createElement("div");
  actions.className = "complete-purchase-bar";
  const reuse = document.createElement("button");
  reuse.type = "button";
  reuse.className = "primary-button";
  reuse.textContent = "Usar novamente";
  reuse.addEventListener("click", async () => {
    const listed = await window.ShoppingApp.api(`/api/history/${purchase.id}/reuse`, { method: "POST" });
    await window.ShoppingApp.refreshActiveList();
    await window.ShoppingApp.loadList(listed.id);
    window.ShoppingNav.navigate("today");
  });
  actions.appendChild(reuse);
  container.appendChild(actions);

  const title = document.getElementById("screen-title");
  const subtitle = document.getElementById("screen-subtitle");
  if (title) title.textContent = window.ShoppingApp.formatLongDate(purchase.completed_at);
  if (subtitle) {
    subtitle.textContent = place;
    subtitle.hidden = false;
  }
}

async function loadHistory() {
  const app = window.ShoppingApp;
  if (!app) return;
  const payload = await app.api("/api/history");
  renderHistoryList(payload.history || []);
}

async function openHistoryDetail(historyId) {
  const purchase = await window.ShoppingApp.api(`/api/history/${historyId}`);
  renderHistoryDetail(purchase);
  window.ShoppingNav.navigate("history-detail");
}

window.ShoppingHistory = {
  load: loadHistory,
  open: openHistoryDetail,
};
