const THEME_KEY = "shopping-list.theme";
const DEFAULT_THEME = "forest";

const THEMES = [
  {
    id: "classic",
    name: "Clássico",
    hint: "Pergaminho quente e verde-loja",
    preview: { bg: "#d4c4a8", surface: "#efe4d0", primary: "#0f6e66", text: "#1f1a14" },
  },
  {
    id: "forest",
    name: "Floresta",
    hint: "Musgo escuro para compras no telemóvel",
    preview: { bg: "#1a3d1a", surface: "#1e3c22", primary: "#6db36d", text: "#d8f0d8" },
  },
  {
    id: "midnight",
    name: "Meia-noite",
    hint: "Índigo profundo, pouco brilho",
    preview: { bg: "#08102e", surface: "#121a3a", primary: "#7b93e8", text: "#d4def8" },
  },
  {
    id: "ocean",
    name: "Oceano",
    hint: "Azul-petróleo e água-marinha",
    preview: { bg: "#0a3a4a", surface: "#0e4a5c", primary: "#2ec4b6", text: "#d4f4f4" },
  },
  {
    id: "sand",
    name: "Areia",
    hint: "Deserto quente e ouro velho",
    preview: { bg: "#6b4a18", surface: "#4a3210", primary: "#e0b050", text: "#f5e8c8" },
  },
  {
    id: "plum",
    name: "Ameixa",
    hint: "Vinho e rosa-pálido",
    preview: { bg: "#3a1830", surface: "#4a2240", primary: "#d478b0", text: "#f4d8ec" },
  },
  {
    id: "slate",
    name: "Ardósia",
    hint: "Cinza-azulado discreto",
    preview: { bg: "#2c333d", surface: "#3a424e", primary: "#7aa2d4", text: "#e6eaef" },
  },
  {
    id: "contrast",
    name: "Alto contraste",
    hint: "Preto, branco e amarelo",
    preview: { bg: "#000000", surface: "#161616", primary: "#ffe14d", text: "#ffffff" },
  },
];

function getPreference(key) {
  try {
    return localStorage.getItem(key);
  } catch (error) {
    return null;
  }
}

function setPreference(key, value) {
  try {
    localStorage.setItem(key, value);
  } catch (error) {
    /* private mode or blocked storage */
  }
}

function getTheme() {
  const stored = getPreference(THEME_KEY);
  if (THEMES.some((theme) => theme.id === stored)) {
    return stored;
  }
  return DEFAULT_THEME;
}

function applyTheme(themeId) {
  const id = THEMES.some((theme) => theme.id === themeId) ? themeId : DEFAULT_THEME;
  document.documentElement.setAttribute("data-theme", id);
  const shell = document.getElementById("app-shell");
  if (shell) {
    shell.setAttribute("data-theme", id);
  }
  return id;
}

function setTheme(themeId) {
  const id = applyTheme(themeId);
  setPreference(THEME_KEY, id);
  renderThemePicker();
  return id;
}

function renderThemePicker() {
  const container = document.getElementById("themes-grid");
  if (!container) return;
  const active = getTheme();
  container.innerHTML = "";
  THEMES.forEach((theme) => {
    const button = document.createElement("button");
    button.type = "button";
    button.className = `theme-card${theme.id === active ? " is-active" : ""}`;
    button.setAttribute("aria-pressed", theme.id === active ? "true" : "false");
    button.innerHTML = `
      <span class="theme-preview" aria-hidden="true">
        <span class="theme-preview-body" style="background:${theme.preview.bg}"></span>
        <span class="theme-preview-bar">
          <span class="theme-preview-chip" style="background:${theme.preview.surface}"></span>
          <span class="theme-preview-chip" style="background:${theme.preview.primary}"></span>
          <span class="theme-preview-chip" style="background:${theme.preview.text}"></span>
        </span>
      </span>
      <span class="theme-card-copy">
        <span class="theme-card-name">${theme.name}</span>
        <span class="theme-card-badge">${theme.id === active ? "Activo" : theme.hint}</span>
      </span>
    `;
    button.addEventListener("click", () => setTheme(theme.id));
    container.appendChild(button);
  });
}

function initTheme() {
  applyTheme(getTheme());
  renderThemePicker();
}

window.ShoppingTheme = {
  THEMES,
  DEFAULT_THEME,
  getPreference,
  setPreference,
  getTheme,
  setTheme,
  applyTheme,
  renderThemePicker,
  initTheme,
};
