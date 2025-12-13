#!/usr/bin/env python3
from __future__ import annotations

import os
from pathlib import Path
from datetime import datetime

# ---- Config ----
DOCS_DIR_NAME = "Docs"  # change to "docs" if you prefer GitHub Pages /docs convention
ASSETS_DIR = "assets"
CSS_FILE = "styles.css"

# ---- Content ----
STYLES_CSS = r"""
:root{
  --bg: #0b1020;
  --panel: rgba(255,255,255,.06);
  --panel-2: rgba(255,255,255,.09);
  --text: rgba(255,255,255,.92);
  --muted: rgba(255,255,255,.70);
  --line: rgba(255,255,255,.12);
  --shadow: 0 12px 40px rgba(0,0,0,.35);
  --r-xl: 18px;
  --r-lg: 14px;
  --r-md: 12px;
  --max: 1100px;
}

*{box-sizing:border-box}
html,body{height:100%}
body{
  margin:0;
  font-family: ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial, "Apple Color Emoji", "Segoe UI Emoji";
  color: var(--text);
  background:
    radial-gradient(1200px 700px at 15% 10%, rgba(99,102,241,.35), transparent 55%),
    radial-gradient(900px 600px at 85% 20%, rgba(34,197,94,.20), transparent 55%),
    radial-gradient(900px 700px at 70% 90%, rgba(236,72,153,.20), transparent 55%),
    linear-gradient(180deg, #070a14 0%, #0b1020 35%, #0b1020 100%);
  line-height:1.45;
}

a{color:inherit; text-decoration:none}
.container{
  max-width: var(--max);
  margin: 0 auto;
  padding: 36px 20px 60px;
}

.topbar{
  display:flex;
  align-items:center;
  justify-content:space-between;
  gap:14px;
  padding: 14px 16px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.04);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow);
  backdrop-filter: blur(10px);
}

.brand{
  display:flex;
  align-items:center;
  gap:12px;
}
.logo{
  width: 40px; height: 40px;
  border-radius: 14px;
  background:
    linear-gradient(135deg, rgba(99,102,241,.85), rgba(236,72,153,.55)),
    radial-gradient(40px 40px at 65% 35%, rgba(255,255,255,.45), transparent 60%);
  border: 1px solid rgba(255,255,255,.18);
  box-shadow: 0 10px 24px rgba(99,102,241,.20);
}
.brand h1{
  font-size: 16px;
  margin:0;
  letter-spacing: .2px;
}
.brand p{
  margin:0;
  font-size: 13px;
  color: var(--muted);
}

.badges{display:flex; gap:10px; flex-wrap:wrap; justify-content:flex-end}
.badge{
  font-size:12px;
  color: var(--muted);
  padding: 6px 10px;
  border: 1px solid var(--line);
  background: rgba(255,255,255,.04);
  border-radius: 999px;
}

.hero{
  padding: 26px 8px 8px;
}
.hero h2{
  font-size: 30px;
  line-height: 1.15;
  margin: 18px 0 10px;
  letter-spacing:.2px;
}
.hero p{
  margin: 0;
  color: var(--muted);
  max-width: 78ch;
}

.grid{
  margin-top: 18px;
  display:grid;
  grid-template-columns: repeat(12, 1fr);
  gap: 14px;
}

.card{
  grid-column: span 4;
  min-height: 150px;
  border: 1px solid var(--line);
  background: linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));
  border-radius: var(--r-xl);
  box-shadow: var(--shadow);
  overflow:hidden;
  position:relative;
  transition: transform .12s ease, border-color .12s ease, background .12s ease;
}
.card:hover{
  transform: translateY(-2px);
  border-color: rgba(255,255,255,.22);
  background: linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));
}
.card .inner{
  padding: 18px 18px 16px;
}
.card h3{
  margin: 0 0 6px;
  font-size: 16px;
}
.card p{
  margin: 0;
  color: var(--muted);
  font-size: 13px;
}

.card .pillrow{
  margin-top: 12px;
  display:flex;
  gap:8px;
  flex-wrap:wrap;
}
.pill{
  font-size: 12px;
  padding: 6px 10px;
  border-radius: 999px;
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(255,255,255,.04);
  color: rgba(255,255,255,.82);
}

.card::after{
  content:"";
  position:absolute;
  inset:-40px -60px auto auto;
  width:160px; height:160px;
  background: radial-gradient(circle at 30% 30%, rgba(255,255,255,.35), transparent 55%),
              linear-gradient(135deg, rgba(99,102,241,.35), rgba(34,197,94,.18));
  transform: rotate(18deg);
  border-radius: 48px;
  filter: blur(.2px);
  opacity: .9;
}

@media (max-width: 980px){
  .card{grid-column: span 6;}
}
@media (max-width: 640px){
  .card{grid-column: span 12;}
  .hero h2{font-size: 26px;}
}

.page{
  max-width: var(--max);
  margin: 0 auto;
  padding: 26px 20px 60px;
}
.breadcrumbs{
  margin: 18px 0 12px;
  color: var(--muted);
  font-size: 13px;
}
.panel{
  border: 1px solid var(--line);
  background: rgba(255,255,255,.04);
  border-radius: var(--r-xl);
  box-shadow: var(--shadow);
  padding: 18px 18px 14px;
}
.panel h2{margin: 6px 0 8px; font-size: 24px;}
.panel p{margin: 10px 0; color: var(--muted);}
.panel h3{margin: 18px 0 6px; font-size: 16px;}
.panel ul{margin: 8px 0 14px; padding-left: 18px; color: rgba(255,255,255,.86);}
.panel li{margin: 6px 0;}
.code{
  margin: 10px 0 14px;
  padding: 12px 12px;
  border-radius: var(--r-lg);
  border: 1px solid rgba(255,255,255,.14);
  background: rgba(0,0,0,.25);
  overflow-x:auto;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
  font-size: 12px;
  color: rgba(255,255,255,.88);
}
.footer{
  margin-top: 14px;
  color: var(--muted);
  font-size: 12px;
}
"""

