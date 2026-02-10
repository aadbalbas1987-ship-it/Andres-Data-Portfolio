import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            # Recorremos todas las páginas
            for page in pdf.pages:
                texto = page.extract_text()
                if not texto: continue
                
                for linea in texto.split('\n'):
                    # 1. Buscamos el código de 5 dígitos (Pernod)
                    match_cod = re.search(r'(\d{5})', linea)
                    
                    if match_cod:
                        codigo = match_cod.group(1)
                        
                        # 2. Separamos la línea usando el código como eje
                        partes = linea.split(codigo)
                        # Lo que está antes del código suele ser la marca o categoría
                        prefijo = partes[0].strip()
                        # Lo que está después es la descripción y los números
                        resto = partes[1].strip()
                        
                        # 3. Identificamos los precios (buscamos el formato 00.000,00)
                        # Limpiamos el símbolo $ y espacios dobles para no confundir al buscador
                        resto_limpio = resto.replace('$', '').replace('  ', ' ')
                        precios = re.findall(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2}))', resto_limpio)
                        
                        # 4. Extraemos la descripción pura
                        # Es lo que queda entre el código y el primer número de precio
                        descripcion = resto
                        if precios:
                            descripcion = resto.split(precios[0])[0].strip()
                        
                        # Unimos marca + descripción para que no quede cortado
                        producto_completo = f"{prefijo} {descripcion}".strip()
                        
                        # 5. Guardamos en columnas separadas
                        if len(producto_completo) > 2:
                            datos_finales.append({
                                "CODIGO_ART": codigo,
                                "DESCRIPCION": producto_completo,
                                "PRECIO_BASE": precios[0] if len(precios) > 0 else "",
                                "PRECIO_FINAL": precios[-1] if len(precios) > 1 else "",
                                "LINEA_ORIGINAL": linea # Siempre dejamos el original para auditoría
                            })

        if not datos_finales:
            return None
            
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
