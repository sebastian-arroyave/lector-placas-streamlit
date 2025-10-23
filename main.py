import streamlit as st
import easyocr
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import io

# -----------------------------
# CONFIGURACIÓN INICIAL
# -----------------------------

st.title("🔍 Lector de Placas Vehiculares con Búsqueda en DataFrame")

st.write("""
Toma una foto de una placa (o carga una imagen).  
El sistema detectará la placa y buscará la información asociada en un DataFrame.
""")

# Cargar lector OCR (solo una vez)
@st.cache_resource
def load_ocr():
    return easyocr.Reader(['en'])
reader = load_ocr()

# Simulación de base de datos
data = {
    "PLACA": ["ABC123", "XYZ789", "KLM456", "DEF321"],
    "PROPIETARIO": ["Carlos Pérez", "María Gómez", "Luis Torres", "Ana López"],
    "MARCA": ["Chevrolet", "Mazda", "Toyota", "Renault"],
    "VIGENCIA": ["2025", "2024", "2023", "2025"],
    "IMPUESTO_PAGADO": ["Sí", "No", "Sí", "No"]
}
df = pd.DataFrame(data)

# -----------------------------
# CAPTURA DE IMAGEN
# -----------------------------

enable = st.checkbox("📸 Activar cámara")
picture = st.camera_input("Toma una foto", disabled=not enable)
uploaded = st.file_uploader("O carga una imagen desde tu dispositivo", type=["jpg", "jpeg", "png"])

image_data = picture or uploaded

if image_data:
    # Mostrar imagen original
    st.image(image_data, caption="Imagen original", use_column_width=True)

    # Convertir imagen a formato OpenCV
    image = Image.open(io.BytesIO(image_data.getvalue()))
    image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

    # Ejecutar OCR
    with st.spinner("Procesando imagen..."):
        results = reader.readtext(image_cv)

    # Dibujar cajas y capturar texto
    output = image_cv.copy()
    detected_plate = None

    for (bbox, text, prob) in results:
        clean_text = text.replace(" ", "").upper()
        if len(clean_text) >= 5 and len(clean_text) <= 8 and prob > 0.4:
            detected_plate = clean_text
            pts = np.array(bbox, dtype=np.int32)
            cv2.polylines(output, [pts], True, (0, 255, 0), 2)
            cv2.putText(output, clean_text, (pts[0][0], pts[0][1] - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

    # Mostrar imagen procesada
    st.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB), caption="Resultado OCR", use_column_width=True)

    # -----------------------------
    # BÚSQUEDA EN DATAFRAME
    # -----------------------------
    if detected_plate:
        st.subheader("📄 Placa detectada:")
        st.success(f"➡️ {detected_plate}")

        # Buscar en el DataFrame
        result = df[df["PLACA"] == detected_plate.replace('-', '')]

        if not result.empty:
            st.subheader("🚘 Información del vehículo:")
            st.dataframe(result, hide_index=True)
        else:
            st.warning("❌ No se encontró la placa en la base de datos.")
    else:
        st.error("No se detectó ninguna placa con suficiente confianza.")
