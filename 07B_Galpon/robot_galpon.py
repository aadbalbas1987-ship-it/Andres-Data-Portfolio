import pandas as pd
import pyautogui
import time
import os
import shutil
import pygetwindow as gw
import keyboard
import sys
import ctypes

# --- RUTAS ---
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07B_Galpon"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

def forzar_caps_off():
    hllDll = ctypes.WinDLL("User32.dll")
    if hllDll.GetKeyState(0x14) & 0x0001:
        pyautogui.press('capslock')
        time.sleep(0.2) # Tiempo reducido

def check_abort():
    if keyboard.is_pressed('esc'):
        print("\n[🚨] ABORTO MANUAL.")
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
    forzar_caps_off()

    c1 = str(p_c1).strip()
    c2 = str(p_c2).strip().upper()
    c3 = str(p_c3).strip().upper()

    # 1. NAVEGACIÓN (Tiempos reducidos)
    check_abort()
    pyautogui.write('2'); time.sleep(0.3)
    pyautogui.write('2'); pyautogui.press('enter'); time.sleep(0.5)

    # 2. CABECERA
    check_abort()
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(0.3)
    pyautogui.press('enter'); time.sleep(0.5)
    
    # C2 MAYÚSCULAS
    for letra in c2:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift')
    pyautogui.press('enter'); time.sleep(0.3); pyautogui.press('enter'); time.sleep(0.5)

    # C3 MAYÚSCULAS
    for letra in c3:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift')
    pyautogui.press('enter'); time.sleep(1.5) # Reducido de 2.5

    # 3. RE-VALIDACIÓN C1
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(3.0) # Reducido de 4.0

    # 4. GRILLA
    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break
        
        sku = str(int(fila[0]))
        cant = str(int(fila[1]))

        pyautogui.write(sku)
        for _ in range(4):
            pyautogui.press('enter')
            time.sleep(0.1) # Tiempos de grilla mínimos
        
        pyautogui.write('b')
        time.sleep(0.15)
        pyautogui.write(cant)
        pyautogui.press('enter')
        time.sleep(0.3) # Mucho más rápido entre artículos

    # 5. FINALIZACIÓN Y RETORNO AL MENÚ (Secuencia solicitada)
    check_abort()
    pyautogui.press('f5'); time.sleep(1.0)
    pyautogui.hotkey('ctrl', 'l'); time.sleep(0.5)
    
    # Volver al inicio: End, Enter, End
    print("[*] Volviendo al menú principal...")
    pyautogui.press('end'); time.sleep(0.3)
    pyautogui.press('enter'); time.sleep(0.3)
    pyautogui.press('end'); time.sleep(1.0) # Espera final para el próximo archivo
    
    return True

def main():
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]: 
        os.makedirs(p, exist_ok=True)
        
    print(f"[*] Robot Galpón ULTRA-FAST activo.")
    
    while True:
        check_abort()
        archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
        if not archivos:
            time.sleep(2); continue
            
        for archivo in archivos:
            check_abort()
            ruta = os.path.join(PATH_INPUT, archivo)
            try:
                df = pd.read_excel(ruta, header=None)
                if ejecutar_carga_galpon(df, df.iloc[0,2], df.iloc[1,2], df.iloc[2,2]):
                    shutil.move(ruta, os.path.join(PATH_DONE, f"OK_GALPON_{archivo}"))
                    print(f"[✅] Terminado: {archivo}")
            except Exception as e:
                print(f"[❌] Error: {e}")
                shutil.move(ruta, os.path.join(PATH_REJECTED, f"ERR_{archivo}"))

if __name__ == "__main__":
    main()