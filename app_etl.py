import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Usamos una estrategia de 'espaciado' en lugar de 'líneas'
                table = page.extract_table({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 4,
                })
                if table:
                    for row in table:
                        # Limpiamos cada celda de saltos de línea molestos
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        # FILTRO CRÍTICO: Solo guardamos la fila si tiene datos reales
                        # En Pernod, las filas de productos suelen tener el código en la col 1 o 2
                        # y un precio o dato numérico más adelante.
                        if any(clean_row): 
                            all_rows.append(clean_row)
        
        if not all_rows:
            return None

        df = pd.DataFrame(all_rows)

        # --- REGLAS DE ORO PARA PERNOD / DIST ENERO ---
        
        # 1. Eliminar filas que son encabezados repetidos o basura legal
        palabras_basura = ['SUB CATEGORÍA', 'IVA (%)', 'Precio Base', 'Código CAJA', 'relevantes del Código']
        # Filtramos: Si la fila contiene alguna de estas palabras en la primera columna, la borramos
        df = df[~df[0].str.contains('|'.join(palabras_basura), case=False, na=False)]
        
        # 2. Identificar el Código (PK) y la Descripción
        # En este PDF, si la columna 1 tiene un número de 5 dígitos, ese es nuestro código.
        def extraer_datos_sentinel(row):
            # Buscamos un número de 4 a 6 dígitos en las primeras celdas
            for cell in row[:3]:
                match = re.search(r'(\d{4,6})', str(cell))
                if match:
                    # Si encontramos el código, el resto de esa celda o la siguiente es la descripción
                    codigo = match.group(1)
                    desc = str(cell).replace(codigo, "").strip()
                    if len(desc) < 5 and len(row) > 2: # Si la desc quedó corta, probamos la siguiente celda
                        desc = str(row[2])
                    return pd.Series([codigo, desc])
            return pd.Series(["", ""])

        # Aplicamos la lógica para crear las columnas de tu portafolio
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_datos_sentinel, axis=1)

        # 3. Limpieza final: No queremos filas donde no pudimos encontrar ni código ni descripción útil
        df = df[(df['SENTINEL_PK'] != "") | (df['SENTINEL_DESC'] != "")]

        # Reordenar para que lo importante esté al principio
        cols = ['SENTINEL_PK', 'SENTINEL_DESC'] + [c for c in df.columns if c not in ['SENTINEL_PK', 'SENTINEL_DESC']]
        return df[cols]

    except Exception as e:
        return None
