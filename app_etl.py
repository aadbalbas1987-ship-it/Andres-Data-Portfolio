import pandas as pd
import pdfplumber
import re

# MOTOR PARA PIPAS Y LISTAS SIMPLES
def procesar_estandar(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table()
                if table:
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(clean_row): all_rows.append(clean_row)
        
        if not all_rows: return None
        df = pd.DataFrame(all_rows)

        # Buscamos códigos de 4 dígitos (como Pipas)
        def extraer_simple(row):
            for i, cell in enumerate(row[:2]):
                match = re.search(r'(\d{4})', str(cell))
                if match:
                    return pd.Series([match.group(1), str(row[i+1])])
            return pd.Series(["", ""])

        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_simple, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except:
        return None

# MOTOR PARA PERNOD RICARD Y LISTAS DIFÍCILES
def procesar_complejo(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Estrategia de texto para PDFs sin líneas
                table = page.extract_table({
                    "vertical_strategy": "text", 
                    "horizontal_strategy": "text", 
                    "snap_tolerance": 4
                })
                if table:
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(clean_row): all_rows.append(clean_row)
        
        if not all_rows: return None
        df = pd.DataFrame(all_rows)

        # Buscamos códigos de 5 dígitos y unimos descripción larga
        def extraer_complejo(row):
            for i, cell in enumerate(row[:3]):
                match = re.search(r'(\d{5})', str(cell))
                if match:
                    codigo = match.group(1)
                    # Unimos las siguientes celdas para no perder la descripción
                    desc = " ".join([str(row[i+1]) if i+1 < len(row) else "", 
                                     str(row[i+2]) if i+2 < len(row) else ""]).strip()
                    return pd.Series([codigo, desc])
            return pd.Series(["", ""])

        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_complejo, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except:
        return None
