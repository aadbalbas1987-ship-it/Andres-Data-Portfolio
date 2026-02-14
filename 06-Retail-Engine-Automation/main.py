import pandas as pd
from src.normalizer import motor_limpieza_retail, clasificar_segun_maestro

# RUTAS - Asegúrate de poner el CSV en data/raw
input_file = "data/raw/lpcio_mbf.andres - 2026-02-14T110020.632.csv"
output_file = "data/processed/Maestro_Para_Putty.xlsx"

def ejecutar_limpieza():
    print("✨ Iniciando proceso de normalización...")
    try:
        # Leer el CSV original
        df = pd.read_csv(input_file, sep='\t')
        
        # Crear descripción optimizada (Nombre Propio + 40 chars)
        df['DESCRIPCION_NUEVA'] = df['Descripcion'].apply(motor_limpieza_retail)
        
        # Asignar Familia y Depto
        df[['FAM_NUEVA', 'DEP_NUEVO']] = df['Descripcion'].apply(
            lambda x: pd.Series(clasificar_segun_maestro(x))
        )
        
        # Guardar para el robot
        df.to_excel(output_file, index=False)
        print(f"✅ ¡Éxito! Archivo listo en: {output_file}")
        
    except FileNotFoundError:
        print(f"❌ Error: No encontré el archivo en {input_file}")

if __name__ == "__main__":
    ejecutar_limpieza()