import streamlit as st
import networkx as nx
from pyvis.network import Network
import pandas as pd
import requests
import os

# 1. Configuración obligatoria de la página al inicio
st.set_page_config(page_title="UCE-MATCH v2", layout="wide")

# 🔗 REEMPLAZA ESTO CON LA URL QUE TE DIO APPS SCRIPT
URL_API = "https://script.google.com/macros/s/AKfycbwa4g2gcuiYN2dYYBDSPFV5ypuWISi4nlH2h7upKOSzt7HJd28xtk6CrIby8Oc4HzB8Pg/exec"

# ==========================================
# DISEÑO Y ESTILOS PERSONALIZADOS (CSS INTERNO)
# ==========================================
st.markdown("""
    <style>
    [data-testid="stMetricValue"] {
        color: #1A365D;
        font-weight: bold;
    }
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

ESTRUCTURA_ÁREAS = {
    "Ciencias Exactas": {
        "carreras": ["Ing. Civil", "Sistemas", "Computación", "Matemáticas", "Geología", "Petróleos", "Minas", "Diseño Industrial", "Mecánica", "Ing. Ambiental", "Ing. Química", "Bioprocesos"],
        "materias_comun": ["Análisis I (Cálculo I)", "Análisis II (Cálculo II)", "Programación", "Introducción al Análisis Matemático", "Geometría Descriptiva", "Química General"]
    },
    "Artes y Arquitectura": {
        "carreras": ["Artes Escénicas", "Artes Musicales", "Artes Plásticas", "Danza", "Arquitectura y Urbanismo"],
        "materias_comun": ["Movimiento y Voz Auténticos/Primarios", "Armonía, Contrapunto y Entrenamiento Auditivo II", "Morfología", "Técnicas de Danza Contemporánea: Inicial II", "Taller de Diseño Básico II"]
    },
    "Ciencias de la Vida": {
        "carreras": ["Biología", "Agronomía", "Medicina Veterinaria", "Turismo", "Química", "Recursos Naturales Renovables", "Bioquímica y Farmacia"],
        "materias_comun": ["Análisis I (Cálculo I)", "Química Orgánica", "Anatomía Animal I", "Contabilidad / Matemática Financiera", "Física I", "Topografía I", "Química Inorgánica"]
    },
    "Ciencias de la Salud Humana": {
        "carreras": ["Medicina", "Enfermería", "Obstetricia", "Laboratorio Clínico", "Imageneología y Radiología", "Fonoaudiología", "Fisioterapia", "Terapia Ocupacional", "Atención Prehospitalaria", "Psicología Clínica", "Psicología Educativa", "Odontología", "Pedagogía de la Act. Física", "Entrenamiento Deportivo"],
        "materias_comun": ["Anatomía Humana I", "Bioquímica Aplicada", "Embriología y Genética", "Química Analítica", "Física Radiológica", "Anatomofisiología", "Biomecánica General", "Neuroanatomía Funcional", "Soporte Vital Básico", "Neurofisiología", "Bases Biológicas del Comportamiento", "Histología Estomatológica", "Anatomía Funcional y del Movimiento", "Fisiología del Esfuerzo Físico"]
    }
}

if "paso" not in st.session_state:
    st.session_state.paso = 1  
if "rol" not in st.session_state:
    st.session_state.rol = None  

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

# PASO 1
if st.session_state.paso == 1:
    st.markdown("<h3 style='text-align: center; color: #2D3748;'>🎯 Paso 1: Elija cómo desea ingresar al sistema</h3>", unsafe_allow_html=True)
    col_e, col_t = st.columns(2)
    with col_e:
        st.info("### 👨‍🎓 Modo Estudiante\nSi necesitas refuerzo académico.")
        if st.button("Ingresar como Estudiante", use_container_width=True):
            st.session_state.rol = "Estudiante"
            st.session_state.paso = 2
            st.rerun()
    with col_t:
        st.success("### 👨‍🏫 Modo Tutor\nSi deseas ofertar acompañamiento.")
        if st.button("Ingresar como Tutor", use_container_width=True):
            st.session_state.rol = "Tutor"
            st.session_state.paso = 2
            st.rerun()

# PASO 2
elif st.session_state.paso == 2:
    st.subheader(f"📝 Paso 2: Formulario de Registro para {st.session_state.rol}")
    col1, col2 = st.columns(2)
    
    # Manejo unificado de variables según rol
    key_prefix = "e" if st.session_state.rol == "Estudiante" else "t"
    sheet_target = "Estudiantes" if st.session_state.rol == "Estudiante" else "Tutores"
    
    with col1:
        nom = st.text_input("Nombres", key=f"nom_{key_prefix}")
        ape = st.text_input("Apellidos", key=f"ape_{key_prefix}")
        rango_horas = st.slider("Disponibilidad Horaria", value=(14, 18), min_value=7, max_value=22, format="%d:00", key=f"horas_{key_prefix}")
        tipo_asistencia = st.selectbox("Modalidad", ["Presencial", "Virtual", "Cualquiera"] if key_prefix == "e" else ["Presencial", "Virtual", "Ambas Modalidades"], key=f"tipo_as_{key_prefix}")
        
    with col2:
        area = st.selectbox("Área de Conocimiento", list(ESTRUCTURA_ÁREAS.keys()), key=f"area_{key_prefix}")
        carrera = st.selectbox("Carrera", ESTRUCTURA_ÁREAS[area]["carreras"], key=f"carrera_{key_prefix}")
        materia = st.selectbox("Materia Crítica", sorted(ESTRUCTURA_ÁREAS[area]["materias_comun"]), key=f"materia_{key_prefix}")
        
    c_atras, c_sig = st.columns([1, 4])
    if c_atras.button("⬅ Regresar", use_container_width=True):
        st.session_state.paso = 1
        st.rerun()
        
    if c_sig.button("Guardar Registro Global ➡", type="primary", use_container_width=True):
        if nom.strip() and ape.strip():
            payload = {
                "sheet": sheet_target,
                "nombre": f"{nom.strip()} {ape.strip()}",
                "area": area,
                "carrera": carrera,
                "materia": materia,
                "hora_inicio": rango_horas[0],
                "hora_fin": rango_horas[1],
                "asistencia": tipo_asistencia
            }
            try:
                response = requests.post(URL_API, params=payload)
                if response.status_code == 200:
                    st.toast("¡Guardado exitosamente en la nube!", icon="☁️")
                    st.session_state.paso = 3
                    st.rerun()
                else:
                    st.error("Error en la respuesta del servidor de Google.")
            except Exception as e:
                st.error(f"Error de red: {e}")
        else:
            st.error("Por favor, rellene los campos de nombres y apellidos.")

# PASO 3
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
    
    # Lectura a través del script API
    try:
        lista_estudiantes = requests.get(URL_API, params={"sheet": "Estudiantes"}).json()
        lista_tutores = requests.get(URL_API, params={"sheet": "Tutores"}).json()
    except Exception:
        lista_estudiantes, lista_tutores = [], []
        st.error("No se pudo sincronizar la red dinámica.")

    G = nx.Graph()
    
    for est in lista_estudiantes:
        if not est.get("nombre"): continue
        hover = f"**Estudiante:** {est['nombre']}\n**Carrera:** {est['carrera']}\n**Materia:** {est['materia']}\n**Horario:** {int(est['hora_inicio'])}:00 - {int(est['hora_fin'])}:00"
        G.add_node(est["nombre"], label=est["nombre"], color="#2ecc71", title=hover, size=20)
        
    for tut in lista_tutores:
        if not tut.get("nombre"): continue
        hover = f"**Tutor:** {tut['nombre']}\n**Carrera:** {tut['carrera']}\n**Materia:** {tut['materia']}\n**Horario:** {int(tut['hora_inicio'])}:00 - {int(tut['hora_fin'])}:00"
        G.add_node(tut["nombre"], label=tut["nombre"], color="#9b59b6", title=hover, size=24)
        
    for est in lista_estudiantes:
        if not est.get("nombre"): continue
        for tut in lista_tutores:
            if not tut.get("nombre"): continue
            if est["materia"] == tut["materia"]:
                se_cruzan = (max(float(est["hora_inicio"]), float(tut["hora_inicio"])) < min(float(est["hora_fin"]), float(tut["hora_fin"])))
                if se_cruzan:
                    G.add_edge(est["nombre"], tut["nombre"], color="#e67e22", width=3)
                    
    if len(G.nodes) == 0:
        st.info("La red se encuentra vacía.")
    else:
        net = Network(height="600px", width="100%", bgcolor="#ffffff", font_color="black")
        net.from_nx(G)
        path_html = "grafo_interactivo.html"
        try:
            net.save_graph(path_html)
            with open(path_html, 'r', encoding='utf-8') as f:
                html_content = f.read()
            st.components.v1.html(html_content, height=620)
        except Exception as e:
            st.error(f"Error al compilar el grafo: {e}")