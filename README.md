# 🛡️ Dashboard de Gestión de Seguridad y Salud Ocupacional (SSO)

## Cumplimiento Normativa IESS CD 513 - Ecuador

Dashboard empresarial profesional para el seguimiento y análisis de indicadores de Seguridad y Salud Ocupacional, diseñado específicamente para cumplir con los requerimientos técnicos y legales de la normativa ecuatoriana. Incorpora motores de cálculo separados para indicadores reactivos y proactivos, así como generación de informes auditables.

---

## 📋 Tabla de Contenidos

- [Características](#-características)
- [Novedades v2.1](#-novedades-v21)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Instalación](#-instalación)
- [Uso](#-uso)
- [Indicadores Implementados](#-indicadores-implementados)
- [Formato de Datos](#-formato-de-datos)
- [Arquitectura](#-arquitectura)

---

## ✨ Características

- ✅ **Gestión Integral de Indicadores**: Cálculo automático de 11 indicadores clave (3 reactivos y 8 proactivos).
- 📊 **Visualización Avanzada**: 
  - Gráficos interactivos Plotly (Barras, Líneas, Radar Charts).
  - KPI Cards con resumen de desempeño anual.
  - Tablas de detalle con formato condicional.
- 📄 **Reportes PDF Auditables**: Generación automática de informes técnicos listos para firma y auditoría, incluyendo gráficos estáticos de alta calidad.
- 📁 **Gestión de Datos Flexibles**:
  - Carga masiva mediante Excel.
  - Edición manual directa en la interfaz para correcciones rápidas.
  - Plantillas descargables para facilitar la carga de información.
- 🎯 **Evaluación de Cumplimiento**: Configuración personalizada de metas con alertas visuales de estado (Cumple/No Cumple).

## 🚀 Novedades v2.1

- **Generador de PDF Incorporado**: Motor propio para crear informes PDF A4 con portada, metodología, análisis gráfico y secciones de firma.
- **Gráficos Estáticos**: Integración con Matplotlib para generar gráficos de alta resolución incrustados en los reportes PDF.
- **Validación Mejorada**: Sistema robusto de validación de estructuras de archivos Excel.

---

## 📁 Estructura del Proyecto

```
PROYECTO_SSO/
├── data/                    # Almacenamiento temporal
├── modules/                 # Módulos del Core de Negocio
│   ├── __init__.py          # Inicialización
│   ├── calculator.py        # Motor de fórmulas matemáticas
│   ├── validator.py         # Validación de integridad de datos
│   ├── visualizer.py        # Motor de visualización (Plotly + Matplotlib)
│   ├── pdf_generator.py     # Motor de reportes PDF (FPDF)
│   ├── reactive_engine.py   # Lógica específica reactiva
│   ├── proactive_engine.py  # Lógica específica proactiva
│   └── data_manager.py      # Orquestación de datos
├── app.py                   # Aplicación Web (Streamlit)
├── requirements.txt         # Dependencias del proyecto
└── README.md                # Documentación
```

---

## 🚀 Instalación

### Requisitos Previos

- Python 3.9 o superior
- pip (gestor de paquetes)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**

```bash
cd "c:\Users\Mathias\Documents\REACTIVOS PROACTIVOS\PROYECTO_SSO"
```

2. **Crear entorno virtual (recomendado)**

```bash
python -m venv venv
.\venv\Scripts\activate  # En Windows
# source venv/bin/activate  # En Linux/Mac
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación**

```bash
streamlit run app.py
```

La aplicación se abrirá automáticamente en `http://localhost:8501`.

---

## 📖 Uso

### 1. Dashboard Principal
Navegue entre las pestañas "Reactivos" y "Proactivos" para visualizar el estado de cada grupo de indicadores. El dashboard presenta tarjetas de resumen al inicio para una visión rápida del desempeño anual.

### 2. Carga de Datos
Utilice la barra lateral para:
- **Descargar Plantillas**: Obtenga los archivos Excel formato (`.xlsx`) vacíos y listos para llenar.
- **Cargar Datos**: Suba sus archivos llenos. El sistema validará automáticamente la estructura.
- **Configurar Metas y Constantes**: Ajuste la constante K (200,000 por defecto) y las metas porcentuales de cumplimiento.

### 3. Generación de Informes
En cada pestaña (Reactivos/Proactivos), encontrará la sección "Descargar Informes".
- **Configuración**: Despliegue el panel para ingresar datos de la empresa, responsable y aprobadores.
- **Descarga PDF**: Obtenga un informe completo y profesional, incluyendo análisis de tendencias y conclusiones automáticas basadas en sus datos.
- **Exportar Excel**: Descargue los datos procesados y calculados.

---

## 📊 Indicadores Implementados

### Indicadores Reactivos (Siniestralidad)

| Código | Nombre | Fórmula | Propósito |
|--------|--------|---------|-----------|
| **IF** | Índice de Frecuencia | (Lesiones × K) / Horas_Trabajadas | Frecuencia de eventos |
| **IG** | Índice de Gravedad | (Días_Perdidos × K) / Horas_Trabajadas | Severidad de eventos |
| **TR** | Tasa de Riesgo | Días_Perdidos / Lesiones | Promedio de baja por evento |

### Indicadores Proactivos (Gestión Preventiva)

| Código | Nombre | Fórmula Básica | Ponderación Recomendada |
|--------|--------|----------------|-------------------------|
| **IART** | Análisis de Riesgos de Tarea | Ejecutadas / Programadas | 5 |
| **OPAS** | Observaciones Planeadas | (Realizadas × Calidad) / Programadas | 3 |
| **IDPS** | Diálogos Periódicos | Asistencia / Programación | 2 |
| **IDS** | Demanda de Seguridad | Eliminadas / Detectadas | 3 |
| **IENTS** | Entrenamiento | Entrenados / Programados | 4 |
| **IOSEA** | Órdenes de Servicio | Cumplidos / Aplicables | 4 |
| **ICAI** | Control Accidentes/Incidentes | Implementadas / Propuestas | 4 |
| **IEF** | Índice de Eficacia | Auditados / Totales | - |
| **IG_TOTAL** | Índice de Gestión Total | Promedio Ponderado | Global |

---

## 🏗️ Arquitectura Técnica

El sistema utiliza una arquitectura modular limpia para facilitar el mantenimiento y la escalabilidad:

- **Frontend**: Streamlit con componentes personalizados HTML/CSS para una experiencia de usuario "Premium".
- **Motores de Cálculo**: Clases Python puras desacopladas de la interfaz visual para garantizar la precisión de los cálculos.
- **Visualización Híbrida**: 
  - *Interactivas*: Plotly para exploración de datos en pantalla.
  - *Estáticas*: Matplotlib para generación de imágenes de alta resolución incrustadas en reportes PDF.
- **Persistencia**: Manejo de estado de sesión para edición de datos en tiempo real sin bases de datos complejas.

---

## 📄 Licencia

Este software ha sido desarrollado para uso empresarial interno, cumpliendo estrictamente con los lineamientos técnicos de la normativa ecuatoriana vigente (CD 513).

---
**Desarrollado con ❤️ para la Excelencia en Seguridad Industrial**
