document.addEventListener("DOMContentLoaded", function () {
    setTimeout(() => {
      const flash = document.getElementById('flash-message-wrapper');
      if (flash) {
        flash.classList.remove('opacity-100');
        flash.classList.add('opacity-0');
        setTimeout(() => flash.remove(), 500);
      }
    }, 3000);
  });
  