import pandas as pd
import pdfplumber
import re
import io

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            # Iteramos por TODAS las páginas del documento
            for page in pdf.pages:
                texto_pagina = page.extract_text()
                if not texto_pagina:
                    continue
                
                lineas = texto_pagina.split('\n')
                
                for linea in lineas:
                    # Buscamos el código (PK): 5 dígitos (Pernod) o 4-6 en general
                    match_cod = re.search(r'(\d{5})', linea)
                    
                    if match_cod:
                        codigo = match_cod.group(1)
                        
                        # Capturamos todos los precios/números con formato decimal
                        # Esta regex es más robusta para capturar números con o sin símbolo $
                        precios = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))', linea)
                        
                        # Limpiamos la descripción:
                        # Tomamos lo que está DESPUÉS del código y ANTES de los precios
                        temp_desc = linea.split(codigo)[-1]
                        if precios:
                            temp_desc = temp_desc.split(precios[0])[0]
                        
                        desc_limpia = temp_desc.strip()
                        
                        # Solo ignoramos líneas que sean puramente legales (muy largas)
                        if len(linea) < 300: 
                            datos_finales.append({
                                "SENTINEL_PK": codigo,
                                "SENTINEL_DESC": desc_limpia,
                                "PRECIO_BASE": precios[0] if len(precios) > 0 else "",
                                "IVA_VALOR": precios[2] if len(precios) > 2 else "",
                                "PRECIO_FINAL": precios[-1] if len(precios) > 1 else "",
                                "LINEA_COMPLETA": linea
                            })
        
        if not datos_finales:
            return None
            
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
