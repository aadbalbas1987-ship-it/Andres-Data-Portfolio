import pandas as pd
import pdfplumber
import re
import pytesseract
import cv2
import numpy as np
from PIL import Image

# --- MOTORES PROYECTO 1 ---
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

# --- MOTORES PROYECTO 2 (RE-CALIBRADO) ---

def extraer_datos_de_texto(texto):
    lineas = texto.split('\n')
    productos = []
    # Buscamos números de 4 cifras o más (precios tipo 29.700)
    patron_precio = r'(\d{1,3}(?:\.\d{3})*)'
    
    for l in lineas:
        l_limpia = re.sub(r'[|\\/_]', ' ', l).strip()
        precios = re.findall(patron_precio, l_limpia)
        
        if precios:
            precio_f = precios[-1]
            # Solo si el número parece un precio (ej: 29.700 tiene al menos 5 caracteres con el punto)
            if len(precio_f) >= 4:
                desc = l_limpia.replace(precio_f, "").replace("$", "").strip()
                if len(desc) > 2:
                    productos.append({"Descripción / Pack": desc, "Precio": f"$ {precio_f}"})
    
    return pd.DataFrame(productos)

def procesar_pdf_como_foto(file):
    try:
        texto = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto += (page.extract_text() or "") + "\n"
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame()

def procesar_foto(imagen_pil):
    try:
        # 1. Convertir a OpenCV
        img = np.array(imagen_pil.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # 2. FILTRO ADAPTATIVO (La clave para que vuelva a ver)
        # En lugar de un corte fijo, analiza el brillo por bloques
        processed_img = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
        
        # 3. OCR con configuración balanceada
        texto = pytesseract.image_to_string(processed_img, lang='spa', config='--psm 6')
        
        df = extraer_datos_de_texto(texto)
        return df
    except Exception as e:
        return pd.DataFrame([{"Error": str(e)}])
