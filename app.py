import streamlit as st
import networkx as nx
from pyvis.network import Network
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import os

# 1. Configuración obligatoria de la página al inicio
st.set_page_config(page_title="UCE-MATCH v2", layout="wide")

# ==========================================
# DISEÑO Y ESTILOS PERSONALIZADOS (CSS INTERNO)
# ==========================================
st.markdown("""
    <style>
    /* Cambiar el fondo del bloque de métricas */
    [data-testid="stMetricValue"] {
        color: #1A365D;
        font-weight: bold;
    }
    /* Estilizar botones primarios con el color azul institucional */
    div.stButton > button:first-child {
        border-radius: 8px;
    }
    div.stButton > button[kind="primary"] {
        background-color: #1A365D;
        color: white;
        border: none;
    }
    div.stButton > button[kind="primary"]:hover {
        background-color: #2A4D7C;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Estructura oficial del proyecto
ESTRUCTURA_ÁREAS = {
    "Ciencias Exactas": {
        "carreras": [
            "Ing. Civil", "Sistemas", "Computación", "Matemáticas", "Geología", 
            "Petróleos", "Minas", "Diseño Industrial", "Mecánica", "Ing. Ambiental", 
            "Ing. Química", "Bioprocesos"
        ],
        "materias_comun": [
            "Análisis I (Cálculo I)", "Análisis II (Cálculo II)", "Programación", 
            "Introducción al Análisis Matemático", "Geometría Descriptiva", "Química General"
        ]
    },
    "Artes y Arquitectura": {
        "carreras": ["Artes Escénicas", "Artes Musicales", "Artes Plásticas", "Danza", "Arquitectura y Urbanismo"],
        "materias_comun": [
            "Movimiento y Voz Auténticos/Primarios", "Armonía, Contrapunto y Entrenamiento Auditivo II", 
            "Morfología", "Técnicas de Danza Contemporánea: Inicial II", "Taller de Diseño Básico II"
        ]
    },
    "Ciencias de la Vida": {
        "carreras": ["Biología", "Agronomía", "Medicina Veterinaria", "Turismo", "Química", "Recursos Naturales Renovables", "Bioquímica y Farmacia"],
        "materias_comun": [
            "Análisis I (Cálculo I)", "Química Orgánica", "Anatomía Animal I", 
            "Contabilidad / Matemática Financiera", "Física I", "Topografía I", "Química Inorgánica"
        ]
    },
    "Ciencias de la Salud Humana": {
        "carreras": [
            "Medicina", "Enfermería", "Obstetricia", "Laboratorio Clínico", "Imageneología y Radiología", 
            "Fonoaudiología", "Fisioterapia", "Terapia Ocupacional", "Atención Prehospitalaria", 
            "Psicología Clínica", "Psicología Educativa", "Odontología", "Pedagogía de la Act. Física", 
            "Entrenamiento Deportivo"
        ],
        "materias_comun": [
            "Anatomía Humana I", "Bioquímica Aplicada", "Embriología y Genética", "Química Analítica", 
            "Física Radiológica", "Anatomofisiología", "Biomecánica General", "Neuroanatomía Funcional", 
            "Soporte Vital Básico", "Neurofisiología", "Bases Biológicas del Comportamiento", 
            "Histología Estomatológica", "Anatomía Funcional y del Movimiento", "Fisiología del Esfuerzo Físico"
        ]
    }
}

# 🔗 Tu nuevo enlace limpio e integrado
URL_SHEETS = "https://docs.google.com/spreadsheets/d/1os6jZgGLayMMVu5P_ltainpvKw-VSrva9UVmW_uhwIw/"

# Conexión con Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    conn = None

# Inicializar variables de navegación
if "paso" not in st.session_state:
    st.session_state.paso = 1  
if "rol" not in st.session_state:
    st.session_state.rol = None  

# ==========================================
# ENCABEZADO INSTITUCIONAL CON TU LOGO PNG
# ==========================================
col_logo, col_titulo = st.columns([1, 5])
NOMBRE_LOGO = "Logo_Universidad_Central_del_Ecuador.png"

with col_logo:
    if os.path.exists(NOMBRE_LOGO):
        st.image(NOMBRE_LOGO, width=110)
    else:
        st.warning(f"Falta el archivo '{NOMBRE_LOGO}'")

with col_titulo:
    st.markdown("""
        <div style="padding-top: 5px;">
            <h1 style="color: white; margin-bottom: 0px; font-family: 'Helvetica Neue', sans-serif;">UNIVERSIDAD CENTRAL DEL ECUADOR</h1>
            <h3 style="color: #D69E2E; margin-top: 0px; font-weight: 400; font-family: 'Helvetica Neue', sans-serif;">UCE-MATCH v2: Optimización de Tutorías Académicas</h3>
        </div>
    """, unsafe_allow_html=True)

st.write(f"**Progreso actual: Paso {st.session_state.paso} de 3**")
st.progress(st.session_state.paso / 3)
st.write("---")

# ==========================================
# PASO 1: SELECCIÓN OBLIGATORIA DE ROL
# ==========================================
if st.session_state.paso == 1:
    st.markdown("<h3 style='text-align: center; color: #2D3748;'>🎯 Paso 1: Elija cómo desea ingresar al sistema</h3>", unsafe_allow_html=True)
    st.write("")
    
    col_e, col_t = st.columns(2)
    
    with col_e:
        st.info("### 👨‍🎓 Modo Estudiante\nSi necesitas refuerzo académico, resolver dudas o prepararte para exámenes.")
        if st.button("Ingresar como Estudiante", use_container_width=True):
            st.session_state.rol = "Estudiante"
            st.session_state.paso = 2
            st.rerun()
            
    with col_t:
        st.success("### 👨‍🏫 Modo Tutor\nSi eres estudiante de semestres superiores y deseas ofertar acompañamiento académico.")
        if st.button("Ingresar como Tutor", use_container_width=True):
            st.session_state.rol = "Tutor"
            st.session_state.paso = 2
            st.rerun()

# ==========================================
# PASO 2: FORMULARIO DE REGISTRO EN LA NUBE
# ==========================================
elif st.session_state.paso == 2:
    st.subheader(f"📝 Paso 2: Formulario de Registro para {st.session_state.rol}")
    
    col1, col2 = st.columns(2)
    
    if st.session_state.rol == "Estudiante":
        with col1:
            nom_est = st.text_input("Nombres", key="nom_e")
            ape_est = st.text_input("Apellidos", key="ape_e")
            rango_horas_est = st.slider("Disponibilidad Horaria", value=(14, 18), min_value=7, max_value=22, format="%d:00", key="horas_e")
            tipo_asistencia_est = st.selectbox("Tipo de Asistencia Preferido", ["Presencial", "Virtual", "Indiferente (Cualquiera)"], key="tipo_as_e")
            
        with col2:
            area_est = st.selectbox("Seleccione su Área de Conocimiento", list(ESTRUCTURA_ÁREAS.keys()), key="area_e")
            carrera_est = st.selectbox("Seleccione su Carrera", ESTRUCTURA_ÁREAS[area_est]["carreras"], key="carrera_e")
            materia_est = st.selectbox("Materia Crítica Requerida", sorted(ESTRUCTURA_ÁREAS[area_est]["materias_comun"]), key="materia_e")
            
        c_atras, c_sig = st.columns([1, 4])
        if c_atras.button("⬅ Regresar", use_container_width=True):
            st.session_state.paso = 1
            st.rerun()
        if c_sig.button("Guardar Registro Global ➡", type="primary", use_container_width=True):
            if nom_est.strip() and ape_est.strip():
                nuevo_registro = pd.DataFrame([{
                    "nombre": f"{nom_est.strip()} {ape_est.strip()}", "area": area_est, "carrera": carrera_est,
                    "materia": materia_est, "hora_inicio": rango_horas_est[0], "hora_fin": rango_horas_est[1],
                    "asistencia": tipo_asistencia_est
                }])
                try:
                    df_actual = conn.read(spreadsheet=URL_SHEETS, worksheet="Estudiantes", ttl=0)
                    df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True).dropna(subset=["nombre"])
                    conn.update(spreadsheet=URL_SHEETS, worksheet="Estudiantes", data=df_final)
                    st.toast("¡Guardado exitosamente en la nube!", icon="☁️")
                    st.session_state.paso = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {e}. Verifique la configuración de los secretos de la app.")
            else:
                st.error("Por favor, rellene los campos de nombres y apellidos.")

    elif st.session_state.rol == "Tutor":
        with col1:
            nom_tut = st.text_input("Nombres", key="nom_t")
            ape_tut = st.text_input("Apellidos", key="ape_t")
            rango_horas_tut = st.slider("Disponibilidad Horaria", value=(13, 17), min_value=7, max_value=22, format="%d:00", key="horas_t")
            tipo_asistencia_tut = st.selectbox("Tipo de Asistencia Ofertado", ["Presencial", "Virtual", "Ambas Modalidades"], key="tipo_as_t")
            
        with col2:
            area_tut = st.selectbox("Seleccione el Área de Competencia", list(ESTRUCTURA_ÁREAS.keys()), key="area_t")
            carrera_tut = st.selectbox("Seleccione la Carrera de Origen", ESTRUCTURA_ÁREAS[area_tut]["carreras"], key="carrera_t")
            materia_tut = st.selectbox("Materia Crítica a Dictar", sorted(ESTRUCTURA_ÁREAS[area_tut]["materias_comun"]), key="materia_t")
            
        c_atras, c_sig = st.columns([1, 4])
        if c_atras.button("⬅ Regresar", use_container_width=True):
            st.session_state.paso = 1
            st.rerun()
        if c_sig.button("Guardar Registro Global ➡", type="primary", use_container_width=True):
            if nom_tut.strip() and ape_tut.strip():
                nuevo_registro = pd.DataFrame([{
                    "nombre": f"{nom_tut.strip()} {ape_tut.strip()}", "area": area_tut, "carrera": carrera_tut,
                    "materia": materia_tut, "hora_inicio": rango_horas_tut[0], "hora_fin": rango_horas_tut[1],
                    "asistencia": tipo_asistencia_tut
                }])
                try:
                    df_actual = conn.read(spreadsheet=URL_SHEETS, worksheet="Tutores", ttl=0)
                    df_final = pd.concat([df_actual, nuevo_registro], ignore_index=True).dropna(subset=["nombre"])
                    conn.update(spreadsheet=URL_SHEETS, worksheet="Tutores", data=df_final)
                    st.toast("¡Guardado exitosamente en la nube!", icon="☁️")
                    st.session_state.paso = 3
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al conectar con la base de datos: {e}. Verifique la configuración de los secretos de la app.")
            else:
                st.error("Por favor, rellene los campos de nombres y apellidos.")

# ==========================================
# PASO 3: RED GLOBAL DE EMPAREJAMIENTO
# ==========================================
elif st.session_state.paso == 3:
    st.subheader("🌐 Red de Emparejamiento en Tiempo Real")
    
    c_izq, c_der = st.columns([1, 1])
    if c_izq.button("⬅ Registrar otro perfil (Volver al Inicio)", use_container_width=True):
        st.session_state.paso = 1
        st.session_state.rol = None
        st.rerun()
    if c_der.button("🔄 Forzar Actualización / Recargar Grafo", type="primary", use_container_width=True):
        st.rerun()
        
    st.write("---")
    
    # Cargar datos desde la nube en tiempo real anulando la caché (ttl=0)
    try:
        lista_estudiantes = conn.read(spreadsheet=URL_SHEETS, worksheet="Estudiantes", ttl=0).to_dict(orient="records")
        lista_tutores = conn.read(spreadsheet=URL_SHEETS, worksheet="Tutores", ttl=0).to_dict(orient="records")
    except Exception:
        lista_estudiantes, lista_tutores = [], []
        st.error("No se pudo sincronizar la red interactiva con el servidor central.")

    G = nx.Graph()
    
    for est in lista_estudiantes:
        if pd.isna(est.get("nombre")): continue
        hover = f"**Estudiante:** {est['nombre']}\n**Carrera:** {est['carrera']}\n**Materia Requerida:** {est['materia']}\n**Horario:** {int(est['hora_inicio'])}:00 - {int(est['hora_fin'])}:00\n**Modalidad:** {est['asistencia']}"
        G.add_node(est["nombre"], label=est["nombre"], color="#2ecc71", title=hover, size=20)
        
    for tut in lista_tutores:
        if pd.isna(tut.get("nombre")): continue
        hover = f"**Tutor:** {tut['nombre']}\n**Carrera:** {tut['carrera']}\n**Materia Ofertada:** {tut['materia']}\n**Horario:** {int(tut['hora_inicio'])}:00 - {tut['hora_fin']}:00\n**Modalidad:** {tut['asistencia']}"
        G.add_node(tut["nombre"], label=tut["nombre"], color="#9b59b6", title=hover, size=24)
        
    for est in lista_estudiantes:
        if pd.isna(est.get("nombre")): continue
        for tut in lista_tutores:
            if pd.isna(tut.get("nombre")): continue
            if est["materia"] == tut["materia"]:
                se_cruzan = (max(est["hora_inicio"], tut["hora_inicio"]) < min(est["hora_fin"], tut["hora_fin"]))
                modalidad_compatible = (
                    est["asistencia"] == "Indiferente (Cualquiera)" or 
                    tut["asistencia"] == "Ambas Modalidades" or 
                    est["asistencia"] == tut["asistencia"]
                )
                
                if se_cruzan and modalidad_compatible:
                    h_i = int(max(est["hora_inicio"], tut["hora_inicio"]))
                    h_f = int(min(est["hora_fin"], tut["hora_fin"]))
                    asistencia_final = est["asistencia"] if est["asistencia"] != "Indiferente (Cualquiera)" else tut["asistencia"]
                    if asistencia_final == "Ambas Modalidades": asistencia_final = "A convenir"
                        
                    G.add_edge(
                        est["nombre"], tut["nombre"], 
                        title=f"Match en {est['materia']}\nHorario: {h_i}:00 - {h_f}:00\nModalidad: {asistencia_final}",
                        color="#e67e22", width=3
                    )
                    
    if len(G.nodes) == 0:
        st.info("La red se encuentra vacía. Escanea el código e ingresa los primeros perfiles.")
    else:
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        net.from_nx(G)
        net.toggle_physics(True)
        
        path_html = "grafo_interactivo.html"
        try:
            net.save_graph(path_html)
            if os.path.exists(path_html):
                with open(path_html, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                st.components.v1.html(html_content, height=620)
        except Exception as e:
            st.error(f"Error al compilar el grafo interactivo: {e}")
            
    st.write("---")
    c1, c2 = st.columns(2)
    c1.metric("Estudiantes Totales Registrados", len([e for e in lista_estudiantes if not pd.isna(e.get("nombre"))]))
    c2.metric("Tutores Totales en Red", len([t for t in lista_tutores if not pd.isna(t.get("nombre"))]))