import pandas as pd
import pdfplumber
import re
import pytesseract
import cv2
import numpy as np
from PIL import Image

# --- MOTORES P1: PROCESAMIENTO DE LISTAS ---
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

# --- MOTOR P2: AUDITORÍA CON VISIÓN ARTIFICIAL ---

def extraer_datos_de_texto(texto):
    lineas = texto.split('\n')
    data_final = []
    
    # Patrón para precios argentinos (ej: 29.700 o 30.600)
    patron_precio = r'(\d{1,3}(?:\.\d{3})*)'

    for l in lineas:
        # Limpiamos caracteres raros pero mantenemos letras y números
        l_limpia = re.sub(r'[|\\/_]', ' ', l).strip()
        
        # Buscamos números que parezcan precios (mínimo 4 dígitos para evitar años o IDs cortos)
        precios = re.findall(patron_precio, l_limpia)
        
        if precios:
            precio_candidato = precios[-1]
            # Si el número tiene 5 cifras o más, o es un precio lógico de la lista (ej: > 10.000)
            if len(precio_candidato.replace('.', '')) >= 4:
                # Todo lo que NO es el precio es la descripción
                descripcion = l_limpia.replace(precio_candidato, "").replace("$", "").strip()
                
                # Solo agregamos si hay una descripción válida
                if len(descripcion) > 3:
                    data_final.append({
                        "Ítem / Producto": descripcion,
                        "Precio Detectado": f"$ {precio_candidato}"
                    })

    df = pd.DataFrame(data_final)
    
    # Si el DF está vacío, mandamos un mensaje amigable
    if df.empty:
        return pd.DataFrame([{"Aviso": "No se detectaron filas con el formato 'Descripción + Precio'. Intenta una foto más cercana."}])
        
    return df
    
def procesar_pdf_como_foto(file):
    try:
        texto = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto += (page.extract_text() or "") + "\n"
        return extraer_datos_de_texto(texto)
    except: return pd.DataFrame([{"Error": "No se pudo leer el PDF"}])

def procesar_foto(imagen_pil):
    img = np.array(imagen_pil.convert('RGB'))
    gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
    
    # Este paso es CLAVE: aumenta el contraste para que el fondo verde desaparezca
    # y solo queden las letras negras.
    rect, thresh = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY) 
    
    texto = pytesseract.image_to_string(thresh, lang='spa', config='--psm 6')
    return extraer_datos_de_texto(texto)

