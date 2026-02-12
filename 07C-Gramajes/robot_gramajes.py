import pandas as pd
import pyautogui
import time
import os
import shutil
import pygetwindow as gw
import keyboard
import sys
import ctypes
import pyperclip 

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07C-Gramajes"
PATH_INPUT_G = os.path.join(BASE_DIR, "input_gramajes") 
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

def forzar_caps_off():
    hllDll = ctypes.WinDLL("User32.dll")
    if hllDll.GetKeyState(0x14) & 0x0001:
        pyautogui.press('capslock')
        time.sleep(0.5)

def check_abort():
    if keyboard.is_pressed('esc'):
        print("\n[🛑] ABORTO MANUAL.")
        sys.exit()

def enfocar_y_centrar_mouse():
    titulo = "35.198.62.182 - PuTTY"
    try:
        ventanas = gw.getWindowsWithTitle(titulo)
        if ventanas:
            win = ventanas[0]
            win.activate()
            centro_x = win.left + (win.width // 2)
            centro_y = win.top + (win.height // 2)
            pyautogui.moveTo(centro_x, centro_y)
            return True
        return False
    except: return False

def pegar_clic_derecho(dato, es_entero=True):
    check_abort()
    try:
        valor = str(int(float(dato))) if es_entero else str(dato)
    except:
        valor = str(dato)
    pyperclip.copy(valor)
    time.sleep(0.2) 
    pyautogui.rightClick()
    time.sleep(0.3)
    pyautogui.press('enter')

def ejecutar_carga_gramajes(df, p_c1, p_c2, p_c3):
    if not enfocar_y_centrar_mouse(): return False
    forzar_caps_off()
    pedido_str = str(int(p_c1)).strip()
    obs_str = str(p_c2).strip()
    comando_im = str(p_c3).strip().upper() 

    for t in ['3', '6', '1']:
        check_abort(); pyautogui.write(t); pyautogui.press('enter'); time.sleep(1.2)

    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(1.2)
    pyautogui.write(obs_str); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(1.8)
    for letra in comando_im:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift'); time.sleep(0.1)
    pyautogui.press('enter'); time.sleep(3.5)
    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(4.5)

    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break
        sku = str(int(fila[0]))
        dato_b = fila[1] 
        dato_d = fila[3] 
        pyautogui.write(sku); time.sleep(0.5)
        for _ in range(4): pyautogui.press('enter'); time.sleep(0.2)
        pyautogui.write('g'); time.sleep(1.5) 
        pegar_clic_derecho(dato_b) 
        time.sleep(0.5)
        pegar_clic_derecho(dato_d, es_entero=False)
        time.sleep(0.8)

    pyautogui.press('f5'); time.sleep(3)
    pyautogui.press('end'); time.sleep(1.5); pyautogui.press('enter'); time.sleep(1.5)
    pyautogui.press('end'); time.sleep(1.5); pyautogui.press('end'); time.sleep(3) 
    return True

def main():
    # --- BLOQUE CON SANGRIÁ CORRECTA ---
    for p in [PATH_INPUT_G, PATH_DONE, PATH_REJECTED]: 
        os.makedirs(p, exist_ok=True)
    
    print(f"\n[*] Robot de Gramajes iniciado.")
    archivos = [f for f in os.listdir(PATH_INPUT_G) if f.endswith('.xlsx')]
    
    if not archivos:
        print("[!] No hay archivos .xlsx en la carpeta.")
        return

    for archivo in archivos:
        check_abort()
        ruta = os.path.join(PATH_INPUT_G, archivo)
        try:
            df = pd.read_excel(ruta, header=None)
            if ejecutar_carga_gramajes(df, df.iloc[0,2], df.iloc[1,2], df.iloc[2,2]):
                shutil.move(ruta, os.path.join(PATH_DONE, f"PESO_OK_{archivo}"))
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()