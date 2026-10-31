"""Builds the README's hero and project cards as self-contained animated SVGs.

Fonts are the site's own (Bricolage Grotesque, Instrument Sans, JetBrains Mono,
all OFL), subset and embedded so GitHub's image proxy needs nothing external.
The map is denyskoval.com's route map (Natural Earth 1:50m).

    python3 scripts/build_assets.py   # writes assets/*.svg
"""

import base64
import json
import math
import random
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FONTS = ROOT / "scripts" / "fonts"
OUT = ROOT / "assets"
DATA = json.loads((ROOT / "scripts" / "data.json").read_text())

NIGHT = "#0b0e14"
PANEL = "#0f141d"
AURORA = "#6fe3c1"
SIGNAL = "#ff8a5c"
STAR = "#eef4fa"
TEXT = "#c4cedb"
DIM = "#7d8899"
LINE = "rgba(111,227,193,0.18)"
LINE_SOFT = "rgba(255,255,255,0.09)"


def font_face(family, file, weight="100 900"):
    data = base64.b64encode((FONTS / file).read_bytes()).decode()
    return (
        f"@font-face{{font-family:'{family}';font-weight:{weight};"
        f"src:url(data:font/woff2;base64,{data}) format('woff2')}}"
    )


def fonts(*which):
    faces = {
        "display": font_face("Bricolage", "bricolage.woff2", "200 800"),
        "body": font_face("Instrument", "instrument-400.woff2", "400")
        + font_face("Instrument", "instrument-500.woff2", "500"),
        "mono": font_face("JetBrains", "jetbrains.woff2", "500"),
    }
    return "".join(faces[w] for w in which)


BASE_CSS = """
.display{font-family:'Bricolage',system-ui,sans-serif;font-weight:700}
.body{font-family:'Instrument',system-ui,sans-serif}
.mono{font-family:'JetBrains',ui-monospace,monospace;font-weight:500}
@keyframes rise{from{opacity:0;transform:translateY(14px)}}
@keyframes fade{from{opacity:0}}
@keyframes twinkle{50%{opacity:.12}}
@keyframes drift{from{transform:translateX(-40px)}to{transform:translateX(40px)}}
.rise{animation:rise .9s cubic-bezier(.2,.7,.2,1) both}
.fade{animation:fade 1.4s ease-out both}
.tw{animation:twinkle 3.6s ease-in-out infinite}
@media (prefers-reduced-motion:reduce){*{animation:none!important}}
"""


def esc(s):
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def svg(w, h, css, body, label):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-label="{esc(label)}">\n<title>{esc(label)}</title>\n'
        f"<style>{css}</style>\n{body}\n</svg>\n"
    )


def stars(rng, n, w, h, max_y):
    out = []
    for i in range(n):
        x, y = rng.uniform(0, w), rng.uniform(0, max_y) ** 1.15 / max_y ** 0.15
        r = rng.choice([0.6, 0.8, 0.9, 1.1, 1.4])
        o = rng.uniform(0.15, 0.6) * (1 - y / h)
        cls = f' class="tw" style="animation-delay:{rng.uniform(0, 4):.1f}s"' if i % 4 == 0 else ""
        out.append(f'<circle cx="{x:.0f}" cy="{y:.0f}" r="{r}" fill="{STAR}" opacity="{o:.2f}"{cls}/>')
    return "".join(out)


def aurora(w, cx_list, idp):
    blobs = "".join(
        f'<ellipse cx="{cx}" cy="{cy}" rx="{rx}" ry="{ry}" fill="{c}" opacity="{o}"/>'
        for cx, cy, rx, ry, c, o in cx_list
    )
    return (
        f'<filter id="{idp}blur" x="-50%" y="-50%" width="200%" height="200%">'
        f'<feGaussianBlur stdDeviation="60"/></filter>'
        f'<g filter="url(#{idp}blur)"><g style="animation:drift 14s ease-in-out infinite alternate">{blobs}</g></g>'
    )


def chip(x, y, label, color=TEXT, border=LINE_SOFT, size=14):
    w = len(label) * size * 0.6 + 30
    return (
        f'<g transform="translate({x} {y})"><rect width="{w:.0f}" height="34" rx="17" fill="rgba(255,255,255,0.03)" '
        f'stroke="{border}"/><text x="15" y="22" class="mono" font-size="{size}" fill="{color}">{esc(label)}</text></g>',
        w,
    )


