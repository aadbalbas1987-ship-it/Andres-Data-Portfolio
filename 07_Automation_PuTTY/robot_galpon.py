import pandas as pd
import pyautogui
import time
import os
import shutil
import pygetwindow as gw
import keyboard
import sys
import ctypes

# --- RUTAS MODIFICADAS PARA GALPÓN ---
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07B_Galpon"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

def forzar_caps_off():
    """Apaga el Bloque Mayús para asegurar que la 'b' salga minúscula"""
    hllDll = ctypes.WinDLL("User32.dll")
    if hllDll.GetKeyState(0x14) & 0x0001:
        pyautogui.press('capslock')
        time.sleep(0.5)

def check_abort():
    if keyboard.is_pressed('esc'):
        print("\n[🛑] ABORTO MANUAL ACTIVADO.")
        sys.exit()

def enfocar_putty():
    titulo = "35.198.62.182 - PuTTY"
    try:
        ventanas = gw.getWindowsWithTitle(titulo)
        if ventanas:
            win = ventanas[0]
            win.activate()
            if win.isMinimized: win.restore()
            return True
        return False
    except: return False

def ejecutar_carga_galpon(df, p_c1, p_c2, p_c3):
    if not enfocar_putty(): return False
    
    # Aseguramos teclado en minúsculas al inicio
    forzar_caps_off()

    c1 = str(p_c1).strip()
    c2 = str(p_c2).strip().upper() # C2 SIEMPRE MAYÚSCULAS
    c3 = str(p_c3).strip().upper() # C3 (IM) SIEMPRE MAYÚSCULAS

    # 1. NAVEGACIÓN GALPÓN: 2 -> 2 -> ENTER
    print(">>> Paso 1: Navegación 2-2-Enter")
    pyautogui.write('2'); time.sleep(0.5)
    pyautogui.write('2'); pyautogui.press('enter'); time.sleep(1.5)

    # 2. CABECERA C1: C1 -> ENTER -> ENTER
    check_abort()
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(0.5)
    pyautogui.press('enter'); time.sleep(1.2)

    # 3. CABECERA C2 (MAYÚSCULAS): C2 -> ENTER -> ENTER
    check_abort()
    print(f">>> Escribiendo C2: {c2}")
    for letra in c2:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift')
    pyautogui.press('enter'); time.sleep(0.5)
    pyautogui.press('enter'); time.sleep(1.2)

    # 4. COMANDO C3 (IM MAYÚSCULAS): C3 -> ENTER
    check_abort()
    print(f">>> Escribiendo C3 (IM): {c3}")
    for letra in c3:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift')
    pyautogui.press('enter'); time.sleep(2.5)

    # 5. RE-VALIDACIÓN C1: C1 -> ENTER
    check_abort()
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(4.0)

    # 6. GRILLA GALPÓN: SKU -> 3 ENTER -> b (minúscula) -> CANT -> ENTER
    print(">>> Cargando artículos en Grilla Galpón...")
    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break
        
        sku = str(int(fila[0]))
        cant = str(int(fila[1]))

        pyautogui.write(sku)
        for _ in range(3):
            pyautogui.press('enter'); time.sleep(0.2)
        
        # LA 'b' ESTRICTAMENTE MINÚSCULA
        pyautogui.write('b'); time.sleep(0.3)
        
        pyautogui.write(cant)
        pyautogui.press('enter'); time.sleep(0.8)

    # 7. FINALIZAR ARCHIVO
    check_abort()
    pyautogui.press('f5')
    print("[✅] Archivo procesado correctamente.")
    return True

def main():
    # Creamos las carpetas si no existen
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]:
        os.makedirs(p, exist_ok=True)
    
    print(f"[*] Robot Galpón iniciado. Escuchando en: {PATH_INPUT}")
    
    while True:
        archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
        
        if not archivos:
            time.sleep(5)
            check_abort()
            continue

        for archivo_nombre in archivos:
            check_abort()
            ruta_full = os.path.join(PATH_INPUT, archivo_nombre)
            
            try:
                df = pd.read_excel(ruta_full, header=None)
                print(f"\n[PROCESANDO] -> {archivo_nombre}")
                
                if ejecutar_carga_galpon(df, df.iloc[0,2], df.iloc[1,2], df.iloc[2,2]):
                    shutil.move(ruta_full, os.path.join(PATH_DONE, f"OK_GALPON_{archivo_nombre}"))
                    print(f"[✅] Movido a procesados.")
                    time.sleep(2)
            
            except Exception as e:
                print(f"[❌] Error en {archivo_nombre}: {e}")
                shutil.move(ruta_full, os.path.join(PATH_REJECTED, f"ERR_GALPON_{archivo_nombre}"))

if __name__ == "__main__":
    main()