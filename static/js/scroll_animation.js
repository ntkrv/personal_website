document.addEventListener("DOMContentLoaded", () => {
    if (typeof gsap === "undefined" || typeof ScrollTrigger === "undefined") {
      console.warn("GSAP или ScrollTrigger не загружены.");
      return;
    }
  
    gsap.registerPlugin(ScrollTrigger);
  
    // Section animation
    gsap.utils.toArray(".animate-on-scroll").forEach((el) => {
      gsap.fromTo(
        el,
        { opacity: 0, y: 24 },
        {
          opacity: 1,
          y: 0,
          duration: 0.8,
          ease: "power2.out",
          scrollTrigger: {
            trigger: el,
            start: "top 85%",
            toggleActions: "play none none reverse",
          },
        }
      );
    });
  

    gsap.utils.toArray("h2").forEach((el) => {
      gsap.fromTo(
        el,
        { opacity: 0, x: -20 },
        {
          opacity: 1,
          x: 0,
          duration: 0.6,
          ease: "power2.out",
          scrollTrigger: {
            trigger: el,
            start: "top 90%",
            toggleActions: "play none none reverse",
          },
        }
      );
    });
  

    gsap.fromTo(
      "footer a",
      { opacity: 0, y: 10 },
      {
        opacity: 1,
        y: 0,
        duration: 0.4,
        stagger: 0.1,
        ease: "power2.out",
        scrollTrigger: {
          trigger: "footer",
          start: "top 90%",
          toggleActions: "play none none reverse",
        },
      }
    );

    // Stat counters: count up from 0 to data-stat-end on first reveal.
    gsap.utils.toArray("[data-stat-end]").forEach((el) => {
      const end = parseFloat(el.getAttribute("data-stat-end"));
      const suffix = el.getAttribute("data-stat-suffix") || "";
      if (Number.isNaN(end)) return;

      const obj = { val: 0 };
      el.textContent = "0" + suffix;

      ScrollTrigger.create({
        trigger: el,
        start: "top 85%",
        once: true,
        onEnter: () => {
          gsap.to(obj, {
            val: end,
            duration: 1.4,
            ease: "power2.out",
            onUpdate: () => {
              el.textContent = Math.round(obj.val) + suffix;
            },
          });
        },
      });
    });
  });
  