def chips(x, y, labels, gap=10, **kw):
    out = []
    for label in labels:
        g, w = chip(x, y, label, **kw)
        out.append(g)
        x += w + gap
    return "".join(out)


# ---------------------------------------------------------------- hero

def hero():
    W, H = 1200, 480
    m = DATA["routeMap"]
    rng = random.Random(7)
    j, c, legs = m["journey"], m["cities"], m["legs"]
    # map space → card space
    tx, ty = 470, -52
    route = legs["toSlovakia"] + legs["toNorway"].replace("M297 444", "")

    city_specs = [
        ("dnipro", "DNIPRO · 2004", 0, -22, "middle", STAR),
        ("senica", "SENICA · 2019", 0, 34, "middle", STAR),
        ("oslo", "OSLO · 2023 · HOME", 16, 5, "start", SIGNAL),
    ]
    cities = []
    for k, (cid, label, dx, dy, anchor, color) in enumerate(city_specs):
        x, y = c[cid]
        delay = [0.4, 2.0, 3.6][k]
        cities.append(
            f'<g class="fade" style="animation-delay:{delay}s">'
            f'<circle cx="{x}" cy="{y}" r="5" fill="none" stroke="{color}" stroke-width="1.5">'
            f'<animate attributeName="r" values="5;20" dur="2.6s" begin="{delay}s" repeatCount="indefinite"/>'
            f'<animate attributeName="opacity" values="0.8;0" dur="2.6s" begin="{delay}s" repeatCount="indefinite"/></circle>'
            f'<circle cx="{x}" cy="{y}" r="5.5" fill="{color}"/>'
            f'<text x="{x + dx}" y="{y + dy}" text-anchor="{anchor}" class="mono" font-size="14" '
            f'letter-spacing="1.5" fill="{color}">{label}</text></g>'
        )

    css = (
        fonts("display", "body", "mono")
        + BASE_CSS
        + """
@keyframes draw{from{stroke-dashoffset:1}}
@keyframes grow{from{font-variation-settings:'wght' 200,'wdth' 75;letter-spacing:6px}}
.leg{stroke-dasharray:1;stroke-dashoffset:0;animation:draw 1.6s cubic-bezier(.6,0,.3,1) both}
.name{font-variation-settings:'wght' 720,'wdth' 100;letter-spacing:-0.5px;animation:grow 1.8s cubic-bezier(.2,.7,.2,1) both,rise .9s cubic-bezier(.2,.7,.2,1) both}
"""
    )

    lede = [
        "I build web products from the database row to the button",
        "you tap – in Oslo, by way of Ukraine and Slovakia.",
    ]

    body = f"""
<defs>
  <clipPath id="h-card"><rect width="{W}" height="{H}" rx="28"/></clipPath>
  <linearGradient id="h-fade" x1="0" x2="1">
    <stop offset="0.38" stop-color="#fff" stop-opacity="0"/><stop offset="0.6" stop-color="#fff" stop-opacity="1"/><stop offset="0.8" stop-color="#fff" stop-opacity="1"/><stop offset="0.92" stop-color="#fff" stop-opacity="0"/>
  </linearGradient>
  <linearGradient id="h-floor" x1="0" y1="0" x2="0" y2="1">
    <stop offset="0.7" stop-color="#fff" stop-opacity="1"/><stop offset="1" stop-color="#fff" stop-opacity="0.25"/>
  </linearGradient>
  <mask id="h-mask"><rect width="{W}" height="{H}" fill="url(#h-fade)"/></mask>
  <radialGradient id="h-dot"><stop offset="0" stop-color="{SIGNAL}"/><stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#h-card)">
  <rect width="{W}" height="{H}" fill="{NIGHT}"/>
  {aurora(W, [(260, -30, 420, 110, AURORA, 0.30), (720, -50, 360, 120, "#7c6cff", 0.22), (1060, 0, 320, 110, AURORA, 0.22)], "h-")}
  {stars(rng, 90, W, H, 300)}
  <g mask="url(#h-mask)">
    <g transform="translate({tx} {ty})">
      <path d="{m['land']}" fill="#111925"/>
      <path d="{m['borders']}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="0.8"/>
      <path d="{j['ukraine']}{j['slovakia']}{j['norway']}" fill="rgba(111,227,193,0.08)" stroke="rgba(111,227,193,0.32)" stroke-width="0.8"/>
    </g>
  </g>
  <g>
    <g transform="translate({tx} {ty})">
      <path d="{route}" fill="none" stroke="{AURORA}" stroke-opacity="0.18" stroke-width="2" stroke-dasharray="2 6"/>
      <path d="{legs['toSlovakia']}" pathLength="1" class="leg" fill="none" stroke="{AURORA}" stroke-width="2.4" stroke-linecap="round" style="animation-delay:.6s"/>
      <path d="{legs['toNorway']}" pathLength="1" class="leg" fill="none" stroke="{AURORA}" stroke-width="2.4" stroke-linecap="round" style="animation-delay:2.2s"/>
      <text x="430" y="502" text-anchor="middle" class="mono fade" font-size="12" fill="{DIM}" style="animation-delay:1.6s">1,298 km</text>
      <text x="196" y="330" text-anchor="end" class="mono fade" font-size="12" fill="{DIM}" style="animation-delay:3.2s">1,319 km</text>
      {''.join(cities)}
      <g opacity="0">
        <set attributeName="opacity" to="1" begin="4.4s"/>
        <circle r="14" fill="url(#h-dot)" opacity="0.6"/><circle r="3.5" fill="{SIGNAL}"/>
        <animateMotion dur="7s" begin="4.4s" repeatCount="indefinite" path="{route}" keyPoints="0;1;1" keyTimes="0;0.8;1" calcMode="linear"/>
      </g>
    </g>
  </g>
  <g transform="translate(68 0)">
    <g class="rise" style="animation-delay:.1s">
      <circle cx="5" cy="99" r="4" fill="{AURORA}"><animate attributeName="opacity" values="1;.25;1" dur="2.4s" repeatCount="indefinite"/></circle>
      <text x="20" y="104" class="mono" font-size="15" letter-spacing="2.5" fill="{AURORA}">59.91°N 10.75°E – OSLO</text>
    </g>
    <text x="-4" y="208" class="display name" font-size="100" fill="{STAR}">Denys Koval</text>
    <text x="0" y="262" class="body rise" font-weight="500" font-size="29" fill="{STAR}" style="animation-delay:.5s">Full-stack developer&#160;&#8201;<tspan fill="{SIGNAL}">·</tspan>&#8201;&#160;drone pilot</text>
    <text class="body rise" font-size="20" fill="{TEXT}" style="animation-delay:.7s">
      <tspan x="0" y="312">{esc(lede[0])}</tspan><tspan x="0" y="341">{esc(lede[1])}</tspan>
    </text>
    <g class="rise" style="animation-delay:.9s">{chips(0, 376, ["Next.js + TypeScript", "IT apprentice @ Comono", "5 languages"])}</g>
  </g>
  <rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="27.5" fill="none" stroke="{LINE}"/>
</g>"""
    return svg(W, H, css, body, "Denys Koval – full-stack developer and drone pilot in Oslo")


