import pandas as pd
import pdfplumber
import io

def procesar_lista(file):
    all_data = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Cambiamos la estrategia para que capture TODO lo que parezca tabla
                tables = page.extract_tables()
                for table in tables:
                    if table:
                        all_data.extend(table)
        
        if not all_data:
            return None

        # Creamos el DataFrame inicial
        df = pd.DataFrame(all_data)

        # LIMPIEZA DE SALTOS DE LÍNEA (El error de los espacios vacíos)
        # Esto quita los enters internos que hacen que las filas se vean gigantes o vacías
        df = df.replace(r'\n', ' ', regex=True)

        # ELIMINACIÓN DE FILAS TOTALMENTE VACÍAS
        # Si toda la fila es None o vacío, se va. Si tiene aunque sea un dato, se queda.
        df = df.dropna(how='all').reset_index(drop=True)

        # CREACIÓN DE COLUMNAS SENTINEL (Sin borrar nada)
        # Vamos a llamar SENTINEL_1, 2 y 3 a las primeras tres columnas para que 
        # siempre sepas que ahí suele estar el Código, Descripción y Precio.
        df.insert(0, "SENTINEL_REF_A", df.iloc[:, 0])
        df.insert(1, "SENTINEL_REF_B", df.iloc[:, 1] if len(df.columns) > 1 else "")
        
        return df
    except Exception as e:
        return None
