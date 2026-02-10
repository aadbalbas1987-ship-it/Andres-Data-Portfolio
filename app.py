# --- SECCIÓN PROYECTO 2 ---
elif proyecto == "Proyecto 2: Monitor de Ejecución Presupuestaria":
    st.title("📊 Monitor Presupuestario (Escáner)")
    st.write("Registra un gasto escaneando un comprobante.")

    # 1. Preguntamos cómo quiere subir la info
    origen = st.radio(
        "¿Cómo deseas cargar el comprobante?",
        ["Subir foto de la galería", "Tomar foto con la cámara"],
        index=None, # Para que no entre directo a ninguna y espere la elección
        placeholder="Selecciona una opción..."
    )

    archivo_foto = None

    # 2. Mostramos el componente según la elección
    if origen == "Tomar foto con la cámara":
        archivo_foto = st.camera_input("Capturar Comprobante")
    
    elif origen == "Subir foto de la galería":
        archivo_foto = st.file_uploader("Selecciona una imagen del ticket", type=["jpg", "jpeg", "png"])

    # 3. Procesamiento común para ambos
    if archivo_foto:
        img = Image.open(archivo_foto)
        st.image(img, caption="Imagen cargada", use_container_width=True)
        
        if st.button("🚀 Escanear con Motor Sentinel"):
            with st.spinner("Analizando texto y montos..."):
                try:
                    # Usamos la misma función para ambos casos
                    datos = procesar_foto(img)
                    st.table(datos)
                except Exception as e:
                    st.error(f"Error al leer la imagen: {e}")
