"""
Módulo de Gestión de Datos SSO
Carga, transformación y generación de datos

Este módulo maneja todas las operaciones de datos incluyendo
carga de archivos, generación de datos de prueba y exportación.
"""

import pandas as pd
import numpy as np
from io import BytesIO
from typing import Optional, Dict, Any
from datetime import datetime
import random


class DataManager:
    """
    Gestor de datos para el sistema SSO.
    
    Maneja la carga, transformación, generación de datos dummy
    y exportación de resultados.
    
    Attributes:
        MESES: Lista de meses en español
        COLUMNAS_BASE: Columnas requeridas para el sistema
    """
    
    MESES = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    
    COLUMNAS_BASE = [
        'mes', 'anio', 'horas_trabajadas', 'accidentes', 'dias_perdidos',
        'nart_prog', 'nart_ejec',
        'opas_prog', 'opas_real', 'opas_personas_prev', 'opas_personas_conf',
        'dps_plan', 'dps_real', 'dps_previstos', 'dps_asistentes',
        'ds_detectadas', 'ds_eliminadas',
        'ent_programados', 'ent_entrenados',
        'osea_aplicables', 'osea_cumplidos',
        'cai_propuestas', 'cai_implement',
        'ef_totales', 'ef_auditados',
    ]
    
    def __init__(self, anio: int = None):
        """
        Inicializa el gestor de datos.
        
        Args:
            anio: Año para los datos (default: año actual)
        """
        self.anio = anio or datetime.now().year
        self.df = None
    
    def cargar_excel(self, archivo) -> pd.DataFrame:
        """
        Carga datos desde un archivo Excel.
        
        Args:
            archivo: Archivo Excel (path o file-like object)
            
        Returns:
            pd.DataFrame: DataFrame con los datos cargados
            
        Raises:
            ValueError: Si hay error en la carga
        """
        try:
            df = pd.read_excel(archivo)
            # Normalizar nombres de columnas
            df.columns = [col.lower().strip() for col in df.columns]
            self.df = df
            return df
        except Exception as e:
            raise ValueError(f"Error al cargar archivo Excel: {str(e)}")
    
    def generar_datos_dummy(self, anio: int = None, 
                            semilla: int = None) -> pd.DataFrame:
        """
        Genera un DataFrame con datos aleatorios coherentes.
        
        Los datos generados son realistas y evitan denominadores
        en cero para todos los cálculos.
        
        Args:
            anio: Año para los datos (default: año de la instancia)
            semilla: Semilla para reproducibilidad (opcional)
            
        Returns:
            pd.DataFrame: DataFrame con datos de prueba para 12 meses
        """
        if semilla is not None:
            random.seed(semilla)
            np.random.seed(semilla)
        
        anio = anio or self.anio
        
        datos = []
        
        for i, mes in enumerate(self.MESES):
            # Variación estacional (más actividad en algunos meses)
            factor_estacional = 1 + 0.1 * np.sin(i * np.pi / 6)
            
            # Datos base
            trabajadores = random.randint(80, 150)
            dias_laborables = random.randint(20, 23)
            horas_dia = 8
            horas_trabajadas = trabajadores * dias_laborables * horas_dia
            
            # Accidentes y días perdidos (bajos para empresa con buen SSO)
            accidentes = random.choices([0, 1, 2], weights=[0.7, 0.25, 0.05])[0]
            dias_perdidos = accidentes * random.randint(1, 5) if accidentes > 0 else 0
            
            # IART - Análisis de Riesgos de Tarea
            nart_prog = random.randint(8, 15)
            # Ejecutados suelen ser alto porcentaje de programados
            nart_ejec = int(nart_prog * random.uniform(0.75, 1.0))
            
            # OPAS - Observaciones Planeadas
            opas_prog = random.randint(10, 20)
            opas_real = int(opas_prog * random.uniform(0.70, 1.0))
            opas_personas_prev = random.randint(30, 50)
            # Personas conformes como porcentaje de previstas ajustado
            opas_personas_conf = int(opas_personas_prev * random.uniform(0.75, 0.95))
            
            # IDPS - Diálogos Periódicos de Seguridad
            dps_plan = random.randint(4, 8)
            dps_real = int(dps_plan * random.uniform(0.75, 1.0))
            dps_previstos = random.randint(20, 40)
            dps_asistentes = int(dps_previstos * random.uniform(0.80, 1.0))
            
            # IDS - Demanda de Seguridad
            ds_detectadas = random.randint(5, 15)
            # Eliminadas como porcentaje de detectadas
            ds_eliminadas = int(ds_detectadas * random.uniform(0.70, 0.95))
            
            # IENTS - Entrenamiento
            ent_programados = random.randint(15, 30)
            ent_entrenados = int(ent_programados * random.uniform(0.75, 1.0))
            
            # IOSEA - Órdenes de Servicio
            osea_aplicables = random.randint(10, 20)
            osea_cumplidos = int(osea_aplicables * random.uniform(0.75, 0.98))
            
            # ICAI - Control de Accidentes/Incidentes
            cai_propuestas = random.randint(3, 8)
            cai_implement = int(cai_propuestas * random.uniform(0.70, 1.0))
            
            # IEF - Eficacia
            ef_totales = random.randint(15, 25)
            ef_auditados = int(ef_totales * random.uniform(0.75, 0.95))
            
            # Asegurar que ningún denominador sea cero
            fila = {
                'mes': mes,
                'anio': anio,
                'horas_trabajadas': max(horas_trabajadas, 1000),
                'accidentes': accidentes,
                'dias_perdidos': dias_perdidos,
                'nart_prog': max(nart_prog, 1),
                'nart_ejec': nart_ejec,
                'opas_prog': max(opas_prog, 1),
                'opas_real': opas_real,
                'opas_personas_prev': max(opas_personas_prev, 1),
                'opas_personas_conf': opas_personas_conf,
                'dps_plan': max(dps_plan, 1),
                'dps_real': dps_real,
                'dps_previstos': max(dps_previstos, 1),
                'dps_asistentes': dps_asistentes,
                'ds_detectadas': max(ds_detectadas, 1),
                'ds_eliminadas': ds_eliminadas,
                'ent_programados': max(ent_programados, 1),
                'ent_entrenados': ent_entrenados,
                'osea_aplicables': max(osea_aplicables, 1),
                'osea_cumplidos': osea_cumplidos,
                'cai_propuestas': max(cai_propuestas, 1),
                'cai_implement': cai_implement,
                'ef_totales': max(ef_totales, 1),
                'ef_auditados': ef_auditados,
            }
            
            datos.append(fila)
        
        self.df = pd.DataFrame(datos)
        return self.df
    
    def actualizar_mes(self, mes: str, datos: Dict[str, Any]) -> pd.DataFrame:
        """
        Actualiza los datos de un mes específico.
        
        Args:
            mes: Nombre del mes a actualizar
            datos: Diccionario con los nuevos valores
            
        Returns:
            pd.DataFrame: DataFrame actualizado
            
        Raises:
            ValueError: Si el mes no existe o no hay datos cargados
        """
        if self.df is None:
            raise ValueError("No hay datos cargados. Cargue o genere datos primero.")
        
        mes_lower = mes.lower().strip()
        
        if mes_lower not in self.df['mes'].str.lower().values:
            raise ValueError(f"Mes '{mes}' no encontrado en los datos")
        
        idx = self.df[self.df['mes'].str.lower() == mes_lower].index[0]
        
        for columna, valor in datos.items():
            if columna in self.df.columns:
                self.df.loc[idx, columna] = valor
        
        return self.df
    
    def agregar_mes(self, datos: Dict[str, Any]) -> pd.DataFrame:
        """
        Agrega un nuevo mes a los datos.
        
        Args:
            datos: Diccionario con los datos del nuevo mes
            
        Returns:
            pd.DataFrame: DataFrame con el nuevo mes agregado
        """
        if self.df is None:
            self.df = pd.DataFrame(columns=self.COLUMNAS_BASE)
        
        # Verificar que tenga las columnas mínimas
        if 'mes' not in datos:
            raise ValueError("El campo 'mes' es requerido")
        
        # Completar con valores por defecto
        fila_completa = {col: 0 for col in self.COLUMNAS_BASE}
        fila_completa.update(datos)
        
        # Asegurar año
        if 'anio' not in datos or datos['anio'] is None:
            fila_completa['anio'] = self.anio
        
        self.df = pd.concat([self.df, pd.DataFrame([fila_completa])], 
                           ignore_index=True)
        
        return self.df
    
    def exportar_excel(self, df: pd.DataFrame = None, 
                       incluir_formulas: bool = True) -> BytesIO:
        """
        Exporta el DataFrame a un archivo Excel en memoria.
        
        Args:
            df: DataFrame a exportar (default: df de la instancia)
            incluir_formulas: Si incluir columnas calculadas
            
        Returns:
            BytesIO: Buffer con el archivo Excel
        """
        df_export = df if df is not None else self.df
        
        if df_export is None:
            raise ValueError("No hay datos para exportar")
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_export.to_excel(writer, sheet_name='Datos_SSO', index=False)
            
            # Agregar hoja de metadata
            metadata = pd.DataFrame({
                'Campo': ['Fecha de Exportación', 'Total Registros', 'Año'],
                'Valor': [
                    datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    len(df_export),
                    df_export['anio'].iloc[0] if 'anio' in df_export.columns else 'N/A'
                ]
            })
            metadata.to_excel(writer, sheet_name='Metadata', index=False)
        
        buffer.seek(0)
        return buffer
    
    def exportar_plantilla(self) -> BytesIO:
        """
        Genera una plantilla Excel vacía con las columnas correctas.
        
        Returns:
            BytesIO: Buffer con la plantilla Excel
        """
        # Crear DataFrame con columnas y una fila de ejemplo
        df_plantilla = pd.DataFrame(columns=self.COLUMNAS_BASE)
        
        # Agregar fila de ejemplo
        ejemplo = {
            'mes': 'enero',
            'anio': self.anio,
            'horas_trabajadas': 15000,
            'accidentes': 0,
            'dias_perdidos': 0,
            'nart_prog': 10,
            'nart_ejec': 8,
            'opas_prog': 15,
            'opas_real': 12,
            'opas_personas_prev': 40,
            'opas_personas_conf': 35,
            'dps_plan': 6,
            'dps_real': 5,
            'dps_previstos': 30,
            'dps_asistentes': 28,
            'ds_detectadas': 10,
            'ds_eliminadas': 8,
            'ent_programados': 20,
            'ent_entrenados': 18,
            'osea_aplicables': 15,
            'osea_cumplidos': 13,
            'cai_propuestas': 5,
            'cai_implement': 4,
            'ef_totales': 20,
            'ef_auditados': 17,
        }
        
        df_plantilla = pd.concat([df_plantilla, pd.DataFrame([ejemplo])], 
                                 ignore_index=True)
        
        buffer = BytesIO()
        
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            df_plantilla.to_excel(writer, sheet_name='Datos', index=False)
            
            # Agregar hoja de instrucciones
            from modules.validator import DataValidator
            descripciones = DataValidator.obtener_descripcion_columnas()
            
            instrucciones = pd.DataFrame({
                'Columna': list(descripciones.keys()),
                'Descripción': list(descripciones.values()),
                'Tipo': ['Texto' if col == 'mes' else 'Número' 
                        for col in descripciones.keys()]
            })
            instrucciones.to_excel(writer, sheet_name='Instrucciones', index=False)
        
        buffer.seek(0)
        return buffer
    
    def obtener_resumen_estadistico(self, df: pd.DataFrame = None) -> Dict:
        """
        Genera un resumen estadístico de los datos.
        
        Args:
            df: DataFrame a analizar (default: df de la instancia)
            
        Returns:
            Dict: Diccionario con estadísticas
        """
        df_analisis = df if df is not None else self.df
        
        if df_analisis is None:
            return {}
        
        resumen = {
            'total_registros': len(df_analisis),
            'periodo': {
                'inicio': df_analisis['mes'].iloc[0] if 'mes' in df_analisis.columns else 'N/A',
                'fin': df_analisis['mes'].iloc[-1] if 'mes' in df_analisis.columns else 'N/A',
                'anio': df_analisis['anio'].iloc[0] if 'anio' in df_analisis.columns else 'N/A',
            },
            'indicadores': {}
        }
        
        # Estadísticas de indicadores calculados
        indicadores = ['IF', 'IG', 'IART', 'OPAS', 'IDPS', 'IDS', 
                      'IENTS', 'IOSEA', 'ICAI', 'IEF', 'IG_TOTAL']
        
        for ind in indicadores:
            if ind in df_analisis.columns:
                resumen['indicadores'][ind] = {
                    'promedio': df_analisis[ind].mean(),
                    'minimo': df_analisis[ind].min(),
                    'maximo': df_analisis[ind].max(),
                    'desv_std': df_analisis[ind].std(),
                }
        
        return resumen
    
    def obtener_dataframe(self) -> Optional[pd.DataFrame]:
        """
        Retorna el DataFrame actual.
        
        Returns:
            Optional[pd.DataFrame]: DataFrame o None si no hay datos
        """
        return self.df
    
    def establecer_dataframe(self, df: pd.DataFrame) -> None:
        """
        Establece el DataFrame de la instancia.
        
        Args:
            df: DataFrame a establecer
        """
        self.df = df.copy()
    
    @staticmethod
    def obtener_meses() -> list:
        """
        Retorna la lista de meses en español.
        
        Returns:
            list: Lista de nombres de meses
        """
        return DataManager.MESES.copy()
    
    @staticmethod
    def obtener_columnas_requeridas() -> list:
        """
        Retorna la lista de columnas requeridas.
        
        Returns:
            list: Lista de nombres de columnas
        """
        return DataManager.COLUMNAS_BASE.copy()
