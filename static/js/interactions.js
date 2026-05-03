// Cursor-driven micro-interactions: 3D tilt on .tilt cards. Pure
// DOM APIs, no GSAP needed.
(function () {
  const reduceMotion =
    window.matchMedia &&
    window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  if (reduceMotion) return;

  const isCoarsePointer =
    window.matchMedia && window.matchMedia("(pointer: coarse)").matches;

  document.addEventListener("DOMContentLoaded", () => {
    if (!isCoarsePointer) {
      initTilt();
    }
  });

  // --- Tilt -----------------------------------------------------------
  // Reads pointer position relative to each .tilt card and writes
  // CSS variables --rx / --ry. CSS handles the actual transform.
  function initTilt() {
    const MAX_ANGLE = 6; // degrees at the edge of the card
    document.querySelectorAll(".tilt").forEach((card) => {
      let raf = 0;
      let pendingX = 0;
      let pendingY = 0;

      const apply = () => {
        raf = 0;
        card.style.setProperty("--ry", pendingX.toFixed(2) + "deg");
        card.style.setProperty("--rx", pendingY.toFixed(2) + "deg");
      };

      card.addEventListener("pointermove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = (e.clientX - rect.left) / rect.width - 0.5;
        const y = (e.clientY - rect.top) / rect.height - 0.5;
        pendingX = x * MAX_ANGLE * 2;       // rotateY
        pendingY = -y * MAX_ANGLE * 2;      // rotateX
        if (!raf) raf = requestAnimationFrame(apply);
      });

      const reset = () => {
        if (raf) {
          cancelAnimationFrame(raf);
          raf = 0;
        }
        card.style.setProperty("--rx", "0deg");
        card.style.setProperty("--ry", "0deg");
      };
      card.addEventListener("pointerleave", reset);
      card.addEventListener("blur", reset, true);
    });
  }
})();
