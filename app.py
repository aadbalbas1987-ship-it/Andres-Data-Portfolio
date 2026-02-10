import streamlit as st
import pandas as pd
from PIL import Image
from app_etl import procesar_estandar, procesar_complejo, procesar_excel_csv, procesar_foto, procesar_pdf_como_foto

st.set_page_config(page_title="Andrés Data Portfolio", layout="wide")

# --- NAVEGACIÓN ---
st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", [
    "Inicio", 
    "Proyecto 1: El Limpiador Automático", 
    "Proyecto 2: Monitor de Ejecución Presupuestaria"
])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("### Plataforma de Automatización y Auditoría Forense")
    st.info("Utilice el menú lateral para navegar entre las herramientas de ETL y Monitoreo.")

# --- PROYECTO 1 ---
elif proyecto == "Proyecto 1: El Limpiador Automático":
    st.title("🧹 El Limpiador Automático (ETL)")
    tipo_motor = st.selectbox("Tipo de lista:", ["PDF Estándar", "PDF Complejo", "Archivo Excel o CSV"])
    
    formatos = ["pdf"] if "PDF" in tipo_motor else ["xlsx", "csv"]
    archivo = st.file_uploader(f"Subir archivo ({', '.join(formatos)})", type=formatos)

    if archivo:
        if tipo_motor == "PDF Estándar": df_res = procesar_estandar(archivo)
        elif tipo_motor == "PDF Complejo": df_res = procesar_complejo(archivo)
        else: df_res = procesar_excel_csv(archivo)

        if df_res is not None and not df_res.empty:
            st.success("Limpieza completada.")
            st.dataframe(df_res, use_container_width=True)
            st.download_button("Descargar CSV", df_res.to_csv(index=False).encode('utf-8'), "limpio.csv", "text/csv")
        else:
            st.error("No se detectaron datos.")

# --- PROYECTO 2 ---
elif proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor Presupuestario (Escáner)")
    st.write("Extraiga códigos, descripciones y precios automáticamente.")

    origen = st.radio("Seleccione origen:", ["Subir archivo (Galería/PDF)", "Tomar foto con la cámara"], index=None)

    archivo_comprobante = None
    if origen == "Tomar foto con la cámara":
        archivo_comprobante = st.camera_input("Capturar")
    elif origen == "Subir archivo (Galería/PDF)":
        archivo_comprobante = st.file_uploader("Imagen o PDF", type=["jpg", "jpeg", "png", "pdf"])

    if archivo_comprobante:
        if st.button("🚀 Escanear con Motor Sentinel"):
            with st.spinner("Mapeando información del documento..."):
                if archivo_comprobante.name.lower().endswith('.pdf'):
                    df_final = procesar_pdf_como_foto(archivo_comprobante)
                else:
                    img = Image.open(archivo_comprobante)
                    df_final = procesar_foto(img)
                
                st.write("### Detalle Detectado")
                st.dataframe(df_final, use_container_width=True)
                
                if not df_final.empty:
                    st.download_button("Exportar Auditoría a Excel", df_final.to_csv(index=False).encode('utf-8'), "auditoria_gasto.csv", "text/csv")
