import streamlit as st
import easyocr
import numpy as np
import pandas as pd
import cv2
from PIL import Image
import io

# ------------------------------------------------
# CONFIGURACIÓN GENERAL
# ------------------------------------------------
st.set_page_config(page_title="OCR Placas Vehiculares", page_icon="🚗", layout="centered")

# ------------------------------------------------
# USUARIOS PERMITIDOS (login simulado)
# ------------------------------------------------
USUARIOS = {
    "admin": "1234",
    "ceiva": "2025",
    "demo": "demo"
}

# ------------------------------------------------
# FUNCIÓN DE LOGOUT
# ------------------------------------------------
def logout():
    st.session_state["autenticado"] = False
    st.experimental_rerun()

# ------------------------------------------------
# FUNCIÓN DE LOGIN
# ------------------------------------------------
def login():
    st.title("🔐 Ingreso al Sistema OCR de Placas")
    st.write("Ingrese sus credenciales para acceder a la aplicación.")

    usuario = st.text_input("👤 Usuario")
    contraseña = st.text_input("🔑 Contraseña", type="password")

    if st.button("Iniciar sesión"):
        if usuario in USUARIOS and USUARIOS[usuario] == contraseña:
            st.session_state["autenticado"] = True
            st.session_state["usuario"] = usuario
            st.success(f"✅ Bienvenido, {usuario}")
            st.experimental_rerun()
        else:
            st.error("❌ Usuario o contraseña incorrectos.")

# ------------------------------------------------
# FUNCIÓN PRINCIPAL DEL SISTEMA OCR
# ------------------------------------------------
def app_ocr():
    st.sidebar.success(f"Usuario: {st.session_state['usuario']}")
    st.sidebar.button("Cerrar sesión", on_click=logout)

    st.title("🔍 Lector de Placas Vehiculares con Búsqueda en DataFrame")

    st.write("""
    Toma una foto de una placa (o carga una imagen).  
    El sistema detectará la placa y buscará la información asociada en un DataFrame.
    """)

    # Cargar el lector OCR (solo una vez)
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
        st.image(image_data, caption="Imagen original", use_container_width=True)

