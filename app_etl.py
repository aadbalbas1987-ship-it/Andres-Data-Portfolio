import pandas as pd
import pdfplumber
import re

# --- MOTORES PDF (Mantener igual que antes) ---
def procesar_estandar(file):
    # (Código de Pipas que ya tenemos)
    ...

def procesar_complejo(file):
    # (Código de Pernod que ya tenemos)
    ...

# --- MOTOR 3: LIMPIADOR EXPRESS (Excel / CSV) ---
def procesar_excel_csv(file):
    try:
        # 1. Carga inteligente
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # 2. LIMPIEZA INMEDIATA
        # Eliminamos filas y columnas que estén 100% vacías
        df = df.dropna(how='all').dropna(axis=1, how='all')
        
        # 3. IDENTIFICACIÓN AUTOMÁTICA SENTINEL
        # Buscamos la primera columna que tenga números (PK) 
        # y la primera que tenga texto largo (Descripción)
        pk_col = ""
        desc_col = ""
        
        for col in df.columns:
            # Si la columna tiene números de más de 3 dígitos, es nuestra PK
            if df[col].astype(str).str.contains(r'\d{3,}').any() and not pk_col:
                pk_col = col
            # Si tiene texto de más de 10 caracteres, es la descripción
            elif df[col].astype(str).str.len().mean() > 10 and not desc_col:
                desc_col = col

        # 4. REESTRUCTURACIÓN
        if pk_col and desc_col:
            # Creamos las columnas Sentinel y las ponemos al principio
            df.insert(0, 'SENTINEL_PK', df[pk_col])
            df.insert(1, 'SENTINEL_DESC', df[desc_col])
            
            # Limpiamos espacios y basura en las nuevas columnas
            df['SENTINEL_PK'] = df['SENTINEL_PK'].astype(str).str.replace(r'\.0$', '', regex=True).str.strip()
            df['SENTINEL_DESC'] = df['SENTINEL_DESC'].astype(str).str.strip()
            
            # Filtramos filas donde la PK no sea un número real (quita encabezados)
            df = df[df['SENTINEL_PK'].str.contains(r'\d')]
            
        return df.reset_index(drop=True)
    except Exception as e:
        print(f"Error en Excel: {e}")
        return None
