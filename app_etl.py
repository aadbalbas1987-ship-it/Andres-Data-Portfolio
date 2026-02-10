import pandas as pd
import pdfplumber
import re
import pytesseract
import cv2
import numpy as np
from PIL import Image

# --- UTILERÍA: LIMPIEZA DE TEXTO COMÚN ---
def extraer_datos_de_texto(texto):
    lineas = texto.split('\n')
    productos = []
    # Patrón para precios (ej: 29.700)
    patron_precio = r'(\d{1,3}(?:\.\d{3})*)'
    
    for l in lineas:
        # Limpiamos ruido de escaneo (puntos suspensivos largos, barras, etc)
        l_limpia = re.sub(r'[\.\-_]{2,}', ' ', l)
        l_limpia = re.sub(r'[|\\/_]', ' ', l_limpia).strip()
        
        precios = re.findall(patron_precio, l_limpia)
        if precios:
            precio_f = precios[-1]
            if len(precio_f) >= 4:
                desc = l_limpia.replace(precio_f, "").replace("$", "").strip()
                if len(desc) > 3:
                    productos.append({"Descripción / Producto": desc.upper(), "Precio": f"$ {precio_f}"})
    return pd.DataFrame(productos)

# --- PROYECTO 1: ETL ---
def procesar_estandar(file):
    all_rows = []
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

def procesar_complejo(file):
    # (Lógica simplificada para el ejemplo, similar a la anterior)
    return procesar_estandar(file) 

def procesar_excel_csv(file):
    try:
        return pd.read_csv(file) if file.name.endswith('.csv') else pd.read_excel(file)
    except: return pd.DataFrame()

# --- PROYECTO 2: MOTORES MODULARES ---

# MOTOR 1: DIGITAL (Para PDFs con texto seleccionable)
def procesar_pdf_digital(file):
    texto = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += (page.extract_text() or "") + "\n"
    return extraer_datos_de_texto(texto)

# MOTOR 2: ESCÁNER PDF (Para los archivos SCAN que me pasaste)
def procesar_pdf_escaneado_vision(file):
    try:
        with pdfplumber.open(file) as pdf:
            # Convertimos PDF a imagen a 300 DPI para no perder detalle
            page_image = pdf.pages[0].to_image(resolution=300).original
            return procesar_foto_vision(page_image)
    except: return pd.DataFrame()

# MOTOR 3: VISIÓN ARTIFICIAL (OpenCV + Tesseract)
def procesar_foto_vision(imagen_pil):
    try:
        img = np.array(imagen_pil.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # Filtro Adaptativo: clave para resaltar texto en escaneos con sombras
        processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
        
        texto = pytesseract.image_to_string(processed, lang='spa', config='--psm 6')
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame()
