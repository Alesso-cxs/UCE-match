import streamlit as st
import networkx as nx
from pyvis.network import Network
import os

# 1. Configuración de página obligatoria al inicio
st.set_page_config(page_title="UCE-MATCH v2", layout="wide")

# Diccionario Jerárquico Exacto con las 3 Áreas de la UCE
ESTRUCTURA_UCE = {
    "Área de Ciencia, Tecnología e Ingeniería": {
        "Ingeniería en Sistemas de la Información": {
            "1° Semestre": ["Algoritmos y Lógica", "Álgebra Lineal", "Cálculo Diferencial", "Física Básica"],
            "2° Semestre": ["Programación Orientada a Objetos", "Cálculo Integral", "Matemáticas Discretas", "Estructuras de Datos"]
        },
        "Ingeniería Civil": {
            "1° Semestre": ["Introducción a la Ingeniería Civil", "Geometría Descriptiva", "Cálculo Diferencial"],
            "2° Semestre": ["Mecánica Racional", "Topografía I", "Cálculo Integral"]
        }
    },
    "Área de Ciencias de la Salud": {
        "Medicina": {
            "1° Semestre": ["Anatomía Humana I", "Histología", "Biología Celular"],
            "2° Semestre": ["Anatomía Humana II", "Fisiología I", "Bioquímica Médica"]
        },
        "Enfermería": {
            "1° Semestre": ["Anatomía y Fisiología Básica", "Socioantropología", "Fundamentos de Enfermería I"],
            "2° Semestre": ["Bioquímica Descriptiva", "Microbiología y Parasitología", "Fundamentos de Enfermería II"]
        }
    },
    "Área de Ciencias Sociales y Humanidades": {
        "Derecho": {
            "1° Semestre": ["Introducción al Derecho", "Derecho Romano", "Historia del Derecho"],
            "2° Semestre": ["Teoría del Estado", "Derecho Civil I (Personas)", "Sociología Jurídica"]
        },
        "Administración de Empresas": {
            "1° Semestre": ["Fundamentos de Administración", "Contabilidad General I", "Matemática Financiera"],
            "2° Semestre": ["Procesos Administrativos", "Contabilidad de Costos", "Microeconomía I"]
        }
    }
}

# 2. Inicializar la memoria temporal en segundo plano si no existe
if "estudiantes" not in st.session_state:
    st.session_state.estudiantes = []
if "tutores" not in st.session_state:
    st.session_state.tutores = []

# 3. Creación de las Pestañas (Tabs)
tab_registro, tab_grafo = st.tabs(["📝 Registrar Datos", "🌐 Ver Grafo Interactivo"])

