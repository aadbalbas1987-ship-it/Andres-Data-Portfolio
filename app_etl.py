import pandas as pd
import pdfplumber
import re

# --- MOTOR 1: PDF ESTÁNDAR (Pipas) ---
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
        def extraer_simple(row):
            for i, cell in enumerate(row[:2]):
                match = re.search(r'(\d{4,8})', str(cell))
                if match: return pd.Series([match.group(1), str(row[i+1])])
            return pd.Series(["", ""])
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_simple, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except: return None

# --- MOTOR 2: PDF COMPLEJO (Pernod Ricard) ---
def procesar_complejo(file):
    all_rows = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                table = page.extract_table({"vertical_strategy": "text", "horizontal_strategy": "text", "snap_tolerance": 4})
                if table:
                    for row in table:
                        clean_row = [str(cell).replace('\n', ' ').strip() if cell else "" for cell in row]
                        if any(clean_row): all_rows.append(clean_row)
        if not all_rows: return None
        df = pd.DataFrame(all_rows)
        def extraer_complejo(row):
            for i, cell in enumerate(row[:3]):
                match = re.search(r'(\d{5})', str(cell))
                if match:
                    codigo = match.group(1)
                    desc = " ".join([str(row[i+1]), str(row[i+2])]).strip()
                    return pd.Series([codigo, desc])
            return pd.Series(["", ""])
        df[['SENTINEL_PK', 'SENTINEL_DESC']] = df.apply(extraer_complejo, axis=1)
        return df[df['SENTINEL_PK'] != ""].reset_index(drop=True)
    except: return None

# --- MOTOR 3: EXCEL O CSV (Limpiador Directo) ---
def procesar_excel_csv(file):
    try:
        # Detectar si es CSV o Excel
        if file.name.endswith('.csv'):
            df = pd.read_csv(file)
        else:
            df = pd.read_excel(file)
        
        # En Excel, buscamos la columna que tenga números largos (códigos)
        # y la primera que tenga texto largo (descripción)
        df.insert(0, 'SENTINEL_PK', df.iloc[:, 0]) # Asumimos col 1 como PK
        df.insert(1, 'SENTINEL_DESC', df.iloc[:, 1]) # Asumimos col 2 como Desc
        
        return df
    except:
        return None
