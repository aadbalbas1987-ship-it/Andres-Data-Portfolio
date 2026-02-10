import streamlit as st
import pandas as pd
from PIL import Image
from app_etl import procesar_estandar, procesar_complejo, procesar_excel_csv, procesar_foto

st.set_page_config(page_title="Andrés Data Portfolio", layout="wide")

st.sidebar.title("Navegación")
# Aquí definimos las opciones del menú
proyecto = st.sidebar.radio("Ir a:", [
    "Inicio", 
    "Proyecto 1: El Limpiador Automático", 
    "Proyecto 2: Monitor de Ejecución Presupuestaria"
])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("Bienvenido a mi plataforma de automatización de procesos y auditoría forense.")
    st.info("Selecciona un proyecto en el menú lateral para comenzar.")

elif proyecto == "Proyecto 1: El Limpiador Automático":
    st.title("🧹 El Limpiador Automático (ETL)")
    
    tipo_motor = st.selectbox(
        "¿Qué tipo de lista vas a procesar?",
        ["PDF Estándar (Pipas, Arcor, etc.)", 
         "PDF Complejo (Pernod Ricard / DIST)", 
         "Archivo Excel o CSV"]
    )

    formatos = ["pdf"] if "PDF" in tipo_motor else ["xlsx", "csv"]
    archivo = st.file_uploader(f"Sube tu archivo ({', '.join(formatos)})", type=formatos)

    if archivo:
        if tipo_motor == "PDF Estándar (Pipas, Arcor, etc.)":
            df_resultado = procesar_estandar(archivo)
        elif tipo_motor == "PDF Complejo (Pernod Ricard / DIST)":
            df_resultado = procesar_complejo(archivo)
        else:
            df_resultado = procesar_excel_csv(archivo)

        if df_resultado is not None and not df_resultado.empty:
            st.success("¡Limpieza automática completada!")
            st.dataframe(df_resultado)
            
            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Resultado Limpio",
                data=csv,
                file_name=f"sentinel_{archivo.name}.csv",
                mime="text/csv",
            )
        else:
            st.error("No se detectaron datos. Verifica el motor seleccionado.")

elif proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor Presupuestario (Escáner)")
    st.write("Registra tus gastos escaneando comprobantes.")

    # VERSION COMPATIBLE: Quitamos placeholder e index=None
    origen = st.radio(
        "¿Cómo deseas cargar el comprobante?",
        ["Seleccionar después...", "Subir foto de la galería", "Tomar foto con la cámara"]
    )

    archivo_foto = None
    
    if origen == "Tomar foto con la cámara":
        archivo_foto = st.camera_input("Capturar Comprobante")
    
    elif origen == "Subir foto de la galería":
        archivo_foto = st.file_uploader("Selecciona una imagen", type=["jpg", "jpeg", "png"])

    if archivo_foto:
        # El resto del código sigue igual...
        img = Image.open(archivo_foto)
        st.image(img, caption="Imagen cargada", use_container_width=True)
        
        if st.button("🚀 Escanear con Motor Sentinel"):
            with st.spinner("El OCR está leyendo el comprobante..."):
                datos = procesar_foto(img)
                st.table(datos)
