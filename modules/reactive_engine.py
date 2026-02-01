"""
Motor de Análisis Reactivo SSO
Lógica de Reporte Trimestral con Índices Variables

Este módulo implementa el análisis reactivo con generación automática
de filas de resumen trimestral y anual, usando constantes K variables
según el período de análisis.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Dict, Optional
from dataclasses import dataclass


@dataclass
class ConstantesK:
    """
    Constantes K para cálculo de índices según período.
    
    - MENSUAL: 16,666.67 (200,000 / 12 meses)
    - TRIMESTRAL: 50,000 (200,000 / 4 trimestres)
    - ANUAL: 200,000 (estándar internacional)
    """
    MENSUAL: float = 16_666.67
    TRIMESTRAL: float = 50_000.0
    ANUAL: float = 200_000.0


class ReactiveAnalyzer:
    """
    Analizador de Indicadores Reactivos SSO.
    
    Genera reportes estructurados con filas de resumen trimestral
    y anual, calculando índices con constantes K variables.
    
    Attributes:
        K: Constantes para cálculo de índices
        MESES_TRIMESTRE: Mapeo de meses a trimestres
        HORAS_MENSUALES_STD: Horas estándar por trabajador/mes (173.33)
    """
    
    K = ConstantesK()
    
    # Horas estándar mensuales por trabajador (40h/semana * 4.33 semanas)
    HORAS_MENSUALES_STD = 173.33
    
    # Mapeo de meses a trimestres
    MESES_ORDEN = [
        'enero', 'febrero', 'marzo',
        'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre',
        'octubre', 'noviembre', 'diciembre'
    ]
    
    TRIMESTRES = {
        1: {'nombre': 'PRIMER TRIMESTRE', 'meses': ['enero', 'febrero', 'marzo']},
        2: {'nombre': 'SEGUNDO TRIMESTRE', 'meses': ['abril', 'mayo', 'junio']},
        3: {'nombre': 'TERCER TRIMESTRE', 'meses': ['julio', 'agosto', 'septiembre']},
        4: {'nombre': 'CUARTO TRIMESTRE', 'meses': ['octubre', 'noviembre', 'diciembre']},
    }
    
    # Columnas requeridas del input
    COLUMNAS_REQUERIDAS = [
        'mes', 'num_trabajadores', 'horas_hombre_mes', 
        'acc_baja', 'acc_sin_baja', 'enf_ocupacionales', 'dias_perdidos'
    ]
    
    # Columnas opcionales
    COLUMNAS_OPCIONALES = ['horas_extras', 'anio']
    
    def __init__(self):
        """Inicializa el analizador reactivo."""
        self.df_input = None
        self.df_reporte = None
        self.df_charts = None
    
    def procesar(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """
        Procesa el DataFrame de entrada y genera el reporte completo.
        
        Args:
            df: DataFrame con datos mensuales de accidentabilidad
            
        Returns:
            Tuple[pd.DataFrame, pd.DataFrame]: 
                - df_reporte: Tabla completa con meses, trimestres y año
                - df_charts: Solo filas de meses para gráficos
        """
        # Normalizar columnas
        df = df.copy()
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Validar columnas mínimas
        self._validar_columnas(df)
        
        # Preparar datos base
        df_base = self._preparar_datos_base(df)
        
        # Calcular índices para meses
        df_meses = self._calcular_indices_meses(df_base)
        
        # Generar filas de trimestre y año
        df_reporte = self._insertar_resúmenes(df_meses)
        
        # Separar datos para gráficos (solo meses)
        df_charts = df_reporte[df_reporte['tipo_fila'] == 'mes'].copy()
        
        self.df_reporte = df_reporte
        self.df_charts = df_charts
        
        return df_reporte, df_charts
    
    def _validar_columnas(self, df: pd.DataFrame) -> None:
        """
        Valida que existan las columnas requeridas.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            ValueError: Si faltan columnas requeridas
        """
        columnas_df = set(df.columns)
        faltantes = []
        
        for col in self.COLUMNAS_REQUERIDAS:
            if col not in columnas_df:
                faltantes.append(col)
        
        if faltantes:
            raise ValueError(
                f"Columnas requeridas faltantes: {', '.join(faltantes)}\n"
                f"Columnas encontradas: {', '.join(df.columns)}"
            )
    
    def _preparar_datos_base(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara los datos base con cálculos preliminares.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            pd.DataFrame: DataFrame con columnas calculadas
        """
        df = df.copy()
        
        # Asegurar tipos numéricos
        columnas_numericas = [
            'num_trabajadores', 'horas_hombre_mes', 'acc_baja', 
            'acc_sin_baja', 'enf_ocupacionales', 'dias_perdidos'
        ]
        
        for col in columnas_numericas:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Horas extras (opcional)
        if 'horas_extras' in df.columns:
            df['horas_extras'] = pd.to_numeric(df['horas_extras'], errors='coerce').fillna(0)
        else:
            df['horas_extras'] = 0
        
        # Calcular Total de Lesiones
        df['total_lesiones'] = (
            df['acc_baja'] + 
            df['acc_sin_baja'] + 
            df['enf_ocupacionales']
        )
        
        # Calcular Total de Horas
        # Si horas_hombre_mes tiene valor, usar ese; sino calcular
        df['total_horas'] = df.apply(
            lambda row: row['horas_hombre_mes'] 
            if row['horas_hombre_mes'] > 0 
            else (row['num_trabajadores'] * self.HORAS_MENSUALES_STD) + row['horas_extras'],
            axis=1
        )
        
        # Normalizar mes a minúsculas
        df['mes'] = df['mes'].str.lower().str.strip()
        
        # Ordenar por mes
        df['mes_orden'] = df['mes'].apply(
            lambda x: self.MESES_ORDEN.index(x) if x in self.MESES_ORDEN else 99
        )
        df = df.sort_values('mes_orden').reset_index(drop=True)
        
        return df
    
    def _calcular_indices_meses(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula los índices para cada mes usando K mensual.
        
        Args:
            df: DataFrame con datos preparados
            
        Returns:
            pd.DataFrame: DataFrame con índices calculados
        """
        df = df.copy()
        
        # Usar constante K mensual
        K = self.K.MENSUAL
        
        # Índice de Frecuencia (IF)
        df['IF'] = df.apply(
            lambda row: self._safe_divide(
                row['total_lesiones'] * K,
                row['total_horas']
            ),
            axis=1
        )
        
        # Índice de Gravedad (IG)
        df['IG'] = df.apply(
            lambda row: self._safe_divide(
                row['dias_perdidos'] * K,
                row['total_horas']
            ),
            axis=1
        )
        
        # Tasa de Riesgo (TR)
        df['TR'] = df.apply(
            lambda row: self._safe_divide(
                row['dias_perdidos'],
                row['total_lesiones']
            ),
            axis=1
        )
        
        # Marcar como fila de mes
        df['tipo_fila'] = 'mes'
        df['constante_k'] = K
        
        return df
    
    def _insertar_resúmenes(self, df_meses: pd.DataFrame) -> pd.DataFrame:
        """
        Inserta filas de resumen trimestral y anual.
        
        Args:
            df_meses: DataFrame con datos mensuales
            
        Returns:
            pd.DataFrame: DataFrame completo con resúmenes
        """
        filas_resultado = []
        
        for trimestre_num, config in self.TRIMESTRES.items():
            meses_trim = config['meses']
            nombre_trim = config['nombre']
            
            # Filtrar meses del trimestre
            df_trim = df_meses[df_meses['mes'].isin(meses_trim)]
            
            # Agregar filas de meses
            for _, row in df_trim.iterrows():
                filas_resultado.append(row.to_dict())
            
            # Calcular y agregar fila de trimestre
            if len(df_trim) > 0:
                fila_trim = self._crear_fila_resumen(
                    df_trim, 
                    nombre_trim, 
                    'trimestre',
                    self.K.TRIMESTRAL,
                    trimestre_num * 3  # Orden después del último mes
                )
                filas_resultado.append(fila_trim)
        
        # Crear fila de TOTAL AÑO
        fila_anual = self._crear_fila_resumen(
            df_meses,
            'TOTAL AÑO',
            'anual',
            self.K.ANUAL,
            99  # Orden al final
        )
        filas_resultado.append(fila_anual)
        
        # Construir DataFrame final
        df_reporte = pd.DataFrame(filas_resultado)
        
        # Ordenar por mes_orden
        df_reporte = df_reporte.sort_values('mes_orden').reset_index(drop=True)
        
        return df_reporte
    
    def _crear_fila_resumen(self, df_periodo: pd.DataFrame, 
                            nombre: str, tipo: str, 
                            constante_k: float, orden: int) -> Dict:
        """
        Crea una fila de resumen (trimestre o año).
        
        Args:
            df_periodo: DataFrame del período a resumir
            nombre: Nombre del período (ej: "PRIMER TRIMESTRE")
            tipo: Tipo de fila ('trimestre' o 'anual')
            constante_k: Constante K a usar para cálculos
            orden: Número de orden para sorting
            
        Returns:
            Dict: Diccionario con los datos de la fila
        """
        # Sumar valores acumulables
        total_lesiones = df_periodo['total_lesiones'].sum()
        total_horas = df_periodo['total_horas'].sum()
        dias_perdidos = df_periodo['dias_perdidos'].sum()
        num_trabajadores = df_periodo['num_trabajadores'].mean()  # Promedio
        acc_baja = df_periodo['acc_baja'].sum()
        acc_sin_baja = df_periodo['acc_sin_baja'].sum()
        enf_ocupacionales = df_periodo['enf_ocupacionales'].sum()
        
        # Calcular índices con la constante K correspondiente
        IF = self._safe_divide(total_lesiones * constante_k, total_horas)
        IG = self._safe_divide(dias_perdidos * constante_k, total_horas)
        TR = self._safe_divide(dias_perdidos, total_lesiones)
        
        return {
            'mes': nombre,
            'num_trabajadores': num_trabajadores,
            'horas_hombre_mes': total_horas,
            'horas_extras': df_periodo['horas_extras'].sum() if 'horas_extras' in df_periodo else 0,
            'acc_baja': acc_baja,
            'acc_sin_baja': acc_sin_baja,
            'enf_ocupacionales': enf_ocupacionales,
            'dias_perdidos': dias_perdidos,
            'total_lesiones': total_lesiones,
            'total_horas': total_horas,
            'IF': IF,
            'IG': IG,
            'TR': TR,
            'tipo_fila': tipo,
            'constante_k': constante_k,
            'mes_orden': orden,
        }
    
    @staticmethod
    def _safe_divide(numerador: float, denominador: float) -> float:
        """
        División segura que maneja división por cero.
        
        Args:
            numerador: Valor del numerador
            denominador: Valor del denominador
            
        Returns:
            float: Resultado de la división o 0 si hay error
        """
        try:
            if denominador == 0 or pd.isna(denominador):
                return 0.0
            resultado = numerador / denominador
            return 0.0 if pd.isna(resultado) or np.isinf(resultado) else resultado
        except (ZeroDivisionError, TypeError, ValueError):
            return 0.0
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas resumidas del análisis.
        
        Returns:
            Dict: Diccionario con estadísticas clave
        """
        if self.df_reporte is None:
            return {}
        
        df_meses = self.df_charts
        df_anual = self.df_reporte[self.df_reporte['tipo_fila'] == 'anual']
        
        stats = {
            'total_accidentes_baja': df_meses['acc_baja'].sum(),
            'total_accidentes_sin_baja': df_meses['acc_sin_baja'].sum(),
            'total_enfermedades': df_meses['enf_ocupacionales'].sum(),
            'total_lesiones_año': df_meses['total_lesiones'].sum(),
            'total_dias_perdidos': df_meses['dias_perdidos'].sum(),
            'total_horas_año': df_meses['total_horas'].sum(),
            'if_promedio_mensual': df_meses['IF'].mean(),
            'ig_promedio_mensual': df_meses['IG'].mean(),
            'tr_promedio': df_meses['TR'].mean(),
            'if_anual': df_anual['IF'].iloc[0] if len(df_anual) > 0 else 0,
            'ig_anual': df_anual['IG'].iloc[0] if len(df_anual) > 0 else 0,
            'meses_sin_accidentes': (df_meses['total_lesiones'] == 0).sum(),
        }
        
        return stats
    
    @staticmethod
    def generar_datos_demo(anio: int = 2025, semilla: int = None) -> pd.DataFrame:
        """
        Genera datos de demostración para pruebas.
        
        Args:
            anio: Año para los datos
            semilla: Semilla para reproducibilidad
            
        Returns:
            pd.DataFrame: DataFrame con datos de ejemplo
        """
        if semilla is not None:
            np.random.seed(semilla)
        
        meses = [
            'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
            'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'
        ]
        
        datos = []
        for mes in meses:
            trabajadores = np.random.randint(80, 120)
            horas_mes = trabajadores * 173.33
            
            datos.append({
                'Mes': mes,
                'Num_Trabajadores': trabajadores,
                'Horas_Hombre_Mes': round(horas_mes, 2),
                'Horas_Extras': np.random.randint(0, 500),
                'Acc_Baja': np.random.choice([0, 0, 0, 1, 1, 2], p=[0.4, 0.2, 0.15, 0.15, 0.07, 0.03]),
                'Acc_Sin_Baja': np.random.choice([0, 1, 2, 3], p=[0.5, 0.3, 0.15, 0.05]),
                'Enf_Ocupacionales': np.random.choice([0, 0, 1], p=[0.7, 0.2, 0.1]),
                'Dias_Perdidos': np.random.choice([0, 0, 2, 5, 10, 15], p=[0.4, 0.25, 0.15, 0.1, 0.07, 0.03]),
            })
        
        return pd.DataFrame(datos)
    
    def obtener_columnas_reporte(self) -> list:
        """
        Retorna las columnas para mostrar en el reporte.
        
        Returns:
            list: Lista de nombres de columnas para display
        """
        return [
            'mes', 'num_trabajadores', 'total_horas', 
            'acc_baja', 'acc_sin_baja', 'enf_ocupacionales',
            'total_lesiones', 'dias_perdidos', 
            'IF', 'IG', 'TR', 'constante_k'
        ]
    
    def obtener_nombres_columnas_display(self) -> Dict[str, str]:
        """
        Retorna mapeo de columnas a nombres para mostrar.
        
        Returns:
            Dict[str, str]: Diccionario de mapeo
        """
        return {
            'mes': 'Período',
            'num_trabajadores': 'Trabajadores',
            'total_horas': 'Total Horas',
            'acc_baja': 'Acc. c/Baja',
            'acc_sin_baja': 'Acc. s/Baja',
            'enf_ocupacionales': 'Enf. Ocup.',
            'total_lesiones': 'Total Lesiones',
            'dias_perdidos': 'Días Perdidos',
            'IF': 'Índ. Frecuencia',
            'IG': 'Índ. Gravedad',
            'TR': 'Tasa Riesgo',
            'constante_k': 'Constante K'
        }
