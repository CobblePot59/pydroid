(function () {
  const STORAGE_KEY = "pydroid.webui.theme";

  function setTheme(theme) {
    const root = document.documentElement;
    if (theme === "dark") root.setAttribute("data-theme", "dark");
    else root.removeAttribute("data-theme");
    syncNavbarTheme();
  }

  function getPreferredTheme() {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored === "light" || stored === "dark") return stored;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light";
  }

  function toggleTheme() {
    const next = document.documentElement.getAttribute("data-theme") === "dark" ? "light" : "dark";
    localStorage.setItem(STORAGE_KEY, next);
    setTheme(next);
    updateThemeToggleLabel();
  }

  function updateThemeToggleLabel() {
    const btn = document.querySelector("[data-theme-toggle]");
    if (!btn) return;
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    btn.setAttribute("aria-pressed", String(isDark));
    btn.title = isDark ? "Switch to light theme" : "Switch to dark theme";
  }

  function syncNavbarTheme() {
    const isDark = document.documentElement.getAttribute("data-theme") === "dark";
    document.querySelectorAll("[data-navbar-theme]").forEach(function (nav) {
      nav.classList.toggle("navbar-dark", isDark);
      nav.classList.toggle("navbar-light", !isDark);
    });
  }

  // Theme init (early)
  try {
    setTheme(getPreferredTheme());
  } catch (_) {
    // ignore localStorage failures
  }

  document.addEventListener("DOMContentLoaded", function () {
    syncNavbarTheme();

    const themeToggle = document.querySelector("[data-theme-toggle]");
    if (themeToggle) {
      themeToggle.addEventListener("click", function (e) {
        e.preventDefault();
        toggleTheme();
      });
      updateThemeToggleLabel();
    }

    // Bootstrap tooltips
    if (window.bootstrap && bootstrap.Tooltip) {
      document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(function (el) {
        new bootstrap.Tooltip(el);
      });
    }

    // Toastr defaults (if available)
    if (window.toastr) {
      toastr.options = Object.assign(
        {
          closeButton: true,
          newestOnTop: true,
          progressBar: true,
          timeOut: 3000,
          positionClass: "toast-bottom-right",
        },
        toastr.options || {},
      );
    }
  });
})();
