import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Mantenemos la estrategia de texto pero bajamos la tolerancia de quiebre
                table = page.extract_table({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 3,
                })
                if table:
                    for row in table:
                        # Limpieza inicial de saltos de línea
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(clean_row):
                            all_rows.append(clean_row)
        
        if not all_rows: return None

        df = pd.DataFrame(all_rows)

        # --- SOLUCIÓN DE COLUMNAS DISPERSAS ---
        # 1. Unificar Descripción (Columnas 3, 4 y 5)
        # Usamos fillna('') por seguridad y sumamos los textos
        if len(df.columns) >= 6:
            df['SENTINEL_DESC'] = df.iloc[:, 2].astype(str) + " " + df.iloc[:, 3].astype(str) + " " + df.iloc[:, 4].astype(str)
            # Limpiamos espacios dobles creados por la unión
            df['SENTINEL_DESC'] = df['SENTINEL_DESC'].str.replace(r'\s+', ' ', regex=True).str.strip()

        # 2. Unificar Precios y Valores (13+14, 16+17, 18+19, 20+21)
        # Función interna para pegar y quitar espacios locos como "$ 1 6.122" -> "$16122"
        def soldar_y_limpiar(col_a, col_b):
            union = df.iloc[:, col_a].astype(str) + df.iloc[:, col_b].astype(str)
            return union.str.replace(" ", "").str.replace("None", "")

        if len(df.columns) >= 22:
            df['PRECIO_BASE_BOTELLA'] = soldar_y_limpiar(12, 13)
            df['IVA_VALOR'] = soldar_y_limpiar(15, 16)
            df['II_VALOR'] = soldar_y_limpiar(17, 18)
            df['PRECIO_FINAL'] = soldar_y_limpiar(19, 20)

        # 3. Extraer el Código (SENTINEL_PK)
        # Buscamos el código de 5 dígitos en las primeras columnas
        def extraer_pk(row):
            for cell in row[:4]:
                match = re.search(r'(\d{5})', str(cell))
                if match: return match.group(1)
            return ""
        
        df['SENTINEL_PK'] = df.apply(extraer_pk, axis=1)

        # --- LIMPIEZA FINAL DEL RUIDO ---
        # Filtramos solo filas que tengan un código detectado
        df = df[df['SENTINEL_PK'] != ""].copy()

        # Reordenar: Primero nuestras columnas limpias, luego el desastre original por si las dudas
        columnas_finales = ['SENTINEL_PK', 'SENTINEL_DESC', 'PRECIO_BASE_BOTELLA', 'PRECIO_FINAL']
        resto_columnas = [c for c in df.columns if c not in columnas_finales]
        
        return df[columnas_finales + resto_columnas]

    except Exception as e:
        return None
