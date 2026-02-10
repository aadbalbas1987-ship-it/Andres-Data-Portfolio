import pandas as pd
import pdfplumber
import re

def procesar_lista(file):
    datos_finales = []
    try:
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                # Extraemos las palabras con sus coordenadas (x, y)
                words = page.extract_words(horizontal_ltr=True, y_tolerance=3)
                
                if not words: continue
                
                # Agrupamos palabras que están en la misma línea (misma 'top')
                lineas = {}
                for w in words:
                    y = float(w['top'])
                    # Agrupamos líneas con una pequeña tolerancia de 2 puntos
                    encontrado = False
                    for line_y in lineas.keys():
                        if abs(y - line_y) < 2:
                            lineas[line_y].append(w)
                            encontrado = True
                            break
                    if not encontrado:
                        lineas[y] = [w]
                
                # Procesamos cada línea detectada
                for y in sorted(lineas.keys()):
                    # Ordenamos palabras de izquierda a derecha
                    palabras_linea = sorted(lineas[y], key=lambda x: x['x0'])
                    
                    # Convertimos a texto simple para buscar el código
                    texto_linea = " ".join([w['text'] for w in palabras_linea])
                    
                    # Buscamos el código de 5 dígitos
                    match_cod = re.search(r'(\d{5})', texto_linea)
                    
                    if match_cod:
                        codigo = match_cod.group(1)
                        
                        # Buscamos los precios (números con coma al final)
                        precios = [w['text'] for w in palabras_linea if re.search(r'\d+,\d{2}', w['text'])]
                        
                        # Identificamos la descripción (palabras entre el código y los precios)
                        desc_parts = []
                        capturar = False
                        for w in palabras_linea:
                            if w['text'] == codigo:
                                capturar = True
                                continue
                            if any(p in w['text'] for p in precios[:1]): # Paramos en el primer precio
                                break
                            if capturar:
                                desc_parts.append(w['text'])
                        
                        desc_final = " ".join(desc_parts).strip()
                        
                        if codigo and desc_final:
                            datos_finales.append({
                                "SENTINEL_PK": codigo,
                                "PRODUCTO": desc_final,
                                "PRECIO_BASE": precios[0] if len(precios) > 0 else "",
                                "PRECIO_FINAL": precios[-1] if len(precios) > 1 else "",
                                "ORIGINAL": texto_linea
                            })

        if not datos_finales: return None
        return pd.DataFrame(datos_finales)

    except Exception as e:
        return None
