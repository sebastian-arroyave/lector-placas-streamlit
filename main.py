import streamlit as st
import easyocr
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import io

# ------------------------------------------------
# CONFIGURACIÓN DE LA APP
# ------------------------------------------------
st.set_page_config(page_title="OCR Placas", page_icon="🚗", layout="centered")

# ------------------------------------------------
# BASE DE DATOS SIMULADA
# ------------------------------------------------
df = pd.DataFrame({
    "PLACA": ["ABC123", "XYZ789", "KLM456", "DEF321"],
    "PROPIETARIO": ["Carlos Pérez", "María Gómez", "Luis Torres", "Ana López"],
    "MARCA": ["Chevrolet", "Mazda", "Toyota", "Renault"],
    "VIGENCIA": ["2025", "2024", "2023", "2025"],
    "IMPUESTO_PAGADO": ["Sí", "No", "Sí", "No"]
})

# ------------------------------------------------
# CREDENCIALES DE USUARIO
# ------------------------------------------------
USUARIOS = {"admin": "1234", "ceiva": "2025", "demo": "demo"}


# ------------------------------------------------
# FUNCIÓN LOGIN
# ------------------------------------------------
def mostrar_login():
    st.title("🔐 Ingreso al Sistema OCR de Placas")

    with st.form("login_form"):
        usuario = st.text_input("👤 Usuario")
        contraseña = st.text_input("🔑 Contraseña", type="password")
        enviar = st.form_submit_button("Iniciar sesión")

    if enviar:
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.success("✅ Inicio de sesión exitoso.")
            st.rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")


# ------------------------------------------------
# FUNCIÓN OCR
# ------------------------------------------------
def app_ocr():
    st.sidebar.success(f"👤 Usuario: {st.session_state['usuario']}")
    if st.sidebar.button("Cerrar sesión"):
        st.session_state["autenticado"] = False
        st.rerun()

    st.title("🚘 OCR de Placas Vehiculares")

    @st.cache_resource
    def load_ocr():
        return easyocr.Reader(["en"])

    reader = load_ocr()

    enable = st.checkbox("📸 Activar cámara")
    picture = st.camera_input("Toma una foto", disabled=not enable)
    uploaded = st.file_uploader("O carga una imagen desde tu dispositivo", type=["jpg", "jpeg", "png"])

    image_data = picture or uploaded

    if image_data:
        st.image(image_data, caption="Imagen cargada", use_container_width=True)
        image = Image.open(io.BytesIO(image_data.getvalue()))
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)

        with st.spinner("Leyendo placa..."):
            results = reader.readtext(image_cv)

        detected_plate = None
        output = image_cv.copy()

        for (bbox, text, prob) in results:
            clean_text = text.replace(" ", "").upper()
            if 5 <= len(clean_text) <= 8 and prob > 0.4:
                detected_plate = clean_text
                pts = np.array(bbox, dtype=np.int32)
                cv2.polylines(output, [pts], True, (0, 255, 0), 2)
                cv2.putText(output, clean_text, (pts[0][0], pts[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        st.image(cv2.cvtColor(output, cv2.COLOR_BGR2RGB),
                 caption="Resultado OCR", use_container_width=True)

        if detected_plate:
            st.success(f"📄 Placa detectada: {detected_plate}")
            result = df[df["PLACA"] == detected_plate.replace("-", "")]
            if not result.empty:
                st.dataframe(result, hide_index=True)
            else:
                st.warning("No se encontró la placa en la base de datos.")
        else:
            st.error("No se detectó ninguna placa.")


# ------------------------------------------------
# CONTROL DEL FLUJO
# ------------------------------------------------
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if st.session_state["autenticado"]:
    app_ocr()
else:
    mostrar_login()
