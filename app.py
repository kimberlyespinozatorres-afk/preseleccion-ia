import streamlit as st
import google.generativeai as genai
import pdfplumber
import docx2txt

# 1. Configuración de la página web con identidad visual UCR
st.set_page_config(
    page_title="Sistema de Preselección Automatizada (AEP) - ORH",
    page_icon="💼",
    layout="wide"
)

# Estilos visuales corporativos UCR
st.markdown("""
    <style>
    .stApp { background-color: #ffffff; }
    .main-title { font-size: 32px; font-weight: bold; color: #042d62; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 18px; color: #0076a8; text-align: center; margin-bottom: 30px; font-weight: bold;}
    .section-header { font-size: 22px; font-weight: bold; color: #042d62; border-bottom: 2px solid #0076a8; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    .metadata-box { background-color: #f0f4f8; padding: 15px; border-radius: 8px; border-left: 5px solid #0076a8; margin-bottom: 20px; border-top: 1px solid #0076a8; border-right: 1px solid #0076a8; border-bottom: 1px solid #0076a8;}
    .stButton>button { background-color: #0076a8; color: white; border-radius: 5px; border: none;}
    .stButton>button:hover { background-color: #042d62; color: white;}
    .identidad-encabezado { text-align: center; margin-bottom: 20px;}
    </style>
""", unsafe_allow_html=True)

# Encabezado con Logo y Acrónimo UCR - ORH
st.markdown("""
<div class="identidad-encabezado">
    <img src="https://ucr.ac.cr/medios/imagenes/2015/firma-ucr-institucional-azul.png" width="300px" alt="UCR logo">
    <div style="color: #042d62; font-size: 24px; font-weight: bold; margin-top: 10px;">Oficina de Recursos Humanos (ORH)</div>
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Propuesta de Modernización: Algoritmo Estándar de Preselección (AEP)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Módulo de IA para la Evaluación y Ajuste de Candidatos</div>', unsafe_allow_html=True)

# Inicializar variables de estado
if "nombre_puesto" not in st.session_state:
    st.session_state["nombre_puesto"] = "No detectado aún"
if "nombre_candidato" not in st.session_state:
    st.session_state["nombre_candidato"] = "No detectado aún"
if "contenido_cv" not in st.session_state:
    st.session_state["contenido_cv"] = ""
if "contenido_perfil" not in st.session_state:
    st.session_state["contenido_perfil"] = ""

# 2. Conexión segura con Gemini
if "GEMINI_API_KEY" in st.secrets:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
    model = genai.GenerativeModel('gemini-1.5-flash')
else:
    st.error("Falta la configuración de la clave de seguridad (API Key) en los Secrets.")
    st.stop()

# Funciones auxiliares
def detectar_puesto(texto_perfil):
    if texto_perfil.strip():
        try:
            peticion = f"Analiza el siguiente perfil de puesto y responde ÚNICAMENTE con el título o nombre del cargo, de forma breve (máximo 5 palabras):\n\n{texto_perfil}"
            respuesta = model.generate_content(peticion)
            st.session_state["nombre_puesto"] = respuesta.text.strip()
        except Exception as e:
            st.session_state["nombre_puesto"] = f"Error al detectar: {e}"

def detectar_candidato(texto_cv):
    if texto_cv.strip():
        try:
            peticion_nombre = f"Analiza el siguiente currículum vitae y responde ÚNICAMENTE con el nombre completo del candidato o postulante (máximo 4 palabras). Si no lo encuentras responde 'No especificado':\n\n{texto_cv}"
            respuesta_nombre = model.generate_content(peticion_nombre)
            st.session_state["nombre_candidato"] = respuesta_nombre.text.strip()
        except Exception as e:
            st.session_state["nombre_candidato"] = f"Error al detectar: {e}"

# Función para extraer texto de archivos
def extraer_texto(archivo):
    texto = ""
    try:
        if archivo.type == "application/pdf":
            with pdfplumber.open(archivo) as pdf:
                for pagina in pdf.pages:
                    texto_pag = pagina.extract_text()
                    if texto_pag:
                        texto += texto_pag + "\n"
        elif archivo.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
            texto = docx2txt.process(archivo)
        elif archivo.type == "text/plain":
            texto = archivo.read().decode("utf-8")
        else:
            st.error("⚠️ Formato de archivo no compatible. Use PDF, DOCX o TXT.")
    except Exception as e:
        st.error(f"⚠️ Error al leer el archivo: {e}")
    return texto

# 3. Interfaz de entrada de datos
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">1. Perfil del Puesto / Requisitos</div>', unsafe_allow_html=True)

    # Igual que el CV: selector de método
    metodo_perfil = st.radio("Seleccione el método de carga para el Perfil:", ("Subir archivo (PDF, DOCX, TXT)", "Pegar texto manualmente"), key="radio_perfil")

    if metodo_perfil == "Subir archivo (PDF, DOCX, TXT)":
        archivo_perfil = st.file_uploader("Examinar o arrastrar el archivo del Perfil:", type=["pdf", "docx", "txt"], key="uploader_perfil")
        if archivo_perfil is not None:
            contenido_p = extraer_texto(archivo_perfil)
            if contenido_p:
                st.session_state["contenido_perfil"] = contenido_p
                st.success(f"✅ ¡Archivo '{archivo_perfil.name}' cargado con éxito!")
                detectar_puesto(contenido_p)
            else:
                st.error("⚠️ El archivo subido está vacío o no se pudo leer el texto.")
                st.session_state["contenido_perfil"] = ""
        else:
            st.session_state["contenido_perfil"] = ""
    else:
        perfil_texto = st.text_area(
            "Pegue aquí los requisitos oficiales del cargo:",
            height=250,
            placeholder="Ejemplo: Título del Cargo: Analista de Gestión Corporativa de la ORH...",
            key="perfil_input",
            on_change=lambda: detectar_puesto(st.session_state.get("perfil_input", ""))
        )
        st.session_state["contenido_perfil"] = perfil_texto

with col2:
    st.markdown('<div class="section-header">2. Currículum Vitae (CV) - Carga ORH</div>', unsafe_allow_html=True)

    metodo_carga = st.radio("Seleccione el método de carga para el CV:", ("Subir archivo (PDF, DOCX, TXT)", "Pegar texto manualmente"), key="radio_cv")

    if metodo_carga == "Subir archivo (PDF, DOCX, TXT)":
        archivo_cargado = st.file_uploader("Examinar o arrastrar el archivo del CV:", type=["pdf", "docx", "txt"], key="uploader_cv")
        if archivo_cargado is not None:
            contenido = extraer_texto(archivo_cargado)
            if contenido:
                st.session_state["contenido_cv"] = contenido
                st.success(f"✅ ¡Archivo '{archivo_cargado.name}' cargado con éxito por la ORH!")
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
            on_change=lambda: detectar_candidato(st.session_state.get("cv_input", ""))
        )
        st.session_state["contenido_cv"] = cv_texto

# Tomar contenidos finales
perfil_puesto = st.session_state["contenido_perfil"]
cv_final = st.session_state["contenido_cv"]

# 4. Cuadro de Metadatos
st.markdown('<div class="section-header">🔍 Detección Automática de Variables - ORH</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metadata-box">
    <strong>📋 Puesto Identificado:</strong> {st.session_state["nombre_puesto"]} <br>
    <strong>👤 Candidato Identificado:</strong> {st.session_state["nombre_candidato"]}
</div>
""", unsafe_allow_html=True)

