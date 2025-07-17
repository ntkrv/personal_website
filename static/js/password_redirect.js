document.addEventListener("DOMContentLoaded", () => {
  const box = document.querySelector('[data-redirect-after-success="true"]');
  if (box) {
    const redirectUrl = box.dataset.redirectUrl;
    const progress = document.getElementById("redirect-progress");

    // Animate progress bar
    requestAnimationFrame(() => {
      progress.style.width = "100%";
    });

    // Redirect after 5 seconds
    setTimeout(() => {
      window.location.href = redirectUrl;
    }, 5000);
  }
});
