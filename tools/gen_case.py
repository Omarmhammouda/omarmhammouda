#!/usr/bin/env python3
"""Generate the 11 case-study pages from content/<slug>.json curation files.

Contract (enforced, build fails on violation):
- Only curated prose reaches the page; OCR text is never emitted as paragraphs.
- Every figure needs a real caption and specific alt text, and must exist on disk.
- No em/en dashes, no career-stat tokens, no OCR-debris patterns, terminal
  punctuation on paragraphs, no paragraph duplicated across slugs.
"""
import html
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
OUT = ROOT / "projects"
CASE_ASSETS = ROOT / "assets" / "case"

ORDER = ["karma", "hm", "mockquestions", "imperfect-foods", "wnder", "morgan-morgan",
         "sanctify", "content-cloud", "duradry", "nuvie", "oh-snap"]

PALETTE = {
    "karma": ("#dcefe3", "#0e3b2e", "#58b98b"),
    "hm": ("#14383b", "#e8f1ef", "#3f979c"),
    "mockquestions": ("#2f4a34", "#e9f2ea", "#5aa072"),
    "imperfect-foods": ("#f6c6ce", "#5a1a24", "#e2798f"),
    "wnder": ("#16294a", "#d8e4f4", "#5b82d8"),
    "morgan-morgan": ("#e9e2c7", "#191a1c", "#c9a227"),
    "sanctify": ("#d9ebd2", "#1c3a22", "#78b568"),
    "content-cloud": ("#131a33", "#c9d4f6", "#6e86e8"),
    "duradry": ("#1d3c3c", "#f0e9e4", "#d64545"),
    "nuvie": ("#f6c89b", "#3a2415", "#e8923f"),
    "oh-snap": ("#d9c1a3", "#191a1c", "#c29a62"),
}

LIMIT_LINE = "As a concept project, testing was moderated task walkthroughs, not longitudinal use."

errors = []
all_paragraphs = {}


def err(slug, msg):
    errors.append(f"[{slug}] {msg}")


def esc(t):
    return html.escape(str(t), quote=False)


def lint_text(slug, where, t):
    if not t:
        return
    if "—" in t or "–" in t:
        err(slug, f"em/en dash in {where}: {t[:60]}")
    if re.search(r"\b\d+(\.\d+)?%", t) or re.search(r"\b100k\b|\b100,000\b|\b20,000\b|\b2x\b", t):
        err(slug, f"career-stat token in {where}: {t[:80]}")
    if re.search(r"\s1\s+[a-z]", t):
        err(slug, f"OCR digit-one artifact in {where}: {t[:60]}")
    if re.search(r"\bUl\b", t):
        err(slug, f"'Ul' OCR artifact in {where}: {t[:60]}")


def lint_paragraph(slug, where, t):
    lint_text(slug, where, t)
    if t and not re.search(r"[.!?:]$", t.strip().rstrip('"')):
        err(slug, f"no terminal punctuation in {where}: ...{t[-50:]}")
    key = re.sub(r"\W+", " ", t or "").lower().strip()
    if len(key) > 60:
        if key in all_paragraphs and all_paragraphs[key] != slug:
            err(slug, f"paragraph duplicated with [{all_paragraphs[key]}]: {t[:60]}")
        all_paragraphs[key] = slug


def lint_figure(slug, fig, caption, alt):
    if not fig:
        return
    p = CASE_ASSETS / slug / fig
    if not p.exists():
        err(slug, f"figure missing on disk: {fig}")
    if not caption or len(caption) < 12:
        err(slug, f"figure {fig} missing real caption")
    if not alt or "case study visual" in (alt or "").lower() or len(alt) < 20:
        err(slug, f"figure {fig} missing specific alt text")
    lint_text(slug, f"caption {fig}", caption)
    lint_text(slug, f"alt {fig}", alt)


def figure_html(slug, fig, caption, alt, frame=None, cls="case-fig"):
    lint_figure(slug, fig, caption, alt)
    light = ' data-frame="light"' if frame == "light" else ""
    return (f'<figure class="{cls}"{light}><img src="../assets/case/{slug}/{fig}" alt="{esc(alt)}" '
            f'loading="lazy" decoding="async">'
            f'<figcaption>{esc(caption)}</figcaption></figure>')


def bold_thesis(thesis, rest):
    out = f"<strong>{esc(thesis)}</strong>"
    if rest:
        out += " " + esc(rest)
    return f"<p>{out}</p>"


def count_words(c):
    bits = [c["dek"], c["problem"]["thesis"], c["problem"]["body"],
            c["problem"].get("research_note") or "", c["design"]["intro"],
            c["validation"]["honest_line"], c["appendix"]["framing"]]
    bits += c["problem"]["bullets"]
    bits += [d["rationale"] + d["thesis"] for d in c["decisions"]]
    bits += c["learnings"]
    bits += [f["caption"] for f in c["design"]["figures"]]
    bits += list(c["at_a_glance"].values())
    return len(" ".join(str(b) for b in bits if b).split())


