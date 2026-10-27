"""Confere, antes de um patch, que cada âncora aparece exatamente uma vez no conteúdo atual do documento.

Uso: python3 -I check-anchors.py parte-1.md [parte-2.md ...] anchors.json
Com várias partes, conta sobre todas juntas (o título de um evento tem que estar em uma parte só).
anchors.json: ["### `checkout_completed`", "| **Total** | **308** |", ...]
Sai com 1 e lista as âncoras com 0 ou 2+ ocorrências.
"""
import json, sys

text = "\n".join(open(path, encoding="utf-8").read() for path in sys.argv[1:-1])
anchors = json.load(open(sys.argv[-1], encoding="utf-8"))
bad = [(a, text.count(a)) for a in anchors if text.count(a) != 1]
for anchor, count in bad:
    print(f"{count}x  {anchor[:90]}")
print(json.dumps({"ancoras": len(anchors), "problemas": len(bad), "caracteres": len(text)}))
sys.exit(1 if bad else 0)
