# -*- coding: utf-8 -*-
"""
Dashboard SSO - Seguridad y Salud Ocupacional v2.0
Aplicación Principal con Arquitectura Reactivo/Proactivo

Normativa: IESS CD 513 Ecuador
Autor: Arquitecto de Software Senior
"""

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import streamlit.components.v1 as components

# Importaciones de módulos propios
from modules import (
    ReactiveAnalyzer,
    ConstantesK,
    ProactiveCalculator,
    IndicadorConfig,
    DataValidator,
    TipoAnalisis,
    SSOVisualizer
)
from modules.pdf_generator import generar_informe_reactivos, generar_informe_proactivos

# ============================================================================
# CONFIGURACIÓN DE LA PÁGINA
# ============================================================================

st.set_page_config(
    page_title="Dashboard SSO - IESS CD 513",
    page_icon="S",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyectar script de Iconify (CDN)
# Usamos el componente HTML para asegurar que el script se cargue
st.markdown(
    """
    <script src="https://code.iconify.design/iconify-icon/1.0.7/iconify-icon.min.js"></script>
    """,
    unsafe_allow_html=True
)

# Estilos CSS Profesionales (Badges, Chips, Tipografía)
st.markdown("""
<style>
    /* Importar fuente Inter */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', 'Segoe UI', sans-serif;
    }

    /* --- COMPONENTES: BADGES & CHIPS --- */
    .sso-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        padding: 4px 12px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        letter-spacing: 0.02em;
        line-height: 1.5;
        white-space: nowrap;
        transition: all 0.2s ease;
    }
    
    .sso-badge iconify-icon {
        font-size: 1.1em;
        vertical-align: text-bottom;
    }

    /* Variantes de Badges */
    .badge-primary {
        background-color: #e3f2fd;
        color: #1565c0;
        border: 1px solid #bbdefb;
    }
    
    .badge-success {
        background-color: #e8f5e9;
        color: #2e7d32;
        border: 1px solid #c8e6c9;
    }
    
    .badge-warning {
        background-color: #fff3e0;
        color: #ef6c00;
        border: 1px solid #ffe0b2;
    }
    
    .badge-danger {
        background-color: #ffebee;
        color: #c62828;
        border: 1px solid #ffcdd2;
    }
    
    .badge-neutral {
        background-color: #f5f5f5;
        color: #616161;
        border: 1px solid #e0e0e0;
    }

    /* --- HEADER PRINCIPAL --- */
    .app-header {
        display: flex;
        align-items: center;
        padding: 20px 0;
        border-bottom: 2px solid #f0f2f6;
        margin-bottom: 30px;
        background: white;
    }

    .app-header-icon {
        font-size: 48px;
        color: #1f77b4;
        margin-right: 20px;
        filter: drop-shadow(0 4px 6px rgba(31, 119, 180, 0.2));
    }

    .app-header-title h1 {
        margin: 0;
        font-size: 2.2rem;
        color: #2c3e50;
        font-weight: 700;
    }

    .app-header-subtitle {
        color: #7f8c8d;
        font-size: 1.1rem;
        margin-top: 5px;
    }

    /* --- TARJETAS METRICAS --- */
    .kpi-card {
        background: white;
        border-radius: 12px;
        padding: 24px;
        border: 1px solid #f0f0f0;
        box-shadow: 0 4px 12px rgba(0,0,0,0.03);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    
    .kpi-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.06);
        border-color: #e0e0e0;
    }

    /* --- SIDEBAR PERSONALIZADO --- */
    [data-testid="stSidebar"] {
        background-color: #f8f9fa;
        border-right: 1px solid #e9ecef;
    }
    
    /* --- TABS --- */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
        border-bottom: 2px solid #e9ecef;
        padding-bottom: 2px;
    }
    
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        border: none !important;
        font-weight: 600;
        color: #6c757d;
        padding-bottom: 12px;
    }
    
    .stTabs [aria-selected="true"] {
        color: #1f77b4 !important;
        border-bottom: 3px solid #1f77b4 !important;
    }

    /* Utilitarios */
    .flex-center {
        display: flex;
        align-items: center;
        gap: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# INICIALIZACIÓN DE COMPONENTES
# ============================================================================

@st.cache_resource
def inicializar_componentes():
    """Inicializa y cachea los componentes principales"""
    return {
        'reactive_analyzer': ReactiveAnalyzer(),
        'proactive_calculator': ProactiveCalculator(),
        'visualizer': SSOVisualizer()
    }

componentes = inicializar_componentes()

# ============================================================================
# FUNCIONES AUXILIARES UI
# ============================================================================

def badge(texto: str, tipo: str = 'neutral', icon: str = None) -> str:
    """Genera HTML para un badge"""
    icon_html = f'<iconify-icon icon="{icon}"></iconify-icon>' if icon else ''
    return f'<span class="sso-badge badge-{tipo}">{icon_html} {texto}</span>'


def render_pdf_config(key_prefix: str):
    """Renderiza formulario de configuración PDF y retorna diccionarios de datos"""
    with st.expander("Configuración del Informe PDF (Empresa, Responsable, Firmas)", expanded=False):
        st.markdown(f"#### {badge('Documento', 'primary')} Información del Documento", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            codigo = st.text_input("Código", value="R-SSO-001", key=f"{key_prefix}_codigo")
        with c2:
            version = st.text_input("Versión", value="01", key=f"{key_prefix}_version")
        with c3:
            periodo = st.text_input("Periodo/Año", value=str(datetime.now().year), key=f"{key_prefix}_periodo")
        
        st.markdown(f"#### {badge('Empresa', 'primary')} Datos de la Organización", unsafe_allow_html=True)
        col_emp1, col_emp2 = st.columns(2)
        with col_emp1:
            razon_social = st.text_input("Razón Social", value="Mi Empresa S.A.", key=f"{key_prefix}_razon")
            ruc = st.text_input("RUC", value="1790000000001", key=f"{key_prefix}_ruc")
            direccion = st.text_input("Dirección", value="Av. Principal y Calle Secundaria", key=f"{key_prefix}_dir")
            actividad = st.text_input("Actividad Económica", value="Servicios Generales", key=f"{key_prefix}_actividad")
        with col_emp2:
            rep_legal = st.text_input("Representante Legal", value="Juan Pérez", key=f"{key_prefix}_rep")
            sucursales = st.text_input("N° Sucursales", value="1", key=f"{key_prefix}_suc")
            ubicacion = st.text_input("Provincia/Cantón/Parr", value="Pichincha / Quito", key=f"{key_prefix}_ubic")
            trabajadores = st.text_input("N° Trabajadores", value="50", key=f"{key_prefix}_trab")
            
        st.markdown(f"#### {badge('Responsable', 'primary')} Responsable del Proceso", unsafe_allow_html=True)
        col_resp1, col_resp2 = st.columns(2)
        with col_resp1:
            resp_nombre = st.text_input("Nombre Responsable", value="Ing. María López", key=f"{key_prefix}_resp_nom")
            resp_cargo = st.text_input("Cargo", value="Jefe de SSO", key=f"{key_prefix}_resp_cargo")
            resp_cedula = st.text_input("Cédula", value="1700000000", key=f"{key_prefix}_resp_ci")
        with col_resp2:
            resp_profesion = st.text_input("Profesión", value="Ingeniero Industrial", key=f"{key_prefix}_resp_prof")
            resp_registro = st.text_input("Registro SENESCYT/MDT", value="1025-2023", key=f"{key_prefix}_resp_reg")

        st.markdown(f"#### {badge('Aprobación', 'primary')} Firmas de Aprobación", unsafe_allow_html=True)
        col_apr1, col_apr2 = st.columns(2)
        with col_apr1:
            rev_nombre = st.text_input("Revisado por (Nombre)", value="Ing. Carlos Ruiz", key=f"{key_prefix}_rev_nom")
            rev_cargo = st.text_input("Cargo Revisor", value="Gerente Técnico", key=f"{key_prefix}_rev_cargo")
        with col_apr2:
            apr_nombre = st.text_input("Aprobado por (Nombre)", value="Dr. Pedro Alava", key=f"{key_prefix}_apr_nom")
            apr_cargo = st.text_input("Cargo Aprobador", value="Gerente General", key=f"{key_prefix}_apr_cargo")
            
    return {
        'codigo': codigo,
        'version': version,
        'periodo': periodo,
        'datos_empresa': {
            'razon_social': razon_social,
            'ruc': ruc,
            'direccion': direccion,
            'actividad': actividad,
            'rep_legal': rep_legal,
            'sucursales': sucursales,
            'ubicacion': ubicacion,
            'trabajadores': trabajadores
        },
        'datos_responsable': {
            'nombre': resp_nombre,
            'cargo': resp_cargo,
            'cedula': resp_cedula,
            'profesion': resp_profesion,
            'registro': resp_registro
        },
        'datos_aprobacion': {
            'nombre_revisor': rev_nombre,
            'cargo_revisor': rev_cargo,
            'nombre_aprobador': apr_nombre,
            'cargo_aprobador': apr_cargo
        }
    }

# ============================================================================
# FUNCIONES DE PROCESAMIENTO DE DATOS
# ============================================================================

INDICADORES_PROACTIVOS = {
    'IART': {'cols': ['mes', 'narp', 'nart'], 'formula': lambda r: (r['nart'] / r['narp']) * 100 if r['narp'] > 0 else 0},
    'OPAS': {'cols': ['mes', 'opasp', 'pobp', 'opasr', 'pc'], 'formula': lambda r: (r['opasr'] * r['pc']) / (r['opasp'] * r['pobp']) * 100 if (r['opasp'] * r['pobp']) > 0 else 0},
    'IDS': {'cols': ['mes', 'ncsd', 'ncse'], 'formula': lambda r: (r['ncse'] / r['ncsd']) * 100 if r['ncsd'] > 0 else 0},
    'IDPS': {'cols': ['mes', 'dpsp', 'pp', 'dpsr', 'nas'], 'formula': lambda r: (r['dpsr'] * r['nas']) / (r['dpsp'] * r['pp']) * 100 if (r['dpsp'] * r['pp']) > 0 else 0},
    'IENTS': {'cols': ['mes', 'nteep', 'nee'], 'formula': lambda r: (r['nee'] / r['nteep']) * 100 if r['nteep'] > 0 else 0},
    'IOSEA': {'cols': ['mes', 'oseaa', 'oseac'], 'formula': lambda r: (r['oseac'] / r['oseaa']) * 100 if r['oseaa'] > 0 else 0},
    'ICAI': {'cols': ['mes', 'nmp', 'nmi'], 'formula': lambda r: (r['nmi'] / r['nmp']) * 100 if r['nmp'] > 0 else 0},
    'IEF': {'cols': ['mes', 'capp', 'cape'], 'formula': lambda r: (r['cape'] / r['capp']) * 100 if r['capp'] > 0 else 0},
}


def procesar_excel_reactivo(uploaded_file) -> pd.DataFrame:
    """Procesa Excel de reactivos (hoja única)"""
    try:
        df = pd.read_excel(uploaded_file, sheet_name=0)
        
        # Columnas de entrada (no calculadas)
        cols_entrada = [
            'mes', 'num_trabajadores', 'horas_trabajador', 'horas_extras',
            'acc_con_baja', 'acc_sin_baja', 'enf_ocupacional', 'dias_perdidos'
        ]
        
        # Verificar columnas
        cols_faltantes = [c for c in cols_entrada if c not in df.columns]
        if cols_faltantes:
            st.error(f"Columnas faltantes: {', '.join(cols_faltantes)}")
            return None
        
        df = df[cols_entrada].copy()
        df = df.dropna(subset=['mes'])
        
        # Convertir a numérico
        for col in cols_entrada[1:]:  # Excepto 'mes'
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Calcular campos derivados
        # Total Horas Trabajadas = num_trabajadores * horas_trabajador + horas_extras
        df['horas_hombre_mes'] = df['num_trabajadores'] * df['horas_trabajador'] + df['horas_extras']
        
        # Renombrar para coincidir con ReactiveAnalyzer
        df = df.rename(columns={
            'acc_con_baja': 'acc_baja',
            'enf_ocupacional': 'enf_ocupacionales'
        })
        
        return df
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None


def procesar_excel_proactivo(uploaded_file) -> dict:
    """Procesa Excel de proactivos (múltiples hojas)"""
    try:
        excel = pd.ExcelFile(uploaded_file)
        hojas_disponibles = excel.sheet_names
        
        datos = {}
        hojas_encontradas = []
        
        for indicador, config in INDICADORES_PROACTIVOS.items():
            # Buscar hoja (puede ser nombre exacto o parcial)
            hoja_match = None
            for hoja in hojas_disponibles:
                if indicador.upper() in hoja.upper():
                    hoja_match = hoja
                    break
            
            if hoja_match:
                df = pd.read_excel(excel, sheet_name=hoja_match)
                
                # Verificar columnas mínimas
                cols_presentes = [c for c in config['cols'] if c in df.columns]
                if len(cols_presentes) >= 2:  # Al menos mes + 1 dato
                    datos[indicador] = df[cols_presentes].dropna(subset=['mes']).copy()
                    hojas_encontradas.append(indicador)
        
        if hojas_encontradas:
            st.markdown(badge(f"Hojas detectadas: {', '.join(hojas_encontradas)}", "success", "lucide:check-circle"), unsafe_allow_html=True)
        else:
            st.warning("No se detectaron hojas de indicadores proactivos")
        
        return datos
    except Exception as e:
        st.error(f"Error: {str(e)}")
        return {}


def calcular_indicadores_proactivos(datos_raw: dict) -> pd.DataFrame:
    """Calcula indicadores desde datos raw"""
    if not datos_raw:
        return pd.DataFrame()
    
    # Obtener lista de meses del primer indicador disponible
    primer_indicador = list(datos_raw.values())[0]
    meses = primer_indicador['mes'].tolist()
    
    resultado = pd.DataFrame({'mes': meses})
    
    for indicador, config in INDICADORES_PROACTIVOS.items():
        if indicador in datos_raw:
            df = datos_raw[indicador]
            valores = []
            for _, row in df.iterrows():
                try:
                    valor = config['formula'](row)
                    valores.append(min(100, max(0, valor)))  # Limitar 0-100
                except:
                    valores.append(0)
            resultado[indicador.lower()] = valores[:len(meses)]
    
    # Calcular IG Total (ponderado según CD 513)
    pesos = {'iart': 5, 'opas': 3, 'idps': 2, 'ids': 3, 'ients': 4, 'iosea': 4, 'icai': 4}
    suma_pesos = sum(pesos.values())
    
    def calcular_ig(row):
        total = 0
        for ind, peso in pesos.items():
            if ind in row.index and pd.notna(row[ind]):
                total += row[ind] * peso
        return total / suma_pesos
    
    resultado['ig_total'] = resultado.apply(calcular_ig, axis=1)
    
    return resultado


def cargar_plantilla(nombre: str) -> bytes:
    """Carga una plantilla como bytes para descarga"""
    import os
    ruta = os.path.join('templates', nombre)
    if os.path.exists(ruta):
        with open(ruta, 'rb') as f:
            return f.read()
    return None


# ============================================================================
# SIDEBAR
# ============================================================================

def render_sidebar():
    """Renderiza la barra lateral con configuraciones"""
    with st.sidebar:
        # Logo
        st.markdown("""
            <div style="text-align: center; padding: 20px 0;">
                <iconify-icon icon="mdi:shield-check-outline" style="font-size: 80px; color: #1f77b4;"></iconify-icon>
                <div style="font-weight: 700; font-size: 1.2rem; color: #333; margin-top: 10px;">
                    SSO MANAGEMENT
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # --- DESCARGAR PLANTILLAS ---
        st.markdown(f"### {badge('Plantillas', 'primary', 'lucide:download')}", unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            plantilla_react = cargar_plantilla('plantilla_reactivos.xlsx')
            if plantilla_react:
                st.download_button(
                    label="Reactivos",
                    data=plantilla_react,
                    file_name="plantilla_reactivos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        with col2:
            plantilla_proact = cargar_plantilla('plantilla_proactivos.xlsx')
            if plantilla_proact:
                st.download_button(
                    label="Proactivos",
                    data=plantilla_proact,
                    file_name="plantilla_proactivos.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
        
        st.markdown("---")
        
        # --- CARGAR ARCHIVOS ---
        st.markdown(f"### {badge('Cargar Datos', 'neutral', 'lucide:upload-cloud')}", unsafe_allow_html=True)
        
        # Reactivos
        st.markdown("**Indicadores Reactivos:**")
        archivo_reactivo = st.file_uploader(
            "Excel reactivos",
            type=['xlsx', 'xls'],
            key='reactivo_upload',
            label_visibility='collapsed'
        )
        
        if archivo_reactivo:
            df = procesar_excel_reactivo(archivo_reactivo)
            if df is not None:
                st.session_state['df_reactivo_raw'] = df
        
        # Proactivos
        st.markdown("**Indicadores Proactivos:**")
        archivo_proactivo = st.file_uploader(
            "Excel proactivos",
            type=['xlsx', 'xls'],
            key='proactivo_upload',
            label_visibility='collapsed'
        )
        
        if archivo_proactivo:
            datos = procesar_excel_proactivo(archivo_proactivo)
            if datos:
                st.session_state['datos_proactivos_raw'] = datos
        
        st.markdown("---")
        
        # --- CONSTANTES K ---
        st.markdown(f"### {badge('Constantes K', 'neutral', 'tb:math-function')}", unsafe_allow_html=True)
        with st.expander("Configurar", expanded=False):
            k_mensual = st.number_input("K Mensual", value=16666.67, format="%.2f")
            k_trimestral = st.number_input("K Trimestral", value=50000.00, format="%.2f")
            k_anual = st.number_input("K Anual", value=200000.00, format="%.2f")
        
        # --- METAS ---
        st.markdown(f"### {badge('Metas %', 'neutral', 'lucide:target')}", unsafe_allow_html=True)
        with st.expander("Configurar", expanded=False):
            metas = {}
            for ind in ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai', 'ief', 'ig_total']:
                metas[ind] = st.slider(f"Meta {ind.upper()}", 50, 100, 80)
            metas['general'] = 80
            st.session_state['metas'] = metas
        
        st.markdown("---")
        st.markdown(f"### {badge('Info', 'neutral', 'lucide:info')}", unsafe_allow_html=True)
        st.info(f"**Versión:** 2.1.0\n**Normativa:** IESS CD 513\n**Fecha:** {datetime.now().strftime('%Y-%m-%d')}")
        
        return {
            'k_mensual': k_mensual if 'k_mensual' in locals() else 16666.67,
            'k_trimestral': k_trimestral if 'k_trimestral' in locals() else 50000.00,
            'k_anual': k_anual if 'k_anual' in locals() else 200000.00,
            'metas': st.session_state.get('metas', {ind: 80 for ind in ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai', 'ief', 'ig_total', 'general']})
        }


# ============================================================================
# TABS PRINCIPALES
# ============================================================================

def render_tab_reactivos(constantes_k: ConstantesK):
    """Renderiza el tab de indicadores reactivos con tabla editable"""
    st.markdown(f"""
    ## <div class='flex-center'><iconify-icon icon='lucide:alert-triangle' style='color:#e74c3c'></iconify-icon> Indicadores Reactivos</div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos
    if 'df_reactivo_raw' not in st.session_state:
        st.info("Cargue un archivo Excel con datos reactivos desde la barra lateral.")
        st.markdown("""
        **Columnas de entrada requeridas:**
        - `mes`: Nombre del mes
        - `num_trabajadores`: Número de trabajadores
        - `horas_trabajador`: Horas por trabajador
        - `horas_extras`: Horas extras
        - `acc_con_baja`: Accidentes con baja
        - `acc_sin_baja`: Accidentes sin baja
        - `enf_ocupacional`: Enfermedades ocupacionales
        - `dias_perdidos`: Días perdidos
        """)
        return
    
    df_raw = st.session_state['df_reactivo_raw'].copy()
    
    # Columnas de entrada para edición (nombres que usa ReactiveAnalyzer)
    cols_edicion = ['mes', 'num_trabajadores', 'horas_trabajador', 'horas_extras',
                    'acc_baja', 'acc_sin_baja', 'enf_ocupacionales', 'dias_perdidos']
    
    # Filtrar solo columnas de entrada para edición
    cols_disponibles = [c for c in cols_edicion if c in df_raw.columns]
    df_editar = df_raw[cols_disponibles].copy()
    
    # Tabla editable
    st.markdown(f"### {badge('Datos de Entrada', 'primary', 'lucide:table-2')} (Editable)", unsafe_allow_html=True)
    
    edited_df = st.data_editor(
        df_editar,
        num_rows="dynamic",
        use_container_width=True,
        hide_index=True,
        column_config={
            "mes": st.column_config.TextColumn("Mes", disabled=True),
            "num_trabajadores": st.column_config.NumberColumn("# Trabajadores", min_value=0, format="%d"),
            "horas_trabajador": st.column_config.NumberColumn("Horas/Trab", min_value=0, format="%.1f"),
            "horas_extras": st.column_config.NumberColumn("H. Extras", min_value=0, format="%.1f"),
            "acc_baja": st.column_config.NumberColumn("Acc. c/Baja", min_value=0, format="%d"),
            "acc_sin_baja": st.column_config.NumberColumn("Acc. s/Baja", min_value=0, format="%d"),
            "enf_ocupacionales": st.column_config.NumberColumn("Enf. Ocup.", min_value=0, format="%d"),
            "dias_perdidos": st.column_config.NumberColumn("Días Perd.", min_value=0, format="%d"),
        },
        key="reactivo_editor"
    )
    
    # Recalcular campos derivados después de edición
    edited_df['horas_hombre_mes'] = edited_df['num_trabajadores'] * edited_df['horas_trabajador'] + edited_df['horas_extras']
    
    # Actualizar session_state con datos editados
    st.session_state['df_reactivo_raw'] = edited_df
    
    st.markdown("---")
    
    # Procesar y mostrar resultados
    if not edited_df.empty:
        reactive_analyzer = componentes['reactive_analyzer']
        reactive_analyzer.constantes = constantes_k
        
        try:
            df_reporte, df_charts = reactive_analyzer.procesar(edited_df)
            
            metricas = {
                'total_lesiones': df_charts['total_lesiones'].sum(),
                'total_dias': df_charts['dias_perdidos'].sum(),
                'if_promedio': df_charts['IF'].mean(),
                'ig_promedio': df_charts['IG'].mean(),
                'tr_promedio': df_charts['TR'].mean()
            }
            
            componentes['visualizer'].render_metricas_resumen(metricas, tipo="reactivo")
            st.markdown("---")
            
            componentes['visualizer'].render_reactive_dashboard(
                df_reporte=df_reporte,
                df_charts=df_charts,
                titulo="<div class='flex-center'><iconify-icon icon='lucide:line-chart'></iconify-icon> Análisis</div>",
                mostrar_tabla=True,
                mostrar_graficos=True
            )
            
            # Descarga
            st.markdown("### Descargar Informes")
            
            # Configuración del informe PDF (inline)
            pdf_config = render_pdf_config("reactivos")
            
            col1, col2 = st.columns(2)
            with col1:
                excel_data = componentes['visualizer'].exportar_a_excel(df_reactivo=df_reporte)
                st.download_button(
                    label="Descargar Reporte Excel",
                    data=excel_data,
                    file_name=f"reporte_reactivos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                    use_container_width=True
                )
            with col2:
                # Generar imágenes para el PDF
                img_graficos = componentes['visualizer'].generar_imagenes_reactivas(df_charts)
                
                # Generar PDF profesional
                pdf_data = generar_informe_reactivos(
                    df_charts=df_charts,
                    metricas=metricas,
                    datos_empresa=pdf_config['datos_empresa'],
                    datos_responsable=pdf_config['datos_responsable'],
                    datos_aprobacion=pdf_config['datos_aprobacion'],
                    imagenes=img_graficos,
                    periodo=pdf_config['periodo'],
                    codigo=pdf_config['codigo'],
                    version=pdf_config['version']
                )
                st.download_button(
                    label="Descargar Informe PDF",
                    data=pdf_data,
                    file_name=f"informe_reactivos_{datetime.now().strftime('%Y%m%d')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
        except Exception as e:
            st.error(f"Error: {str(e)}")


def render_tab_proactivos(metas: dict):
    """Renderiza el tab de indicadores proactivos con tablas editables"""
    st.markdown(f"""
    ## <div class='flex-center'><iconify-icon icon='lucide:shield-check' style='color:#2ecc71'></iconify-icon> Indicadores Proactivos</div>
    """, unsafe_allow_html=True)
    
    # Verificar si hay datos
    if 'datos_proactivos_raw' not in st.session_state:
        st.info("Cargue un archivo Excel con datos proactivos desde la barra lateral.")
        st.markdown("""
        **Hojas esperadas (una por indicador):**
        - `IART`: Análisis de Riesgos de Tareas
        - `OPAS`: Observación Planeada de Acciones Subestándar
        - `IDS`: Demanda de Seguridad
        - `IDPS`: Diálogo Periódico de Seguridad
        - `IENTS`: Entrenamiento de Seguridad
        - `IOSEA`: Órdenes de Servicios Estandarizados
        - `ICAI`: Control de Accidentes e Incidentes
        """)
        return
    
    datos_raw = st.session_state['datos_proactivos_raw']
    
    # Tabs para editar cada indicador
    st.markdown(f"### {badge('Datos por Indicador', 'primary', 'lucide:layers')} (Editables)", unsafe_allow_html=True)
    
    indicadores_presentes = list(datos_raw.keys())
    
    if indicadores_presentes:
        tabs_indicadores = st.tabs(indicadores_presentes)
        
        for i, indicador in enumerate(indicadores_presentes):
            with tabs_indicadores[i]:
                df = datos_raw[indicador].copy()
                
                edited = st.data_editor(
                    df,
                    num_rows="dynamic",
                    use_container_width=True,
                    hide_index=True,
                    key=f"proactivo_{indicador}_editor"
                )
                
                # Actualizar
                st.session_state['datos_proactivos_raw'][indicador] = edited
    
    st.markdown("---")
    
    # Calcular y mostrar resultados
    df_resultado = calcular_indicadores_proactivos(st.session_state['datos_proactivos_raw'])
    
    if not df_resultado.empty:
        metricas = {
            'ig_promedio': df_resultado['ig_total'].mean() if 'ig_total' in df_resultado.columns else 0,
            'cumplimiento_general': df_resultado['ig_total'].mean() if 'ig_total' in df_resultado.columns else 0,
            'meses': len(df_resultado)
        }
        
        componentes['visualizer'].render_metricas_resumen(metricas, tipo="proactivo")
        st.markdown("---")
        
        componentes['visualizer'].render_proactive_dashboard(
            df=df_resultado,
            metas=metas,
            titulo="<div class='flex-center'><iconify-icon icon='lucide:clipboard-check'></iconify-icon> Cumplimiento</div>",
            mostrar_tabla=True,
            mostrar_graficos=True
        )
        
        # Descarga
        st.markdown("### Descargar Informes")
        
        # Configuración del informe PDF (inline)
        pdf_config = render_pdf_config("proactivos")
        
        col1, col2 = st.columns(2)
        with col1:
            excel_data = componentes['visualizer'].exportar_a_excel(df_proactivo=df_resultado)
            st.download_button(
                label="Descargar Reporte Excel",
                data=excel_data,
                file_name=f"reporte_proactivos_{datetime.now().strftime('%Y%m%d')}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        with col2:
            # Generar imágenes para el PDF
            img_graficos = componentes['visualizer'].generar_imagenes_proactivas(df_resultado, metas)
            
            # Generar PDF profesional
            pdf_data = generar_informe_proactivos(
                df_resultados=df_resultado,
                metas=metas,
                datos_empresa=pdf_config['datos_empresa'],
                datos_responsable=pdf_config['datos_responsable'],
                datos_aprobacion=pdf_config['datos_aprobacion'],
                imagenes=img_graficos,
                periodo=pdf_config['periodo'],
                codigo=pdf_config['codigo'],
                version=pdf_config['version']
            )
            st.download_button(
                label="Descargar Informe PDF",
                data=pdf_data,
                file_name=f"informe_proactivos_{datetime.now().strftime('%Y%m%d')}.pdf",
                mime="application/pdf",
                use_container_width=True
            )




# ============================================================================
# FUNCIÓN PRINCIPAL
# ============================================================================

def main():
    """Función principal de la aplicación"""
    
    # Header profesional con Iconify
    st.markdown("""
    <div class="app-header">
        <iconify-icon icon="mdi:shield-lock" class="app-header-icon"></iconify-icon>
        <div class="app-header-title">
            <h1>Dashboard SSO</h1>
            <div class="app-header-subtitle">
                Sistema de Gestión de Seguridad y Salud Ocupacional | IESS CD 513
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Renderizar sidebar y obtener configuración
    config = render_sidebar()
    
    # Crear constantes K desde la configuración
    constantes_k = ConstantesK(
        MENSUAL=config['k_mensual'],
        TRIMESTRAL=config['k_trimestral'],
        ANUAL=config['k_anual']
    )
    
    # Tabs principales con iconos
    tab_reactivos, tab_proactivos = st.tabs([
        "Indicadores Reactivos",
        "Indicadores Proactivos"
    ])
    
    with tab_reactivos:
        render_tab_reactivos(constantes_k)
    
    with tab_proactivos:
        render_tab_proactivos(config['metas'])
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #888; font-size: 0.8rem; margin-top: 20px;'>
        <div style="display: flex; justify-content: center; gap: 10px; align-items: center;">
            <span>Dashboard SSO v2.0 Professional</span>
            <span>•</span>
            <span>Normativa IESS CD 513</span>
        </div>
        <div style="margin-top: 5px;">
             © 2024 - Arquitectura de Software Modular
        </div>
    </div>
    """, unsafe_allow_html=True)


# ============================================================================
# PUNTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    main()