# ---------------------------------------------------------------- cards

CW, CH = 1200, 300
ART_W = 440


def card(idp, art, kicker, title, text, tags, label):
    lines = textwrap.wrap(text, 54)
    tx = ART_W + 56
    body_lines = "".join(f'<tspan x="{tx}" y="{150 + i * 31}">{esc(l)}</tspan>' for i, l in enumerate(lines))
    css = fonts("display", "body", "mono") + BASE_CSS + art[1]
    body = f"""
<defs>
  <clipPath id="{idp}card"><rect width="{CW}" height="{CH}" rx="24"/></clipPath>
  <pattern id="{idp}grid" width="18" height="18" patternUnits="userSpaceOnUse"><circle cx="1" cy="1" r="1" fill="rgba(255,255,255,0.07)"/></pattern>
  <radialGradient id="{idp}glow"><stop offset="0" stop-color="{AURORA}" stop-opacity="0.18"/><stop offset="1" stop-color="{AURORA}" stop-opacity="0"/></radialGradient>
</defs>
<g clip-path="url(#{idp}card)">
  <rect width="{CW}" height="{CH}" fill="{PANEL}"/>
  <rect width="{ART_W}" height="{CH}" fill="{NIGHT}"/>
  <rect width="{ART_W}" height="{CH}" fill="url(#{idp}grid)"/>
  <ellipse cx="{ART_W / 2}" cy="{CH / 2}" rx="200" ry="130" fill="url(#{idp}glow)"/>
  {art[0]}
  <line x1="{ART_W}" y1="0" x2="{ART_W}" y2="{CH}" stroke="{LINE_SOFT}"/>
  <g class="rise" style="animation-delay:.1s"><text x="{tx}" y="62" class="mono" font-size="14" letter-spacing="2.5" fill="{AURORA}">{esc(kicker)}</text></g>
  <g class="rise" style="animation-delay:.2s"><text x="{tx - 2}" y="112" class="display" font-size="46" letter-spacing="-1" fill="{STAR}">{esc(title)}</text></g>
  <g class="rise" style="animation-delay:.3s"><text class="body" font-size="21" fill="{TEXT}">{body_lines}</text></g>
  <g class="rise" style="animation-delay:.4s">{chips(tx, 238, tags, size=13)}</g>
  <rect x="0.5" y="0.5" width="{CW - 1}" height="{CH - 1}" rx="23.5" fill="none" stroke="{LINE}"/>
</g>"""
    return svg(CW, CH, css, body, label)


