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
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07_Automation_PuTTY"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

def forzar_caps_off():
    """Detecta si Bloque Mayús está activo y lo apaga"""
    hllDll = ctypes.WinDLL("User32.dll")
    if hllDll.GetKeyState(0x14) & 0x0001:
        print("[⚠️] Detectado Bloque Mayús encendido. Apagándolo automáticamente...")
        pyautogui.press('capslock')
        time.sleep(0.5)

def check_abort():
    if keyboard.is_pressed('esc'):
        print("\n[🛑] ABORTO MANUAL.")
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

def ejecutar_carga(df, p_c1, p_c2, p_c3):
    if not enfocar_putty(): return False
    
    # ASEGURAR MAYÚSCULAS APAGADAS
    forzar_caps_off()

    pedido_str = str(int(p_c1)).strip()
    obs_str = str(p_c2).strip()
    comando_im = str(p_c3).strip().upper() 

    # 1. NAVEGACIÓN
    for t in ['3', '6', '1']:
        check_abort()
        pyautogui.write(t); pyautogui.press('enter'); time.sleep(1.2)

    # 2. PEDIDO C1
    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(0.5)
    pyautogui.press('enter'); time.sleep(1.2)

    # 3. OBSERVACIONES C2
    pyautogui.write(obs_str); pyautogui.press('enter'); time.sleep(0.5)
    pyautogui.press('enter'); time.sleep(1.8)

    # 4. PASO CRÍTICO: IM
    check_abort()
    print(f">>> Enviando comando: {comando_im}")
    for letra in comando_im:
        pyautogui.keyDown('shift')
        pyautogui.press(letra.lower())
        pyautogui.keyUp('shift')
        time.sleep(0.1)
    
    pyautogui.press('enter'); time.sleep(3.5)

    # 5. RE-VALIDACIÓN C1
    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(4.5)

    # 6. GRILLA (UNIDADES)
    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break
        sku, cant = str(int(fila[0])), str(int(fila[1]))
        pyautogui.write(sku)
        for _ in range(4): pyautogui.press('enter'); time.sleep(0.2)
        pyautogui.write('u'); pyautogui.write(cant); pyautogui.press('enter'); time.sleep(0.8)

    # 7. CIERRE (End, Enter, End, End)
    pyautogui.press('f5'); time.sleep(3)
    pyautogui.press('end'); time.sleep(1.5)
    pyautogui.press('enter'); time.sleep(1.5)
    pyautogui.press('end'); time.sleep(1.5)
    pyautogui.press('end'); time.sleep(3) 
    return True

def main():
    # Asegurar que las carpetas existan
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]: 
        os.makedirs(p, exist_ok=True)
    
    # Obtener lista de archivos excel en la carpeta input
    archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
    
    if not archivos:
        print("[!] No se encontraron archivos para procesar. El robot se cerrará.")
        return

    print(f"[*] Iniciando procesamiento de {len(archivos)} archivo(s)...")

    for archivo in archivos:
        check_abort()
        ruta = os.path.join(PATH_INPUT, archivo)
        print(f"\n>>> Trabajando en: {archivo}")
        
        try:
            # Leemos el excel
            df = pd.read_excel(ruta, header=None)
            
            # Ejecutamos la carga usando los datos de la columna C (C1, C2, C3)
            if ejecutar_carga(df, df.iloc[0,2], df.iloc[1,2], df.iloc[2,2]):
                shutil.move(ruta, os.path.join(PATH_DONE, f"OK_{archivo}"))
                print(f"[✅] Finalizado con éxito: {archivo}")
                time.sleep(2)
                
        except Exception as e:
            print(f"[❌] Error procesando {archivo}: {e}")
            shutil.move(ruta, os.path.join(PATH_REJECTED, f"ERR_{archivo}"))

    print("\n[🏁] PROCESO TERMINADO. No quedan más archivos. Hasta pronto.")

if __name__ == "__main__":
    main()