# 5. Construcción dinámica del Prompt Maestro
prompt_completo = f"Actúa como un Consultor Experto en Reclutamiento y Selección de Personal de la Oficina de Recursos Humanos (ORH) de la Universidad de Costa Rica (UCR). Tu objetivo es realizar un análisis técnico con el rigor técnico institucional para evaluar el nivel de ajuste del candidato frente al perfil oficial.\n\nPor favor, genera un 'Reporte de Evaluación y Ajuste de Candidatos' estructurado con las siguientes secciones:\n\n### 1. RESUMEN EJECUTIVO DE LA CANDIDATURA (Identidad ORH-UCR)\n- Nombre del Candidato: {st.session_state['nombre_candidato']}\n- Puesto al que postula: {st.session_state['nombre_puesto']}\n- Calificación Final: [Asignar nota del 1 al 10]\n- Estatus Sugerido: [PASAS A ENTREVISTA, ELEGIBLE EN RESERVA o NO PRESELECCIONADO]\n\n### 2. MATRIZ DE CALIFICACIÓN DETALLADA (Tabla)\n| Criterio de Evaluación | Requisito del Puesto | Perfil del Candidato | Nivel de Cumplimiento | Nota (1-10) y Justificación Técnica |\n\n### 3. ANÁLISIS CUALITATIVO INSTITUCIONAL\n- Fortalezas Clave para la UCR\n- Brechas / Puntos Ciegos Técnicos\n\n### 4. RECOMENDACIÓN FINAL DE LA ORH\n\n---\nPERFIL DEL PUESTO:\n{perfil_puesto if perfil_puesto else '[Vacío]'}\n\nCURRÍCULUM VITAE:\n{cv_final if cv_final else '[Vacío]'}"

# 6. Zona de Herramientas del Prompt
st.markdown('<div class="section-header">⚙️ Herramientas de Transparencia del Algoritmo</div>', unsafe_allow_html=True)
st.write("Presione el botón inferior si desea copiar el prompt exacto estructurado por el sistema:")

prompt_escapado = prompt_completo.replace("\\", "\\\\").replace("`", "\\`")
st.markdown(f"""
    <button onclick="navigator.clipboard.writeText(`{prompt_escapado}`).then(() => alert('✅ Prompt copiado al portapapeles.'))"
        style="background-color:#0076a8; color:white; border:none; border-radius:5px; padding:8px 16px; font-size:14px; cursor:pointer;">
        📋 Copiar Prompt al Portapapeles
    </button>
""", unsafe_allow_html=True)

# 7. Ejecución del Reporte Final
st.markdown("<br>", unsafe_allow_html=True)
boton_evaluar = st.button("🚀 Generar Reporte de Evaluación con IA (Rigor Técnico UCR)", use_container_width=True, type="primary")

if boton_evaluar:
    if not perfil_puesto or not cv_final:
        st.warning("⚠️ Asegúrese de rellenar el perfil del puesto y cargar un CV.")
    else:
        with st.spinner("Procesando matriz de evaluación con el rigor técnico e institucional de la ORH..."):
            try:
                response = model.generate_content(prompt_completo)
                st.markdown('<div class="section-header">📋 Reporte Técnico Institucional Generado</div>', unsafe_allow_html=True)
                st.markdown(response.text)
                st.success("✓ Análisis finalizado de forma exitosa.")
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
