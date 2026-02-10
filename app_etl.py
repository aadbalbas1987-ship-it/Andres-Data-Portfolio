import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Estrategia de espaciado que te funcionó bien
                table = page.extract_table({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 4,
                })
                if table:
                    for row in table:
                        # Limpiamos cada celda
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        # Solo guardamos si hay algún dato en la fila
                        if any(clean_row): 
                            all_rows.append(clean_row)
        
        if not all_rows:
            return None

        df = pd.DataFrame(all_rows)

        # 1. Filtro de encabezados (Basura legal)
        palabras_basura = ['SUB CATEGORÍA', 'IVA (%)', 'Precio Base', 'Código CAJA', 'relevantes del Código']
        # Filtramos buscando en cualquier columna de la fila
        mask = df.stack().str.contains('|'.join(palabras_basura), case=False, na=False).unstack().any(axis=1)
        df = df[~mask]
        
        # 2. Lógica Sentinel (La que te gustó)
        def extraer_datos_sentinel(row):
            # Buscamos el código de 5 dígitos en las primeras 3 celdas
            for i, cell in enumerate(row[:3]):
                match = re.search(r'(\d{5})', str(cell))
                if match:
                    codigo = match.group(1)
                    # Si el código estaba con texto, extraemos el resto de esa celda
                    desc_propia = str(cell).replace(codigo, "").strip()
                    
                    # Si la celda del código no tenía texto, miramos las siguientes 2 celdas
                    # Esto evita que la descripción salga vacía
                    if len(desc_propia) < 3:
                        # Unimos las siguientes dos columnas para asegurar la descripción completa
                        desc_final = " ".join([str(row[i+1]) if i+1 < len(row) else "", 
                                             str(row[i+2]) if i+2 < len(row) else ""]).strip()
                    else:
                        desc_final = desc_propia
                        
                    return pd.Series([codigo, desc_final])
            return pd.Series(["", ""])

        # Aplicamos la extracción
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_datos_sentinel, axis=1)

        # 3. Limpieza final y orden
        # Solo dejamos filas donde se encontró un código (esto limpia el 99% del ruido)
        df = df[df['SENTINEL_PK'] != ""]

        # Reordenamos: Nuestras columnas primero, luego el resto del PDF
        cols = ['SENTINEL_PK', 'SENTINEL_DESC'] + [c for c in df.columns if c not in ['SENTINEL_PK', 'SENTINEL_DESC']]
        return df[cols]

    except Exception as e:
        return None
