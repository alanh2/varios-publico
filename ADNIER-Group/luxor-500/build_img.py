#!/usr/bin/env python3
"""Redimensiona los renders a versiones web y genera gallery.js. Correr de nuevo si se agregan fotos."""
import json, re, unicodedata
from pathlib import Path
from PIL import Image

SRC = Path(__file__).resolve().parent.parent
OUT = Path(__file__).resolve().parent / "img"
MAXW = 1600

GROUPS = [
    ("torre", ("Torre y amenidades", "Tower & amenities", "Torre e amenidades"), "Renders torre y amenidades"),
    ("apto", ("Apartamento modelo", "Model apartment", "Apartamento modelo"), "Render apto modelo"),
    ("plantas", ("Plantas", "Floor plans", "Plantas"), "Plantas"),
]

# nombre de archivo -> (es, en, pt). Lo que no esté acá se deriva del nombre del archivo.
CAPS = {
    "19.  PISCINA_N600_LUX3.jpg.jpeg": ("Piscina", "Swimming pool", "Piscina"),
    "V01 PORTACOCHERA_N000_LUX3.jpg": ("Portacochera", "Porte-cochère", "Pórtico de entrada"),
    "V04 GYM_N600_LUX3.jpg": ("Fitness Center", "Fitness Center", "Fitness Center"),
    "V07_KIDS ROOM_N600_LUX3.jpg": ("Kids' Club", "Kids' Club", "Kids' Club"),
    "V06 SALON DE EVENTOS_N600_LUX3.jpg": ("Salón de eventos", "Event Lounge", "Salão de eventos"),
    "V08 CINE_N600_LUX3.jpg": ("Cine privado", "Private cinema", "Cinema privativo"),
    "V13 SPA SALÓN MASAJES_N4900_LUX3.jpg": ("Spa · salón de masajes", "Spa · massage room", "Spa · sala de massagem"),
    "V15 CHEF TABLE_N4900_LUX3.jpg": ("Chef's Table", "Chef's Table", "Chef's Table"),
    "V22_CINE EXTERIOR_N600_LUX3.jpg": ("Cine exterior", "Outdoor cinema", "Cinema ao ar livre"),
    "V23_AÉREA PISCINA_N600_LUX3 (1).jpg": ("Piscina · vista aérea", "Pool · aerial view", "Piscina · vista aérea"),
    "V26_VISTA TORRE_600_LUX3_editada.jpg": ("La torre", "The tower", "A torre"),
    "V27_ZOOM_N4900_LUX3.jpg": ("Detalle de fachada", "Facade detail", "Detalhe da fachada"),
    "V01_SALA BALCON_.jpg": ("Sala y balcón", "Living room & balcony", "Sala e varanda"),
    "V02_COMEDOR COCINA_.jpg": ("Comedor y cocina", "Dining & kitchen", "Sala de jantar e cozinha"),
    "V03_HABITACIÓN PRINCIPAL_.jpg": ("Habitación principal", "Primary bedroom", "Suíte principal"),
    "V04_BANO HABITACIÓN PRINCIPAL_.jpg": ("Baño principal", "Primary bathroom", "Banheiro principal"),
    "PLANTAS LUXOR 500-03.jpg": ("78 m² · 2 recámaras · 2 baños · balcón", "78 m² · 2 bedrooms · 2 baths · balcony", "78 m² · 2 quartos · 2 banheiros · varanda"),
    "PLANTAS LUXOR 500-04.jpg": ("85 m² · 2 recámaras · 2 baños · balcón", "85 m² · 2 bedrooms · 2 baths · balcony", "85 m² · 2 quartos · 2 banheiros · varanda"),
    "PLANTAS LUXOR 500-05.jpg": ("95 m² · 2 recámaras · 2 baños · balcón", "95 m² · 2 bedrooms · 2 baths · balcony", "95 m² · 2 quartos · 2 banheiros · varanda"),
    "PLANTAS LUXOR 500-06.jpg": ("100 m² · 3 recámaras · 2 baños · balcón", "100 m² · 3 bedrooms · 2 baths · balcony", "100 m² · 3 quartos · 2 banheiros · varanda"),
    "PLANTAS LUXOR 500-07.jpg": ("136 m² · 3 recámaras · 2 baños · balcón + MD", "136 m² · 3 bedrooms · 2 baths · balcony + MD", "136 m² · 3 quartos · 2 banheiros · varanda + MD"),
    "PLANTAS LUXOR 500_1.jpg": ("Planta típica · unidades A a F", "Typical floor · units A to F", "Planta tipo · unidades A a F"),
    "PLANTAS LUXOR 500_2.jpg": ("64 m² · 2 recámaras · 2 baños · balcón", "64 m² · 2 bedrooms · 2 baths · balcony", "64 m² · 2 quartos · 2 banheiros · varanda"),
}

def caption(name):
    if name in CAPS:
        es, en, pt = CAPS[name]
    else:
        s = re.sub(r"\.(jpe?g|png)$", "", name, flags=re.I)
        s = re.sub(r"^V?\d+[\s_.-]*", "", s)               # V04 , 19.
        s = re.sub(r"_?N\d+.*$", "", s)                    # _N600_LUX3
        s = re.sub(r"[_.]+", " ", s).replace("LUX3", "")
        s = re.sub(r"\(\d+\)|editada|ajustado", "", s, flags=re.I)
        es = en = pt = re.sub(r"\s+", " ", s).strip(" -_").title() or "Luxor 500"
    return {"es": es, "en": en, "pt": pt}

def slug(name):
    s = unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

gallery = {}
for key, labels, folder in GROUPS:
    items, seen = [], set()
    for f in sorted((SRC / folder).iterdir()):
        if f.suffix.lower() not in (".jpg", ".jpeg", ".png"):
            continue
        cap = caption(f.name)
        if cap["es"] in seen:      # el brochure repite vistas casi idénticas
            continue
        seen.add(cap["es"])
        dst = OUT / f"{key}-{slug(f.stem)}.jpg"
        if not dst.exists():
            im = Image.open(f).convert("RGB")
            if im.width > MAXW:
                im = im.resize((MAXW, round(im.height * MAXW / im.width)), Image.LANCZOS)
            im.save(dst, "JPEG", quality=82, optimize=True, progressive=True)
        items.append({"src": f"img/{dst.name}", "cap": cap})
    gallery[key] = {"label": dict(zip(("es", "en", "pt"), labels)), "items": items}

(Path(__file__).resolve().parent / "gallery.js").write_text(
    "// generado por build_img.py\nconst GALLERY = " + json.dumps(gallery, ensure_ascii=False, indent=2) + ";\n",
    encoding="utf-8")
print({k: len(v["items"]) for k, v in gallery.items()})
