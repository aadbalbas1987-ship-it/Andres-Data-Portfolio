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

# --- MOTOR A: DIGITAL PURO (Rápido y preciso) ---
def procesar_pdf_digital(file):
    texto = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            texto += (page.extract_text() or "") + "\n"
    return extraer_datos_de_texto(texto)

# --- MOTOR B: VISIÓN ARTIFICIAL (Para los PDFs que me pasaste) ---
def procesar_pdf_escaneado_vision(file):
    try:
        # Convertimos la página del PDF a una imagen de alta resolución
        with pdfplumber.open(file) as pdf:
            # 300 DPI es el estándar para auditoría forense
            page_image = pdf.pages[0].to_image(resolution=300).original
            return procesar_foto_vision(page_image)
    except Exception as e:
        return pd.DataFrame([{"Error": f"Fallo en motor de visión: {e}"}])

# --- MOTOR C: PROCESADOR DE IMAGEN (OpenCV) ---
def procesar_foto_vision(imagen_pil):
    # 1. Convertimos a formato de visión artificial
    img = np.array(imagen_pil.convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # 2. Limpieza de ruido (Filtro Adaptativo)
    # Ideal para los archivos SCAN que me pasaste que tienen sombras
    processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                      cv2.THRESH_BINARY, 11, 2)
    
    # 3. OCR con segmentación de líneas
    texto = pytesseract.image_to_string(processed, lang='spa', config='--psm 6')
    return extraer_datos_de_texto(texto)
