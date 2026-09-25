# MATH 245 Interactive Demos

Static HTML/JS demos for MATH 245 (ODEs & Linear Algebra), deployed at
<https://math245-demos.vercel.app>. There is no build step: every page is plain
HTML with libraries loaded from a CDN.

Pushing to `main` deploys automatically through Vercel's GitHub integration.

## Layout

```
public/
  index.html        landing page (card grid, grouped by section)
  style.css         shared styles for every demo page
  <demo-name>/
    index.html      one self-contained demo
vercel.json         serves public/ as-is (no build, no install)
```

## Run locally

```bash
python3 -m http.server 4245 --directory public
```

Then open <http://localhost:4245>. Pages must be served over HTTP (not opened as
`file://`) because links are root-relative (`/cooling/`).

## Adding a demo

1. **Create `public/<demo-name>/index.html`.** Copying an existing demo (e.g.
   `cooling/`) is the fastest start. Keep these conventions:
   - `<link rel="stylesheet" href="../style.css">`
   - KaTeX **0.16.11** (CSS, `katex.min.js` and `auto-render.min.js`, both `defer`)
     and Plotly **2.35.2** — the same versions every other demo uses.
   - `<a class="back-link" href="/">← All Demos</a>` at the top of `.demo-wrap`.
   - Page structure: `.demo-wrap` → `h1` + `p.demo-eq` → `.demo-layout` containing
     `.controls` (with `.ctrl-section` / `.ctrl-row`) and `.plot-panel`
     (with `.plot-box`, `.metrics-row`, `.expander`).
   - Initialize with `window.addEventListener('load', build);` — not an inline
     `build()` call, since KaTeX loads deferred.
   - Math inserted after load must be rendered explicitly:
     `el.innerHTML = '...$x$...'; renderMathInElement(el, {delimiters: [...]})`,
     or `katex.renderToString(...)`.
   - Plotly dark theme: transparent paper, `plot_bgcolor: 'rgba(16,32,56,0.6)'`,
     grid color `#1A304D`. Replace `Infinity`/`NaN` with `null` so Plotly skips the
     point instead of wrecking the axis range.

2. **Add a card to `public/index.html`** in the matching section — Foundations
   (prerequisite math), Block I–IV (course blocks), or Advanced Topics. The
   card's tag names the specific topic (e.g. "1st-Order", "Complex", "Chaos"):

   ```html
   <a class="app-card" href="/<demo-name>/" style="--accent:#4d9fff">
     <div class="icon-tile ic-blue"><span class="icon-sym">∫</span></div>
     <div class="app-name">Demo Title</div>
     <div class="app-tag" style="--accent:#4d9fff">Section Tag</div>
   </a>
   ```

   Icon colors: `ic-blue`, `ic-sky`, `ic-cyan`, `ic-teal`, `ic-emerald`,
   `ic-indigo`, `ic-purple`, `ic-rose`, `ic-orange`, `ic-amber`.
   The "N Apps" count in the header updates itself from the number of cards.

3. **Check it locally**, then commit and push to `main`.

Avoid semester- or year-specific text so the site doesn't need updating each term.
