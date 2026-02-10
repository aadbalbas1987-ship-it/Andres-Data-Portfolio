import pandas as pd
import pdfplumber
import re
import pytesseract
import cv2
import numpy as np
from PIL import Image

# --- UTILERÍA: LIMPIEZA Y EXTRACCIÓN AVANZADA ---
def extraer_datos_de_texto(texto):
    if not texto: return pd.DataFrame()
    
    lineas = texto.split('\n')
    productos = []
    
    # Regex mejorada: Busca números que parezcan precios (ej: 29.700, 1.500,50 o 5000)
    # Soporta separadores de miles y decimales comunes en tickets
    patron_precio = r'(\d{1,3}(?:[.,]\d{3})*(?:[.,]\d{2})?)'
    
    for l in lineas:
        # 1. Limpieza de ruido visual típico de OCR
        l_limpia = re.sub(r'[\.\-_]{2,}', ' ', l) # Elimina líneas de puntos ...........
        l_limpia = re.sub(r'[|\\/_]', ' ', l_limpia).strip()
        
        # 2. Búsqueda de precios
        precios = re.findall(patron_precio, l_limpia)
        if precios:
            precio_f = precios[-1] # El último número suele ser el total de la línea
            
            # Validamos que no sea una fecha o un número corto
            if len(precio_f) >= 2:
                # Extraemos la descripción quitando el precio encontrado
                desc = l_limpia.replace(precio_f, "").replace("$", "").strip()
                
                # Solo guardamos si hay una descripción válida
                if len(desc) > 2:
                    productos.append({
                        "Descripción / Producto": desc.upper(), 
                        "Precio": f"$ {precio_f}"
                    })
                    
    return pd.DataFrame(productos)

# --- PROYECTO 1: ETL (EL LIMPIADOR) ---
def procesar_estandar(file):
    all_rows = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                for row in table:
                    # Limpieza de saltos de línea dentro de celdas
                    clean = [str(c).replace('\n', ' ').strip() if c else "" for c in row]
                    if any(clean): all_rows.append(clean)
    
    if not all_rows: return pd.DataFrame()
    
    df = pd.DataFrame(all_rows)
    
    # Lógica Sentinel: Identificar PK y Descripción
    def extraer_logica_sentinel(row):
        for i, c in enumerate(row):
            # Busca un código numérico de 4 a 8 dígitos (PK)
            m = re.search(r'(\d{4,8})', str(c))
            if m:
                # Si lo encuentra, asume que la siguiente columna es la descripción
                desc = row[i+1] if (i+1) < len(row) else ""
                return pd.Series([m.group(1), str(desc)])
        return pd.Series(["", ""])
    
    df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_logica_sentinel, axis=1)
    return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)

def procesar_excel_csv(file):
    try:
        if file.name.endswith('.csv'):
            return pd.read_csv(file)
        return pd.read_excel(file)
    except Exception as e:
        print(f"Error ETL: {e}")
        return pd.DataFrame()

# --- PROYECTO 2: MONITOR DE GASTOS (VISIÓN ARTIFICIAL) ---

def procesar_pdf_digital(file):
    texto = ""
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto += (page.extract_text() or "") + "\n"
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame()

def procesar_foto_vision(imagen_pil):
    try:
        # Convertimos a OpenCV format
        img = np.array(imagen_pil.convert('RGB'))
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        
        # MEJORA MASTER: Reducción de ruido y aumento de contraste
        # Aplicamos un desenfoque leve para eliminar grano antes del threshold
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        processed = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
            cv2.THRESH_BINARY, 11, 2
        )
        
        # Configuración de Tesseract optimizada para tickets
        custom_config = r'--psm 6 --oem 3'
        texto = pytesseract.image_to_string(processed, lang='spa', config=custom_config)
        
        return extraer_datos_de_texto(texto)
    except Exception as e:
        print(f"Error Visión: {e}")
        return pd.DataFrame()

def procesar_pdf_escaneado_vision(file):
    try:
        with pdfplumber.open(file) as pdf:
            # Procesamos solo la primera página por ahora para velocidad
            page = pdf.pages[0]
            # Convertimos a imagen de alta resolución
            img_pil = page.to_image(resolution=300).original
            return procesar_foto_vision(img_pil)
    except: return pd.DataFrame()
