import re
import pandas as pd

def motor_limpieza_retail(texto):
    if pd.isna(texto) or texto == "": return ""
    
    # 1. Quitar basura: Elimina códigos tras '(', '/' o '-'
    limpio = re.sub(r'[\(/\-].*', '', str(texto)).strip()
    
    # 2. Nombre Propio (Title Case)
    limpio = limpio.title()
    
    # 3. Homogeneidad de Unidades: X8, X30, etc. (En mayúscula)
    limpio = re.sub(r'\bx\s?(\d+)', r'X\1', limpio, flags=re.IGNORECASE)
    
    # 4. RESTRICCIÓN PUITY: Máximo 40 caracteres
    return limpio[:40].strip()

def clasificar_segun_maestro(descripcion):
    desc = str(descripcion).upper()
    # Mapeo inicial basado en tus fotos
    if any(k in desc for k in ["NOSOTRAS", "TOALLA", "PROTEC"]):
        return 4, 2  # Fam 4: Limpieza, Dep 2: Perfumería
    return 3, 1      # Por defecto: Almacén / Snacks