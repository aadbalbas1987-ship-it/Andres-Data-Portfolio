# RPA PuTTY Bridge: Automatización de Carga de Inventario

### 📋 Descripción
Este bot de automatización (RPA) soluciona la carga manual de pedidos en sistemas Legacy vía PuTTY. 
Elimina el error humano en la distinción entre Unidades/Bultos y reduce el tiempo de carga en un 90%.

### 🛠️ Tecnologías
- **Python 3.x**
- **Pandas**: Procesamiento de datos del Excel.
- **PyAutoGUI**: Emulación de periféricos para interacción con terminales SSH.

### 🚀 Flujo del Proceso
1. El script lee la cabecera (Pedido y Observaciones) desde celdas específicas.
2. Navega automáticamente por los menús del terminal (3 -> 6 -> 1).
3. Realiza la carga cíclica de artículos, forzando la unidad de medida a "Unidades".
4. Mueve el archivo procesado a una carpeta de historial con marca de tiempo.
