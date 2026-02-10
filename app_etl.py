import pandas as pd
import pdfplumber
import re
import pytesseract

# --- MOTORES P1 (IGUALES) ---
def procesar_estandar(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for row in table:
                        clean = [str(c).replace('\n', ' ').strip() if c else "" for c in row]
                        if any(clean): all_rows.append(clean)
        df = pd.DataFrame(all_rows)
        def extraer(row):
            for i, c in enumerate(row[:2]):
                m = re.search(r'(\d{4,8})', str(c))
                if m: return pd.Series([m.group(1), str(row[i+1])])
            return pd.Series(["", ""])
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except: return None

def procesar_complejo(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 4})
                if table:
                    for row in table:
                        clean = [str(c).replace('\n', ' ').strip() if c else "" for c in row]
                        if any(clean): all_rows.append(clean)
        df = pd.DataFrame(all_rows)
        def extraer(row):
            for i, c in enumerate(row[:3]):
                m = re.search(r'(\d{5})', str(c))
                if m: return pd.Series([m.group(1), " ".join([str(row[i+1]), str(row[i+2])]).strip()])
            return pd.Series(["", ""])
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except: return None

def procesar_excel_csv(file):
    try:
        df = pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
        return df.dropna(how='all').dropna(axis=1, how='all')
    except: return None

# --- MOTORES P2 (AUDITORÍA TOTAL) ---

def extraer_datos_de_texto(texto):
    lineas = texto.split('\n')
    productos = []
    patron_precio = r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})|\d+(?:\.\d{2})?)'
    
    for l in lineas:
        precios = re.findall(patron_precio, l)
        if precios:
            precio_f = precios[-1]
            desc = l.replace(precio_f, "").replace("$", "").strip()
            if len(desc) > 2:
                productos.append({"Descripción / Código": desc, "Precio": f"$ {precio_f}"})
    return pd.DataFrame(productos)

def procesar_pdf_como_foto(file):
    try:
        texto = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto += (page.extract_text() or "") + "\n"
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame([{"Error": "No se pudo leer el PDF"}])

def procesar_foto(imagen):
    try:
        texto = pytesseract.image_to_string(imagen, lang='spa')
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame([{"Error": "No se pudo leer la imagen"}])
