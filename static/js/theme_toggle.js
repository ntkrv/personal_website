// Dark-first theme controller.
// Resolution: localStorage > system preference > "dark".
(function () {
  const html = document.documentElement;

  function resolveInitialTheme() {
    const stored = localStorage.getItem("theme");
    if (stored === "dark" || stored === "light") return stored;
    if (window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches) {
      return "light";
    }
    return "dark";
  }

  function applyTheme(theme) {
    if (theme === "dark") {
      html.classList.add("dark");
      html.classList.remove("light");
    } else {
      html.classList.add("light");
      html.classList.remove("dark");
    }
  }

  // Apply ASAP to avoid flash of wrong theme
  applyTheme(resolveInitialTheme());

  document.addEventListener("DOMContentLoaded", () => {
    const themeToggle = document.getElementById("theme-toggle");
    if (!themeToggle) return;

    themeToggle.addEventListener("click", () => {
      const next = html.classList.contains("dark") ? "light" : "dark";
      applyTheme(next);
      localStorage.setItem("theme", next);
    });
  });
})();
