"""Genera volantini.json con l'elenco dei file nella cartella volantini/
e la data in cui ciascuno è stato caricato (dalla cronologia git).

Per ogni grafica ancora valida prepara anche, in pagine/<nome>/:
  - copertina.jpg       anteprima leggera per la scheda
  - p-N.jpg             le pagine dei PDF, leggibili su qualsiasi telefono
  - m-N.jpg             le miniature delle pagine per il visualizzatore
  - un'anteprima minuscola (sfocata) scritta direttamente nel JSON
"""
import base64
import datetime
import glob
import io
import json
import os
import re
import subprocess
import unicodedata
from urllib.parse import quote

from PIL import Image

CARTELLA = "volantini"
PAGINE = "pagine"
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".pdf")
LARGHEZZA_PAGINA = 1400      # px: nitida anche ingrandita, leggera col 4G
LARGHEZZA_COPERTINA = 500
LARGHEZZA_MINIATURA = 140
LARGHEZZA_SFOCATA = 24

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
    return re.sub(r"[^A-Za-z0-9]+", "-", base).strip("-") or "grafica"


def web(percorso, versione):
    return percorso.replace(os.sep, "/") + f"?v={versione}"


def sfocata(img):
    """Anteprima minuscola in base64: compare subito, poi arriva quella vera."""
    img = img.convert("RGB")
    img.thumbnail((LARGHEZZA_SFOCATA, LARGHEZZA_SFOCATA * 2))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=60)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def pdftoppm(*argomenti):
    subprocess.run(["pdftoppm", "-jpeg", "-jpegopt", "quality=80,progressive=y", *argomenti],
                   check=True)


def prepara_pdf(percorso, dest, v):
    pdftoppm("-scale-to", str(LARGHEZZA_PAGINA), percorso, os.path.join(dest, "p"))
    pdftoppm("-scale-to", str(LARGHEZZA_MINIATURA), percorso, os.path.join(dest, "m"))
    pdftoppm("-f", "1", "-l", "1", "-singlefile", "-scale-to", str(LARGHEZZA_COPERTINA),
             percorso, os.path.join(dest, "copertina"))
    ordina = lambda f: int(re.search(r"-(\d+)\.jpg$", f).group(1))
    pagine = sorted(glob.glob(os.path.join(dest, "p-*.jpg")), key=ordina)
    mini = sorted(glob.glob(os.path.join(dest, "m-*.jpg")), key=ordina)
    copertina = os.path.join(dest, "copertina.jpg")
    with Image.open(copertina) as im:
        anteprima = sfocata(im)
    misure = []
    for f in pagine:
        with Image.open(f) as im:
            misure.append(list(im.size))
    return {
        "misure": misure,
        "copertina": web(copertina, v),
        "sfocata": anteprima,
        "pagine": [web(p, v) for p in pagine],
        "miniature": [web(m, v) for m in mini],
    }


def prepara_immagine(percorso, nome, dest, v):
    copertina = os.path.join(dest, "copertina.jpg")
    with Image.open(percorso) as im:
        anteprima = sfocata(im.copy())
        im = im.convert("RGB")
        im.thumbnail((LARGHEZZA_COPERTINA, LARGHEZZA_COPERTINA * 3))
        im.save(copertina, "JPEG", quality=80, progressive=True)
    return {
        "copertina": web(copertina, v),
        "sfocata": anteprima,
        "pagine": [f"{CARTELLA}/{quote(nome)}?v={v}"],
    }


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
    if not (al and al < oggi):   # le grafiche scadute non si preparano: non verranno mostrate
        dest = os.path.join(PAGINE, cartella_sicura(nome))
        os.makedirs(dest, exist_ok=True)
        v = voce["aggiunto"] or 0
        try:
            if nome.lower().endswith(".pdf"):
                voce.update(prepara_pdf(percorso, dest, v))
            else:
                voce.update(prepara_immagine(percorso, nome, dest, v))
            print(f"{nome}: {len(voce['pagine'])} pagine")
        except Exception as e:  # file rovinato o formato non leggibile: resta il file originale
            print(f"ATTENZIONE {nome}: {e}")
    voci.append(voce)

with open("volantini.json", "w", encoding="utf-8") as f:
    json.dump(voci, f, ensure_ascii=False, indent=1)

print(f"{len(voci)} grafiche trovate")
