import pandas as pd
import pdfplumber

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # 1. Definimos dónde terminan las columnas (en puntos de PDF)
                # Estos números los ajusté para que calcen con el diseño de Pernod
                # Código (0-60), Descripción (60-230), etc.
                tolerancia = 3
                tabla = page.extract_table({
                    "vertical_strategy": "explicit",
                    "explicit_vertical_lines": [40, 80, 240, 270, 290, 310, 340, 380, 420, 460, 500, 540, 580],
                    "horizontal_strategy": "text",
                    "snap_tolerance": tolerancia,
                })
                
                if tabla:
                    for fila in tabla:
                        # Limpiamos cada celda de ruidos y saltos de línea
                        f = [str(c).replace('\n', ' ').strip() if c else "" for c in fila]
                        
                        # Filtro: Solo nos interesan filas donde el primer o segundo campo sea un código de 5 dígitos
                        es_codigo = any(len(str(x)) == 5 and str(x).isdigit() for x in f[:2])
                        
                        if es_codigo:
                            datos_finales.append({
                                "CODIGO_SENTINEL": f[0] if len(f[0])==5 else f[1],
                                "DESCRIPCION": f[2] if len(f[2]) > 5 else f[3],
                                "TIPO": f[3] if len(f[2]) > 5 else f[4],
                                "PRECIO_BASE": f[7],
                                "PRECIO_FINAL_BOT": f[10],
                                "PRECIO_FINAL_CAJA": f[11]
                            })
        
        if not datos_finales:
            return None
            
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
