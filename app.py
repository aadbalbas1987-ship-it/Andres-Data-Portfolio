import streamlit as st
import pandas as pd
from app_etl import procesar_estandar, procesar_complejo, procesar_excel_csv

st.set_page_config(page_title="Data Portfolio - Andres", layout="wide")

st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", ["Inicio", "Proyecto 1: El Limpiador Automático"])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("Bienvenido a mi portafolio de automatización y auditoría de datos.")

elif proyecto == "Proyecto 1: El Limpiador Automático":
    st.title("🧹 El Limpiador Automático (ETL)")
    
    # MENÚ DE SELECCIÓN DE MOTOR
    tipo_motor = st.selectbox(
        "¿Qué tipo de lista vas a procesar?",
        ["PDF Estándar (Pipas, Arcor, etc.)", 
         "PDF Complejo (Pernod Ricard / DIST)", 
         "Archivo Excel o CSV"]
    )

    # Ajustamos los tipos de archivos permitidos según el motor
    formatos = ["pdf"] if "PDF" in tipo_motor else ["xlsx", "csv"]
    archivo = st.file_uploader(f"Sube tu archivo ({', '.join(formatos)})", type=formatos)

    if archivo:
        st.success("Archivo recibido. Procesando...")
        
        # LÓGICA DE DERIVACIÓN A LOS 3 MOTORES
        if tipo_motor == "PDF Estándar (Pipas, Arcor, etc.)":
            df_resultado = procesar_estandar(archivo)
        elif tipo_motor == "PDF Complejo (Pernod Ricard / DIST)":
            df_resultado = procesar_complejo(archivo)
        else:
            df_resultado = procesar_excel_csv(archivo)

        if df_resultado is not None and not df_resultado.empty:
            st.write("### Vista previa de los datos procesados:")
            st.dataframe(df_resultado)

            csv = df_resultado.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="Descargar Resultado",
                data=csv,
                file_name=f"sentinel_{archivo.name}.csv",
                mime="text/csv",
            )
        else:
            st.error("No se detectaron datos válidos. Verifica el tipo de motor seleccionado.")
