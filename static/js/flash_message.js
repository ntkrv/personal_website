document.addEventListener("DOMContentLoaded", () => {
  // Auto-hide standard flash messages
  setTimeout(() => {
    const flash = document.getElementById("flash-message-wrapper");
    if (flash) {
      flash.classList.remove("opacity-100");
      flash.classList.add("opacity-0");
      setTimeout(() => flash.remove(), 500);
    }
  }, 3000);

  // Custom toast-style flash messages
  const container = document.getElementById("toast-container");
  const flashMessages = JSON.parse(document.body.dataset.flashes || "[]");

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
      <span class="material-icons text-white text-lg mt-0.5">${iconName}</span>
      <span class="flex-1">${message}</span>
      <button class="text-white font-bold leading-none focus:outline-none" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    // Auto-remove toast after timeout
    setTimeout(() => {
      toast.classList.add("opacity-0");
      setTimeout(() => toast.remove(), 300);
    }, 4000);
  });
});
