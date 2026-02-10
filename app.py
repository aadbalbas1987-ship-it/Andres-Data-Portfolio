import streamlit as st
import io
import pandas as pd
from app_etl import procesar_lista

st.set_page_config(page_title="Portfolio Andrés Balbas", layout="wide")

# Navegación
st.sidebar.title("Navegación")
seleccion = st.sidebar.radio("Proyectos:", ["Inicio", "Proyecto 1: ETL"])

if seleccion == "Inicio":
    st.title("Data Portfolio - Andrés Balbas")
    st.write("Bienvenido. Este espacio presenta soluciones técnicas para auditoría y finanzas.")

elif seleccion == "Proyecto 1: ETL":
    st.title("Estandarizador de Listas de Precios")
    archivo = st.file_uploader("Subir archivo PDF", type=["pdf"])
    
    if archivo:
        df_final = procesar_lista(archivo)
        if df_final is not None:
            st.dataframe(df_final.head(10))
            
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_final.to_excel(writer, index=False)
            
            st.download_button(
                label="Descargar Excel Estandarizado",
                data=output.getvalue(),
                file_name=f"procesado_{archivo.name}.xlsx"
            )
