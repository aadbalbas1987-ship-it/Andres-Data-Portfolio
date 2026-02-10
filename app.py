import streamlit as st
import pandas as pd
from PIL import Image
import app_etl  # Importamos el módulo de lógica

st.set_page_config(page_title="Andrés Data Portfolio", layout="wide")

# --- NAVEGACIÓN LATERAL ---
st.sidebar.title("Navegación")
proyecto = st.sidebar.radio("Ir a:", [
    "Inicio", 
    "Proyecto 1: El Limpiador Automático", 
    "Proyecto 2: Monitor de Ejecución Presupuestaria"
])

if proyecto == "Inicio":
    st.title("Andrés - Data Portfolio 2026")
    st.write("### Plataforma de Automatización de Procesos y Auditoría Forense")
    st.info("Seleccione una herramienta en el menú lateral para comenzar a procesar datos.")

# --- PROYECTO 1: ETL ---
elif proyecto == "Proyecto 1: El Limpiador Automático":
    st.title("🧹 El Limpiador Automático (ETL)")
    tipo = st.selectbox("Tipo de motor:", ["PDF Estándar", "PDF Complejo", "Excel/CSV"])
    archivo = st.file_uploader("Subir archivo", type=["pdf", "xlsx", "csv"])

    if archivo and st.button("Limpiar Datos"):
        if "PDF" in tipo:
            df = app_etl.procesar_estandar(archivo) if "Estándar" in tipo else app_etl.procesar_complejo(archivo)
        else:
            df = app_etl.procesar_excel_csv(archivo)
        
        if df is not None and not df.empty:
            st.dataframe(df, use_container_width=True)
            st.download_button("Descargar CSV", df.to_csv(index=False).encode('utf-8'), "limpio.csv")
        else:
            st.error("No se detectaron datos en el formato seleccionado.")

# --- PROYECTO 2: MONITOR DE GASTOS (MODULAR) ---
elif proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor de Ejecución Presupuestaria")
    st.write("Seleccione el motor adecuado para el tipo de comprobante que tiene.")

    metodo = st.selectbox(
        "Motor de Captura:",
        ["Digital (PDF Nativo)", "Escáner Pro (PDF Escaneado/Imagen)", "Cámara en Vivo"]
    )

    archivo_comprobante = None
    if metodo == "Cámara en Vivo":
        archivo_comprobante = st.camera_input("Capturar Ticket")
    else:
        ext = ["pdf"] if "Digital" in metodo else ["pdf", "jpg", "jpeg", "png"]
        archivo_comprobante = st.file_uploader(f"Cargar {metodo}", type=ext)

    if archivo_comprobante and st.button("🚀 Ejecutar Auditoría Sentinel"):
        with st.spinner("Procesando con el motor seleccionado..."):
            # Lógica de procesamiento según el método
            if metodo == "Digital (PDF Nativo)":
                df_res = app_etl.procesar_pdf_digital(archivo_comprobante)
            
            elif metodo == "Escáner Pro (PDF Escaneado/Imagen)":
                if archivo_comprobante.name.lower().endswith('.pdf'):
                    df_res = app_etl.procesar_pdf_escaneado_vision(archivo_comprobante)
                else:
                    img = Image.open(archivo_comprobante)
                    df_res = app_etl.procesar_foto_vision(img)
            
            else: # Cámara en Vivo
                img = Image.open(archivo_comprobante)
                df_res = app_etl.procesar_foto_vision(img)

            # --- SECCIÓN DE RESULTADOS ---
            if df_res is not None and not df_res.empty:
                st.write("### Auditoría de Ítems Detectados")
                st.dataframe(df_res, use_container_width=True)
                
                # CÁLCULO DE TOTAL (Lógica Blindada Master)
                try:
                    # 1. Limpiamos caracteres no numéricos excepto comas y puntos
                    temp_monto = df_res["Precio"].str.replace(r'[^\d,.]', '', regex=True)
                    # 2. Manejo de decimales: si hay coma, la pasamos a punto para float
                    temp_monto = temp_monto.str.replace(',', '.')
                    
                    # 3. Conversión y suma
                    solo_nums = pd.to_numeric(temp_monto, errors='coerce').fillna(0)
                    total_final = solo_nums.sum()
                    
                    st.metric("Total Auditado por Sentinel", f"$ {total_final:,.2f}")
                except Exception as e:
                    st.warning("No se pudo calcular el total automáticamente. Revise el formato de los precios.")
            else:
                st.error("El motor no encontró datos legibles. Intente con una imagen más clara o el motor 'Escáner Pro'.")
