import pandas as pd
import pyautogui
import time
import os
import shutil
import pygetwindow as gw
import keyboard
import sys

# --- RUTAS ---
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07_Automation_PuTTY"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

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
            print(f"[✅] PuTTY detectado. (ESC para frenar)")
            time.sleep(2)
            return True
        return False
    except: return False

def ejecutar_carga(df, p_c1, p_c2, p_c3):
    if not enfocar_putty(): return False

    # PROCESO DE TEXTO: Trim y Mayúsculas
    pedido_str = str(p_c1).strip()
    obs_str = str(p_c2).strip()
    comando_im = str(p_c3).strip().upper() 

    # 1. ENTRADA: 3 -> 6 -> 1 -> ENTER
    print(">>> Paso 1: Navegación 3-6-1")
    for tecla in ['3', '6', '1']:
        check_abort()
        pyautogui.write(tecla); pyautogui.press('enter'); time.sleep(1.2)

    # 2. CABECERA PEDIDO: C1 -> ENTER -> ENTER
    check_abort()
    print(f">>> Paso 2: Pedido {pedido_str}")
    pyautogui.write(pedido_str)
    pyautogui.press('enter'); time.sleep(0.8)
    pyautogui.press('enter'); time.sleep(1.5)

    # 3. CABECERA OBS: C2 -> ENTER -> ENTER (Doble Enter marcado)
    check_abort()
    print(f">>> Paso 3: Observaciones {obs_str}")
    pyautogui.write(obs_str)
    pyautogui.press('enter'); time.sleep(1.0) # Primer Enter
    pyautogui.press('enter'); time.sleep(2.0) # Segundo Enter para liberar

    # 4. COMANDO MÁGICO: C3 (IM) -> ENTER (ESCRITURA LENTA)
    check_abort()
    print(f">>> Paso 4: Tipeando Comando {comando_im}...")
    # Tipeamos letra por letra con un intervalo de 0.2 segundos
    pyautogui.write(comando_im, interval=0.2) 
    pyautogui.press('enter'); time.sleep(3.5) # Pausa larga para que el sistema cargue

    # 5. RE-VALIDACIÓN: C1 -> ENTER
    check_abort()
    pyautogui.write(pedido_str)
    pyautogui.press('enter'); time.sleep(4.5) 

    # 6. GRILLA: SKU -> 4 ENTERS -> u -> CANT -> ENTER
    print("[ROBOT] Cargando artículos...")
    for i, fila in df.iterrows():
        check_abort()
        if pd.isna(fila[0]): break 
        
        sku = str(int(fila[0]))
        cant = str(int(fila[1]))

        pyautogui.write(sku)
        for _ in range(4):
            pyautogui.press('enter')
            time.sleep(0.3)
        
        pyautogui.write('u')
        pyautogui.write(cant)
        pyautogui.press('enter')
        time.sleep(1.0)
        print(f"   > {sku} OK")

    # 7. FINALIZAR
    pyautogui.press('f5')
    return True

def main():
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]:
        os.makedirs(p, exist_ok=True)

    archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
    if not archivos: return

    archivo = archivos[0]
    ruta = os.path.join(PATH_INPUT, archivo)

    try:
        df = pd.read_excel(ruta, header=None)
        c1, c2, c3 = df.iloc[0, 2], df.iloc[1, 2], df.iloc[2, 2]

        if ejecutar_carga(df, c1, c2, c3):
            shutil.move(ruta, os.path.join(PATH_DONE, f"OK_{archivo}"))
            print("[✅] CARGA EXITOSA")
    except Exception as e:
        print(f"[!] Error: {e}")
        shutil.move(ruta, os.path.join(PATH_REJECTED, f"ERR_{archivo}"))

if __name__ == "__main__":
    main()