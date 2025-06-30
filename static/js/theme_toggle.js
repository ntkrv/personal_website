document.addEventListener("DOMContentLoaded", function () {
    const toggleBtn = document.getElementById("theme-toggle");
    const html = document.documentElement;
    const moonIcon = document.getElementById("moon-icon");
    const sunIcon = document.getElementById("sun-icon");
  
    const setIcons = (isDark) => {
      if (isDark) {
        moonIcon.classList.remove("hidden");
        sunIcon.classList.add("hidden");
      } else {
        sunIcon.classList.remove("hidden");
        moonIcon.classList.add("hidden");
      }
    };
  
    const isDark = localStorage.getItem("theme") === "dark";
    if (isDark) html.classList.add("dark");
    setIcons(isDark);
  
    toggleBtn.addEventListener("click", () => {
      const currentlyDark = html.classList.toggle("dark");
      localStorage.setItem("theme", currentlyDark ? "dark" : "light");
      setIcons(currentlyDark);
    });
  });