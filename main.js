// Nav hairline after scroll + reveal-on-scroll.
// All motion collapses under prefers-reduced-motion (CSS handles the rest).

(function () {
  var nav = document.querySelector(".nav");
  if (nav && "IntersectionObserver" in window) {
    var sentinel = document.createElement("div");
    sentinel.style.cssText = "position:absolute;top:0;height:1px;width:1px;";
    document.body.prepend(sentinel);
    new IntersectionObserver(function (entries) {
      nav.classList.toggle("scrolled", !entries[0].isIntersecting);
    }).observe(sentinel);
  }

  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var items = document.querySelectorAll(".reveal");
  if (reduced || !("IntersectionObserver" in window)) {
    items.forEach(function (el) { el.classList.add("in"); });
    return;
  }
  var io = new IntersectionObserver(
    function (entries) {
      entries.forEach(function (e) {
        if (e.isIntersecting) {
          e.target.classList.add("in");
          io.unobserve(e.target);
        }
      });
    },
    { threshold: 0.15, rootMargin: "0px 0px -40px 0px" }
  );
  items.forEach(function (el) { io.observe(el); });
})();


// Count-up for attributed stat numbers (fires once per element).
(function () {
  var els = document.querySelectorAll(".stat-num[data-count]");
  if (!els.length) return;
  var reduced = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  function final(el) {
    var n = parseInt(el.dataset.count, 10);
    return (el.dataset.locale ? n.toLocaleString("en-US") : String(n)) + (el.dataset.suffix || "");
  }
  if (reduced || !("IntersectionObserver" in window)) {
    els.forEach(function (el) { el.textContent = final(el); });
    return;
  }
  var io = new IntersectionObserver(function (entries) {
    entries.forEach(function (e) {
      if (!e.isIntersecting) return;
      io.unobserve(e.target);
      var el = e.target;
      var n = parseInt(el.dataset.count, 10);
      var t0 = null;
      function tick(t) {
        if (t0 === null) t0 = t;
        var p = Math.min(1, (t - t0) / 450);
        var eased = 1 - Math.pow(1 - p, 3);
        var v = Math.round(n * eased);
        el.textContent = (el.dataset.locale ? v.toLocaleString("en-US") : String(v)) + (el.dataset.suffix || "");
        if (p < 1) requestAnimationFrame(tick);
        else el.textContent = final(el);
      }
      requestAnimationFrame(tick);
    });
  }, { threshold: 0.6 });
  els.forEach(function (el) { io.observe(el); });
})();


// Case pages: reading progress bar + chapter-rail scroll spy.
(function () {
  var bar = document.querySelector(".progress");
  if (bar) {
    var ticking = false;
    function paint() {
      ticking = false;
      var doc = document.documentElement;
      var max = doc.scrollHeight - window.innerHeight;
      var p = max > 0 ? Math.min(1, window.scrollY / max) : 0;
      bar.style.transform = "scaleX(" + p + ")";
    }
    window.addEventListener("scroll", function () {
      if (!ticking) {
        ticking = true;
        requestAnimationFrame(paint);
      }
    }, { passive: true });
    paint();
  }

  var rail = document.querySelector(".chapter-rail");
  if (rail && "IntersectionObserver" in window) {
    var links = {};
    rail.querySelectorAll("a[href^='#']").forEach(function (a) {
      links[a.getAttribute("href").slice(1)] = a;
    });
    var spy = new IntersectionObserver(function (entries) {
      entries.forEach(function (e) {
        var a = links[e.target.id];
        if (!a) return;
        if (e.isIntersecting) {
          rail.querySelectorAll("a[aria-current]").forEach(function (x) {
            x.removeAttribute("aria-current");
          });
          a.setAttribute("aria-current", "true");
        }
      });
    }, { rootMargin: "-25% 0px -60% 0px" });
    Object.keys(links).forEach(function (id) {
      var el = document.getElementById(id);
      if (el) spy.observe(el);
    });
  }
})();
