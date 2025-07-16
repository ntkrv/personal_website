document.addEventListener("DOMContentLoaded", () => {
  const container = document.getElementById("toast-container");

  if (!container) return;

  const flashData = document.body.dataset.flashes;
  let flashMessages = [];

  try {
    flashMessages = JSON.parse(flashData || "[]");
  } catch (err) {
    console.error("Invalid flash messages JSON:", err);
    return;
  }

  flashMessages.forEach(([category, message]) => {
    const toast = document.createElement("div");

    toast.className = `flex items-start gap-3 max-w-xs w-full p-4 rounded-lg shadow-md text-sm text-white animate-fade-in slide-in-right ${
      category === "success"
        ? "bg-green-600"
        : category === "error"
        ? "bg-red-600"
        : "bg-gray-800"
    }`;

    const iconName = {
      success: "check_circle",
      error: "error",
      info: "info",
    }[category] || "notifications";

    toast.innerHTML = `
    <span class="material-symbols-outlined text-white text-lg self-center">${iconName}</span>
    <span class="flex-1 self-center">${message}</span>
    <button class="text-white font-bold leading-none focus:outline-none self-center" onclick="this.parentElement.remove()">×</button>
  `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add("opacity-0");
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
});
