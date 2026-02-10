import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                texto = page.extract_text()
                if not texto: continue
                
                for linea in texto.split('\n'):
                    # 1. Buscamos el código de 5 dígitos (Nuestro ancla)
                    match_cod = re.search(r'(\d{5})', linea)
                    
                    if match_cod:
                        codigo = match_cod.group(1)
                        
                        # 2. Dividimos la línea en dos: antes del código y después
                        partes = linea.split(codigo)
                        prefijo = partes[0].strip() # A veces la marca está antes del código
                        resto = partes[1].strip()   # Aquí está la descripción y los precios
                        
                        # 3. Limpieza de Precios: 
                        # Buscamos grupos de números que parecen precios (ej: 16.122,77)
                        # Quitamos los "$" para que no molesten
                        linea_sin_dinero = resto.replace('$', '').strip()
                        precios = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))', linea_sin_dinero)
                        
                        # 4. La descripción es lo que queda entre el código y los números
                        descripcion = resto
                        if precios:
                            descripcion = resto.split(precios[0])[0].strip()
                        
                        # Unimos el prefijo (si existe) con la descripción
                        desc_completa = f"{prefijo} {descripcion}".strip()
                        
                        # 5. Guardamos TODO lo que encontramos en la línea
                        datos_finales.append({
                            "CODIGO": codigo,
                            "PRODUCTO": desc_completa,
                            "PRECIO_1": precios[0] if len(precios) > 0 else "",
                            "PRECIO_2": precios[1] if len(precios) > 1 else "",
                            "PRECIO_3": precios[2] if len(precios) > 2 else "",
                            "PRECIO_FINAL": precios[-1] if len(precios) > 1 else "",
                            "DETALLE_ORIGINAL": linea
                        })
        
        if not datos_finales: return None
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
