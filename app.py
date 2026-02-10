import streamlit as st
import pandas as pd
from app_etl import procesar_estandar, procesar_complejo, procesar_excel_csv

st.set_page_config(page_title="Andrés Data Portfolio", layout="wide")

st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", ["Inicio", "Proyecto 1: El Limpiador Automático"])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("Bienvenido a mi plataforma de automatización de procesos.")

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
            st.write("### Vista previa de los datos limpios:")
            st.dataframe(df_resultado)

            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Excel Limpio",
                data=csv,
                file_name=f"SENTINEL_limpio_{archivo.name}.csv",
                mime="text/csv",
            )
        else:
            st.error("No pudimos limpiar el archivo. Verifica el formato.")

elif proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor Presupuestario (Escáner)")
    st.write("Toma una foto a una factura o ticket para registrar el gasto.")

    foto = st.camera_input("Capturar Comprobante")

    if foto:
        img = Image.open(foto)
        st.image(img, caption="Foto para procesar", use_container_width=True)
        
        if st.button("Escanear Información"):
            with st.spinner("El motor Sentinel está leyendo la imagen..."):
                datos = procesar_foto(img)
                st.table(datos)