def boardly_art():
    # Boardly's own wordmark (B-tile with an offset shadow, serif "boardly") in the site palette.
    serif = "Georgia,'Times New Roman',serif"
    art = f"""
<g transform="translate({ART_W / 2 - 170} {CH / 2 - 56}) scale(0.43)">
  <g transform="scale(0.406)">
    <rect class="b-shadow" x="79" y="79" width="380" height="380" rx="101" fill="{SIGNAL}"/>
    <rect x="53" y="53" width="380" height="380" rx="101" fill="#151b27" stroke="rgba(111,227,193,0.35)" stroke-width="6"/>
    <text x="243" y="340" font-family="{serif}" font-weight="800" font-size="274" fill="{AURORA}" text-anchor="middle">B</text>
  </g>
  <text x="222" y="160" font-family="{serif}" font-weight="800" font-size="150" letter-spacing="-4.5" fill="{STAR}">boardly</text>
</g>
<g class="mono" font-size="12" fill="{DIM}">
  <g transform="translate(36 248)"><circle r="4" cx="4" cy="-4" fill="{AURORA}"><animate attributeName="opacity" values="1;.3;1" dur="1.8s" repeatCount="indefinite"/></circle><text x="16" y="0">make a room · share the link · play</text></g>
</g>"""
    css = "@keyframes nudge{50%{transform:translate(10px,10px)}}.b-shadow{animation:nudge 3.2s ease-in-out infinite}"
    return art, css


def brain_art():
    rng = random.Random(7)
    cx, cy, s = ART_W / 2, CH / 2, 0.62
    groups = [("#f2707f", 0.45), ("#62a8ff", 0.25), (AURORA, 0.24), ("#e9b44c", 0.03), ("#a48bff", 0.03)]

    def pick():
        r = rng.random()
        for col, wgt in groups:
            r -= wgt
            if r <= 0:
                return col
        return groups[0][0]

    dots = []
    for i in range(300):
        col = pick()
        x, y = rng.gauss(0, 62), rng.gauss(0, 62)
        if math.hypot(x, y) > 140:
            continue
        r = 2.6 if rng.random() < 0.08 else 1.1 + rng.random() * 1.1
        tw = f' class="tw" style="animation-delay:{rng.random() * 4:.1f}s"' if i % 9 == 0 else ""
        dots.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{col}" opacity="0.85"{tw}/>')
    icons = DATA["icons"]
    nodes = []
    for i, ic in enumerate(icons):
        a = i / len(icons) * math.tau - math.pi / 2 + 0.26
        x, y = math.cos(a) * 190, math.sin(a) * 190
        nodes.append((x, y, ic["path"]))
    lines = "".join(
        f"M{n[0]:.1f} {n[1]:.1f}L{m[0]:.1f} {m[1]:.1f}"
        for i, n in enumerate(nodes)
        for m in (nodes[(i + 1) % len(nodes)], nodes[(i + 3) % len(nodes)])
    )
    node_svg = "".join(
        f'<g transform="translate({x:.1f} {y:.1f})"><circle r="19" fill="#0d1119" stroke="rgba(255,255,255,0.12)"/>'
        f'<path d="{p}" transform="translate(-8.5 -8.5) scale(0.708)" fill="{TEXT}"/></g>'
        for x, y, p in nodes
    )
    art = f"""
<rect width="{ART_W}" height="{CH}" fill="url(#br-sky)"/>
<defs><radialGradient id="br-sky" cx="0.2" cy="0" r="1.2"><stop offset="0" stop-color="#1b1730"/><stop offset="0.6" stop-color="{NIGHT}" stop-opacity="0"/></radialGradient></defs>
<g transform="translate({cx} {cy}) scale({s})">
  <path d="{lines}" fill="none" stroke="rgba(255,255,255,0.07)" stroke-width="1"/>
  <g class="br-spin">{''.join(dots)}</g>
  {node_svg}
</g>"""
    css = "@keyframes spin{to{transform:rotate(360deg)}}.br-spin{animation:spin 90s linear infinite}"
    return art, css


