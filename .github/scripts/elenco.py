"""Genera volantini.json con l'elenco dei file nella cartella volantini/
e la data in cui ciascuno è stato caricato (dalla cronologia git)."""
import json
import os
import subprocess

CARTELLA = "volantini"
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".pdf")

voci = []
for nome in sorted(os.listdir(CARTELLA)):
    if not nome.lower().endswith(ESTENSIONI):
        continue
    percorso = os.path.join(CARTELLA, nome)
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", percorso],
        capture_output=True, text=True,
    ).stdout.strip()
    voci.append({"file": nome, "aggiunto": int(out) if out else None})

with open("volantini.json", "w", encoding="utf-8") as f:
    json.dump(voci, f, ensure_ascii=False, indent=1)

print(f"{len(voci)} grafiche trovate")