def chapter_open(anchor, num, claim):
    return (f'<section class="case-section chapter reveal" id="{anchor}">'
            f'<span class="ch-num" aria-hidden="true">{num}</span>'
            f'<h2>{esc(claim)}</h2>')


def build(slug):
    c = json.loads((CONTENT / f"{slug}.json").read_text())
    bg, ink, chip = PALETTE[slug]
    n = ORDER.index(slug) + 1
    name = c["name"]
    name_html = esc(name).replace("&amp;", "&amp;")
    full = c["tier"] == "full"
    mins = max(2, round(count_words(c) / 200))

    for k, v in c["at_a_glance"].items():
        lint_text(slug, f"glance.{k}", str(v or ""))
    lint_paragraph(slug, "dek", c["dek"])

    nxt = c["next"]
    nbg, nink, nchip = PALETTE[nxt]
    nname = json.loads((CONTENT / f"{nxt}.json").read_text())["name"]

    anchors = [("problem", "The problem")]
    if full and c["decisions"]:
        anchors.append(("decisions", "The decisions"))
    anchors.append(("design", "The design"))
    anchors.append(("validation", "Validation"))
    if full and c["learnings"]:
        anchors.append(("learned", "What I learned"))
    nums = {a: f"{i + 1:02d}" for i, (a, _) in enumerate(anchors)}

    rail = "".join(f'<a href="#{a}"><span>{nums[a]}</span>{title}</a>'
                   for a, title in anchors)

    g = c["at_a_glance"]
    glance_cells = "".join(
        f'<div><div class="m-label">{lbl}</div><div class="m-value">{esc(val)}</div></div>'
        for lbl, val in [("Role", g["role"]), ("Type", g["type"]), ("Year", g.get("year") or "2020s"),
                         ("Platform", g["platform"]), ("Scope", g["scope"]), ("Industry", g["industry"])])

    # Chapter 01: problem
    p = c["problem"]
    lint_paragraph(slug, "problem", p["thesis"] + " " + p["body"])
    bullets = "".join(f"<li>{esc(b)}</li>" for b in p["bullets"][:3])
    for b in p["bullets"][:3]:
        lint_text(slug, "problem bullet", b)
    research = f'<p class="research-note">{esc(p["research_note"])}</p>' if p.get("research_note") else ""
    ch_problem = (chapter_open("problem", nums["problem"], p["claim_h2"])
                  + bold_thesis(p["thesis"], p["body"])
                  + f'<ul class="pain-list">{bullets}</ul>' + research + "</section>")

    # Chapter 02: decisions (full tier)
    ch_decisions = ""
    if full and c["decisions"]:
        parts = [chapter_open("decisions", nums["decisions"], "The calls that shaped it")]
        for i, d in enumerate(c["decisions"]):
            lint_paragraph(slug, f"decision {i}", d["rationale"])
            parts.append(f"<h3>{esc(d['title'])}</h3>")
            parts.append(bold_thesis(d["thesis"], d["rationale"]))
            if d.get("figure"):
                parts.append(figure_html(slug, d["figure"], d.get("caption"), d.get("alt")))
            if i == 0 and c.get("pull_quote"):
                lint_text(slug, "pull quote", c["pull_quote"])
                parts.append(f'<aside class="pull-quote"><p>{esc(c["pull_quote"])}</p></aside>')
        parts.append("</section>")
        ch_decisions = "".join(parts)

    # Chapter 03: design
    d = c["design"]
    lint_paragraph(slug, "design intro", d["intro"])
    figs = d["figures"][:6]
    fig_parts = []
    i = 0
    while i < len(figs):
        f0 = figs[i]
        duo = (i in (1, 4)) and i + 1 < len(figs)
        if duo:
            f1 = figs[i + 1]
            fig_parts.append('<div class="fig-duo">'
                             + figure_html(slug, f0["figure"], f0["caption"], f0["alt"], f0.get("frame"))
                             + figure_html(slug, f1["figure"], f1["caption"], f1["alt"], f1.get("frame"))
                             + "</div>")
            i += 2
        else:
            fig_parts.append(figure_html(slug, f0["figure"], f0["caption"], f0["alt"], f0.get("frame")))
            i += 1
    ch_design = (chapter_open("design", nums["design"], d["claim_h2"])
                 + f"<p>{esc(d['intro'])}</p>" + "".join(fig_parts) + "</section>")

    # Chapter 04: validation
    v = c["validation"]
    lint_paragraph(slug, "validation", v["honest_line"])
    pills = "".join(f'<span class="pill" style="--i:{i}">{esc(f)}</span>'
                    for i, f in enumerate(v["flows"][:5]))
    changed = ""
    if v.get("changed"):
        items = "".join(f"<li>{esc(x)}</li>" for x in v["changed"][:2])
        for x in v["changed"][:2]:
            lint_text(slug, "validation changed", x)
        changed = f'<ul class="changed-list">{items}</ul>'
    ch_validation = (chapter_open("validation", nums["validation"], "What testing could and could not tell me")
                     + f'<div class="pill-row">{pills}</div>'
                     + changed
                     + f"<p>{esc(v['honest_line'])}</p>"
                     + f'<p class="limit-line">{esc(LIMIT_LINE)}</p></section>')

    # Chapter 05: learnings
    ch_learned = ""
    if full and c["learnings"]:
        paras = []
        for l in c["learnings"][:3]:
            lint_paragraph(slug, "learning", l)
            first, _, rest = l.partition(". ")
            if rest:
                paras.append(f"<p><strong>{esc(first)}.</strong> {esc(rest)}</p>")
            else:
                paras.append(f"<p><strong>{esc(l)}</strong></p>")
        ch_learned = (chapter_open("learned", nums["learned"], "What I learned") + "".join(paras) + "</section>")

    # Appendix
    a = c["appendix"]
    lint_text(slug, "appendix framing", a["framing"])
    app_figs = "".join(figure_html(slug, f["figure"], f["caption"], f["alt"]) for f in a["figures"][:3])
    appendix = (f'<details class="appendix reveal"><summary>Appendix: foundations and system</summary>'
                f'<p>{esc(a["framing"])}</p>{app_figs}</details>')

    page = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(name)}, case study by Omar M. Hammouda</title>
  <meta name="description" content="{esc(c['dek'])}">
  <link rel="preload" href="../assets/fonts/satoshi-900.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="preload" href="../assets/fonts/satoshi-500.woff2" as="font" type="font/woff2" crossorigin>
  <link rel="stylesheet" href="../styles.css?v=11">
