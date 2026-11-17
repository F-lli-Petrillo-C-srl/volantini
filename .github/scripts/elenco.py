"""Genera volantini.json con l'elenco dei file nella cartella volantini/
e la data in cui ciascuno è stato caricato (dalla cronologia git).

Per ogni grafica ancora valida prepara anche, in pagine/<nome>/:
  - copertina.webp      anteprima leggera per la scheda
  - p-N.webp            le pagine dei PDF da sfogliare (nitide su ogni telefono)
  - hd-N.webp           le stesse pagine in alta definizione, caricate solo dalla lente
  - m-N.webp            le miniature delle pagine
  - un'anteprima minuscola (sfocata) scritta direttamente nel JSON
"""
import base64
import datetime
import glob
import io
import json
import os
import re
import shutil
import subprocess
import tempfile
import unicodedata
from urllib.parse import quote

from PIL import Image, features

CARTELLA = "volantini"
PAGINE = "pagine"
ESTENSIONI = (".jpg", ".jpeg", ".png", ".webp", ".gif", ".avif", ".pdf")
LARGHEZZA_HD = 2400          # px: lente, testo piccolo leggibile
LARGHEZZA_PAGINA = 1300      # px: pagina da sfogliare, nitida sugli schermi dei telefoni
LARGHEZZA_COPERTINA = 500   # schede: nitide su telefono, metà del peso di prima
LARGHEZZA_MINIATURA = 160
LARGHEZZA_SFOCATA = 24

WEBP = features.check("webp")
EST = "webp" if WEBP else "jpg"
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


def salva(img, percorso, larghezza, qualita):
    """Ridimensiona alla larghezza voluta (mai ingrandire) e salva in WebP (o JPG)."""
    img = img.convert("RGB")
    if img.width > larghezza:
        img = img.resize((larghezza, round(img.height * larghezza / img.width)), Image.LANCZOS)
    if WEBP:
        img.save(percorso, "WEBP", quality=qualita, method=6)
    else:
        img.save(percorso, "JPEG", quality=qualita, optimize=True, progressive=True)
    return img.size


def sfocata(img):
    """Anteprima minuscola in base64: compare subito, poi arriva quella vera."""
    img = img.convert("RGB")
    img.thumbnail((LARGHEZZA_SFOCATA, LARGHEZZA_SFOCATA * 2))
    buf = io.BytesIO()
    img.save(buf, "JPEG", quality=60)
    return "data:image/jpeg;base64," + base64.b64encode(buf.getvalue()).decode()


def prepara_pdf(percorso, dest, v):
    tmp = tempfile.mkdtemp()
    try:
        # una sola resa ad alta risoluzione (PNG senza perdite), da cui si ricavano tutte le misure
        subprocess.run(["pdftoppm", "-png", "-scale-to", str(LARGHEZZA_HD), percorso,
                        os.path.join(tmp, "r")], check=True)
        rese = sorted(glob.glob(os.path.join(tmp, "r-*.png")),
                      key=lambda f: int(re.search(r"-(\d+)\.png$", f).group(1)))
        pagine, hd, mini, misure = [], [], [], []
        for n, f in enumerate(rese, 1):
            with Image.open(f) as im:
                im.load()
                p_hd = os.path.join(dest, f"hd-{n}.{EST}")
                p_pag = os.path.join(dest, f"p-{n}.{EST}")
                p_min = os.path.join(dest, f"m-{n}.{EST}")
                salva(im, p_hd, LARGHEZZA_HD, 78)
                misure.append(list(salva(im, p_pag, LARGHEZZA_PAGINA, 84)))
                salva(im, p_min, LARGHEZZA_MINIATURA, 70)
                if n == 1:
                    copertina = os.path.join(dest, f"copertina.{EST}")
                    salva(im, copertina, LARGHEZZA_COPERTINA, 80)
                    anteprima = sfocata(im)
            hd.append(web(p_hd, v)); pagine.append(web(p_pag, v)); mini.append(web(p_min, v))
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    return {
        "copertina": web(copertina, v),
        "sfocata": anteprima,
        "pagine": pagine,
        "hd": hd,
        "miniature": mini,
        "misure": misure,
    }


def prepara_immagine(percorso, nome, dest, v):
    copertina = os.path.join(dest, f"copertina.{EST}")
    pagina = os.path.join(dest, f"p-1.{EST}")
    with Image.open(percorso) as im:
        im.load()
        anteprima = sfocata(im.copy())
        salva(im, copertina, LARGHEZZA_COPERTINA, 80)
        misura = salva(im, pagina, LARGHEZZA_PAGINA, 84)
    return {
        "copertina": web(copertina, v),
        "sfocata": anteprima,
        "pagine": [web(pagina, v)],
        "hd": [f"{CARTELLA}/{quote(nome)}?v={v}"],   # la lente usa l'originale
        "misure": [list(misura)],
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

print(f"{len(voci)} grafiche trovate ({EST})")