def seo_art():
    c = 2 * math.pi * 52
    issues = [(SIGNAL, "Slow LCP – 3.2 s"), (SIGNAL, "4 images without alt"), (AURORA, "Missing canonical")]
    rows = "".join(
        f'<g transform="translate(0 {i * 30})"><circle cx="4" cy="-5" r="4" fill="{col}"/>'
        f'<text x="18" y="0" class="body" font-size="16" fill="{TEXT}">{esc(t)}</text></g>'
        for i, (col, t) in enumerate(issues)
    )
    art = f"""
<g transform="translate(36 72)">
  <rect width="368" height="156" rx="16" fill="rgba(11,14,20,0.7)" stroke="{LINE_SOFT}"/>
  <g transform="translate(84 78) rotate(-90)">
    <circle r="52" fill="none" stroke="{LINE_SOFT}" stroke-width="9"/>
    <circle r="52" fill="none" stroke="{AURORA}" stroke-width="9" stroke-linecap="round" class="ring"
      stroke-dasharray="{c * 0.87:.1f} {c:.1f}"/>
  </g>
  <text x="84" y="92" text-anchor="middle" class="display" font-size="40" fill="{STAR}">87</text>
  <text x="166" y="44" class="mono" font-size="13" fill="{AURORA}">POST /v1/analyze</text>
  <g transform="translate(166 80)">{rows}</g>
</g>"""
    css = f"@keyframes fill{{from{{stroke-dashoffset:{c * 0.87:.1f}}}}}.ring{{animation:fill 1.8s cubic-bezier(.2,.7,.2,1) .3s both}}"
    return art, css


CARDS = {
    "card-boardly.svg": dict(
        idp="b-", art=boardly_art(), kicker="BOARDLY.ONLINE ↗", title="Boardly",
        text="Board games with friends, right in the browser. Make a room, drop the link in the group chat, and everyone is playing in seconds – no download, no sign-up.",
        tags=["Next.js", "Supabase", "Realtime", "TypeScript"],
        label="Boardly – board games with friends in the browser",
    ),
    "card-brain.svg": dict(
        idp="br-", art=brain_art(), kicker="SECOND BRAIN · OPEN SOURCE BOT ↗", title="Second Brain",
        text="My life on autopilot – almost. Claude Code skills, hooks and timers run my Obsidian vault from a Raspberry Pi, with a Telegram bot on top.",
        tags=["Claude", "Python", "Raspberry Pi", "Telegram"],
        label="Second Brain – Claude Code runs an Obsidian vault from a Raspberry Pi",
    ),
    "card-seo.svg": dict(
        idp="s-", art=seo_art(), kicker="SEO AUDIT LAB · LIVE DEMO ↗", title="SEO Analyzer",
        text="Point it at a website and get a full SEO audit back in one API call. FastAPI underneath, a Next.js product on top, sold as an Apify actor.",
        tags=["FastAPI", "Next.js", "Oracle Cloud", "Apify"],
        label="SEO Analyzer – a full SEO audit in one API call",
    ),
}


def main():
    OUT.mkdir(exist_ok=True)
    (OUT / "hero.svg").write_text(hero())
    for name, spec in CARDS.items():
        (OUT / name).write_text(card(**spec))
    for f in sorted(OUT.glob("*.svg")):
        print(f"{f.name:20} {f.stat().st_size / 1024:6.1f} KB")


if __name__ == "__main__":
    main()
