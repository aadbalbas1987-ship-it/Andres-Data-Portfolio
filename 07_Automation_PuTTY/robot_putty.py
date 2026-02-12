import pandas as pd
import pyautogui
import time
import os
import shutil
import pygetwindow as gw
import keyboard
import sys
import ctypes

# --- CONFIGURACIÓN DE RUTAS ---
BASE_DIR = r"C:\Users\HP\Desktop\Proyecto\Andres-Data-Portfolio\07_Automation_PuTTY"
PATH_INPUT = os.path.join(BASE_DIR, "input")
PATH_DONE = os.path.join(BASE_DIR, "procesados")
PATH_REJECTED = os.path.join(BASE_DIR, "rechazados")

pyautogui.FAILSAFE = True 

def forzar_caps_off():
    """Asegura que el Bloqueo de Mayúsculas esté apagado"""
    hllDll = ctypes.WinDLL("User32.dll")
    if hllDll.GetKeyState(0x14) & 0x0001:
        pyautogui.press('capslock')
        time.sleep(0.5)

def check_abort():
    """Botón de pánico: Mantener ESC para detener el robot"""
    if keyboard.is_pressed('esc'):
        print("\n[🛑] ABORTO MANUAL DETECTADO (ESC).")
        sys.exit()

def enfocar_putty():
    """Busca la ventana de PuTTY y la trae al frente"""
    titulo = "35.198.62.182 - PuTTY"
    try:
        ventanas = gw.getWindowsWithTitle(titulo)
        if ventanas:
            win = ventanas[0]
            win.activate()
            if win.isMinimized: win.restore()
            return True
        return False
    except:
        return False

def ejecutar_maestro_hibrido(df):
    if not enfocar_putty():
        print("[!] No se encontró la ventana de PuTTY.")
        return False
    
    forzar_caps_off()

    # 1. NAVEGACIÓN AL MENÚ 3-6-1
    check_abort()
    pyautogui.write('3'); time.sleep(0.5)
    pyautogui.write('6'); time.sleep(0.5)
    pyautogui.write('1'); pyautogui.press('enter'); time.sleep(2.0)

    # 2. CARGA DE CABECERA (Datos en Columna C)
    try:
        c1 = str(int(df.iloc[0, 2])) # C1 como Entero
        c2 = str(df.iloc[1, 2]).strip().upper()
        c3 = str(df.iloc[2, 2]).strip().upper()
    except Exception as e:
        print(f"[❌] Error leyendo cabecera: {e}")
        return False

    print(f">>> Cargando cabecera: {c1}, {c2}, {c3}")
    
    # Secuencia: C1, Enter, Enter, C2, Enter, Enter, C3, Enter, C1, Enter
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(0.8)
    check_abort()
    pyautogui.write(c2); pyautogui.press('enter'); time.sleep(0.5); pyautogui.press('enter'); time.sleep(0.8)
    check_abort()
    pyautogui.write(c3); pyautogui.press('enter'); time.sleep(1.5)
    pyautogui.write(c1); pyautogui.press('enter'); time.sleep(2.5)

    # 3. BUCLE DE ARTÍCULOS
    print(">>> Iniciando carga híbrida de artículos...")
    
    for i, fila in df.iterrows():
        check_abort()
        # Si la Columna A (SKU) está vacía, terminamos el archivo
        if pd.isna(fila[0]): 
            break 
        
        sku = str(int(fila[0]))
        dato_b = str(fila[1])
        
        # ANALIZAR ANTES SI EXISTE INFO EN COLUMNA D (índice 3)
        tiene_dato_d = len(fila) > 3 and pd.notna(fila[3]) and str(fila[3]).strip() != ""
        
        # Secuencia Común: SKU + Enter + 4 Enters
        pyautogui.write(sku); pyautogui.press('enter'); time.sleep(1.2)
        for _ in range(4):
            check_abort()
            pyautogui.press('enter'); time.sleep(0.2)

        if not tiene_dato_d:
            # --- MODO UNITARIO ---
            pyautogui.write('u'); pyautogui.press('enter'); time.sleep(0.3)
            pyautogui.write(dato_b); pyautogui.press('enter')
            print(f"📦 [U] SKU {sku} cargado como unidad.")
        else:
            # --- MODO PESABLE ---
            dato_d = str(fila[3]) # El valor float de la columna D
            pyautogui.write('g'); pyautogui.press('enter'); time.sleep(0.8)
            
            # Dentro de la ventana emergente: Dato B
            pyautogui.write(dato_b); pyautogui.press('enter'); time.sleep(0.6)
            
            # Fuera de la ventana: Dato D
            pyautogui.write(dato_d); pyautogui.press('enter')
            print(f"⚖️ [G] SKU {sku} cargado: B={dato_b}, D={dato_d}")

        time.sleep(1.0) # Espera para el siguiente artículo

    # 4. SECUENCIA DE CIERRE FINAL
    check_abort()
    print(">>> Carga finalizada. Volviendo al menú...")
    pyautogui.press('enter'); time.sleep(0.5)
    pyautogui.press('end'); time.sleep(0.5)
    pyautogui.press('end')
    
    return True

def main():
    # Crear carpetas necesarias
    for p in [PATH_INPUT, PATH_DONE, PATH_REJECTED]: 
        os.makedirs(p, exist_ok=True)
    
    print(f"[*] Robot Maestro Híbrido Activo. Carpeta: {PATH_INPUT}")
    
    while True:
        check_abort()
        archivos = [f for f in os.listdir(PATH_INPUT) if f.endswith('.xlsx')]
        
        if not archivos:
            time.sleep(2)
            continue
            
        for archivo in archivos:
            check_abort()
            ruta_completa = os.path.join(PATH_INPUT, archivo)
            print(f"[!] Procesando archivo: {archivo}")
            
            try:
                # Cargar Excel sin cabeceras fijas para leer todas las celdas
                df = pd.read_excel(ruta_completa, header=None)
                
                if ejecutar_maestro_hibrido(df):
                    shutil.move(ruta_completa, os.path.join(PATH_DONE, f"OK_{archivo}"))
                    print(f"[✅] {archivo} procesado con éxito.")
            
            except Exception as e:
                print(f"[❌] Error procesando {archivo}: {e}")
                shutil.move(ruta_completa, os.path.join(PATH_REJECTED, f"ERROR_{archivo}"))
                
        time.sleep(1)

if __name__ == "__main__":
    main()