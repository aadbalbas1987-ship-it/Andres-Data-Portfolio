import streamlit as st
import pandas as pd
from app_etl import procesar_estandar, procesar_complejo

st.set_page_config(page_title="Data Portfolio - Andres", layout="wide")

st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", ["Inicio", "Proyecto 1: El Limpiador Automático"])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("Bienvenido a mi portafolio de automatización y auditoría de datos.")

elif proyecto == "Proyecto 1: El Limpiador Automático":
    st.title("🧹 El Limpiador Automático (ETL)")
    st.info("Este motor detecta automáticamente códigos de producto y limpia descripciones.")

    # MENÚ DE SELECCIÓN DE MOTOR
    tipo_motor = st.selectbox(
        "¿Qué tipo de lista vas a procesar?",
        ["PDF Estándar (Pipas, Arcor, etc.)", "PDF Complejo (Pernod Ricard / DIST)"]
    )

    archivo = st.file_uploader("Sube tu archivo PDF", type=["pdf"])

    if archivo:
        st.success("Archivo recibido. Procesando...")
        
        # LÓGICA DE DERIVACIÓN
        if tipo_motor == "PDF Estándar (Pipas, Arcor, etc.)":
            df_resultado = procesar_estandar(archivo)
        else:
            df_resultado = procesar_complejo(archivo)

        if df_resultado is not None and not df_resultado.empty:
            st.write("### Vista previa de los datos procesados:")
            st.dataframe(df_resultado)

            # Botón de descarga
            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Excel (CSV)",
                data=csv,
                file_name=f"procesado_{archivo.name}.csv",
                mime="text/csv",
            )
        else:
            st.error("No se detectaron productos. Prueba con el otro motor o verifica el archivo.")
