import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import datetime

# --- 1. CONFIGURACIÓN Y CSS (ESTILO DASHBOARD IOT) ---
st.set_page_config(
    page_title="People Analytics Dashboard",
    page_icon="😊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectamos CSS para simular el diseño de la imagen
st.markdown("""
    <style>
    /* Fondo general */
    .stApp {
        background-color: #1a1c29;
        color: #ffffff;
    }
    /* Fondo de la barra lateral */
    [data-testid="stSidebar"] {
        background-color: #151724;
        border-right: 1px solid #2b2e43;
    }
    /* Estilo de las Tarjetas (Contenedores) */
    div[data-testid="stVerticalBlock"] > div > div > div[data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e2132;
        border-radius: 15px;
        padding: 15px;
        border: 1px solid #2b2e43;
    }
    /* Títulos */
    h1, h2, h3, h4 {
        color: #ffffff !important;
        font-family: 'Segoe UI', sans-serif;
    }
    /* Estilo de la tabla */
    .stDataFrame {
        background-color: #1e2132;
        border-radius: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# Paleta de colores basada en la imagen
paletaColores = ['#00e5ff', '#ff4d85', '#9575cd', '#69f0ae', '#ffd54f', '#ff9f43', '#050C9C']

# --- 2. FUNCIONES DE ESTILO (Reemplazan a utils.py) ---
def aplicar_tema_neon(fig, titulo="", subtitulo="", legend=False):
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br><span style='font-size:11px;color:#8a8d93;'>{subtitulo}</span>", 
            font=dict(color='#ffffff', size=14)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', size=11),
        xaxis=dict(showgrid=False, zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2b2e43', zeroline=False),
        showlegend=legend,
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff')),
        margin=dict(l=10, r=10, t=50, b=10)
    )
    return fig

# Función para crear los medidores de la parte superior
def crear_medidor(titulo, valor_str, porcentaje, color):
    fig = go.Figure(go.Pie(
        values=[porcentaje, 100-porcentaje],
        hole=0.75,
        marker_colors=[color, '#2b2e43'],
        textinfo='none', hoverinfo='none', showlegend=False
    ))
    fig.update_layout(
        title=dict(text=titulo, font=dict(color='#8a8d93', size=12), x=0.5, y=0.9),
        paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=10, r=10, t=40, b=10), height=160,
        annotations=[dict(text=f"<b>{valor_str}</b>", x=0.5, y=0.5, font_size=18, font_color='#ffffff', showarrow=False)]
    )
    return fig

# --- 3. CARGA Y PREPARACIÓN DE DATOS (Tu código original) ---
archivo = './HR_DATA.csv'
dfDatosHR = pd.read_csv(archivo,parse_dates=['DOB','DateofHire','DateofTermination'])

fechaHoy= datetime.datetime.today()
rangoTrimestre=datetime.timedelta(days=90)
fechaTrimestre=fechaHoy-rangoTrimestre

dfDatosHR['Tenure']=(fechaHoy-dfDatosHR['DateofHire'])/ datetime.timedelta(days=365)
dfDatosHR['Age']=(fechaHoy-dfDatosHR['DOB'])/ datetime.timedelta(days=365)
dfDatosHR['Sex']=dfDatosHR['Sex'].apply(lambda x:'Women' if x=='F' else 'Men')

dfDatosHR['TenureRange']=pd.cut(dfDatosHR['Tenure'], bins=[0, 1 ,3, 5, 10, 15, 20,100],
        labels=["<1 y", "1-3 y", "3-5 y","5-10 y","10-15 y","15-20 y","> 20 y"], ordered=False)
dfDatosHR['AgeRange']=pd.cut(dfDatosHR['Age'], bins=[17, 20 ,30, 40, 50, 60, 70,100],
        labels=["<20 y", "20-30 y", "30-40 y","40-50 y","50-60 y","60-70 y","> 70 y"], ordered=False)

dfDatosHR['PerformanceScore'] = pd.Categorical(dfDatosHR['PerformanceScore'], 
                      categories=['Needs Improvement', 'PIP','Fully Meets','Exceeds'],
                      ordered=True)
dfEmpleadosActivos =dfDatosHR[dfDatosHR['EmploymentStatus']=='Active']

empActivos=len(dfDatosHR[dfDatosHR['EmploymentStatus']=='Active'])
empHombres=len(dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Men'])
empMujeres=len(dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Women'])

empNuevosTrimestre = len(dfDatosHR[dfDatosHR['DateofHire']>=fechaTrimestre])
empTerminadosTrimestre = len(dfDatosHR[dfDatosHR['DateofTermination']>=fechaTrimestre])

empAntiguedad=dfEmpleadosActivos['Tenure'].mean()
empAntiguedadHombres=dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Men']['Tenure'].mean()
empAntiguedadMujeres=dfEmpleadosActivos[dfEmpleadosActivos['Sex']=='Women']['Tenure'].mean()

empActivosDept = dfEmpleadosActivos.groupby(['Department','Sex']).agg(Employees=('EmpID','count')).reset_index()
empActivosDeptTotal = dfEmpleadosActivos.groupby(['Department']).agg(Employees=('EmpID','count')).reset_index()
ordenDeptTotal = empActivosDeptTotal.sort_values('Employees')['Department'].unique()

empActivosDeptTenure = dfEmpleadosActivos.groupby(['Department','TenureRange']).agg(Employees=('EmpID','count')).reset_index()
empActivoAge = dfEmpleadosActivos.groupby(['AgeRange','Sex']).agg(Employees=('EmpID','count')).reset_index()
dfSpanofControl = dfEmpleadosActivos.groupby(['ManagerName']).agg(Employees=('EmpID','count')).reset_index()
empSpanofControl=dfSpanofControl['Employees'].mean()

# NOTA: Cambié freq='M' por freq='ME' para que no de error en Pandas nuevo
empHires=dfDatosHR.groupby(pd.Grouper(key="DateofHire",freq='ME')).agg(Employees=('EmpID','count')).reset_index()
empHires.columns=['Period','Employees']
empHires['action']='Hire'

empTerminations=dfDatosHR.groupby(pd.Grouper(key="DateofTermination",freq='ME')).agg(Employees=('EmpID','count')).reset_index()
empTerminations.columns=['Period','Employees']
empTerminations['Employees']=empTerminations['Employees']*-1
empTerminations['action']='Termination'

empHiresTerminations = pd.concat([empHires,empTerminations])
empHiresTerminations=empHiresTerminations[empHiresTerminations['Period']>=fechaHoy-datetime.timedelta(days=730)]

empTerminations =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby('EmploymentStatus').agg(Employees=('EmpID','count')).reset_index()
empTerminationReason =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby(['EmploymentStatus','TermReason']).agg(Employees=('EmpID','count')).reset_index()
empTerminationReasonTotal =dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated','Terminated for Cause'])].groupby(['TermReason']).agg(Employees=('EmpID','count')).reset_index()
ordenTerminationReason = empTerminationReasonTotal.sort_values('Employees')['TermReason'].unique()

empActivoTenure = dfEmpleadosActivos.groupby(['TenureRange','Sex']).agg(Employees=('EmpID','count')).reset_index()
empActivoDeptTenure = dfEmpleadosActivos.groupby(['TenureRange','Department']).agg(Employees=('EmpID','count')).reset_index()
empActivoPerformance = dfEmpleadosActivos.groupby(['PerformanceScore']).agg(Employees=('EmpID','count')).reset_index()
dfEmpSalarios = dfEmpleadosActivos.groupby(['Position','Sex']).agg(PayRate=('PayRate','mean'),Employees=('EmpID','count')).reset_index()

# --- 4. CREACIÓN DE GRÁFICOS (Aplicando el tema) ---
figPerformance = px.pie(empActivoPerformance.sort_values('Employees'),names='PerformanceScore',values='Employees', color_discrete_sequence=paletaColores)
figPerformance.update_traces(textposition='outside', textinfo='percent+label')
figPerformance = aplicar_tema_neon(figPerformance,titulo="Performance",subtitulo="")

figTerminations = px.pie(empTerminations,names='EmploymentStatus',values='Employees', color_discrete_sequence=paletaColores)
figTerminations.update_traces(textposition='outside', textinfo='percent+label')
figTerminations = aplicar_tema_neon(figTerminations,titulo="Terminations by type",subtitulo="Last 2 years")

figTerminationsReason = px.bar(empTerminationReason,y='TermReason',x='Employees',color='EmploymentStatus', color_discrete_sequence=paletaColores)
figTerminationsReason.update_yaxes(categoryorder='array', categoryarray= ordenTerminationReason)
figTerminationsReason = aplicar_tema_neon(figTerminationsReason,legend=True,titulo="Reason for Terminations",subtitulo="Last 2 years")

figDeptTenure = px.bar(empActivosDeptTenure.sort_values('Employees',ascending=False),y='Department',x='Employees',color='TenureRange', color_discrete_sequence=paletaColores)
figDeptTenure.update_yaxes(categoryorder='array', categoryarray= ordenDeptTotal)
figDeptTenure.update_layout(legend_traceorder="grouped")
figDeptTenure = aplicar_tema_neon(figDeptTenure,legend=True,titulo="Tenure by Department",subtitulo="")

figHireTerminations = px.bar(empHiresTerminations,x='Period',y='Employees',color='action', color_discrete_sequence=paletaColores)
figHireTerminations = aplicar_tema_neon(figHireTerminations,legend=True,titulo="Hires vs Terminations",subtitulo="Last 2 years")

figEmpXDept=px.bar(empActivosDept.sort_values(['Sex','Employees']),x='Employees',y='Department',color='Sex',
           barmode='group',text='Employees',
           color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpXDept = aplicar_tema_neon(figEmpXDept,legend=True,titulo="Employees by Department",subtitulo="Grouped by sex")

figEmpAge=px.bar(empActivoAge.sort_values(['Sex']),y='Employees',x='AgeRange',color='Sex',
           barmode='group',text='Employees', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpAge = aplicar_tema_neon(figEmpAge,legend=True,titulo="Employees by Age",subtitulo="Grouped by sex")

figEmpTenure=px.bar(empActivoTenure.sort_values(['Sex']),y='Employees',x='TenureRange',color='Sex',
           barmode='group',text='Employees', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]})
figEmpTenure = aplicar_tema_neon(figEmpTenure,legend=True,titulo="Employees by Tenure",subtitulo="Grouped by sex")

figPerfvsSat = px.scatter(dfEmpleadosActivos.sort_values('PerformanceScore'),x='EngagementSurvey',y='PerformanceScore', color='EngagementSurvey',
                          color_continuous_scale=px.colors.colorbrewer.RdYlGn)
figPerfvsSat = aplicar_tema_neon(figPerfvsSat,legend=False,titulo="Engagement vs Performance",subtitulo="Turn over risk")

figSalarioSexo = px.bar(dfEmpSalarios.sort_values('PayRate'),x='Position',y='PayRate', color='Sex', color_discrete_map={'Men':paletaColores[0],'Women':paletaColores[1]},
                        barmode='group',text='PayRate')
figSalarioSexo.update_traces(textangle=-90, texttemplate = "%{y:,.1f}")
figSalarioSexo = aplicar_tema_neon(figSalarioSexo,legend=True,titulo="Salary Distribution",subtitulo="Turn over risk")

# --- 5. CONSTRUCCIÓN DEL DASHBOARD ---
st.title("People Analytics Dashboard")

with st.expander('Data'):    
    st.dataframe(dfDatosHR)
    st.write('**Source:** https://www.kaggle.com/datasets/davidepolizzi/hr-data-set-based-on-human-resources-data-set?')

st.markdown("<br>", unsafe_allow_html=True)

# Fila 1: Medidores Circulares (Replicando la parte superior de la imagen)
col1, col2, col3, col4 = st.columns(4)
with col1:
    with st.container(border=True):
        st.plotly_chart(crear_medidor("Active Employees", f"{empActivos:,.0f}", 75, paletaColores[0]), use_container_width=True)
with col2:
    with st.container(border=True):
        st.plotly_chart(crear_medidor("Women", f"{(empMujeres/empActivos)*100:.0f}%", (empMujeres/empActivos)*100, paletaColores[1]), use_container_width=True)
with col3:
    with st.container(border=True):
        st.plotly_chart(crear_medidor("Men", f"{(empHombres/empActivos)*100:.0f}%", (empHombres/empActivos)*100, paletaColores[3]), use_container_width=True)
with col4:
    with st.container(border=True):
        st.plotly_chart(crear_medidor("Avg Tenure", f"{empAntiguedad:.1f} y", 60, paletaColores[2]), use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fila 2: Gráficos Principales
st.subheader("Hires and terminations")
c1, c2 = st.columns([2, 1])
with c1:
    with st.container(border=True):
        st.plotly_chart(figHireTerminations, use_container_width=True)
with c2:
    with st.container(border=True):
        st.plotly_chart(figTerminations, use_container_width=True)

# Fila 3: Gráficos de barras (3 columnas)
st.subheader("Organization & Demographics")
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.plotly_chart(figEmpXDept, use_container_width=True)
with c2:
    with st.container(border=True):
        st.plotly_chart(figEmpAge, use_container_width=True)
with c3:
    with st.container(border=True):
        st.plotly_chart(figPerformance, use_container_width=True)

# Fila 4: Más gráficos (3 columnas)
c1, c2, c3 = st.columns(3)
with c1:
    with st.container(border=True):
        st.plotly_chart(figDeptTenure, use_container_width=True)
with c2:
    with st.container(border=True):
        st.plotly_chart(figEmpTenure, use_container_width=True)
with c3:
    with st.container(border=True):
        st.plotly_chart(figTerminationsReason, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Fila 5: Salarios y Dispersión (2 columnas)
st.subheader("Salary & Risk")
c1, c2 = st.columns(2)
with c1:
    with st.container(border=True):
        st.plotly_chart(figSalarioSexo, use_container_width=True)
with c2:
    with st.container(border=True):
        st.plotly_chart(figPerfvsSat, use_container_width=True)