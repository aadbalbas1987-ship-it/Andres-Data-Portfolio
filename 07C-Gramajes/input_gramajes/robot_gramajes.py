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
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07_Automation_PuTTY"
PATH_INPUT_G = os.path.join(BASE_DIR, "input_gramajes") # <--- CARPETA NUEVA
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
            # IMPORTANTE: Mouse al centro para que el Click Derecho pegue en PuTTY
            centro_x = win.left + (win.width // 2)
            centro_y = win.top + (win.height // 2)
            pyautogui.moveTo(centro_x, centro_y)
            return True
        return False
    except: return False

def pegar_clic_derecho(dato, es_entero=True):
    """Copia al portapapeles y pega usando Clic Derecho"""
    check_abort()
    try:
        # Columna B va como entero (sin .0), Columna D va como está
        valor = str(int(float(dato))) if es_entero else str(dato)
    except:
        valor = str(dato)
    
    pyperclip.copy(valor)
    time.sleep(0.2) # Pausa para que el clipboard procese
    pyautogui.rightClick()
    time.sleep(0.3)
    pyautogui.press('enter')

def ejecutar_carga_gramajes(df, p_c1, p_c2, p_c3):
    if not enfocar_y_centrar_mouse(): return False
    forzar_caps_off()

    # Datos de Cabecera del Código de Oro
    pedido_str = str(int(p_c1)).strip()
    obs_str = str(p_c2).strip()
    comando_im = str(p_c3).strip().upper() 

    # 1. NAVEGACIÓN (3-6-1)
    for t in ['3', '6', '1']:
        check_abort(); pyautogui.write(t); pyautogui.press('enter'); time.sleep(1.2)

    # 2, 3, 4, 5 (Lógica idéntica al Código de Oro para cabecera)
    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(1.2)
    pyautogui.write(obs_str); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(1.8)
    for letra in comando_im:
        pyautogui.keyDown('shift'); pyautogui.press(letra.lower()); pyautogui.keyUp('shift'); time.sleep(0.1)
    pyautogui.press('enter'); time.sleep(3.5)
    pyautogui.write(pedido_str); pyautogui.press('enter'); time.sleep(4.5)

    # 6. GRILLA DE PESABLES (La parte nueva)
    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break
        
        sku = str(int(fila[0]))
        dato_b = fila[1] # Cantidad para ventana g
        dato_d = fila[3] # Gramaje/Dato especial D

        # SKU + 4 Enters
        pyautogui.write(sku); time.sleep(0.5)
        for _ in range(4): pyautogui.press('enter'); time.sleep(0.2)

        # PASO CLAVE: Abrir ventana con 'g' minúscula
        print(f"[*] Procesando SKU {sku} - Abriendo ventana 'g'...")
        pyautogui.write('g'); time.sleep(1.5) 
        
        # PEGAR B EN VENTANA (Usa clic derecho)
        pegar_clic_derecho(dato_b) 
        
        # PEGAR D FUERA DE VENTANA
        time.sleep(0.5)
        pegar_clic_derecho(dato_d, es_entero=False)
        
        time.sleep(0.8)

    # 7. CIERRE (Código de Oro)
    pyautogui.press('f5'); time.sleep(3)
    pyautogui.press('end'); time.sleep(1.5); pyautogui.press('enter'); time.sleep(1.5)
    pyautogui.press('end'); time.sleep(1.5); pyautogui.press('end'); time.sleep(3) 
    return True

def main():
    os.makedirs(PATH_INPUT_G, exist_ok=True)
    archivos = [f for f in os.listdir(PATH_INPUT_G) if f.endswith('.xlsx')]
    
    if not archivos:
        print("[!] Carpeta 'input_gramajes' vacía. Saliendo...")
        return

    for archivo in archivos:
        ruta = os.path.join(PATH_INPUT_G, archivo)
        df = pd.read_excel(ruta, header=None)
        if ejecutar_carga_gramajes(df, df.iloc[0,2], df.iloc[1,2], df.iloc[2,2]):
            shutil.move(ruta, os.path.join(PATH_DONE, f"PESO_OK_{archivo}"))
            print(f"✅ Finalizado: {archivo}")

if __name__ == "__main__":
    main()