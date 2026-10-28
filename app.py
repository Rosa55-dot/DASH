import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA
st.set_page_config(
    page_title="People Analytics - Neon UI",
    page_icon="👥",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. CSS PARA REPLICAR EL DISEÑO (Fondo oscuro, tarjetas, colores)
st.markdown("""
    <style>
    /* Fondo principal */
    .stApp {
        background-color: #1a1c29;
        color: #ffffff;
    }
    /* Estilo del Sidebar */
    [data-testid="stSidebar"] {
        background-color: #151724;
        border-right: 1px solid #2b2e43;
    }
    /* Tarjetas de métricas circulares (Contenedores) */
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e2132;
        border-radius: 15px;
        padding: 10px;
        border: 1px solid #2b2e43;
    }
    /* Títulos */
    h1, h2, h3 {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Tablas y Dataframes */
    .stDataFrame {
        background-color: #1e2132;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# 3. PALETA DE COLORES (Basada en tu imagen)
COLOR_BG = '#1a1c29'
COLOR_CARD = '#1e2132'
COLOR_CYAN = '#00e5ff'
COLOR_PINK = '#ff4d85'
COLOR_PURPLE = '#9575cd'
COLOR_GREEN = '#69f0ae'
COLOR_TEXT = '#ffffff'
COLOR_MUTED = '#8a8d93'

paletaColores = [COLOR_CYAN, COLOR_PINK, COLOR_PURPLE, COLOR_GREEN, '#ffd54f']

# 4. FUNCIONES DE ESTILO
def aplicar_tema_grafico(fig, titulo=""):
    fig.update_layout(
        title=dict(text=titulo, font=dict(color=COLOR_TEXT, size=14), x=0.05),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color=COLOR_TEXT, size=11),
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2b2e43', zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color=COLOR_TEXT))
    )
    return fig

# Función para crear los "Donuts" de la parte superior
def crear_medidor_circular(titulo, valor, sufijo="", color=COLOR_CYAN, porcentaje_visual=75):
    fig = go.Figure(go.Pie(
        values=[porcentaje_visual, 100-porcentaje_visual],
        hole=0.75,
        marker_colors=[color, '#2b2e43'],
        textinfo='none',
        hoverinfo='none',
        showlegend=False
    ))
    fig.update_layout(
        title=dict(text=titulo, font=dict(color=COLOR_MUTED, size=12), x=0.5, y=0.9),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10), height=150,
        annotations=[dict(text=f"<b>{valor}{sufijo}</b>", x=0.5, y=0.5, font_size=18, font_color=COLOR_TEXT, showarrow=False)]
    )
    return fig

# 5. CARGA Y PREPARACIÓN DE DATOS
try:
    dfDatosHR = pd.read_csv('./HR_DATA.csv', parse_dates=['DOB', 'DateofHire', 'DateofTermination'])
except FileNotFoundError:
    st.error("⚠️ Error: No se encontró 'HR_DATA.csv'.")
    st.stop()

fechaHoy = datetime.datetime.today()
dfDatosHR['Tenure'] = (fechaHoy - dfDatosHR['DateofHire']) / datetime.timedelta(days=365)
dfDatosHR['Age'] = (fechaHoy - dfDatosHR['DOB']) / datetime.timedelta(days=365)
dfDatosHR['Sex'] = dfDatosHR['Sex'].apply(lambda x: 'Women' if x == 'F' else 'Men')
dfDatosHR['TenureRange'] = pd.cut(dfDatosHR['Tenure'], bins=[0, 1, 3, 5, 10, 15, 20, 100], labels=["<1y", "1-3y", "3-5y", "5-10y", "10-15y", "15-20y", ">20y"])
dfDatosHR['AgeRange'] = pd.cut(dfDatosHR['Age'], bins=[17, 20, 30, 40, 50, 60, 70, 100], labels=["<20", "20-30", "30-40", "40-50", "50-60", "60-70", ">70"])

dfEmpleadosActivos = dfDatosHR[dfDatosHR['EmploymentStatus'] == 'Active']
empActivos = len(dfEmpleadosActivos)
empHombres = len(dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Men'])
empMujeres = len(dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Women'])
empAntiguedad = dfEmpleadosActivos['Tenure'].mean()

# 6. CREACIÓN DE GRÁFICOS
figHireTerminations = px.bar(
    dfDatosHR.groupby([pd.Grouper(key="DateofHire", freq='ME')]).agg(Employees=('EmpID', 'count')).reset_index(),
    x='DateofHire', y='Employees', color_discrete_sequence=[COLOR_CYAN]
)
figHireTerminations = aplicar_tema_grafico(figHireTerminations, "Contrataciones Recientes")

figEmpXDept = px.bar(
    dfEmpleadosActivos.groupby(['Department', 'Sex']).agg(Employees=('EmpID', 'count')).reset_index(),
    x='Employees', y='Department', color='Sex', barmode='group',
    color_discrete_map={'Men': COLOR_CYAN, 'Women': COLOR_PINK}
)
figEmpXDept = aplicar_tema_grafico(figEmpXDept, "Empleados por Departamento")

figPerformance = px.pie(
    dfEmpleadosActivos.groupby('PerformanceScore').agg(Employees=('EmpID', 'count')).reset_index(),
    names='PerformanceScore', values='Employees', color_discrete_sequence=paletaColores, hole=0.5
)
figPerformance = aplicar_tema_grafico(figPerformance, "Performance")

# 7. CONSTRUCCIÓN DEL DASHBOARD (Layout)
st.markdown(f"<h2 style='margin-bottom: 0;'>Dashboard de Personas</h2>", unsafe_allow_html=True)
st.markdown(f"<p style='color: {COLOR_MUTED}; font-size: 14px;'>Resumen general de la fuerza laboral</p>", unsafe_allow_html=True)

st.divider()

# Fila 1: Medidores Circulares (Replicando la imagen)
col1, col2, col3, col4 = st.columns(4)

with col1:
    with st.container(border=True):
        st.plotly_chart(crear_medidor_circular("Empleados Activos", empActivos, "", COLOR_CYAN, 85), use_container_width=True)

with col2:
    with st.container(border=True):
        porcentaje_mujeres = (empMujeres/empActivos)*100
        st.plotly_chart(crear_medidor_circular("Mujeres", f"{porcentaje_mujeres:.0f}", "%", COLOR_PINK, porcentaje_mujeres), use_container_width=True)

with col3:
    with st.container(border=True):
        porcentaje_hombres = (empHombres/empActivos)*100
        st.plotly_chart(crear_medidor_circular("Hombres", f"{porcentaje_hombres:.0f}", "%", COLOR_GREEN, porcentaje_hombres), use_container_width=True)

with col4:
    with st.container(border=True):
        st.plotly_chart(crear_medidor_circular("Antigüedad Prom.", f"{empAntiguedad:.1f}", " años", COLOR_PURPLE, 65), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fila 2: Gráfico principal y gráfico secundario
col_main, col_side = st.columns([2, 1])

with col_main:
    with st.container(border=True):
        st.plotly_chart(figHireTerminations, use_container_width=True)

with col_side:
    with st.container(border=True):
        st.plotly_chart(figPerformance, use_container_width=True)

# Fila 3: Gráficos de barras y tablas
col_b1, col_b2 = st.columns(2)

with col_b1:
    with st.container(border=True):
        st.plotly_chart(figEmpXDept, use_container_width=True)

with col_b2:
    with st.container(border=True):
        st.write("**Datos Recientes**")
        # Mostramos una tabla estilizada
        st.dataframe(dfEmpleadosActivos[['EmpID', 'Department', 'Sex', 'Tenure']].head(8), use_container_width=True)