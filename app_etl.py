import pandas as pd
import pdfplumber
import re

def separar_codigo_descripcion(texto):
    # Detecta códigos alfanuméricos al inicio seguidos de espacio
    match = re.match(r'^(\w?\d+)\s+(.*)', str(texto).strip())
    if match:
        return match.group(1), match.group(2)
    return "", texto

def procesar_lista(file):
    all_data = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    all_data.extend(table)
        
        if not all_data:
            return None

        df = pd.DataFrame(all_data)
        
        # Generar columnas Sentinel basadas en la primera columna del origen
        df[['COD_SENTINEL', 'DESC_SENTINEL']] = df[0].apply(
            lambda x: pd.Series(separar_codigo_descripcion(x))
        )
        
        # Reordenar: Sentinel al principio, resto de columnas después
        cols_sentinel = ['COD_SENTINEL', 'DESC_SENTINEL']
        otras_cols = [c for c in df.columns if c not in cols_sentinel]
        return df[cols_sentinel + otras_cols]
    except Exception as e:
        return None
