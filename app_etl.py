import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Usamos una tolerancia más alta para que no separe tanto las palabras
                table = page.extract_table({
                    "vertical_strategy": "text",
                    "horizontal_strategy": "text",
                    "snap_tolerance": 5, # Aumentamos para que "suelde" palabras cercanas
                })
                if table:
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(clean_row):
                            all_rows.append(clean_row)
        
        if not all_rows: return None

        df = pd.DataFrame(all_rows)

        # 1. Función para limpiar y pegar números rotos (como "$ 1 6 . 1 2 2")
        def limpiar_numero_roto(texto):
            if not texto: return ""
            # Si detectamos que es un número con espacios locos, quitamos los espacios
            return re.sub(r'(?<=\d)\s+(?=\d)', '', str(texto))

        # Aplicamos la limpieza a todo el DataFrame de una vez
        df = df.applymap(limpiar_numero_roto)

        # 2. Identificar el Código y crear la "Super Descripción"
        def extraer_inteligente(row):
            codigo = ""
            # Buscamos el código de 5 dígitos en las primeras 3 celdas
            for i, cell in enumerate(row[:3]):
                match = re.search(r'(\d{5})', str(cell))
                if match:
                    codigo = match.group(1)
                    break
            
            # La descripción será TODO lo que esté entre la columna 2 y la 8 (donde suelen estar los textos)
            # Esto evita que si se separa en 3 columnas, perdamos info.
            descripcion = " ".join([str(c) for c in row[2:10] if len(str(c)) > 2])
            # Limpiamos si el código se filtró en la descripción
            if codigo: descripcion = descripcion.replace(codigo, "")
            
            return pd.Series([codigo, descripcion.strip()])

        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_inteligente, axis=1)

        # 3. Filtrar y Ordenar
        # Solo nos quedamos con filas que tengan un código de 5 dígitos
        df = df[df['SENTINEL_PK'].str.len() == 5].copy()

        # Reordenamos: Nuestras 2 columnas clave y TODO lo demás tal cual salió del PDF
        cols_finales = ['SENTINEL_PK', 'SENTINEL_DESC'] + [c for c in df.columns if c not in ['SENTINEL_PK', 'SENTINEL_DESC']]
        
        return df[cols_finales]

    except Exception as e:
        return None
