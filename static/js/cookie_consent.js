// Minimal GDPR cookie consent. Shows the banner only when no choice
// has been recorded; relays the user's pick to gtag() if loaded so
// GA4 Consent Mode v2 can flip ad/analytics storage on or off.
(function () {
  const KEY = "cookie-consent";
  const banner = document.getElementById("cookie-consent");
  if (!banner) return;

  function applyConsent(state) {
    if (typeof window.gtag !== "function") return;
    const grant = state === "granted" ? "granted" : "denied";
    window.gtag("consent", "update", {
      ad_storage: grant,
      ad_user_data: grant,
      ad_personalization: grant,
      analytics_storage: grant,
    });
  }

  let saved = null;
  try {
    saved = localStorage.getItem(KEY);
  } catch (e) {}

  if (!saved) {
    banner.classList.remove("hidden");
  } else {
    applyConsent(saved);
  }

  banner.querySelectorAll("[data-consent]").forEach((btn) => {
    btn.addEventListener("click", () => {
      const choice = btn.getAttribute("data-consent");
      try {
        localStorage.setItem(KEY, choice);
      } catch (e) {}
      applyConsent(choice);
      banner.classList.add("hidden");
    });
  });
})();