# ==========================================
# PESTAÑA 1: FORMULARIOS DE INGRESO
# ==========================================
with tab_registro:
    st.title("Ingreso de Datos con Selección Jerárquica Real")
    st.write("Filtros dinámicos adaptados exclusivamente para el ciclo básico (Primer y Segundo Semestre).")
    
    col1, col2 = st.columns(2)
    
    # Formulario para Estudiantes
    with col1:
        st.subheader("👨‍🎓 Datos del Estudiante")
        
        # Selectores REACTIVOS (Fuera del form para que actualicen al cambiar)
        nom_est = st.text_input("Nombres", key="input_nom_est")
        ape_est = st.text_input("Apellidos", key="input_ape_est")
        
        area_est = st.selectbox("Seleccione el Área", list(ESTRUCTURA_UCE.keys()), key="area_e")
        carrera_est = st.selectbox("Seleccione la Carrera", list(ESTRUCTURA_UCE[area_est].keys()), key="carrera_e")
        sem_est = st.selectbox("Seleccione el Semestre", ["1° Semestre", "2° Semestre"], key="sem_e")
        materia_est = st.selectbox("Materia que requiere tutoría", ESTRUCTURA_UCE[area_est][carrera_est][sem_est], key="materia_e")
        
        rango_horas_est = st.slider(
            "Disponibilidad Horaria",
            value=(14, 18), min_value=7, max_value=22, format="%d:00", key="horas_e"
        )
        
        # Formulario solo para encapsular el botón de envío seguro
        with st.form("form_guardar_estudiante"):
            btn_est = st.form_submit_button("Guardar Estudiante")
            if btn_est:
                if nom_est.strip() and ape_est.strip():
                    nombre_completo = f"{nom_est.strip()} {ape_est.strip()}"
                    st.session_state.estudiantes.append({
                        "nombre": nombre_completo,
                        "area": area_est,
                        "carrera": carrera_est,
                        "semestre": sem_est,
                        "materia": materia_est,
                        "hora_inicio": rango_horas_est[0],
                        "hora_fin": rango_horas_est[1]
                    })
                    st.success(f"Estudiante '{nombre_completo}' registrado con éxito.")
                else:
                    st.error("Por favor, llena los campos de nombre y apellido.")

    # Formulario para Tutores
    with col2:
        st.subheader("👨‍🏫 Datos del Tutor")
        
        # Selectores REACTIVOS (Fuera del form)
        nom_tut = st.text_input("Nombres", key="input_nom_tut")
        ape_tut = st.text_input("Apellidos", key="input_ape_tut")
        
        area_tut = st.selectbox("Seleccione el Área", list(ESTRUCTURA_UCE.keys()), key="area_t")
        carrera_tut = st.selectbox("Seleccione la Carrera", list(ESTRUCTURA_UCE[area_tut].keys()), key="carrera_t")
        sem_tut = st.selectbox("Nivel de la Materia", ["1° Semestre", "2° Semestre"], key="sem_t")
        materia_tut = st.selectbox("Materia que puede dictar", ESTRUCTURA_UCE[area_tut][carrera_tut][sem_tut], key="materia_t")
        
        rango_horas_tut = st.slider(
            "Disponibilidad Horaria",
            value=(13, 17), min_value=7, max_value=22, format="%d:00", key="horas_t"
        )
        
        with st.form("form_guardar_tutor"):
            btn_tut = st.form_submit_button("Guardar Tutor")
            if btn_tut:
                if nom_tut.strip() and ape_tut.strip():
                    nombre_completo = f"{nom_tut.strip()} {ape_tut.strip()}"
                    st.session_state.tutores.append({
                        "nombre": nombre_completo,
                        "area": area_tut,
                        "carrera": carrera_tut,
                        "semestre": sem_tut,
                        "materia": materia_tut,
                        "hora_inicio": rango_horas_tut[0],
                        "hora_fin": rango_horas_tut[1]
                    })
                    st.success(f"Tutor '{nombre_completo}' registrado con éxito.")
                else:
                    st.error("Por favor, llena los campos de nombre y apellido.")

    st.write("---")
    c1, c2 = st.columns(2)
    c1.metric("Estudiantes en Cola", len(st.session_state.estudiantes))
    c2.metric("Tutores en Cola", len(st.session_state.tutores))


# ==========================================
# PESTAÑA 2: VISUALIZACIÓN DINÁMICA DEL GRAFO
# ==========================================
with tab_grafo:
    st.title("Visualización Dinámica del Grafo")
    st.write("Conexiones automáticas basadas exclusivamente en coincidencia de **Materia** y cruce en la **Disponibilidad Horaria**.")
    
    if len(st.session_state.estudiantes) == 0 and len(st.session_state.tutores) == 0:
        st.info("Aún no hay registros en la sesión actual. Llena los formularios para mapear las aristas.")
    else:
        G = nx.Graph()
        
        # Insertar nodos de Estudiantes
        for est in st.session_state.estudiantes:
            info_hover = f"Estudiante: {est['nombre']}\n{est['carrera']} ({est['semestre']})\nMateria: {est['materia']}\nHorario: {est['hora_inicio']}:00 a {est['hora_fin']}:00"
            G.add_node(est["nombre"], label=est["nombre"], color="#2ecc71", title=info_hover, size=20)
            
        # Insertar nodos de Tutores
        for tut in st.session_state.tutores:
            info_hover = f"Tutor: {tut['nombre']}\n{tut['carrera']} ({tut['semestre']})\nMateria: {tut['materia']}\nHorario: {tut['hora_inicio']}:00 a {tut['hora_fin']}:00"
            G.add_node(tut["nombre"], label=tut["nombre"], color="#3498db", title=info_hover, size=25)
            
        # Algoritmo de Emparejamiento por Grafos
        for est in st.session_state.estudiantes:
            for tut in st.session_state.tutores:
                misma_materia = (est["materia"] == tut["materia"])
                cruce_horario = (max(est["hora_inicio"], tut["hora_inicio"]) < min(est["hora_fin"], tut["hora_fin"]))
                
                if misma_materia and cruce_horario:
                    h_inicio_match = max(est["hora_inicio"], tut["hora_inicio"])
                    h_fin_match = min(est["hora_fin"], tut["hora_fin"])
                    
                    G.add_edge(
                        est["nombre"], 
                        tut["nombre"], 
                        title=f"Match en {est['materia']}\nCruce: {h_inicio_match}:00 - {h_fin_match}:00\n({est['semestre']})",
                        color="#e74c3c", 
                        width=3
                    )

        # Configurar y renderizar PyVis
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
            st.error(f"Ocurrió un inconveniente al compilar el grafo: {e}")