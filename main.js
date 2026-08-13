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

// Hero project index: floating board preview on hover (desktop pointers only).
(function () {
  var palette = document.querySelector(".palette");
  if (!palette) return;
  if (!window.matchMedia("(hover: hover) and (min-width: 861px)").matches) return;

  var box = document.createElement("div");
  box.className = "palette-preview";
  box.setAttribute("aria-hidden", "true");
  var img = document.createElement("img");
  img.alt = "";
  img.decoding = "async";
  box.appendChild(img);
  document.body.appendChild(box);

  function place(link) {
    var r = link.getBoundingClientRect();
    var w = 272, h = 204, gap = 16;
    var left = r.left - w - gap;
    if (left < 12) left = r.right + gap;
    var top = r.top + r.height / 2 - h / 2;
    top = Math.max(12, Math.min(top, window.innerHeight - h - 12));
    box.style.left = left + "px";
    box.style.top = top + "px";
  }

  palette.addEventListener("mouseover", function (e) {
    var link = e.target.closest("a[data-preview]");
    if (!link) return;
    if (img.getAttribute("src") !== link.dataset.preview) {
      img.src = link.dataset.preview;
    }
    place(link);
    box.classList.add("show");
  });
  palette.addEventListener("mouseleave", function () {
    box.classList.remove("show");
  });
})();
