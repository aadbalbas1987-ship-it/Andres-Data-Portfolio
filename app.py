import streamlit as st
import pandas as pd
import io
# Importamos la lógica de tu archivo especializado
from app_etl import procesar_lista 

# 1. CONFIGURACIÓN DEL PORTAFOLIO
st.set_page_config(page_title="Andrés | Data Portfolio", layout="wide", page_icon="📊")

# CSS personalizado para que todo el portafolio tenga tu marca
st.markdown("""
    <style>
    .stApp { background-color: #0b1117; color: white; }
    .stSidebar { background-color: #161b22 !important; }
    h1 { color: #00f2ff !important; font-weight: 800; }
    .project-card {
        background-color: #1c2128;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. BARRA LATERAL (NAVEGACIÓN)
with st.sidebar:
    st.title("🛡️ Sentinel Suite")
    st.subheader("Navegación Proyectos")
    
    seleccion = st.radio(
        "Ir a:",
        ["🏠 Inicio / CV", 
         "🛠️ Proyecto 1: ETL Inteligente", 
         "📸 Proyecto 2: Lector OCR Facturas", 
         "📊 Proyecto 3: Monitor Presupuestario"]
    )
    
    st.markdown("---")
    st.info("Desarrollado por Andrés Balbas | 2026")

# 3. LÓGICA DE PÁGINAS
if seleccion == "🏠 Inicio / CV":
    st.title("Andrés Balbas | Data & Audit Portfolio")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### Sobre mí
        Especialista en automatización de procesos financieros y auditoría forense. 
        Este portafolio muestra herramientas reales diseñadas para optimizar la carga de datos 
        y el control estratégico.
        
        #### Stack Tecnológico:
        * **Lenguajes:** Python (Pandas, Re, PDFPlumber)
        * **Visualización:** Streamlit, Plotly
        * **Herramientas:** ETL, OCR, Auditoría Forense
        """)
    
    with col2:
        st.markdown("<div class='project-card'><b>Estado del Sistema:</b><br>🟢 Proyecto 1 Activo<br>🟡 Proyecto 2 en Desarrollo</div>", unsafe_allow_html=True)

elif seleccion == "🛠️ Proyecto 1: ETL Inteligente":
    st.title("🛠️ Proyecto 1: ETL - Data Mapper Forense")
    st.write("Esta herramienta normaliza listas de proveedores (PDF/Excel) sin perder la fuente original.")
    
    archivo = st.file_uploader("Cargar lista de proveedor", type=["pdf"])
    
    if archivo:
        with st.spinner("Procesando datos con sensibilidad 'Sentinel'..."):
            # Aquí usamos la función que ya tienes en app_etl.py
            df_final = procesar_lista(archivo)
            
            if df_final is not None:
                st.success("¡Estructura mapeada con éxito!")
                
                # Vista previa
                st.dataframe(df_final.head(15), use_container_width=True)
                
                # Botón de descarga
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                    df_final.to_excel(writer, index=False)
                
                st.download_button(
                    label="📥 Descargar XLSX Estandarizado",
                    data=buffer.getvalue(),
                    file_name=f"SENTINEL_ETL_{archivo.name.replace('.pdf', '')}.xlsx",
                    mime="application/vnd.ms-excel"
                )
            else:
                st.error("No se detectaron tablas en el archivo.")

elif seleccion == "📸 Proyecto 2: Lector OCR Facturas":
    st.title("📸 Proyecto 2: Lector de Facturas por Foto")
    st.warning("⚠️ Este proyecto está siendo migrado al repositorio. Pronto podrás probar la carga ultra-rápida por código de proveedor.")

# ... Espacios para los demás proyectos