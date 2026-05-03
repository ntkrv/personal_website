// Cursor-driven micro-interactions: 3D tilt on cards, magnetic pull
// on CTA buttons, and an angle-driven animated gradient border on
// any element tagged .gradient-border. Pure DOM APIs, no GSAP needed.
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
      initMagnetic();
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

  // --- Magnetic CTA ---------------------------------------------------
  // Pulls .magnetic targets toward the cursor when it's within
  // RADIUS px of the button's center, capped at PULL px.
  function initMagnetic() {
    const RADIUS = 110;
    const PULL = 14;

    document.querySelectorAll(".magnetic").forEach((btn) => {
      let raf = 0;
      let tx = 0;
      let ty = 0;

      const apply = () => {
        raf = 0;
        btn.style.setProperty("--mx", tx.toFixed(2) + "px");
        btn.style.setProperty("--my", ty.toFixed(2) + "px");
      };

      const onMove = (e) => {
        const rect = btn.getBoundingClientRect();
        const cx = rect.left + rect.width / 2;
        const cy = rect.top + rect.height / 2;
        const dx = e.clientX - cx;
        const dy = e.clientY - cy;
        const dist = Math.hypot(dx, dy);
        if (dist > RADIUS) {
          if (btn.classList.contains("is-pulled")) {
            tx = 0;
            ty = 0;
            btn.classList.remove("is-pulled");
            if (!raf) raf = requestAnimationFrame(apply);
          }
          return;
        }
        const strength = (1 - dist / RADIUS) * PULL;
        const angle = Math.atan2(dy, dx);
        tx = Math.cos(angle) * strength;
        ty = Math.sin(angle) * strength;
        btn.classList.add("is-pulled");
        if (!raf) raf = requestAnimationFrame(apply);
      };

      const reset = () => {
        tx = 0;
        ty = 0;
        btn.classList.remove("is-pulled");
        btn.style.setProperty("--mx", "0px");
        btn.style.setProperty("--my", "0px");
      };

      window.addEventListener("pointermove", onMove, { passive: true });
      window.addEventListener("pointerleave", reset);
    });
  }
})();
