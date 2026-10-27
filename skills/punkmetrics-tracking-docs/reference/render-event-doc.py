"""Monta a referência de eventos em markdown: resumo, uma seção por área e pedaços prontos para publicar.

Uso: python3 -I render-event-doc.py config.json

config.json:
{
  "catalog_csv": "docs/tracking-plan.csv",          # colunas Event, Description, Context ("P0 · web · core"), Type, Conversion, Parameters
  "details": ["scratch/core.json", "scratch/journey.json"],   # schema em event-entry.md
  "areas": [{"source": "web", "area": "core", "title": "Web · Autenticação", "catalog_path": "src/lib/analytics/catalog/core.ts"}],
  "badges": {"GA4": {"user_signed_up": "sign_up"}, "Amplitude legado até 26/11": {"user_signed_up": "sign_up"}},
  "chunk_limit": 28000,                             # caracteres por pedaço (append); corta só entre eventos
  "intro_md": "docs/events/.source/intro.md",       # opcional: cabeçalho + parte geral (prosa escrita uma vez); {{resumo}} vira a tabela
  "out_dir": "scratch/doc"
}
Sai com erro se faltar detalhe de algum evento, se sobrar detalhe sem evento, ou se um evento cair fora das áreas.
"""
import csv, json, os, sys
from collections import Counter

cfg = json.load(open(sys.argv[1], encoding="utf-8"))
rows = list(csv.DictReader(open(cfg["catalog_csv"], encoding="utf-8", newline="")))
details = {}
for path in cfg["details"]:
    details.update(json.load(open(path, encoding="utf-8")))

def clean(text):
    return " ".join(str(text or "").split())

def context(row):
    prio, source, area = [part.strip() for part in row["Context"].split("·")][:3]
    return prio, source, area

def params(text):
    out = []
    for line in [l for l in (text or "").split("\n") if l.strip()]:
        optional = line.endswith(" (opcional)")
        line = line[: -len(" (opcional)")] if optional else line
        name, _, typ = line.partition(": ")
        out.append((name.strip(), typ.strip(), optional))
    return out

names = {r["Event"] for r in rows}
missing = sorted(names - details.keys())
extra = sorted(details.keys() - names)
known_areas = {(a["source"], a["area"]) for a in cfg["areas"]}
outside = sorted(r["Event"] for r in rows if context(r)[1:] not in known_areas)
if missing or extra or outside:
    sys.exit(json.dumps({"sem_detalhe": missing, "detalhe_sem_evento": extra, "fora_das_areas": outside}, ensure_ascii=False))

def entry(row, prio, source):
    name, d = row["Event"], details[row["Event"]]
    tags = [f"`{prio}`", source]
    if row.get("Conversion") == "yes":
        tags.append("**conversão**")
    if row.get("Type") == "screenview":
        tags.append("screenview")
    for label, mapping in cfg.get("badges", {}).items():
        if name in mapping:
            tags.append(f"{label}: `{mapping[name]}`")
    if source != "web" and d.get("actor"):
        tags.append(f"ator: {clean(d['actor'])}")
    lines = [f"### `{name}`", "", " · ".join(tags), "", clean(row["Description"]), ""]
    lines.append(f"* **Quando dispara:** {clean(d.get('trigger'))}")
    if d.get("where"):
        lines.append(f"* **Onde:** {clean(d['where'])}")
    if d.get("call_site"):
        lines.append(f"* **Código:** `{clean(d['call_site'])}`")
    meaning = {p.get("name"): clean(p.get("meaning")) for p in d.get("props", [])}
    plist = params(row.get("Parameters"))
    if plist:
        lines.append("* **Propriedades:**")
        for pname, ptype, optional in plist:
            label = f"`{pname}`{' (opcional)' if optional else ''} · `{ptype}`"
            lines.append(f"  * {label} — {meaning[pname]}" if meaning.get(pname) else f"  * {label}")
    else:
        lines.append("* **Propriedades:** nenhuma além do contexto.")
    if d.get("notes"):
        lines.append(f"* **Notas:** {clean(d['notes'])}")
    return "\n".join(lines) + "\n"

by_area = {}
for r in rows:
    prio, source, area = context(r)
    by_area.setdefault((source, area), []).append((r, prio))

summary = ["| Área | Eventos | P0 | P1 | P2 |", "| -- | -- | -- | -- | -- |"]
pieces = []
for a in cfg["areas"]:
    items = by_area.get((a["source"], a["area"]), [])
    count = Counter(p for _, p in items)
    summary.append(f"| {a['title']} | {len(items)} | {count['P0']} | {count['P1']} | {count['P2']} |")
    head = f"## {a['title']}\n\n{len(items)} eventos" + (f" · catálogo `{a['catalog_path']}`" if a.get("catalog_path") else "") + "\n"
    pieces.append(head)
    pieces += [entry(r, p, a["source"]) for r, p in items]
total = Counter(context(r)[0] for r in rows)
summary.append(f"| **Total** | **{len(rows)}** | **{total['P0']}** | **{total['P1']}** | **{total['P2']}** |")

os.makedirs(cfg["out_dir"], exist_ok=True)
open(os.path.join(cfg["out_dir"], "summary.md"), "w", encoding="utf-8").write("\n".join(summary) + "\n")
if cfg.get("intro_md"):
    intro = open(cfg["intro_md"], encoding="utf-8").read().replace("{{resumo}}", "\n".join(summary))
    open(os.path.join(cfg["out_dir"], "chunk-00.md"), "w", encoding="utf-8").write(intro.rstrip() + "\n\n")
limit, chunks, current = cfg.get("chunk_limit", 28000), [], ""
for piece in pieces:
    if current and len(current) + len(piece) + 1 > limit:
        chunks.append(current)
        current = ""
    current += piece + "\n"
if current:
    chunks.append(current)
for i, text in enumerate(chunks, 1):
    open(os.path.join(cfg["out_dir"], f"chunk-{i:02d}.md"), "w", encoding="utf-8").write(text)
print(json.dumps({"eventos": len(rows), "pedacos": len(chunks), "caracteres": sum(map(len, chunks)),
                  "por_pedaco": [len(c) for c in chunks]}, ensure_ascii=False))
