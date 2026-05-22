import streamlit as st
import google.generativeai as genai

# 1. Configuración de la página web
st.set_page_config(
    page_title="Sistema de Preselección Automatizada (AEP)",
    page_icon="💼",
    layout="wide"
)

# Estilos visuales corporativos
st.markdown("""
    <style>
    .main-title { font-size: 32px; font-weight: bold; color: #042d62; text-align: center; margin-bottom: 5px; }
    .subtitle { font-size: 18px; color: #555555; text-align: center; margin-bottom: 30px; }
    .section-header { font-size: 22px; font-weight: bold; color: #042d62; border-bottom: 2px solid #042d62; padding-bottom: 5px; margin-top: 20px; margin-bottom: 15px; }
    .metadata-box { background-color: #f0f4f8; padding: 15px; border-radius: 8px; border-left: 5px solid #042d62; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">Propuesta de Modernización: Algoritmo Estándar de Preselección (AEP)</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Módulo de IA para la Evaluación y Ajuste de Candidatos</div>', unsafe_allow_html=True)

# Inicializar variables de estado para la detección automática
if "nombre_puesto" not in st.session_state:
    st.session_state["nombre_puesto"] = "No detectado aún"
if "nombre_candidato" not in st.session_state:
    st.session_state["nombre_candidato"] = "No detectado aún"

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
            peticion = f"Analiza el siguiente currículum vitae y responde ÚNICAMENTE con el nombre completo del candidato o postulante (máximo 4 palabras). Si no lo encuentras responde 'No especificado':\n\n{texto_cv}"
            respuesta = model.generate_content(peticion)
            st.session_state["nombre_candidato"] = respuesta.text.strip()
        except:
            st.session_state["nombre_candidato"] = "Error al detectar"

# 3. Interfaz de entrada de datos (Dos columnas)
col1, col2 = st.columns(2)

with col1:
    st.markdown('<div class="section-header">1. Perfil del Puesto / Requisitos</div>', unsafe_allow_html=True)
    perfil_puesto = st.text_area(
        "Pegue aquí los requisitos oficiales del cargo:",
        height=250,
        placeholder="Ejemplo: Título del Cargo: Niñera...",
        key="perfil_input",
        on_change=lambda: detectar_puesto(st.session_state.perfil_input)
    )

with col2:
    st.markdown('<div class="section-header">2. Currículum Vitae (CV)</div>', unsafe_allow_html=True)
    cv_candidato = st.text_area(
        "Pegue aquí el texto completo del currículum:",
        height=250,
        placeholder="Ejemplo: Currículum Vitae de María Fernanda...",
        key="cv_input",
        on_change=lambda: detectar_candidato(st.session_state.cv_input)
    )

# 4. Cuadro de Metadatos Detectados Automáticamente
st.markdown('<div class="section-header">🔍 Detección Automática de Variables</div>', unsafe_allow_html=True)
st.markdown(f"""
<div class="metadata-box">
    <strong>📋 Puesto Identificado:</strong> {st.session_state["nombre_puesto"]} <br>
    <strong>👤 Candidato Identificado:</strong> {st.session_state["nombre_candidato"]}
</div>
""", unsafe_allow_html=True)

# 5. Construcción dinámica del Prompt Maestro
prompt_completo = f"""Actúa como un Consultor Experto en Reclutamiento y Selección de Personal.
Tu objetivo es realizar un análisis técnico para evaluar el nivel de ajuste del candidato frente al perfil oficial.

Por favor, genera un "Reporte de Evaluación y Ajuste de Candidatos" estructurado con las siguientes secciones:

### 1. RESUMEN EJECUTIVO DE LA CANDIDATURA
- **Nombre del Candidato:** {st.session_state["nombre_candidato"]}
- **Puesto al que postula:** {st.session_state["nombre_puesto"]}
- **Calificación Final:** [Asignar nota del 1 al 10]
- **Estatus Sugerido:** [PASAS A ENTREVISTA, ELEGIBLE EN RESERVA o NO PRESELECCIONADO]

### 2. MATRIZ DE CALIFICACIÓN DETALLADA (Tabla)
| Criterio de Evaluación | Requisito del Puesto | Perfil del Candidato | Nivel de Cumplimiento | Nota (1-10) y Justificación Técnica |

### 3. ANÁLISIS CUALITATIVO
- Fortalezas Clave
- Brechas / Puntos Ciegos

### 4. RECOMENDACIÓN FINAL

---
PERFIL DEL PUESTO:
{perfil_puesto if perfil_puesto else "[Vacío]"}

CURRÍCULUM VITAE:
{cv_candidato if cv_candidato else "[Vacío]"}"""

# 6. Zona de Herramientas del Prompt (Botón Copiar)
st.markdown('<div class="section-header">⚙️ Herramientas de Transparencia del Algoritmo</div>', unsafe_allow_html=True)
st.write("Presione el botón inferior si desea copiar el prompt exacto estructurado por el sistema para auditarlo o usarlo en otra IA externa:")

# Botón nativo de copia en Streamlit
st.copy_to_clipboard(prompt_completo)
st.button("📋 Copiar Prompt al Portapapeles", help="Copia todo el texto del prompt incluyendo los datos actualizados de arriba.")

# 7. Ejecución del Reporte Final
st.markdown("<br>", unsafe_allow_html=True)
boton_evaluar = st.button("🚀 Generar Reporte de Evaluación con IA", use_container_width=True, type="primary")

if boton_evaluar:
    if not perfil_puesto or not cv_candidato:
        st.warning("⚠️ Asegúrese de rellenar ambos campos de texto para poder procesar la evaluación.")
    else:
        with st.spinner("Procesando matriz de evaluación con rigor técnico institucional..."):
            try:
                response = model.generate_content(prompt_completo)
                st.markdown('<div class="section-header">📋 Reporte Técnico Generado</div>', unsafe_allow_html=True)
                st.markdown(response.text)
                st.success("✓ Análisis finalizado de forma exitosa.")
            except Exception as e:
                st.error(f"Error al conectar con la IA: {e}")
