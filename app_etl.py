import streamlit as st
import pandas as pd
import pdfplumber
import re
import io

st.set_page_config(page_title="ETL Sentinel | Estandarizador", layout="wide")

# CSS para mantener la estética profesional
st.markdown("""
    <style>
    .main { background-color: #0b0f19; color: white; }
    .stButton>button { background-color: #00f2ff; color: black; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

def separar_codigo_descripcion(texto):
    """Lógica para casos como '3902 FIAMBRE COCIDO'"""
    match = re.match(r'^(\w?\d+)\s+(.*)', str(texto))
    if match:
        return match.group(1), match.group(2)
    return "", texto

def procesar_lista(file):
    all_data = []
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            table = page.extract_table()
            if table:
                all_data.extend(table)
    
    if not all_data:
        return None

    df = pd.DataFrame(all_data)
    
    # 1. Identificar columnas (Lógica de sensibilidad)
    # Buscamos la columna de precio (que tenga números, comas o $)
    col_precio = None
    for col in df.columns:
        sample = df[col].astype(str).str.contains(r'\d', na=False).sum()
        if sample > len(df) * 0.5: # Si más del 50% tiene números
            col_precio = col
    
    # 2. Crear las columnas "SENTINEL" al principio
    # Usamos la primera columna como base para Código/Descripción
    df[['COD_SENTINEL', 'DESC_SENTINEL']] = df[0].apply(lambda x: pd.Series(separar_codigo_descripcion(x)))
    
    # 3. Reordenar: Sentinel Primero, Origen Después
    cols_sentinel = ['COD_SENTINEL', 'DESC_SENTINEL']
    otras_cols = [c for c in df.columns if c not in cols_sentinel]
    df = df[cols_sentinel + otras_cols]
    
    return df

st.title("🏦 Proyecto ETL: Estandarizador de Listas")
st.subheader("Sube el PDF del proveedor y obtén un Excel estructurado")

uploaded_file = st.file_uploader("Cargar lista (PDF)", type=["pdf"])

if uploaded_file:
    with st.spinner('Analizando estructura y aplicando reglas de negocio...'):
        # Usamos el nombre del archivo para el resultado final
        nombre_proveedor = uploaded_file.name.replace(".pdf", "").replace(".PDF", "")
        
        df_resultado = procesar_lista(uploaded_file)
        
        if df_resultado is not None:
            st.success(f"Estructura detectada para: {nombre_proveedor}")
            
            # Vista previa
            st.write("Vista previa (Primeras 3 columnas prioritarias + Origen):")
            st.dataframe(df_resultado.head(10))
            
            # Botón de Descarga
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df_resultado.to_excel(writer, index=False, sheet_name='Datos_Limpios')
            
            st.download_button(
                label="📥 Descargar XLSX Estandarizado",
                data=output.getvalue(),
                file_name=f"{nombre_proveedor}_ESTANDARIZADO.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        else:
            st.error("No se pudieron extraer tablas legibles de este archivo.")