def html_shell(title: str, body: str, css_path: str) -> str:
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>{title}</title>
  <link rel="stylesheet" href="{css_path}">
</head>
<body>
{body}
</body>
</html>
"""

def index_html(repo_name: str, generated_at: str) -> str:
    body = f"""
<div class="container">
  <div class="topbar">
    <div class="brand">
      <div class="logo" aria-hidden="true"></div>
      <div>
        <h1>{repo_name} • Documentation</h1>
        <p>Static docs portal generated locally • {generated_at}</p>
      </div>
    </div>
    <div class="badges">
      <div class="badge">Cards</div>
      <div class="badge">HTML + CSS</div>
      <div class="badge">BDA / Blueprints</div>
    </div>
  </div>

  <div class="hero">
    <h2>Project docs, built like a portal.</h2>
    <p>Click a card to open a focused page. Start with <strong>BDA Strategies</strong> to see the recommended document-processing flows for W-2s and bank statements.</p>
  </div>

  <div class="grid">
    <a class="card" href="bda-strategies.html" aria-label="Open BDA Strategies">
      <div class="inner">
        <h3>BDA Strategies</h3>
        <p>Different flows for scanning W-2s and bank statements using Amazon Bedrock Data Automation (BDA): console, reusable blueprints, API, pipelines, and batch review.</p>
        <div class="pillrow">
          <span class="pill">W-2</span>
          <span class="pill">Bank Statements</span>
          <span class="pill">Blueprints</span>
          <span class="pill">Projects</span>
        </div>
      </div>
    </a>

    <div class="card" aria-label="Placeholder - Roadmap">
      <div class="inner">
        <h3>Implementation Roadmap</h3>
        <p>Placeholder card. Add a page later for step-by-step buildout: S3 → BDA → post-processing → portal → export.</p>
        <div class="pillrow">
          <span class="pill">Step Functions</span>
          <span class="pill">Lambda</span>
          <span class="pill">S3</span>
        </div>
      </div>
    </div>

    <div class="card" aria-label="Placeholder - Security">
      <div class="inner">
        <h3>Security &amp; Privacy</h3>
        <p>Placeholder card. Add a page later: PII handling, encryption, retention, access controls, audit logging.</p>
        <div class="pillrow">
          <span class="pill">PII</span>
          <span class="pill">KMS</span>
          <span class="pill">Least privilege</span>
        </div>
      </div>
    </div>
  </div>
</div>
"""
    return html_shell(f"{repo_name} Docs", body, f"{ASSETS_DIR}/{CSS_FILE}")

def bda_strategies_html(repo_name: str, generated_at: str) -> str:
    body = f"""
