#!/usr/bin/env python3
from pathlib import Path
from datetime import datetime

DOCS_DIR = "Docs"
ASSETS_DIR = "assets"
CSS_FILE = "styles.css"

def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]

def write_lines(path: Path, lines: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")

def css_lines() -> list[str]:
    return [
        ":root{--bg:#0b1020;--panel:rgba(255,255,255,.06);--text:rgba(255,255,255,.92);--muted:rgba(255,255,255,.72);"
        "--line:rgba(255,255,255,.12);--shadow:0 16px 55px rgba(0,0,0,.35);--r:18px;--max:1100px;}",
        "*{box-sizing:border-box}",
        "body{margin:0;font-family:system-ui,-apple-system,Segoe UI,Roboto,Helvetica,Arial;"
        "background:radial-gradient(1100px 700px at 15% 10%, rgba(99,102,241,.33), transparent 55%),"
        "radial-gradient(900px 600px at 85% 20%, rgba(34,197,94,.18), transparent 55%),"
        "radial-gradient(900px 650px at 70% 90%, rgba(236,72,153,.18), transparent 55%),"
        "linear-gradient(180deg,#070a14 0%,#0b1020 35%,#0b1020 100%);"
        "color:var(--text);line-height:1.5;padding:0}",
        "a{color:inherit;text-decoration:none}",
        ".wrap{max-width:var(--max);margin:0 auto;padding:34px 18px 70px}",
        ".top{display:flex;align-items:center;justify-content:space-between;gap:14px;border:1px solid var(--line);"
        "background:rgba(255,255,255,.04);border-radius:var(--r);padding:14px 16px;box-shadow:var(--shadow);}",
        ".brand{display:flex;align-items:center;gap:12px}",
        ".logo{width:40px;height:40px;border-radius:14px;background:linear-gradient(135deg, rgba(99,102,241,.85), rgba(236,72,153,.55));"
        "border:1px solid rgba(255,255,255,.18)}",
        ".brand h1{margin:0;font-size:16px}",
        ".brand p{margin:0;font-size:13px;color:var(--muted)}",
        ".badges{display:flex;gap:10px;flex-wrap:wrap;justify-content:flex-end}",
        ".badge{font-size:12px;color:var(--muted);padding:6px 10px;border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:999px}",
        ".hero{padding:22px 8px 6px}",
        ".hero h2{font-size:30px;line-height:1.15;margin:18px 0 10px}",
        ".hero p{margin:0;color:var(--muted);max-width:80ch}",
        ".grid{display:grid;grid-template-columns:repeat(12,1fr);gap:14px;margin-top:16px}",
        ".card{grid-column:span 4;min-height:160px;border:1px solid var(--line);background:linear-gradient(180deg, rgba(255,255,255,.06), rgba(255,255,255,.03));"
        "border-radius:var(--r);box-shadow:var(--shadow);padding:18px;transition:transform .12s ease, background .12s ease,border-color .12s ease}",
        ".card:hover{transform:translateY(-2px);background:linear-gradient(180deg, rgba(255,255,255,.08), rgba(255,255,255,.03));border-color:rgba(255,255,255,.22)}",
        ".card h3{margin:0 0 6px;font-size:16px}",
        ".card p{margin:0;color:var(--muted);font-size:13px}",
        ".pillrow{margin-top:12px;display:flex;gap:8px;flex-wrap:wrap}",
        ".pill{font-size:12px;padding:6px 10px;border-radius:999px;border:1px solid rgba(255,255,255,.14);background:rgba(255,255,255,.04);color:rgba(255,255,255,.82)}",
        "@media (max-width:980px){.card{grid-column:span 6}}",
        "@media (max-width:640px){.card{grid-column:span 12}.hero h2{font-size:26px}}",
        ".page{max-width:var(--max);margin:0 auto;padding:26px 18px 70px}",
        ".crumb{margin:18px 0 12px;color:var(--muted);font-size:13px}",
        ".panel{border:1px solid var(--line);background:rgba(255,255,255,.04);border-radius:var(--r);box-shadow:var(--shadow);padding:18px 18px 14px}",
        ".panel h2{margin:6px 0 8px;font-size:24px}",
        ".panel h3{margin:18px 0 6px;font-size:16px}",
        ".panel p{margin:10px 0;color:var(--muted)}",
        ".panel ul{margin:8px 0 14px;padding-left:18px;color:rgba(255,255,255,.88)}",
        ".panel li{margin:6px 0}",
        ".k{padding:10px 12px;border-radius:14px;border:1px solid rgba(255,255,255,.14);background:rgba(0,0,0,.22);"
        "font-family:ui-monospace,SFMono-Regular,Menlo,Monaco,Consolas,'Courier New',monospace;font-size:12px;overflow-x:auto;color:rgba(255,255,255,.88)}",
        "table{width:100%;border-collapse:collapse;margin:10px 0 14px}",
        "th,td{border:1px solid rgba(255,255,255,.12);padding:10px 10px;font-size:13px}",
        "th{background:rgba(255,255,255,.06);text-align:left}",
        "td{color:rgba(255,255,255,.86)}",
        ".footer{margin-top:14px;color:var(--muted);font-size:12px}",
    ]

def html_page(title: str, css_href: str, body: list[str]) -> list[str]:
    return ["<!doctype html>","<html lang='en'>","<head>","<meta charset='utf-8' />","<meta name='viewport' content='width=device-width, initial-scale=1' />",
            f"<title>{title}</title>",f"<link rel='stylesheet' href='{css_href}'>","</head>","<body>"] + body + ["</body>","</html>"]

def topbar(title: str, subtitle: str, right: list[str]) -> list[str]:
    badges = "".join([f"<div class='badge'>{b}</div>" for b in right])
    return ["<div class='top'>","<div class='brand'><div class='logo'></div><div>",
            f"<h1>{title}</h1>",f"<p>{subtitle}</p>","</div></div>",f"<div class='badges'>{badges}</div>","</div>"]

def index_page(repo: str, ts: str) -> list[str]:
    return html_page(f"{repo} Docs", f"{ASSETS_DIR}/{CSS_FILE}", [
        "<div class='wrap'>",
        *topbar(repo + " • Documentation", f"Generated locally • {ts}", ["Cards","HTML + CSS","BDA"]),
        "<div class='hero'><h2>Docs portal</h2><p>Click a card to open real documentation (not stubs).</p></div>",
        "<div class='grid'>",
        "<a class='card' href='bda-strategies.html'><h3>BDA Strategies</h3><p>Usable flows, when to use each, what you must build.</p>"
        "<div class='pillrow'><span class='pill'>W-2</span><span class='pill'>Bank</span><span class='pill'>Blueprints</span></div></a>",
        "<a class='card' href='implementation-roadmap.html'><h3>Implementation Roadmap</h3><p>Prototype → automate → normalize → publish.</p>"
        "<div class='pillrow'><span class='pill'>S3</span><span class='pill'>Lambda</span><span class='pill'>Step Functions</span></div></a>",
        "<a class='card' href='security-privacy.html'><h3>Security &amp; Privacy</h3><p>PII checklist and guardrails for financial docs.</p>"
        "<div class='pillrow'><span class='pill'>KMS</span><span class='pill'>IAM</span><span class='pill'>Retention</span></div></a>",
        "</div>",
        "</div>",
    ])

def bda_strategies_page(repo: str, ts: str) -> list[str]:
    return html_page(f"{repo} • BDA Strategies", f"{ASSETS_DIR}/{CSS_FILE}", [
        "<div class='page'>",
        *topbar(repo + " • BDA Strategies", f"W-2 + bank statement flows • {ts}", ["<a class='badge' href='index.html'>← Home</a>","Blueprints","Automation"]),
        "<div class='crumb'>Home / BDA Strategies</div>",
        "<div class='panel'>",
        "<h2>What you want</h2>",
        "<p>Drop a PDF (W-2 or bank statement) into a workflow and get structured output back (JSON) plus a portal to browse results.</p>",
        "<h3>Do you need to create a blueprint every time?</h3>",
        "<ul><li><b>No.</b> Create a blueprint once per document type and reuse it.</li><li>Create a new blueprint only when layouts differ a lot (e.g., different bank formats).</li></ul>",
        "<h3>Five practical flows</h3>",
        "<table><tr><th>Flow</th><th>Best for</th><th>What you build</th></tr>",
        "<tr><td>A) Console ad-hoc</td><td>Fast testing / learning</td><td>Project + blueprint + manual runs</td></tr>",
        "<tr><td>B) Create once, reuse</td><td>Repeatable extraction</td><td>Blueprint per doc class</td></tr>",
        "<tr><td>C) API-first</td><td>Developer automation</td><td>Service/script calls extraction + stores output</td></tr>",
        "<tr><td>D) Event-driven pipeline</td><td>Production ingestion</td><td>S3 trigger → orchestration → extraction → storage</td></tr>",
        "<tr><td>E) Batch + review</td><td>Highest accuracy</td><td>Validation + human review for flags</td></tr></table>",
        "<h3>Recommended default production flow</h3>",
        "<div class='k'>S3 upload (raw) → trigger (Lambda/Step Functions) → extraction → normalize → store results → publish to portal</div>",
        "<h3>Outputs to standardize</h3>",
        "<ul><li>Raw extracted JSON</li><li>Normalized JSON (your schema)</li><li>Optional HTML summary per doc</li></ul>",
        "<h3>Simple normalized schemas</h3>",
        "<div class='k'>{ \"w2\": {\"tax_year\": 2025, \"employee\": {\"name\":\"...\",\"ssn_last4\":\"1234\"}, \"wages\": {\"box1\":0,\"box2\":0} },"
        " \"bank\": {\"account_last4\":\"1234\", \"period\": {\"start\":\"YYYY-MM-DD\",\"end\":\"YYYY-MM-DD\"}, \"transactions\": [{\"date\":\"...\",\"desc\":\"...\",\"amount\":0}] } }</div>",
        f"<div class='footer'>Generated by tools/generate_docs_portal.py • {ts}</div>",
        "</div></div>",
    ])

def implementation_page(repo: str, ts: str) -> list[str]:
    return html_page(f"{repo} • Implementation Roadmap", f"{ASSETS_DIR}/{CSS_FILE}", [
        "<div class='page'>",
        *topbar(repo + " • Implementation Roadmap", f"Build plan • {ts}", ["<a class='badge' href='index.html'>← Home</a>","Pipeline","Publishing"]),
        "<div class='crumb'>Home / Implementation Roadmap</div>",
        "<div class='panel'>",
        "<h2>Phased roadmap</h2>",
        "<h3>Phase 1 — Prototype</h3><ul><li>Create W-2 + bank blueprints</li><li>Run 5–10 samples</li><li>Define your normalized schema</li></ul>",
        "<h3>Phase 2 — Automation</h3><ul><li>S3 raw upload</li><li>Lambda/Step Functions trigger</li><li>Write extracted JSON to S3</li></ul>",
        "<h3>Phase 3 — Normalize + publish</h3><ul><li>Normalize to your schema</li><li>Publish summary + index pages</li></ul>",
        "<h3>Phase 4 — Scale + quality</h3><ul><li>Retries + alerts</li><li>Validation rules + review flags</li></ul>",
        f"<div class='footer'>Generated by tools/generate_docs_portal.py • {ts}</div>",
        "</div></div>",
    ])

def security_page(repo: str, ts: str) -> list[str]:
    return html_page(f"{repo} • Security & Privacy", f"{ASSETS_DIR}/{CSS_FILE}", [
        "<div class='page'>",
        *topbar(repo + " • Security & Privacy", f"PII guardrails • {ts}", ["<a class='badge' href='index.html'>← Home</a>","PII","KMS","IAM"]),
        "<div class='crumb'>Home / Security &amp; Privacy</div>",
        "<div class='panel'>",
        "<h2>Checklist for financial docs</h2>",
        "<h3>Storage</h3><ul><li>KMS encryption</li><li>Separate raw vs derived outputs</li><li>Lifecycle retention policies</li></ul>",
        "<h3>Access control</h3><ul><li>Least privilege roles</li><li>Prefer SSO/short-lived creds</li><li>Restrict raw PDF downloads</li></ul>",
        "<h3>Audit</h3><ul><li>Audit logging</li><li>Alert on unusual access</li></ul>",
        "<h3>Don’t do this</h3><ul><li>Don’t commit real PDFs to git</li><li>Don’t store full SSNs unless required</li></ul>",
        f"<div class='footer'>Generated by tools/generate_docs_portal.py • {ts}</div>",
        "</div></div>",
    ])

def main() -> int:
    root = repo_root()
    repo = root.name
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    docs = root / DOCS_DIR
    assets = docs / ASSETS_DIR

    write_lines(assets / CSS_FILE, css_lines())
    write_lines(docs / "index.html", index_page(repo, ts))
    write_lines(docs / "bda-strategies.html", bda_strategies_page(repo, ts))
    write_lines(docs / "implementation-roadmap.html", implementation_page(repo, ts))
    write_lines(docs / "security-privacy.html", security_page(repo, ts))

    print("✅ Docs portal generated at:", str(docs))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
