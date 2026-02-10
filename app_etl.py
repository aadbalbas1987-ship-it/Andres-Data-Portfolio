import pandas as pd
import pdfplumber
import re

def limpiar_precio(valor):
    if not valor: return 0.0
    # Quita $, puntos de miles y cambia coma por punto
    limpio = re.sub(r'[^\d,]', '', str(archivo))
    try:
        return float(limpio.replace(',', '.'))
    except:
        return 0.0

def procesar_lista(file):
    all_data = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Usamos una configuración de tabla más agresiva para Pernod
                table = page.extract_table({
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                })
                if table:
                    all_data.extend(table)
        
        if not all_data:
            return None

        df_raw = pd.DataFrame(all_data)

        # --- MEJORA DE SENSIBILIDAD ---
        # 1. Eliminar filas que son puro ruido (legales o vacías)
        # Filtramos: Solo nos interesan filas donde alguna columna tenga un número de 5 dígitos (típico de Pernod)
        df_filtered = df_raw[df_raw.astype(str).apply(lambda x: x.str.contains(r'\d{5}').any(), axis=1)].copy()

        # 2. Identificar Columnas
        # En Pernod, el código suele estar en la columna 1 y la descripción en la 2
        # Creamos las columnas Sentinel buscando patrones
        df_filtered['SENTINEL_PK'] = df_filtered.iloc[:, 1].astype(str).str.extract(r'(\d+)')[0]
        df_filtered['SENTINEL_DESC'] = df_filtered.iloc[:, 2].fillna('')
        
        # 3. Reordenar y mantener TODO el origen a la derecha
        cols_sentinel = ['SENTINEL_PK', 'SENTINEL_DESC']
        cols_origen = [c for c in df_filtered.columns if c not in cols_sentinel]
        
        df_final = df_filtered[cols_sentinel + cols_origen]
        
        # Limpieza final: eliminar filas donde el código sea nulo
        df_final = df_final.dropna(subset=['SENTINEL_PK'])
        
        return df_final
    except Exception as e:
        print(f"Error: {e}")
        return None
