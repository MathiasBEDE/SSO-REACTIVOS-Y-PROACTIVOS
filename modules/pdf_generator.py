"""
Módulo de Generación de Informes PDF para SSO
Genera informes técnicos profesionales de indicadores reactivos y proactivos
"""

from fpdf import FPDF
from datetime import datetime
from typing import Dict, Any, Optional
import pandas as pd
import tempfile
import os


class InformePDF(FPDF):
    """Clase base para generación de informes PDF SSO - Formato A4 Profesional Auditable"""
    
    def __init__(self, titulo_informe: str, datos_empresa: Dict[str, str], 
                 datos_responsable: Dict[str, str], datos_aprobacion: Dict[str, str],
                 periodo: str = "2026", codigo: str = "R-SSO-00", version: str = "01"):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.titulo_informe = titulo_informe
        self.empresa = datos_empresa
        self.responsable = datos_responsable
        self.aprobacion = datos_aprobacion
        self.periodo = periodo
        self.codigo = codigo
        self.version = version
        self.set_auto_page_break(auto=True, margin=25)
        self.total_pages = 0
        
    def header(self):
        """Encabezado profesional con logos y estructura formal"""
        if self.page_no() > 0:
            # Borde del encabezado
            self.set_draw_color(0, 0, 0)
            self.set_line_width(0.3)
            
            # Logo izquierda (si existiera, aquí iría código para imagen)
            self.set_xy(10, 10)
            self.set_font('Helvetica', 'B', 10)
            self.cell(40, 20, self.codigo, border=1, align='C')
            
            # Título central
            self.set_xy(50, 10)
            self.set_font('Helvetica', 'B', 12)
            self.cell(110, 20, self.titulo_informe.upper(), border=1, align='C')
            
            # Logo/Info derecha
            self.set_xy(160, 10)
            self.set_font('Helvetica', '', 8)
            self.cell(40, 12, "Logo Empresa", border=1, align='C')
            self.set_xy(160, 22)
            self.cell(40, 8, f'Página {self.page_no()}', border=1, align='C')
            
            # Segunda fila de metadatos
            self.set_xy(10, 30)
            self.set_fill_color(220, 220, 220)
            self.set_font('Helvetica', 'B', 8)
            
            # Fecha Reporte
            self.cell(25, 6, "Fecha Reporte", border=1, fill=True, align='C')
            self.set_fill_color(255, 255, 255)
            self.set_font('Helvetica', '', 8)
            self.cell(35, 6, datetime.now().strftime('%d/%m/%Y'), border=1, align='C')
            
            # Año Reportado
            self.set_fill_color(220, 220, 220)
            self.set_font('Helvetica', 'B', 8)
            self.cell(30, 6, "Año Reportado", border=1, fill=True, align='C')
            self.set_fill_color(255, 255, 255)
            self.set_font('Helvetica', '', 8)
            self.cell(30, 6, self.periodo, border=1, align='C')
            
            # Código y Versión
            self.set_fill_color(220, 220, 220)
            self.set_font('Helvetica', 'B', 8)
            self.cell(20, 6, "Versión", border=1, fill=True, align='C')
            self.set_fill_color(255, 255, 255)
            self.set_font('Helvetica', '', 8)
            self.cell(10, 6, self.version, border=1, align='C')
            self.cell(40, 6, self.codigo, border=1, align='C')
            
            self.ln(10)
    
    def footer(self):
        """Pie de página auditable"""
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 7)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Generado auditada por Dashboard SSO - {datetime.now().strftime('%Y-%m-%d %H:%M')}", align='L')
        self.cell(0, 10, f"Página {self.page_no()}", align='R')

    def portada(self, tipo: str = "REACTIVOS"):
        """Genera la página de portada profesional"""
        self.add_page()
        
        # Encabezado de portada
        self.set_fill_color(41, 128, 185)
        self.rect(0, 0, 210, 80, 'F')
        
        # Código y versión en esquina
        self.set_xy(150, 10)
        self.set_font('Helvetica', 'B', 10)
        self.set_text_color(255, 255, 255)
        self.cell(50, 8, f'{self.codigo}', align='R')
        self.set_xy(150, 18)
        self.set_font('Helvetica', '', 9)
        self.cell(50, 6, f'Versión: {self.version}', align='R')
        
        # Título principal
        self.set_y(30)
        self.set_font('Helvetica', 'B', 22)
        self.set_text_color(255, 255, 255)
        self.multi_cell(0, 10, f'REPORTE ÍNDICES {tipo}\nSGSST', align='C')
        
        # Subtítulo
        self.set_y(60)
        self.set_font('Helvetica', '', 12)
        self.cell(0, 8, 'Sistema de Gestión de Seguridad y Salud en el Trabajo', align='C')
        
        # Información del documento
        self.set_y(100)
        self.set_text_color(50, 50, 50)
        
        # Tabla de información
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(255, 204, 0)
        self.cell(60, 10, 'Organización', border=1, align='C', fill=True)
        self.set_fill_color(255, 255, 255)
        self.set_font('Helvetica', '', 11)
        self.cell(130, 10, self.empresa.get('razon_social', 'Organización'), border=1, align='C')
        self.ln()
        
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(255, 204, 0)
        self.cell(60, 10, 'Año Reportado', border=1, align='C', fill=True)
        self.set_fill_color(255, 255, 255)
        self.set_font('Helvetica', '', 11)
        self.cell(130, 10, self.periodo, border=1, align='C')
        self.ln()
        
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(255, 204, 0)
        self.cell(60, 10, 'Fecha de Emisión', border=1, align='C', fill=True)
        self.set_fill_color(255, 255, 255)
        self.set_font('Helvetica', '', 11)
        self.cell(130, 10, datetime.now().strftime('%d de %B de %Y'), border=1, align='C')
        self.ln()
        
        self.set_font('Helvetica', 'B', 11)
        self.set_fill_color(255, 204, 0)
        self.cell(60, 10, 'Código', border=1, align='C', fill=True)
        self.set_fill_color(255, 255, 255)
        self.set_font('Helvetica', '', 11)
        self.cell(130, 10, self.codigo, border=1, align='C')
        
        # Nota al pie
        self.set_y(250)
        self.set_font('Helvetica', 'I', 9)
        self.set_text_color(100, 100, 100)
        self.cell(0, 8, 'Documento generado automáticamente - Dashboard SSO', align='C')

    def seccion_informacion_general(self):
        """Genera la sección de Información General de la Empresa y Responsable"""
        self.ln(5)
        
        # 1. Información de la Empresa
        self.set_fill_color(255, 204, 0) # Amarillo corporativo
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, "1. Información General de la Empresa", border=1, fill=True, align='C')
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)
        
        # Fila 1
        self.cell(35, 6, "Razón Social", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('razon_social', ''), border=1)
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "Rep. Legal", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('rep_legal', ''), border=1)
        self.ln()
        
        # Fila 2
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "Actividad Económica", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('actividad', ''), border=1)
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "RUC", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('ruc', ''), border=1)
        self.ln()
        
        # Fila 3
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "Dirección", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('direccion', ''), border=1)
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "N° Sucursales", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('sucursales', '0'), border=1)
        self.ln()
        
        # Fila 4
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "Provincia/Cantón/Parr", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('ubicacion', ''), border=1)
        self.set_font('Helvetica', 'B', 8)
        self.cell(35, 6, "N° Trabajadores", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(60, 6, self.empresa.get('trabajadores', '0'), border=1)
        self.ln(10)

        # 2. Información del Responsable
        self.set_fill_color(255, 204, 0)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, "2. Información del Responsable y del Proceso", border=1, fill=True, align='C')
        self.ln()
        
        # Lado izquierdo (Datos)
        y_start = self.get_y()
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(220, 220, 220)
        
        self.cell(40, 8, "Nombres y Apellidos", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(100, 8, self.responsable.get('nombre', ''), border=1)
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(40, 8, "Cédula de Identidad", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(100, 8, self.responsable.get('cedula', ''), border=1)
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(40, 8, "Cargo en la empresa", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(100, 8, self.responsable.get('cargo', ''), border=1)
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(40, 8, "Profesión", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(100, 8, self.responsable.get('profesion', ''), border=1)
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(40, 8, "Registro MRL/SENESCYT", border=1, fill=True)
        self.set_font('Helvetica', '', 8)
        self.cell(100, 8, self.responsable.get('registro', ''), border=1)
        self.ln()
        
        self.set_font('Helvetica', 'B', 8)
        self.cell(40, 15, "Firma de Responsabilidad", border=1, fill=True)
        self.cell(100, 15, "", border=1) # Espacio para firma digital
        
        # Lado derecho (Foto)
        x_foto = 150
        self.set_xy(x_foto, y_start)
        self.set_fill_color(220, 220, 220)
        self.cell(50, 8, "Fotografía", border=1, fill=True, align='C')
        self.set_xy(x_foto, y_start + 8)
        self.cell(50, 47, "", border=1) # Espacio para foto
        
        self.ln(55)

    def seccion_titulo(self, titulo: str):
        """Agrega una nueva sección"""
        self.ln(5) # Espacio antes del título
        self.set_fill_color(255, 204, 0)
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 8, titulo, border=1, fill=True, align='L', ln=1)
        self.ln(2)
        self.set_text_color(50, 50, 50)
    
    def parrafo(self, texto: str):
        """Agrega un párrafo de texto"""
        self.set_font('Helvetica', '', 9)
        self.set_text_color(0, 0, 0)
        self.multi_cell(0, 5, texto)
        self.ln(3)
    
    def subtitulo(self, texto: str):
        """Agrega un subtítulo"""
        self.set_font('Helvetica', 'B', 9)
        self.set_text_color(0, 0, 0)
        self.cell(0, 6, texto, align='L')
        self.ln()
    
    def tabla_datos(self, headers: list, data: list):
        """Genera una tabla con datos"""
        self.set_font('Helvetica', 'B', 8)
        self.set_fill_color(240, 240, 240)
        self.set_text_color(0, 0, 0)
        
        col_width = 190 / len(headers)
        for header in headers:
            self.cell(col_width, 6, str(header), border=1, align='C', fill=True)
        self.ln()
        
        self.set_font('Helvetica', '', 8)
        for row in data:
            for item in row:
                self.cell(col_width, 6, str(item), border=1, align='C')
            self.ln()
        self.ln(3)
    
    def indicador_valor(self, nombre: str, valor: float, unidad: str = "%"):
        """Muestra un indicador"""
        self.set_font('Helvetica', '', 9)
        self.cell(80, 6, nombre + ":", border=1)
        self.set_font('Helvetica', 'B', 9)
        self.cell(40, 6, f"{valor:.2f} {unidad}", border=1, align='C')
        self.ln()
    
    def alerta(self, texto: str, tipo: str = "info"):
        """Muestra mensaje"""
        colores = {
            "warning": (255, 255, 200),
            "danger": (255, 220, 220),
            "success": (220, 255, 220),
            "info": (230, 240, 255)
        }
        r, g, b = colores.get(tipo, (255, 255, 255))
        self.set_fill_color(r, g, b)
        self.set_font('Helvetica', '', 8)
        self.multi_cell(0, 5, texto, border=1, fill=True)
        self.ln(3)

    def agregar_grafico(self, imagen_bytes: bytes, titulo: str):
        """Agrega un gráfico desde bytes"""
        import tempfile
        import os
        
        if not imagen_bytes:
            return
            
        self.ln(5)
        self.subtitulo(titulo)
        
        # Guardar temporalmente
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.png') as tmp:
                tmp.write(imagen_bytes)
                tmp_path = tmp.name
            
            # Insertar imagen centrado
            # Ancho A4 es 210mm, margenes default 10mm (x=10). Contenido ~190mm
            # Queremos centrar imagen de unos 140mm de ancho
            x_pos = (210 - 150) / 2
            self.image(tmp_path, x=x_pos, w=150)
            self.ln(5)
            
            # Limpiar
            os.unlink(tmp_path)
        except Exception as e:
            self.parrafo(f"Error al incluir gráfico: {str(e)}")

    def seccion_firmas(self):
        """Genera la sección de firmas de aprobación"""
        self.add_page()
        self.set_font('Helvetica', 'B', 10)
        self.cell(0, 10, "CONTROL DE EMISIÓN Y APROBACIÓN", border=1, align='C', fill=True)
        self.ln(10)
        
        col_w = 63
        self.cell(col_w, 8, "ELABORADO POR:", border=1, align='C', fill=True)
        self.cell(col_w, 8, "REVISADO POR:", border=1, align='C', fill=True)
        self.cell(col_w, 8, "APROBADO POR:", border=1, align='C', fill=True)
        self.ln()
        
        # Espacio firmas
        h_firma = 30
        self.cell(col_w, h_firma, "", border=1)
        self.cell(col_w, h_firma, "", border=1)
        self.cell(col_w, h_firma, "", border=1)
        self.ln()
        
        # Nombres
        self.set_font('Helvetica', '', 8)
        self.cell(col_w, 6, self.responsable.get('nombre', ''), border=1, align='C')
        self.cell(col_w, 6, self.aprobacion.get('nombre_revisor', ''), border=1, align='C')
        self.cell(col_w, 6, self.aprobacion.get('nombre_aprobador', ''), border=1, align='C')
        self.ln()
        
        # Cargos
        self.cell(col_w, 6, self.responsable.get('cargo', ''), border=1, align='C')
        self.cell(col_w, 6, self.aprobacion.get('cargo_revisor', 'Gerente Técnico'), border=1, align='C')
        self.cell(col_w, 6, self.aprobacion.get('cargo_aprobador', 'Gerente General'), border=1, align='C')
        self.ln()


def generar_informe_reactivos(
    df_charts: pd.DataFrame,
    metricas: Dict[str, Any],
    datos_empresa: Dict[str, str],
    datos_responsable: Dict[str, str],
    datos_aprobacion: Dict[str, str],
    imagenes: Dict[str, bytes] = None,
    periodo: str = "2026",
    codigo: str = "R-SSO-IR-00",
    version: str = "01"
) -> bytes:
    """Genera el informe PDF completo de indicadores reactivos"""
    
    pdf = InformePDF("Reporte Indices Reactivos", datos_empresa, datos_responsable, datos_aprobacion, periodo, codigo, version)
    imagenes = imagenes or {}
    
    # === HOJA 1: PORTADA ===
    pdf.portada("REACTIVOS")
    
    # === HOJA 2: INFO EMPRESA Y RESPONSABLE ===
    pdf.add_page()
    pdf.seccion_informacion_general()
    
    # === HOJA 3: INTRODUCCIÓN ===
    pdf.seccion_titulo("3. Introducción")
    pdf.parrafo("""Los indicadores reactivos de Seguridad y Salud Ocupacional constituyen 
herramientas fundamentales para la medición y evaluación del desempeño en materia de 
prevención de riesgos laborales. Estos indicadores se denominan "reactivos" porque miden 
eventos que ya han ocurrido, es decir, responden a hechos consumados dentro de la 
organización.""")
    
    pdf.parrafo("""A diferencia de los indicadores proactivos que miden acciones preventivas, 
los indicadores reactivos cuantifican las consecuencias de los accidentes laborales, 
enfermedades ocupacionales y días perdidos. Su análisis permite identificar patrones de 
siniestralidad, evaluar la severidad de los incidentes y establecer líneas base para la 
mejora continua del sistema de gestión de SSO.""")
    
    pdf.parrafo("""El presente informe analiza tres indicadores reactivos fundamentales 
establecidos en la normativa de seguridad laboral: el Índice de Frecuencia (IF), el 
Índice de Gravedad (IG) y la Tasa de Riesgo (TR). Cada uno de estos indicadores aporta 
información crítica para la toma de decisiones en materia de prevención.""")
    
    # === HOJA 4: METODOLOGÍA ===
    pdf.seccion_titulo("4. Metodología")
    pdf.parrafo("""Los indicadores presentados en este informe fueron calculados mediante 
una aplicación especializada de gestión de SSO que procesa los datos de accidentes, 
lesiones y días perdidos registrados durante el período de evaluación.""")
    
    pdf.subtitulo("Alcance del Análisis")
    pdf.parrafo(f"""El análisis comprende el período {periodo}, durante el cual se 
recopilaron datos de horas hombre trabajadas, número de lesiones (incluyendo accidentes 
con y sin baja, así como enfermedades ocupacionales) y días perdidos por incapacidad.""")
    
    pdf.subtitulo("Constante K")
    pdf.parrafo("""Para el cálculo de los índices se utiliza la constante K, que representa 
un factor de normalización que permite comparar organizaciones de diferentes tamaños. 
Los valores típicos son K=200,000 (mensual) o K=1,000,000 (anual).""")
    
    pdf.subtitulo("Limitaciones")
    pdf.parrafo("""El análisis se basa en los datos proporcionados, por lo que la calidad 
de los resultados depende directamente de la precisión en el registro de accidentes y 
horas trabajadas. Se recomienda validar periódicamente los datos de entrada.""")
    
    # === HOJA 5: ÍNDICE DE FRECUENCIA ===
    pdf.seccion_titulo("5. Índice de Frecuencia (IF)")
    pdf.subtitulo("Descripción Técnica")
    pdf.parrafo("""El Índice de Frecuencia (IF) mide la cantidad de lesiones por cada 
millón (o fracción según K) de horas hombre trabajadas. Es el indicador más utilizado 
para evaluar la ocurrencia de accidentes en una organización.""")
    
    pdf.parrafo("Fórmula: IF = (Número de Lesiones x K) / Horas Hombre Trabajadas")
    
    pdf.subtitulo("Resultados del Período")
    if_promedio = metricas.get('if_promedio', 0)
    pdf.indicador_valor("IF Promedio del Período", if_promedio, "")
    
    # Tabla de valores mensuales
    if 'mes' in df_charts.columns and 'IF' in df_charts.columns:
        headers = ['Mes', 'IF']
        data = [[row['mes'], f"{row['IF']:.2f}"] for _, row in df_charts.iterrows()]
        pdf.tabla_datos(headers, data)
    
    # Gráfico IF
    if 'IF' in imagenes:
        pdf.agregar_grafico(imagenes['IF'], "Gráfico de Evolución IF")
        
    pdf.subtitulo("Interpretación")
    if if_promedio < 5:
        pdf.alerta("EXCELENTE: El IF se encuentra en niveles muy bajos, indicando un control efectivo de la frecuencia de accidentes.", "success")
    elif if_promedio < 15:
        pdf.alerta("ACEPTABLE: El IF se encuentra en niveles moderados. Se recomienda mantener las medidas preventivas actuales.", "info")
    else:
        pdf.alerta("ATENCIÓN: El IF indica una alta frecuencia de accidentes. Se requieren acciones correctivas inmediatas.", "danger")
    
    # === HOJA 6: ÍNDICE DE GRAVEDAD ===
    pdf.seccion_titulo("6. Índice de Gravedad (IG)")
    pdf.subtitulo("Descripción Técnica")
    pdf.parrafo("""El Índice de Gravedad (IG) mide la severidad de los accidentes en 
términos de días perdidos por cada millón de horas trabajadas. A diferencia del IF, 
el IG refleja no solo la ocurrencia sino la magnitud del impacto de los accidentes.""")
    
    pdf.parrafo("Fórmula: IG = (Días Perdidos x K) / Horas Hombre Trabajadas")
    
    pdf.subtitulo("Resultados del Período")
    ig_promedio = metricas.get('ig_promedio', 0)
    pdf.indicador_valor("IG Promedio del Período", ig_promedio, "")
    
    if 'mes' in df_charts.columns and 'IG' in df_charts.columns:
        headers = ['Mes', 'IG']
        data = [[row['mes'], f"{row['IG']:.2f}"] for _, row in df_charts.iterrows()]
        pdf.tabla_datos(headers, data)
        
    # Gráfico IG
    if 'IG' in imagenes:
        pdf.agregar_grafico(imagenes['IG'], "Gráfico de Evolución IG")
    
    pdf.subtitulo("Interpretación")
    if ig_promedio < 50:
        pdf.alerta("Los accidentes registrados presentan baja severidad.", "success")
    elif ig_promedio < 200:
        pdf.alerta("Severidad moderada. Algunos accidentes generan incapacidades significativas.", "warning")
    else:
        pdf.alerta("CRÍTICO: Alta severidad en los accidentes. Revisar causas de lesiones graves.", "danger")
    
    # === HOJA 7: TASA DE RIESGO ===
    pdf.seccion_titulo("7. Tasa de Riesgo (TR)")
    pdf.subtitulo("Descripción Técnica")
    pdf.parrafo("""La Tasa de Riesgo (TR) representa el promedio de días perdidos por 
cada accidente ocurrido. Es útil para entender la gravedad promedio de los incidentes 
independientemente de las horas trabajadas.""")
    
    pdf.parrafo("Fórmula: TR = IG / IF = Días Perdidos / Número de Lesiones")
    
    pdf.subtitulo("Resultados del Período")
    tr_promedio = metricas.get('tr_promedio', 0)
    pdf.indicador_valor("TR Promedio del Período", tr_promedio, "días/accidente")
    
    if 'mes' in df_charts.columns and 'TR' in df_charts.columns:
        headers = ['Mes', 'TR']
        data = [[row['mes'], f"{row['TR']:.2f}"] for _, row in df_charts.iterrows()]
        pdf.tabla_datos(headers, data)
        
    # Gráfico TR
    if 'TR' in imagenes:
        pdf.agregar_grafico(imagenes['TR'], "Gráfico de Evolución TR")
    
    pdf.subtitulo("Interpretación")
    if tr_promedio < 5:
        pdf.alerta("Los accidentes generan incapacidades cortas (lesiones leves).", "success")
    elif tr_promedio < 15:
        pdf.alerta("Gravedad moderada por accidente. Evaluar causas de lesiones.", "warning")
    else:
        pdf.alerta("ATENCIÓN: Cada accidente genera en promedio más de 15 días de baja.", "danger")
    
    # === HOJA 8: ANÁLISIS INTEGRADO ===
    pdf.seccion_titulo("8. Análisis Integrado de Indicadores Reactivos")
    
    pdf.subtitulo("Relación entre Indicadores")
    pdf.parrafo("""El análisis conjunto de IF, IG y TR permite una comprensión integral 
de la siniestralidad organizacional:""")
    
    total_lesiones = metricas.get('total_lesiones', 0)
    total_dias = metricas.get('total_dias', 0)
    
    pdf.parrafo(f"- Total de lesiones registradas en el período: {int(total_lesiones)}")
    pdf.parrafo(f"- Total de días perdidos: {int(total_dias)}")
    pdf.parrafo(f"- Índice de Frecuencia promedio: {if_promedio:.2f}")
    pdf.parrafo(f"- Índice de Gravedad promedio: {ig_promedio:.2f}")
    pdf.parrafo(f"- Tasa de Riesgo promedio: {tr_promedio:.2f}")
    
    pdf.subtitulo("Evaluación Global")
    if if_promedio < 5 and ig_promedio < 50:
        evaluacion = "FAVORABLE"
        texto_eval = "La organización presenta un nivel de siniestralidad bajo tanto en frecuencia como en gravedad."
        tipo_alerta = "success"
    elif if_promedio > 15 or ig_promedio > 200:
        evaluacion = "CRÍTICO"
        texto_eval = "Se requiere atención inmediata para reducir la accidentalidad y/o la severidad de los incidentes."
        tipo_alerta = "danger"
    else:
        evaluacion = "MODERADO"
        texto_eval = "Existen oportunidades de mejora en el control de accidentes y su severidad."
        tipo_alerta = "warning"
    
    pdf.parrafo(f"Estado general de siniestralidad: {evaluacion}")
    pdf.alerta(texto_eval, tipo_alerta)
    
    # === HOJA 9: CONCLUSIONES Y FIRMAS ===
    pdf.seccion_titulo("9. Conclusiones y Recomendaciones")
    
    pdf.subtitulo("Conclusiones")
    pdf.parrafo(f"""1. El Índice de Frecuencia promedio de {if_promedio:.2f} indica que 
{'la frecuencia de accidentes se mantiene controlada' if if_promedio < 10 else 'existe una frecuencia significativa de accidentes que requiere atención'}.""")
    
    pdf.parrafo(f"""2. El Índice de Gravedad promedio de {ig_promedio:.2f} refleja 
{'una severidad baja en los accidentes ocurridos' if ig_promedio < 100 else 'una severidad considerable que impacta la productividad'}.""")
    
    pdf.parrafo(f"""3. La Tasa de Riesgo de {tr_promedio:.2f} días por accidente 
{'es aceptable para las operaciones' if tr_promedio < 10 else 'sugiere la necesidad de mejorar los controles preventivos'}.""")
    
    pdf.subtitulo("Recomendaciones")
    pdf.parrafo("""1. Mantener y fortalecer los programas de capacitación en seguridad 
para todos los niveles de la organización.""")
    
    pdf.parrafo("""2. Realizar análisis de causa raíz para todos los accidentes 
registrados, especialmente aquellos con mayor número de días perdidos.""")
    
    pdf.parrafo("""3. Implementar o reforzar indicadores proactivos que permitan 
anticipar y prevenir la ocurrencia de accidentes futuros.""")
    
    pdf.parrafo("""4. Establecer metas de reducción progresiva para los indicadores 
reactivos como parte del plan de mejora continua del sistema de gestión de SSO.""")

    # Firmas
    pdf.seccion_firmas()
    
    # Generar bytes
    return bytes(pdf.output())


def generar_informe_proactivos(
    df_resultados: pd.DataFrame,
    metas: Dict[str, float],
    datos_empresa: Dict[str, str],
    datos_responsable: Dict[str, str],
    datos_aprobacion: Dict[str, str],
    imagenes: Dict[str, bytes] = None,
    periodo: str = "2026",
    codigo: str = "R-SSO-IP-00",
    version: str = "01"
) -> bytes:
    """Genera el informe PDF completo de indicadores proactivos"""
    
    pdf = InformePDF("Reporte Indices Proactivos", datos_empresa, datos_responsable, datos_aprobacion, periodo, codigo, version)
    imagenes = imagenes or {}
    
    # === HOJA 1: PORTADA ===
    pdf.portada("PROACTIVOS")
    
    # === HOJA 2: INFO EMPRESA Y RESPONSABLE ===
    pdf.add_page()
    pdf.seccion_informacion_general()
    
    # === HOJA 3: INTRODUCCIÓN ===
    pdf.seccion_titulo("3. Introducción")
    pdf.parrafo("""Los indicadores proactivos de Seguridad y Salud Ocupacional representan 
un enfoque preventivo en la gestión de riesgos laborales. A diferencia de los indicadores 
reactivos que miden consecuencias, los proactivos evalúan las acciones tomadas para 
PREVENIR accidentes antes de que ocurran.""")
    
    pdf.parrafo("""Estos indicadores permiten medir el nivel de cumplimiento de las 
actividades planificadas en el programa de prevención de riesgos, tales como 
capacitaciones, inspecciones, análisis de riesgos y cumplimiento de procedimientos 
de trabajo seguro.""")
    
    pdf.parrafo("""Un alto nivel de cumplimiento en indicadores proactivos se correlaciona 
directamente con menores índices de accidentalidad (indicadores reactivos bajos). Por 
tanto, su seguimiento constante es fundamental para una gestión SSO efectiva.""")
    
    # === HOJA 4: METODOLOGÍA ===
    pdf.seccion_titulo("4. Metodología")
    pdf.parrafo("""Los indicadores proactivos fueron calculados mediante una aplicación 
de gestión SSO que procesa los datos de actividades programadas versus ejecutadas 
durante el período de evaluación.""")
    
    pdf.subtitulo("Meta de Cumplimiento")
    meta_general = metas.get('general', 80)
    pdf.parrafo(f"""La meta establecida para los indicadores proactivos es del {meta_general}%. 
Este valor es configurable según las políticas de cada organización y puede ajustarse 
de acuerdo al nivel de madurez del sistema de gestión de SSO.""")
    
    pdf.subtitulo("Criterios de Evaluación")
    pdf.parrafo(f"""- Cumplimiento >= {meta_general}%: El indicador se considera SATISFACTORIO""")
    pdf.parrafo(f"""- Cumplimiento < {meta_general}%: El indicador requiere ATENCIÓN y acciones correctivas""")
    
    # Gráfico de Cumplimiento General
    if 'barras_resumen' in imagenes:
        pdf.agregar_grafico(imagenes['barras_resumen'], "Cumplimiento Promedio por Indicador")
    
    # === INDICADORES INDIVIDUALES ===
    indicadores_info = {
        'iart': {
            'nombre': 'IART - Índice de Análisis de Riesgos de Tareas',
            'descripcion': """El IART mide el porcentaje de análisis de riesgos completados 
respecto a los programados. Un análisis de riesgos permite identificar peligros en las 
tareas antes de ejecutarlas.""",
            'formula': 'IART = (NART / NARP) x 100',
            'variables': 'NARP: Análisis Programados | NART: Análisis Terminados'
        },
        'opas': {
            'nombre': 'OPAS - Observación Planeada de Acciones Subestándar',
            'descripcion': """El OPAS evalúa el cumplimiento de las observaciones de 
comportamiento programadas. Estas observaciones permiten detectar y corregir 
conductas inseguras de los trabajadores.""",
            'formula': 'OPAS = (OPASR x PC) / (OPASP x POBP) x 100',
            'variables': 'OPASP: Observaciones Programadas | OPASR: Observaciones Realizadas | POBP: Población Programada | PC: Población Cubierta'
        },
        'ids': {
            'nombre': 'IDS - Índice de Diálogos de Seguridad',
            'descripcion': """El IDS mide el cumplimiento de las charlas de seguridad 
programadas. Los diálogos de seguridad son herramientas de comunicación directa 
con los trabajadores sobre temas de prevención.""",
            'formula': 'IDS = (NCSE / NCSD) x 100',
            'variables': 'NCSD: Charlas Programadas | NCSE: Charlas Ejecutadas'
        },
        'idps': {
            'nombre': 'IDPS - Índice de Demandas de Seguridad',
            'descripcion': """El IDPS evalúa la atención a las solicitudes de mejora en 
seguridad realizadas por los trabajadores o áreas. Refleja la capacidad de respuesta 
de la organización ante necesidades de seguridad.""",
            'formula': 'IDPS = (DPSR x NAS) / (DPSP x PP) x 100',
            'variables': 'DPSP: Demandas Programadas | DPSR: Demandas Realizadas | PP: Población Programada | NAS: Áreas Supervisadas'
        },
        'ients': {
            'nombre': 'IENTS - Índice de Entrenamiento en Seguridad',
            'descripcion': """El IENTS mide el porcentaje de trabajadores que han recibido 
la capacitación programada en seguridad. La formación es fundamental para una cultura 
preventiva efectiva.""",
            'formula': 'IENTS = (NEE / NTEEP) x 100',
            'variables': 'NTEEP: Empleados a Entrenar | NEE: Empleados Entrenados'
        },
        'iosea': {
            'nombre': 'IOSEA - Índice de Órdenes de Servicio Estandarizadas',
            'descripcion': """El IOSEA evalúa el cumplimiento de los procedimientos de 
trabajo seguro acordados. Un alto IOSEA indica que los trabajadores siguen los 
protocolos establecidos.""",
            'formula': 'IOSEA = (OSEAC / OSEAA) x 100',
            'variables': 'OSEAA: Órdenes Acordadas | OSEAC: Órdenes Cumplidas'
        },
        'icai': {
            'nombre': 'ICAI - Índice de Control de Accidentes e Incidentes',
            'descripcion': """El ICAI mide el porcentaje de medidas correctivas implementadas 
tras la investigación de accidentes o incidentes. Un alto ICAI indica que la organización 
aprende de los eventos y toma acciones.""",
            'formula': 'ICAI = (NMI / NMP) x 100',
            'variables': 'NMP: Medidas Propuestas | NMI: Medidas Implementadas'
        },
        'ief': {
            'nombre': 'IEF - Índice de Eficacia de la Formación',
            'descripcion': """El IEF evalúa el cumplimiento del plan de capacitaciones. 
Mide la relación entre las capacitaciones ejecutadas y las programadas en el período.""",
            'formula': 'IEF = (CAPE / CAPP) x 100',
            'variables': 'CAPP: Capacitaciones Programadas | CAPE: Capacitaciones Ejecutadas'
        }
    }
    
    num_hoja = 4 # Empezamos en la hoja 5 (después de Portada, Info, Intro, Metodología)
    for ind_key, ind_info in indicadores_info.items():
        num_hoja += 1
        pdf.seccion_titulo(f"{num_hoja}. {ind_info['nombre']}")
        
        pdf.subtitulo("Descripción")
        pdf.parrafo(ind_info['descripcion'])
        
        pdf.subtitulo("Fórmula de Cálculo")
        pdf.parrafo(ind_info['formula'])
        pdf.parrafo(ind_info['variables'])
        
        # Buscar datos del indicador
        meta_ind = metas.get(ind_key, meta_general)
        
        pdf.subtitulo("Resultados del Período")
        if ind_key in df_resultados.columns:
            # Calcular promedio
            promedio = df_resultados[ind_key].mean()
            pdf.indicador_valor(f"{ind_key.upper()} Promedio", promedio)
            pdf.indicador_valor("Meta establecida", meta_ind)
            
            # Tabla mensual
            headers = ['Mes', ind_key.upper()]
            data = [[row['mes'], f"{row[ind_key]:.1f}%"] for _, row in df_resultados.iterrows()]
            pdf.tabla_datos(headers, data)
            
            # Evaluación
            if promedio >= meta_ind:
                pdf.alerta(f"CUMPLE: El indicador supera la meta establecida del {meta_ind}%.", "success")
            else:
                brecha = meta_ind - promedio
                pdf.alerta(f"NO CUMPLE: Existe una brecha de {brecha:.1f}% respecto a la meta.", "danger")
        else:
            pdf.alerta("No se encontraron datos para este indicador en el período.", "warning")
    
    # === ANÁLISIS GLOBAL ===
    pdf.seccion_titulo(f"{num_hoja + 1}. Análisis Global de Indicadores Proactivos")
    
    pdf.subtitulo("Nivel de Madurez Preventiva")
    
    # Calcular cumplimiento general
    indicadores_cols = [k for k in indicadores_info.keys() if k in df_resultados.columns]
    if indicadores_cols:
        promedios = [df_resultados[col].mean() for col in indicadores_cols]
        promedio_general = sum(promedios) / len(promedios)
        cumplimiento_count = sum(1 for p in promedios if p >= meta_general)
        
        pdf.indicador_valor("Promedio General de Cumplimiento", promedio_general)
        pdf.parrafo(f"Indicadores que cumplen la meta: {cumplimiento_count} de {len(indicadores_cols)}")
        
        if promedio_general >= 90:
            nivel = "ALTO"
            descripcion = "La organización demuestra un nivel avanzado de gestión preventiva."
            tipo = "success"
        elif promedio_general >= 70:
            nivel = "MEDIO"
            descripcion = "Existen oportunidades de mejora en algunos indicadores."
            tipo = "warning"
        else:
            nivel = "BAJO"
            descripcion = "Se requiere fortalecer significativamente las acciones preventivas."
            tipo = "danger"
        
        pdf.parrafo(f"Nivel de madurez preventiva: {nivel}")
        pdf.alerta(descripcion, tipo)
        
        # Gráfico Evolución IG Total
        if 'evolucion_ig' in imagenes:
            pdf.agregar_grafico(imagenes['evolucion_ig'], "Evolución IG Total")
        
        # Indicadores críticos
        pdf.subtitulo("Indicadores con Oportunidad de Mejora")
        for i, col in enumerate(indicadores_cols):
            if promedios[i] < meta_general:
                pdf.parrafo(f"- {col.upper()}: {promedios[i]:.1f}% (brecha de {meta_general - promedios[i]:.1f}%)")
    
    pdf.subtitulo("Impacto en Indicadores Reactivos")
    pdf.parrafo("""El nivel de cumplimiento de los indicadores proactivos tiene un impacto 
directo en los indicadores reactivos futuros. Un alto cumplimiento en prevención reduce 
la probabilidad de accidentes y, por tanto, mejora los índices IF, IG y TR.""")
    
    # === CONCLUSIONES Y FIRMAS ===
    pdf.seccion_titulo(f"{num_hoja + 2}. Conclusiones y Recomendaciones")
    
    pdf.subtitulo("Conclusiones")
    if indicadores_cols:
        pdf.parrafo(f"""1. El promedio general de cumplimiento de indicadores proactivos es 
de {promedio_general:.1f}%, lo que indica un nivel {nivel.lower()} de gestión preventiva.""")
        
        pdf.parrafo(f"""2. De los {len(indicadores_cols)} indicadores evaluados, {cumplimiento_count} 
cumplen con la meta establecida del {meta_general}%.""")
    
    pdf.parrafo("""3. Las brechas identificadas en los indicadores proactivos representan 
riesgos potenciales que podrían manifestarse como accidentes futuros si no se corrigen.""")
    
    pdf.subtitulo("Recomendaciones")
    pdf.parrafo("""1. Priorizar la mejora de los indicadores que no cumplen la meta, 
estableciendo planes de acción específicos con responsables y fechas.""")
    
    pdf.parrafo("""2. Revisar la planificación de actividades preventivas para asegurar 
que sean alcanzables con los recursos disponibles.""")
    
    pdf.parrafo("""3. Fortalecer el seguimiento mensual de indicadores para detectar 
desviaciones oportunamente y tomar acciones correctivas.""")
    
    pdf.parrafo("""4. Vincular el cumplimiento de indicadores proactivos con objetivos 
de desempeño y reconocimiento del personal.""")
    
    pdf.seccion_firmas()
    
    # Generar bytes
    return bytes(pdf.output())

