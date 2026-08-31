const SCREENS = {
  home: {
    title: "Shopping List",
    subtitle: "Listas rápidas para o supermercado",
    tab: "home",
    back: null,
  },
  general: {
    title: "Lista Geral",
    subtitle: "Todos os produtos do utilizador",
    tab: "general",
    back: null,
  },
  today: {
    title: "Comprar Hoje",
    subtitle: "Lista activa e modo compras",
    tab: "today",
    back: null,
  },
  locations: {
    title: "Locais",
    subtitle: "Onde costumas comprar",
    tab: "locations",
    back: null,
  },
  more: {
    title: "Mais",
    subtitle: "Histórico, temas e definições",
    tab: "more",
    back: null,
  },
  themes: {
    title: "Temas",
    subtitle: "Escolhe o visual da app",
    tab: "more",
    back: "more",
  },
  history: {
    title: "Histórico",
    subtitle: "Compras anteriores",
    tab: "more",
    back: "more",
  },
  settings: {
    title: "Definições",
    subtitle: "Preferências da aplicação",
    tab: "more",
    back: "more",
  },
  about: {
    title: "Sobre",
    subtitle: "Shopping List",
    tab: "more",
    back: "more",
  },
};

const navState = {
  currentScreen: "home",
};

function navigate(screenId) {
  const screen = SCREENS[screenId] || SCREENS.home;
  navState.currentScreen = screenId in SCREENS ? screenId : "home";

  document.querySelectorAll(".shell-screen").forEach((node) => {
    const active = node.dataset.screen === navState.currentScreen;
    node.classList.toggle("is-active", active);
    node.hidden = !active;
    node.setAttribute("aria-hidden", active ? "false" : "true");
  });

  document.getElementById("screen-title").textContent = screen.title;
  const subtitle = document.getElementById("screen-subtitle");
  subtitle.textContent = screen.subtitle;
  subtitle.hidden = !screen.subtitle;

  const back = document.getElementById("header-back");
  if (screen.back) {
    back.hidden = false;
    back.dataset.navigate = screen.back;
  } else {
    back.hidden = true;
    delete back.dataset.navigate;
  }

  document.querySelectorAll(".bottom-nav-item").forEach((item) => {
    const active = item.dataset.tab === screen.tab;
    item.classList.toggle("active", active);
    if (active) {
      item.setAttribute("aria-current", "page");
    } else {
      item.removeAttribute("aria-current");
    }
  });

  if (navState.currentScreen === "themes") {
    window.ShoppingTheme.renderThemePicker();
  }

  window.scrollTo(0, 0);
}

function initNavigation() {
  document.body.addEventListener("click", (event) => {
    const target = event.target.closest("[data-navigate]");
    if (!target || target.hidden) return;
    const screenId = target.dataset.navigate;
    if (!screenId) return;
    event.preventDefault();
    navigate(screenId);
  });

  document.querySelectorAll(".bottom-nav-item").forEach((item) => {
    item.addEventListener("click", () => navigate(item.dataset.tab));
  });

  navigate("home");
}

window.ShoppingNav = {
  SCREENS,
  state: navState,
  navigate,
  initNavigation,
};
