import streamlit as st
import pandas as pd
from PIL import Image
from app_etl import *

st.set_page_config(page_title="Andrés Data Portfolio", layout="wide")

st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", [
    "Inicio", 
    "Proyecto 1: El Limpiador Automático", 
    "Proyecto 2: Monitor de Ejecución Presupuestaria"
])

# (Sección Inicio y Proyecto 1 igual que antes...)

if proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor de Ejecución Presupuestaria")
    st.write("Escáner Sentinel con Visión Artificial para Auditoría.")

    origen = st.radio("Origen del comprobante:", ["Seleccionar...", "Subir archivo (Galería/PDF)", "Tomar foto con la cámara"])

    archivo_comprobante = None
    if origen == "Tomar foto con la cámara":
        archivo_comprobante = st.camera_input("Capturar")
    elif origen == "Subir archivo (Galería/PDF)":
        archivo_comprobante = st.file_uploader("Imagen o PDF", type=["jpg", "jpeg", "png", "pdf"])

    if archivo_comprobante:
        if st.button("🚀 Ejecutar Auditoría Sentinel"):
            with st.spinner("Procesando con Visión Artificial..."):
                if archivo_comprobante.name.lower().endswith('.pdf'):
                    df_final = procesar_pdf_como_foto(archivo_comprobante)
                else:
                    img = Image.open(archivo_comprobante)
                    df_final = procesar_foto(img)
                
                if not df_final.empty and "Precio" in df_final.columns:
                    st.write("### Detalle Detectado")
                    st.dataframe(df_final, use_container_width=True)
                    
                    # CÁLCULO DE MÉTRICA TOTAL
                    try:
                        # Limpiamos el texto del precio para convertir a número
                        solo_nums = df_final["Precio"].str.replace('$', '').str.replace('.', '').str.replace(',', '.').astype(float)
                        total_sum = solo_nums.sum()
                        st.metric("Total Detectado", f"$ {total_sum:,.2f}")
                    except:
                        st.warning("No se pudo calcular el total automáticamente.")
                else:
                    st.error("No se detectaron datos legibles. Revisa la iluminación de la foto.")