<div class="page">
  <div class="topbar">
    <div class="brand">
      <div class="logo" aria-hidden="true"></div>
      <div>
        <h1>{repo_name} • BDA Strategies</h1>
        <p>Amazon Bedrock Data Automation • {generated_at}</p>
      </div>
    </div>
    <div class="badges">
      <a class="badge" href="index.html">← Home</a>
      <div class="badge">Blueprints</div>
      <div class="badge">Projects</div>
    </div>
  </div>

  <div class="breadcrumbs">Home / BDA Strategies</div>

  <div class="panel">
    <h2>BDA document scanning flows</h2>
    <p>
      This page explains the common ways to extract structured data from documents like <strong>W-2s</strong> and
      <strong>bank statements</strong> using <strong>Amazon Bedrock Data Automation (BDA)</strong> and <strong>Blueprints</strong>.
      The key idea: you typically create blueprints once and reuse them across many documents.
    </p>

    <h3>Flow A — Console “ad-hoc” (fast testing)</h3>
    <ul>
      <li>Create a BDA project and a blueprint in the AWS console.</li>
      <li>Upload one document, run extraction, inspect the output.</li>
      <li>Best for: learning, demoing, quick validation.</li>
    </ul>

    <h3>Flow B — Create once, reuse forever (recommended)</h3>
    <ul>
      <li>Create a blueprint for each document type (e.g., W-2, Bank Statement).</li>
      <li>Attach blueprints to a project. Run the same project for many documents.</li>
      <li>Best for: repeatable extraction, consistent outputs.</li>
    </ul>

    <h3>Flow C — API-first (no console in daily use)</h3>
    <ul>
      <li>Upload docs to S3 (or provide inputs per your integration).</li>
      <li>Invoke BDA via API from a script/service.</li>
      <li>Store JSON results in S3/DB for downstream processing.</li>
      <li>Best for: automated apps, developer workflows, CI-style processing.</li>
    </ul>

    <h3>Flow D — Event-driven pipeline (production)</h3>
    <ul>
      <li>S3 put event triggers Lambda / Step Functions.</li>
      <li>Pipeline runs BDA, then normalizes output, then stores results.</li>
      <li>Optional: notify user, generate summary report, publish to a portal.</li>
      <li>Best for: hands-off processing at scale.</li>
    </ul>

    <h3>Flow E — Batch + human review (high accuracy)</h3>
    <ul>
      <li>Batch ingest many docs (statements over many months).</li>
      <li>Auto-extract, then apply validation rules.</li>
      <li>Flag uncertain fields for review (human-in-the-loop).</li>
      <li>Best for: compliance, high-confidence financial totals.</li>
    </ul>

    <h3>W-2 vs Bank statements</h3>
    <ul>
      <li><strong>W-2:</strong> tends to be stable/standard → a single blueprint is often enough.</li>
      <li><strong>Bank statements:</strong> layouts vary by bank → you may need multiple blueprints or more flexible post-processing.</li>
    </ul>

    <h3>Suggested repo structure</h3>
    <div class="code">ai016BdaStrategiesDemo/
├── README.md
└── Docs/
    ├── index.html
    ├── bda-strategies.html
    └── assets/
        └── styles.css</div>

    <h3>Next pages to add</h3>
    <ul>
      <li>“W-2 Field Map” (schema & examples)</li>
      <li>“Bank Statement Normalization” (schema, tables, edge cases)</li>
      <li>“Cost & Providers” (where data comes from, pricing notes)</li>
      <li>“Security & Privacy” (PII handling checklist)</li>
    </ul>

    <div class="footer">Generated locally by tools/generate_docs_portal.py • {generated_at}</div>
  </div>
</div>
"""
    return html_shell(f"{repo_name} • BDA Strategies", body, f"{ASSETS_DIR}/{CSS_FILE}")

# ---- Writer ----
def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")

def main() -> int:
    repo_root = Path.cwd()
    repo_name = repo_root.name

    docs_dir = repo_root / DOCS_DIR_NAME
    assets_dir = docs_dir / ASSETS_DIR

    generated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    write_text(assets_dir / CSS_FILE, STYLES_CSS.strip() + "\n")
    write_text(docs_dir / "index.html", index_html(repo_name, generated_at))
    write_text(docs_dir / "bda-strategies.html", bda_strategies_html(repo_name, generated_at))

    print(f"✅ Docs portal generated:")
    print(f"   {docs_dir / 'index.html'}")
    print(f"   {docs_dir / 'bda-strategies.html'}")
    print(f"   {assets_dir / CSS_FILE}")

    print("\nOpen locally:")
    print(f"   open {docs_dir / 'index.html'}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

