import streamlit as st
import google.generativeai as genai
# Bibliotecas para leer archivos PDF y Word (se deben agregar a requisitos.txt si no están)
import pdfplumber
import docx2txt

# 1. Configuración de la página web con identidad visual UCR
st.set_page_config(
    page_title="Sistema de Preselección Automatizada (AEP) - ORH",
    page_icon="💼",
    layout="wide"
)

# Estilos visuales corporativos UCR
# Azul Principal UCR: #0076a8 | Azul Oscuro: #042d62
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    
    /* Títulos e Identidad UCR */
    .main-title { font-size: 32px; font-weight: bold; color: #042d62; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 18px; color: #0076a8; text-align: center; margin-bottom: 30px; font-weight: bold;}
    
    /* Secciones */
    .section-header { font-size: 22px; font-weight: bold; color: #042d62; border-bottom: 2px solid #0076a8; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    
    /* Cuadro de Metadatos UCR */
    .metadata-box { background-color: #f0f4f8; padding: 15px; border-radius: 8px; border-left: 5px solid #0076a8; margin-bottom: 20px; border-top: 1px solid #0076a8; border-right: 1px solid #0076a8; border-bottom: 1px solid #0076a8;}
    
    /* Botones UCR */
    .stButton>button { background-color: #0076a8; color: white; border-radius: 5px; border: none;}
    .stButton>button:hover { background-color: #042d62; color: white;}
    
    /* Logo UCR e Identidad de ORH */
    .identidad-encabezado { text-align: center; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Encabezado con Logo y Acrónimo
# Se usa una imagen de firma de UCR en azul corporativo
st.markdown("""
<div class="identidad-encabezado">
    <img src="https://ucr.ac.cr/medios/imagenes/2015/firma-ucr-institucional-azul.png" width="300px" alt="UCR logo">
    <div style="color: #042d62; font-size: 24px; font-weight: bold; margin-top: 10px;">Oficina de Recursos Humanos (ORH)</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Propuesta de Modernización: Algoritmo Estándar de Preselección (AEP)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Módulo de IA para la Evaluación y Ajuste de Candidatos</div>', unsafe_allow_html=True)

# Inicializar variables de estado para la detección automática
if "nombre_puesto" not in st.session_state:
    st.session_state["nombre_puesto"] = "No detectado aún"
if "nombre_candidato" not in st.session_state:
    st.session_state["nombre_candidato"] = "No detectado aún"
if "contenido_cv" not in st.session_state:
    st.session_state["contenido_cv"] = ""

# 2. Conexión segura con Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Falta la configuración de la clave de seguridad (API Key) en los Secrets.")
    st.stop()

# Funciones auxiliares para la detección inmediata mediante IA
def detectar_puesto(texto_perfil):
    if texto_perfil.strip():
        try:
            peticion = f"Analiza el siguiente perfil de puesto y responde ÚNICAMENTE con el título o nombre del cargo, de forma breve (máximo 5 palabras):\n\n{texto_perfil}"
            respuesta = model.generate_content(peticion)
            st.session_state["nombre_puesto"] = respuesta.text.strip()
        except:
            st.session_state["nombre_puesto"] = "Error al detectar"

def detectar_candidato(texto_cv):
    if texto_cv.strip():
        try:
            # Petición para detectar nombre y cargo del CV
            peticion_nombre = f"Analiza el siguiente currículum vitae y responde ÚNICAMENTE con el nombre completo del candidato o postulante (máximo 4 palabras). Si no lo encuentras responde 'No especificado':\n\n{texto_cv}"
            respuesta_nombre = model.generate_content(peticion_nombre)
            st.session_state["nombre_candidato"] = respuesta_nombre.text.strip()
        except:
            st.session_state["nombre_candidato"] = "Error al detectar"

# Función para extraer texto de archivos (PDF, Word, TXT)
def extraer_texto(archivo):
    texto = ""
    try:
        if archivo.type == "application/pdf":
            with pdfplumber.open(archivo) as pdf:
                for pagina in pdf.pages:
                    texto += pagina.extract_text()
        elif archivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            texto = docx2txt.process(archivo)
        elif archivo.type == "text/plain":
            texto = archivo.read().decode("utf-8")
        else:
            st.error("⚠️ Formato de archivo no compatible. Use PDF, DOCX o TXT.")
    except Exception as e:
        st.error(f"⚠️ Error al leer el archivo: {e}")
    return texto

# 3. Interfaz de entrada de datos (Dos columnas)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">1. Perfil del Puesto / Requisitos</div>', unsafe_allow_html=True)
    perfil_puesto = st.text_area(
        "Pegue aquí los requisitos oficiales del cargo:",
        height=280,
        placeholder="Ejemplo: Título del Cargo: Analista de Gestión Corporativa de la ORH...",
        key="perfil_input",
        on_change=lambda: detectar_puesto(st.session_state.perfil_input)
    )

with col2:
    st.markdown('<div class="section-header">2. Currículum Vitae (CV) - Carga ORH</div>', unsafe_allow_html=True)
    
    # Selector interactivo UCR para decidir cómo cargar el CV
    metodo_carga = st.radio("Seleccione el método de carga para el CV:", ("Subir archivo (PDF, DOCX, TXT)", "Pegar texto manualmente"))
    
    if metodo_carga == "Subir archivo (PDF, DOCX, TXT)":
        archivo_cargado = st.file_uploader("Examinar o arrastrar el archivo del CV:", type=["pdf", "docx", "txt"])
        if archivo_cargado is not None:
            # Extraer y leer el contenido del archivo
            contenido = extraer_texto(archivo_cargado)
            if contenido:
                st.session_state["contenido_cv"] = contenido
                st.success(f"✅ ¡Archivo '{archivo_cargado.name}' cargado con éxito por la ORH!")
                # Forzar la detección automática del nombre con el texto leído DE INMEDIATO
                detectar_candidato(contenido)
            else:
                st.error("⚠️ El archivo subido está vacío o no se pudo leer el texto.")
                st.session_state["contenido_cv"] = ""
        else:
            st.session_state["contenido_cv"] = ""
    else:
        cv_texto = st.text_area(
            "Pegue aquí el texto completo del currículum:",
            height=200,
            placeholder="Ejemplo: Currículum Vitae de Juan Pérez Gamboa...",
            key="cv_input",
            on_change=lambda: detectar_candidato(st.session_state.cv_input)
        )
        st.session_state["contenido_cv"] = cv_texto

# Tomar el contenido final del CV según el método usado
cv_final = st.session_state["contenido_cv"]

# 4. Cuadro de Metadatos Detectados Automáticamente por la IA
st.markdown('<div class="section-header">🔍 Detección Automática de Variables - ORH</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metadata-box">
    <strong>📋 Puesto Identificado:</strong> {st.session_state["nombre_puesto"]} <br>
    <strong>👤 Candidato Identificado:</strong> {st.session_state["nombre_candidato"]}
</div>
""", unsafe_allow_html=True)

# 5. Construcción dinámica del Prompt Maestro
prompt_completo = f"""Actúa como un Consultor Experto en Reclutamiento y Selección de Personal de la Oficina de Recursos Humanos (ORH) de la Universidad de Costa Rica (UCR).
Tu objetivo es realizar un análisis técnico con el rigor técnico institucional para evaluar el nivel de
