// Asks for confirmation before submitting any form whose submit button
// carries data-confirm="…". Replaces inline onclick="return confirm()"
// handlers, which the CSP blocks.
document.addEventListener("click", (event) => {
  const button = event.target.closest("[data-confirm]");
  if (button && !window.confirm(button.dataset.confirm)) {
    event.preventDefault();
  }
});
