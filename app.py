import streamlit as st
import plotly.express as px
import pandas as pd
import datetime

# 1. CONFIGURACIÓN DE LA PÁGINA Y ESTILO NEÓN
st.set_page_config(
    page_title="People Analytics",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectamos CSS para poner el fondo oscuro estilo Cyberpunk/Neón
st.markdown("""
    <style>
    /* Fondo principal oscuro */
    .stApp {
        background-color: #121218;
        color: #ffffff;
    }
    /* Estilo para las métricas (KPIs) */
    [data-testid="stMetricValue"] {
        color: #4dd0e1 !important; /* Cian neón */
    }
    [data-testid="stMetricLabel"] {
        color: #ffffff !important;
    }
    /* Color de los títulos */
    h1, h2, h3 {
        color: #ffffff !important;
    }
    </style>
""", unsafe_allow_html=True)

# 2. PALETA DE COLORES NEÓN
# Cian, Rosa, Morado, Verde Menta, Amarillo, Naranja Neón, Azul Eléctrico
paletaColores = ['#4dd0e1', '#ff4d85', '#9575cd', '#69f0ae', '#ffd54f', '#ff9f43', '#00e5ff']

# 3. FUNCIÓN PARA APLICAR EL TEMA A LOS GRÁFICOS
# (Reemplaza al archivo utils.py que no tienes)
def aplicar_tema_neon(fig, titulo="", subtitulo=""):
    fig.update_layout(
        title=dict(
            text=f"<b>{titulo}</b><br><span style='font-size:12px;color:#8a8d93;'>{subtitulo}</span>", 
            font=dict(color='#ffffff', size=16)
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#ffffff', size=11),
        xaxis=dict(showgrid=True, gridcolor='#2b2b40', zeroline=False),
        yaxis=dict(showgrid=True, gridcolor='#2b2b40', zeroline=False),
        legend=dict(bgcolor='rgba(0,0,0,0)', font=dict(color='#ffffff'))
    )
    return fig

# 4. CARGA Y PREPARACIÓN DE DATOS
# Asegúrate de tener el archivo HR_DATA.csv en la misma carpeta
try:
    archivo = './HR_DATA.csv'
    dfDatosHR = pd.read_csv(archivo, parse_dates=['DOB', 'DateofHire', 'DateofTermination'])
except FileNotFoundError:
    st.error("⚠️ Error: No se encontró el archivo 'HR_DATA.csv'. Asegúrate de ponerlo en la misma carpeta que este script.")
    st.stop()

fechaHoy = datetime.datetime.today()
rangoTrimestre = datetime.timedelta(days=90)
fechaTrimestre = fechaHoy - rangoTrimestre

dfDatosHR['Tenure'] = (fechaHoy - dfDatosHR['DateofHire']) / datetime.timedelta(days=365)
dfDatosHR['Age'] = (fechaHoy - dfDatosHR['DOB']) / datetime.timedelta(days=365)
dfDatosHR['Sex'] = dfDatosHR['Sex'].apply(lambda x: 'Women' if x == 'F' else 'Men')

dfDatosHR['TenureRange'] = pd.cut(dfDatosHR['Tenure'], bins=[0, 1, 3, 5, 10, 15, 20, 100],
                                  labels=["<1 y", "1-3 y", "3-5 y", "5-10 y", "10-15 y", "15-20 y", "> 20 y"], ordered=False)
dfDatosHR['AgeRange'] = pd.cut(dfDatosHR['Age'], bins=[17, 20, 30, 40, 50, 60, 70, 100],
                               labels=["<20 y", "20-30 y", "30-40 y", "40-50 y", "50-60 y", "60-70 y", "> 70 y"], ordered=False)

dfDatosHR['PerformanceScore'] = pd.Categorical(dfDatosHR['PerformanceScore'], 
                      categories=['Needs Improvement', 'PIP', 'Fully Meets', 'Exceeds'], ordered=True)
dfEmpleadosActivos = dfDatosHR[dfDatosHR['EmploymentStatus'] == 'Active']

# Cálculos de métricas
empActivos = len(dfDatosHR[dfDatosHR['EmploymentStatus'] == 'Active'])
empHombres = len(dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Men'])
empMujeres = len(dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Women'])
empNuevosTrimestre = len(dfDatosHR[dfDatosHR['DateofHire'] >= fechaTrimestre])
empTerminadosTrimestre = len(dfDatosHR[dfDatosHR['DateofTermination'] >= fechaTrimestre])
empAntiguedad = dfEmpleadosActivos['Tenure'].mean()
empAntiguedadHombres = dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Men']['Tenure'].mean()
empAntiguedadMujeres = dfEmpleadosActivos[dfEmpleadosActivos['Sex'] == 'Women']['Tenure'].mean()
empSpanofControl = dfEmpleadosActivos.groupby(['ManagerName']).agg(Employees=('EmpID', 'count'))['Employees'].mean()

# Agrupaciones para gráficos
empActivosDept = dfEmpleadosActivos.groupby(['Department', 'Sex']).agg(Employees=('EmpID', 'count')).reset_index()
empActivosDeptTotal = dfEmpleadosActivos.groupby(['Department']).agg(Employees=('EmpID', 'count')).reset_index()
ordenDeptTotal = empActivosDeptTotal.sort_values('Employees')['Department'].unique()
empActivosDeptTenure = dfEmpleadosActivos.groupby(['Department', 'TenureRange']).agg(Employees=('EmpID', 'count')).reset_index()
empActivoAge = dfEmpleadosActivos.groupby(['AgeRange', 'Sex']).agg(Employees=('EmpID', 'count')).reset_index()

empHires = dfDatosHR.groupby(pd.Grouper(key="DateofHire", freq='ME')).agg(Employees=('EmpID', 'count')).reset_index()
empHires.columns = ['Period', 'Employees']
empHires['action'] = 'Hire'
empTerminations = dfDatosHR.groupby(pd.Grouper(key="DateofTermination", freq='ME')).agg(Employees=('EmpID', 'count')).reset_index()
empTerminations.columns = ['Period', 'Employees']
empTerminations['Employees'] = empTerminations['Employees'] * -1
empTerminations['action'] = 'Termination'
empHiresTerminations = pd.concat([empHires, empTerminations])
empHiresTerminations = empHiresTerminations[empHiresTerminations['Period'] >= fechaHoy - datetime.timedelta(days=730)]

empTerminations_pie = dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated', 'Terminated for Cause'])].groupby('EmploymentStatus').agg(Employees=('EmpID', 'count')).reset_index()
empTerminationReason = dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated', 'Terminated for Cause'])].groupby(['EmploymentStatus', 'TermReason']).agg(Employees=('EmpID', 'count')).reset_index()
empTerminationReasonTotal = dfDatosHR[dfDatosHR['EmploymentStatus'].isin(['Voluntarily Terminated', 'Terminated for Cause'])].groupby(['TermReason']).agg(Employees=('EmpID', 'count')).reset_index()
ordenTerminationReason = empTerminationReasonTotal.sort_values('Employees')['TermReason'].unique()

empActivoTenure = dfEmpleadosActivos.groupby(['TenureRange', 'Sex']).agg(Employees=('EmpID', 'count')).reset_index()
empActivoPerformance = dfEmpleadosActivos.groupby(['PerformanceScore']).agg(Employees=('EmpID', 'count')).reset_index()
dfEmpSalarios = dfEmpleadosActivos.groupby(['Position', 'Sex']).agg(PayRate=('PayRate', 'mean'), Employees=('EmpID', 'count')).reset_index()

# 5. CREACIÓN DE GRÁFICOS CON TEMA NEÓN
figPerformance = px.pie(empActivoPerformance.sort_values('Employees'), names='PerformanceScore', values='Employees', color_discrete_sequence=paletaColores)
figPerformance.update_traces(textposition='outside', textinfo='percent+label')
figPerformance = aplicar_tema_neon(figPerformance, "Performance", "Distribución general")

figTerminations = px.pie(empTerminations_pie, names='EmploymentStatus', values='Employees', color_discrete_sequence=paletaColores)
figTerminations.update_traces(textposition='outside', textinfo='percent+label')
figTerminations = aplicar_tema_neon(figTerminations, "Terminations by type", "Últimos 2 años")

figTerminationsReason = px.bar(empTerminationReason, y='TermReason', x='Employees', color='EmploymentStatus', color_discrete_sequence=paletaColores)
figTerminationsReason.update_yaxes(categoryorder='array', categoryarray=ordenTerminationReason)
figTerminationsReason = aplicar_tema_neon(figTerminationsReason, "Reason for Terminations", "Últimos 2 años")

figDeptTenure = px.bar(empActivosDeptTenure.sort_values('Employees', ascending=False), y='Department', x='Employees', color='TenureRange', color_discrete_sequence=paletaColores)
figDeptTenure.update_yaxes(categoryorder='array', categoryarray=ordenDeptTotal)
figDeptTenure.update_layout(legend_traceorder="grouped")
figDeptTenure = aplicar_tema_neon(figDeptTenure, "Tenure by Department", "Antigüedad por área")

figHireTerminations = px.bar(empHiresTerminations, x='Period', y='Employees', color='action', color_discrete_sequence=[paletaColores[3], paletaColores[1]]) # Verde y Rosa
figHireTerminations = aplicar_tema_neon(figHireTerminations, "Hires vs Terminations", "Últimos 2 años")

figEmpXDept = px.bar(empActivosDept.sort_values(['Sex', 'Employees']), x='Employees', y='Department', color='Sex', barmode='group', text='Employees', color_discrete_map={'Men': paletaColores[0], 'Women': paletaColores[1]}) # Cian y Rosa
figEmpXDept = aplicar_tema_neon(figEmpXDept, "Employees by Department", "Agrupado por sexo")

figEmpAge = px.bar(empActivoAge.sort_values(['Sex']), y='Employees', x='AgeRange', color='Sex', barmode='group', text='Employees', color_discrete_map={'Men': paletaColores[0], 'Women': paletaColores[1]})
figEmpAge = aplicar_tema_neon(figEmpAge, "Employees by Age", "Agrupado por sexo")

figEmpTenure = px.bar(empActivoTenure.sort_values(['Sex']), y='Employees', x='TenureRange', color='Sex', barmode='group', text='Employees', color_discrete_map={'Men': paletaColores[0], 'Women': paletaColores[1]})
figEmpTenure = aplicar_tema_neon(figEmpTenure, "Employees by Tenure", "Agrupado por sexo")

figPerfvsSat = px.scatter(dfEmpleadosActivos.sort_values('PerformanceScore'), x='EngagementSurvey', y='PerformanceScore', color='EngagementSurvey', color_continuous_scale=[[0, paletaColores[1]], [0.5, paletaColores[4]], [1, paletaColores[3]]]) # Rosa -> Amarillo -> Verde
figPerfvsSat = aplicar_tema_neon(figPerfvsSat, "Engagement vs Performance", "Riesgo de rotación")

figSalarioSexo = px.bar(dfEmpSalarios.sort_values('PayRate'), x='Position', y='PayRate', color='Sex', color_discrete_map={'Men': paletaColores[0], 'Women': paletaColores[1]}, barmode='group', text='PayRate')
figSalarioSexo.update_traces(textangle=-90, texttemplate="%{y:,.1f}")
figSalarioSexo = aplicar_tema_neon(figSalarioSexo, "Salary Distribution", "Promedio por puesto y sexo")

# 6. CONSTRUCCIÓN DEL DASHBOARD EN STREAMLIT
st.title(" People Analytics Dashboard")
st.markdown("Análisis de Recursos Humanos con métricas clave de rendimiento, retención y diversidad.")

with st.expander('Ver Datos Crudos (Dataframe)'):    
    st.dataframe(dfDatosHR)

st.divider()

# Fila de Métricas (KPIs)
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric('Active Employees', f'{empActivos:,.0f}')
col2.metric('Women', f'{(empMujeres/empActivos):,.1%}', f'{empMujeres:,.0f} emp.')
col3.metric('Men', f'{(empHombres/empActivos):,.1%}', f'{empHombres:,.0f} emp.')
col4.metric('Avg Tenure', f'{empAntiguedad:,.2f} years')
col5.metric('Span of Control', f'{empSpanofControl:,.1f}')

st.divider()

# Sección 1: Retención
st.subheader("Hires and Terminations")
c1, c2, c3 = st.columns([4, 3, 4])
c1.plotly_chart(figHireTerminations, use_container_width=True)
c2.plotly_chart(figTerminations, use_container_width=True)
c3.plotly_chart(figTerminationsReason, use_container_width=True)

# Sección 2: Organización
st.subheader("🏢 Tenure and Organization")
c1, c2, c3, c4 = st.columns(4)
c1.plotly_chart(figPerformance, use_container_width=True)    
c2.plotly_chart(figPerfvsSat, use_container_width=True)
c3.plotly_chart(figDeptTenure, use_container_width=True)        
c4.plotly_chart(figEmpTenure, use_container_width=True)

# Sección 3: Demografía
st.subheader("👥 Demographics")
c1, c2 = st.columns(2)
c1.plotly_chart(figEmpXDept, use_container_width=True)
c2.plotly_chart(figEmpAge, use_container_width=True)

# Sección 4: Salarios
st.subheader(" Salary Distribution")
st.plotly_chart(figSalarioSexo, use_container_width=True)