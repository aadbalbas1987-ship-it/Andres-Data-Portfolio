import pandas as pd
import pyautogui
import time
import os
import shutil
from datetime import datetime

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = "07_Automation_PuTTY"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")
LOG_FILE = os.path.join(BASE_DIR, "logs", "audit_log.txt")

def log_event(mensaje):
    """Guarda registro de lo que pasa en un archivo de texto"""
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    with open(LOG_FILE, "a") as f:
        f.write(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {mensaje}\n")

def ejecutar_secuencia_putty(df_items, nro_pedido, observaciones):
    """La secuencia exacta de teclado en la terminal"""
    print(f">>> Iniciando Carga de Pedido: {nro_pedido}")
    print(">>> Tienes 5 segundos para hacer clic en la ventana de PuTTY...")
    time.sleep(5)
    
    # 1. NAVEGACIÓN INICIAL (3 -> 6 -> 1)
    pyautogui.write('3'); pyautogui.press('enter'); time.sleep(0.6)
    pyautogui.write('6'); pyautogui.press('enter'); time.sleep(1.2)
    pyautogui.write('1'); pyautogui.press('enter'); time.sleep(1.2)
    
    # 2. CABECERA
    # Escribir Pedido (C1)
    pyautogui.write(str(nro_pedido)); pyautogui.press('enter')
    time.sleep(0.5)
    pyautogui.press('enter') # Segundo enter según proceso
    
    # Escribir Observaciones (C2)
    pyautogui.write(str(observaciones)); pyautogui.press('enter')
    time.sleep(0.8)
    
    # Validación IM y re-confirmar pedido
    pyautogui.write('IM'); pyautogui.press('enter'); time.sleep(0.6)
    pyautogui.write(str(nro_pedido)); pyautogui.press('enter')
    time.sleep(2.0) # Espera a que abra la grilla de artículos

    # 3. BUCLE DE ARTÍCULOS (Columnas A y B)
    for i, fila in df_items.iterrows():
        # Si la columna A está vacía, terminamos el bucle
        if pd.isna(fila[0]):
            break
            
        sku = str(int(fila[0]))
        cant = str(int(fila[1]))
        
        # Secuencia: SKU -> Enter (x3) -> 'u' -> Cantidad -> Enter
        pyautogui.write(sku)
        pyautogui.press('enter'); time.sleep(1.0) # Validación de SKU en el sistema
        pyautogui.press('enter')
        pyautogui.press('enter')
        
        pyautogui.write('u') # Selección de Unidades
        pyautogui.write(cant) # Ingreso de cantidad
        pyautogui.press('enter')
        time.sleep(0.8) # Pausa entre artículos
        
        print(f"Cargado Item {i+1}: SKU {sku} - Cant {cant} [OK]")

    # 4. CIERRE FINAL
    pyautogui.press('f5')
    print(">>> Carga finalizada con F5.")

def main():
    # Crear carpetas si no existen
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]:
        os.makedirs(p, exist_ok=True)

    # Buscar el primer Excel en la carpeta input
    archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
    
    if not archivos:
        print("Esperando archivo .xlsx en la carpeta /input...")
        return

    archivo = archivos[0]
    ruta_completa = os.path.join(PATH_INPUT, archivo)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    try:
        # Leemos el Excel sin encabezados para usar coordenadas exactas (C1, C2)
        df_raw = pd.read_excel(ruta_completa, header=None)
        
        # C1 es (Fila 0, Columna 2) | C2 es (Fila 1, Columna 2)
        nro_pedido = int(df_raw.iloc[0, 2])
        observaciones = str(df_raw.iloc[1, 2])
        
        # Ejecutamos el robot
        ejecutar_secuencia_putty(df_raw, nro_pedido, observaciones)
        
        # Éxito: Mover a procesados
        shutil.move(ruta_completa, os.path.join(PATH_DONE, f"OK_{timestamp}_{archivo}"))
        log_event(f"SUCCESS: {archivo} procesado correctamente.")
        print(f"✔ Archivo {archivo} movido a 'procesados'.")

    except Exception as e:
        # Error: Mover a rechazados
        shutil.move(ruta_completa, os.path.join(PATH_REJECTED, f"RECHAZADO_{timestamp}_{archivo}"))
        error_msg = f"ERROR en archivo {archivo}: {str(e)}"
        log_event(error_msg)
        print(f"❌ {error_msg}")

if __name__ == "__main__":
    main()
