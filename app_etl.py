import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Extraemos el texto de la página línea por línea, no como tabla
                texto_pagina = page.extract_text()
                if not texto_pagina: continue
                
                lineas = texto_pagina.split('\n')
                
                for linea in lineas:
                    # Buscamos el patrón del código de Pernod (5 dígitos)
                    match_cod = re.search(r'(\d{5})', linea)
                    
                    if match_cod:
                        codigo = match_cod.group(1)
                        # Buscamos todos los precios (números que tienen puntos y comas)
                        # Esta regex busca algo como 16.122,77 o 96.736,62
                        precios = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))', linea)
                        
                        # La descripción es lo que queda entre el código y el primer precio
                        # Limpiamos la línea para sacar la descripción
                        parte_desc = linea.split(codigo)[-1]
                        if precios:
                            parte_desc = parte_desc.split(precios[0])[0]
                        
                        desc_limpia = parte_desc.strip()
                        
                        # Si encontramos datos mínimos, guardamos
                        if codigo and desc_limpia:
                            datos_finales.append({
                                "SENTINEL_PK": codigo,
                                "SENTINEL_DESC": desc_limpia,
                                "PRECIO_BASE": precios[0] if len(precios) > 0 else "",
                                "PRECIO_FINAL": precios[-1] if len(precios) > 1 else "",
                                "LINEA_ORIGINAL": linea # Dejamos la fuente completa por si acaso
                            })
        
        if not datos_finales: return None
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
