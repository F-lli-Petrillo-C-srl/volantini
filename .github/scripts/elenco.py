"""Genera volantini.json con l'elenco dei file nella cartella volantini/
e la data in cui ciascuno è stato caricato (dalla cronologia git).

Per ogni PDF ancora valido crea anche le immagini delle pagine in pagine/<nome>/,
così il telefono le mostra senza bisogno di un lettore PDF."""
import datetime
import glob
import json
import os
import re
import subprocess
import unicodedata

CARTELLA = "volantini"
PAGINE = "pagine"
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".pdf")
LARGHEZZA_PAGINA = 1400   # px: nitida anche ingrandita, leggera col 4G
LARGHEZZA_COPERTINA = 500

oggi = datetime.date.today()


def scadenza(nome):
    """Data di fine dal nome file (stesse regole della pagina), oppure None."""
    parti = os.path.splitext(nome)[0].split("_")
    date = []
    for p in parti[:2]:
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", p):
            try:
                date.append(datetime.date.fromisoformat(p))
                continue
            except ValueError:
                pass
        break
    if len(date) == 2 and len(parti) >= 3:
        return date[1]
    if date and len(parti) >= 2:
        return date[0]
    return None


def cartella_sicura(nome):
    base = unicodedata.normalize("NFKD", os.path.splitext(nome)[0])
    base = base.encode("ascii", "ignore").decode()
    return re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-") or "pdf"


def immagini_pdf(percorso, nome):
    dest = os.path.join(PAGINE, cartella_sicura(nome))
    os.makedirs(dest, exist_ok=True)
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80,progressive=y",
                    "-scale-to", str(LARGHEZZA_PAGINA), percorso, os.path.join(dest, "p")],
                   check=True)
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80", "-f", "1", "-l", "1",
                    "-singlefile", "-scale-to", str(LARGHEZZA_COPERTINA), percorso,
                    os.path.join(dest, "copertina")], check=True)
    pagine = sorted(glob.glob(os.path.join(dest, "p-*.jpg")))
    return (dest + "/copertina.jpg").replace(os.sep, "/"), [p.replace(os.sep, "/") for p in pagine]


voci = []
for nome in sorted(os.listdir(CARTELLA)):
    if not nome.lower().endswith(ESTENSIONI):
        continue
    percorso = os.path.join(CARTELLA, nome)
    out = subprocess.run(
        ["git", "log", "-1", "--format=%ct", "--", percorso],
        capture_output=True, text=True,
    ).stdout.strip()
    voce = {"file": nome, "aggiunto": int(out) if out else None}
    al = scadenza(nome)
    if nome.lower().endswith(".pdf") and not (al and al < oggi):
        try:
            voce["copertina"], voce["pagine"] = immagini_pdf(percorso, nome)
            print(f"{nome}: {len(voce['pagine'])} pagine")
        except Exception as e:  # PDF rovinato: resta l'icona e il download
            print(f"ATTENZIONE {nome}: {e}")
    voci.append(voce)

with open("volantini.json", "w", encoding="utf-8") as f:
    json.dump(voci, f, ensure_ascii=False, indent=1)

print(f"{len(voci)} grafiche trovate")