</head>
<body>

  <header class="nav">
    <div class="wrap nav-inner">
      <a class="nav-name" href="../index.html">Omar M. Hammouda</a>
      <ul class="nav-links">
        <li><a href="../index.html#work">Work</a></li>
        <li class="hide-sm"><a href="../index.html#experience">Experience</a></li>
        <li class="hide-sm"><a href="../assets/Omar_M_Hammouda_Resume.pdf">Resume</a></li>
        <li><a class="nav-cta" href="../index.html#contact">Contact</a></li>
      </ul>
    </div>
    <div class="progress" style="--chip:{chip}" aria-hidden="true"></div>
  </header>

  <main>
    <section class="case-hero" style="--c-bg:{bg};--c-ink:{ink}">
      <span class="case-ghost" aria-hidden="true">{name_html}</span>
      <div class="wrap">
        <p class="case-kicker">Case study {n:02d} of 11 &middot; {esc(c['category'])} &middot; Independent concept project</p>
        <h1>{name_html}</h1>
        <p class="case-lede">{esc(c['dek'])}</p>
        <p class="case-mins">{mins} min read</p>
      </div>
    </section>

    <div class="wrap case-featured reveal">
      <figure class="case-fig cover-fig"><img src="../assets/covers/{slug}.jpg" alt="{esc(name)} case study cover" width="1440" height="780" loading="eager" decoding="async"></figure>
    </div>

    <section class="glance wrap reveal">
      <div class="glance-grid">{glance_cells}</div>
      <div class="glance-row"><span class="m-label">The hard part</span><p>{esc(g['hard_part'])}</p></div>
      <div class="glance-row"><span class="m-label">Look for</span><p>{esc(g['look_for'])}</p></div>
    </section>

    <div class="case-shell wrap" style="--chip:{chip};--c-bg:{bg}">
      <nav class="chapter-rail" aria-label="Chapters">{rail}</nav>
      <div class="case-body case-stream">
        {ch_problem}
        {ch_decisions}
        {ch_design}
        {ch_validation}
        {ch_learned}
        {appendix}
      </div>
    </div>

    <p class="wrap all-link"><a href="../index.html#work">All case studies</a></p>
    <a class="next-band" href="{nxt}.html" style="--c-bg:{nbg};--c-ink:{nink}">
      <span class="case-ghost" aria-hidden="true">{esc(nname)}</span>
      <span class="wrap next-inner"><span class="n-label">Next story</span><span class="n-name">{esc(nname)} &rarr;</span></span>
    </a>
  </main>

  <footer class="footer">
    <div class="wrap footer-inner">
      <span>&copy; 2026 Omar M. Hammouda</span>
      <a href="../index.html">Back to home</a>
    </div>
  </footer>

  <script src="../main.js?v=11"></script>
</body>
</html>
"""
    (OUT / f"{slug}.html").write_text(page)
    return mins


if __name__ == "__main__":
    mins_map = {}
    for slug in ORDER:
        mins_map[slug] = build(slug)
    print("reading times:", json.dumps(mins_map))
    if errors:
        print(f"\nBUILD FAILED: {len(errors)} lint error(s)")
        for e in errors:
            print(" -", e)
        sys.exit(1)
    print("11 pages generated, all lints green")
