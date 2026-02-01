"""
Motor de Cálculo de Indicadores Proactivos SSO
Fórmulas estándar según Normativa IESS CD 513

Este módulo implementa el cálculo de indicadores proactivos
con fórmulas de numerador/denominador * 100.
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional, List
from dataclasses import dataclass


@dataclass 
class IndicadorConfig:
    """Configuración de un indicador proactivo."""
    codigo: str
    nombre: str
    descripcion: str
    col_numerador: str
    col_denominador: str
    peso: int = 0  # Peso para IG_TOTAL


class ProactiveCalculator:
    """
    Calculadora de Indicadores Proactivos SSO.
    
    Implementa los indicadores proactivos según la Normativa IESS CD 513:
    - IART: Índice de Análisis de Riesgos de Tarea
    - OPAS: Observaciones Planeadas de Acciones Subestándar
    - IDPS: Índice de Diálogos Periódicos de Seguridad
    - IDS: Índice de Demanda de Seguridad
    - IENTS: Índice de Entrenamiento de Seguridad
    - IOSEA: Índice de Órdenes de Servicio Estandarizadas
    - ICAI: Índice de Control de Accidentes e Incidentes
    - IEF: Índice de Eficacia
    - IG_TOTAL: Índice de Gestión Total (Ponderado)
    
    Attributes:
        META_DEFAULT: Meta por defecto (80%)
        INDICADORES: Configuración de cada indicador
    """
    
    META_DEFAULT = 80.0
    
    # Configuración de indicadores
    INDICADORES = {
        'IART': IndicadorConfig(
            codigo='IART',
            nombre='Análisis de Riesgos de Tarea',
            descripcion='Cumplimiento de análisis de riesgos programados',
            col_numerador='nart_ejec',
            col_denominador='nart_prog',
            peso=5
        ),
        'OPAS': IndicadorConfig(
            codigo='OPAS',
            nombre='Observaciones Planeadas',
            descripcion='Efectividad del programa de observaciones',
            col_numerador='opas_efectivo',  # Calculado
            col_denominador='opas_programado',  # Calculado
            peso=3
        ),
        'IDPS': IndicadorConfig(
            codigo='IDPS',
            nombre='Diálogos de Seguridad',
            descripcion='Cumplimiento de diálogos periódicos',
            col_numerador='dps_efectivo',  # Calculado
            col_denominador='dps_programado',  # Calculado
            peso=2
        ),
        'IDS': IndicadorConfig(
            codigo='IDS',
            nombre='Demanda de Seguridad',
            descripcion='Resolución de condiciones subestándar',
            col_numerador='ds_eliminadas',
            col_denominador='ds_detectadas',
            peso=3
        ),
        'IENTS': IndicadorConfig(
            codigo='IENTS',
            nombre='Entrenamiento de Seguridad',
            descripcion='Cumplimiento de capacitaciones',
            col_numerador='ent_entrenados',
            col_denominador='ent_programados',
            peso=1
        ),
        'IOSEA': IndicadorConfig(
            codigo='IOSEA',
            nombre='Órdenes de Servicio',
            descripcion='Cumplimiento de estándares',
            col_numerador='osea_cumplidos',
            col_denominador='osea_aplicables',
            peso=4
        ),
        'ICAI': IndicadorConfig(
            codigo='ICAI',
            nombre='Control de Accidentes/Incidentes',
            descripcion='Implementación de medidas correctivas',
            col_numerador='cai_implement',
            col_denominador='cai_propuestas',
            peso=4
        ),
        'IEF': IndicadorConfig(
            codigo='IEF',
            nombre='Índice de Eficacia',
            descripcion='Eficacia de auditorías internas',
            col_numerador='ef_auditados',
            col_denominador='ef_totales',
            peso=0  # No entra en ponderación
        ),
    }
    
    # Columnas requeridas del input
    COLUMNAS_REQUERIDAS = [
        'mes',
        # IART
        'nart_prog', 'nart_ejec',
        # OPAS
        'opas_prog', 'opas_real', 'opas_personas_prev', 'opas_personas_conf',
        # IDPS
        'dps_plan', 'dps_real', 'dps_previstos', 'dps_asistentes',
        # IDS
        'ds_detectadas', 'ds_eliminadas',
        # IENTS
        'ent_programados', 'ent_entrenados',
        # IOSEA
        'osea_aplicables', 'osea_cumplidos',
        # ICAI
        'cai_propuestas', 'cai_implement',
        # IEF
        'ef_totales', 'ef_auditados',
    ]
    
    # Meses en orden
    MESES_ORDEN = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre'
    ]
    
    def __init__(self, meta: float = None):
        """
        Inicializa la calculadora proactiva.
        
        Args:
            meta: Meta de cumplimiento (default 80%)
        """
        self.meta = meta or self.META_DEFAULT
        self.df_resultado = None
    
    def procesar(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa el DataFrame y calcula todos los indicadores.
        
        Args:
            df: DataFrame con datos mensuales
            
        Returns:
            pd.DataFrame: DataFrame con indicadores calculados
        """
        # Normalizar columnas
        df = df.copy()
        df.columns = [col.lower().strip().replace(' ', '_') for col in df.columns]
        
        # Validar columnas
        self._validar_columnas(df)
        
        # Preparar datos
        df = self._preparar_datos(df)
        
        # Calcular columnas intermedias para OPAS e IDPS
        df = self._calcular_columnas_compuestas(df)
        
        # Calcular cada indicador
        for codigo, config in self.INDICADORES.items():
            df[codigo] = df.apply(
                lambda row: self._calcular_indicador(
                    row.get(config.col_numerador, 0),
                    row.get(config.col_denominador, 0)
                ),
                axis=1
            )
        
        # Calcular IG_TOTAL (ponderado)
        df['IG_TOTAL'] = df.apply(self._calcular_ig_total, axis=1)
        
        # Agregar columna de meta
        df['Meta'] = self.meta
        
        # Agregar estado de cumplimiento
        df['Estado'] = df['IG_TOTAL'].apply(
            lambda x: 'CUMPLE' if x >= self.meta else 'NO CUMPLE'
        )
        
        self.df_resultado = df
        return df
    
    def _validar_columnas(self, df: pd.DataFrame) -> None:
        """
        Valida que existan las columnas requeridas.
        
        Args:
            df: DataFrame a validar
            
        Raises:
            ValueError: Si faltan columnas requeridas
        """
        columnas_df = set(df.columns)
        faltantes = [col for col in self.COLUMNAS_REQUERIDAS if col not in columnas_df]
        
        if faltantes:
            raise ValueError(
                f"Columnas requeridas faltantes: {', '.join(faltantes)}"
            )
    
    def _preparar_datos(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Prepara los datos convirtiendo tipos y ordenando.
        
        Args:
            df: DataFrame a preparar
            
        Returns:
            pd.DataFrame: DataFrame preparado
        """
        df = df.copy()
        
        # Convertir a numérico todas las columnas excepto 'mes'
        for col in df.columns:
            if col != 'mes':
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        # Normalizar mes
        df['mes'] = df['mes'].str.lower().str.strip()
        
        # Ordenar por mes
        df['mes_orden'] = df['mes'].apply(
            lambda x: self.MESES_ORDEN.index(x) if x in self.MESES_ORDEN else 99
        )
        df = df.sort_values('mes_orden').reset_index(drop=True)
        
        return df
    
    def _calcular_columnas_compuestas(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula columnas compuestas para OPAS e IDPS.
        
        OPAS = (Realizadas * Personas_Conformes) / (Programadas * Personas_Previstas)
        IDPS = (Realizadas * Asistentes) / (Planeadas * Previstos)
        
        Args:
            df: DataFrame con datos base
            
        Returns:
            pd.DataFrame: DataFrame con columnas compuestas
        """
        df = df.copy()
        
        # OPAS: numerador y denominador compuestos
        df['opas_efectivo'] = df['opas_real'] * df['opas_personas_conf']
        df['opas_programado'] = df['opas_prog'] * df['opas_personas_prev']
        
        # IDPS: numerador y denominador compuestos
        df['dps_efectivo'] = df['dps_real'] * df['dps_asistentes']
        df['dps_programado'] = df['dps_plan'] * df['dps_previstos']
        
        return df
    
    def _calcular_indicador(self, numerador: float, denominador: float) -> float:
        """
        Calcula un indicador porcentual.
        
        Fórmula: (Numerador / Denominador) * 100
        
        Args:
            numerador: Valor del numerador
            denominador: Valor del denominador
            
        Returns:
            float: Porcentaje calculado (0-100+)
        """
        try:
            if denominador == 0 or pd.isna(denominador):
                return 0.0
            resultado = (numerador / denominador) * 100
            return 0.0 if pd.isna(resultado) or np.isinf(resultado) else min(resultado, 100.0)
        except (ZeroDivisionError, TypeError, ValueError):
            return 0.0
    
    def _calcular_ig_total(self, row: pd.Series) -> float:
        """
        Calcula el Índice de Gestión Total ponderado.
        
        Fórmula: (5*IART + 3*OPAS + 2*IDPS + 3*IDS + 1*IENTS + 4*IOSEA + 4*ICAI) / 22
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            float: IG_TOTAL calculado
        """
        try:
            suma_ponderada = 0
            suma_pesos = 0
            
            for codigo, config in self.INDICADORES.items():
                if config.peso > 0:
                    suma_ponderada += config.peso * row.get(codigo, 0)
                    suma_pesos += config.peso
            
            if suma_pesos == 0:
                return 0.0
            
            return suma_ponderada / suma_pesos
            
        except (TypeError, ValueError):
            return 0.0
    
    def obtener_estadisticas(self) -> Dict:
        """
        Obtiene estadísticas resumidas de los indicadores.
        
        Returns:
            Dict: Diccionario con estadísticas
        """
        if self.df_resultado is None:
            return {}
        
        df = self.df_resultado
        stats = {
            'meta': self.meta,
            'meses_cumplen': (df['IG_TOTAL'] >= self.meta).sum(),
            'meses_no_cumplen': (df['IG_TOTAL'] < self.meta).sum(),
            'ig_total_promedio': df['IG_TOTAL'].mean(),
            'indicadores': {}
        }
        
        for codigo in self.INDICADORES.keys():
            if codigo in df.columns:
                stats['indicadores'][codigo] = {
                    'promedio': df[codigo].mean(),
                    'minimo': df[codigo].min(),
                    'maximo': df[codigo].max(),
                    'cumple_meta': (df[codigo] >= self.meta).sum(),
                }
        
        return stats
    
    def obtener_lista_indicadores(self) -> List[tuple]:
        """
        Retorna lista de indicadores para selectbox.
        
        Returns:
            List[tuple]: Lista de (codigo, nombre_completo)
        """
        lista = []
        for codigo, config in self.INDICADORES.items():
            lista.append((codigo, f"{config.nombre} ({codigo})"))
        lista.append(('IG_TOTAL', 'Índice de Gestión Total (IG_TOTAL)'))
        return lista
    
    def obtener_config_indicador(self, codigo: str) -> Optional[IndicadorConfig]:
        """
        Obtiene la configuración de un indicador.
        
        Args:
            codigo: Código del indicador
            
        Returns:
            Optional[IndicadorConfig]: Configuración o None
        """
        return self.INDICADORES.get(codigo)
    
    @staticmethod
    def generar_datos_demo(anio: int = 2025, semilla: int = None) -> pd.DataFrame:
        """
        Genera datos de demostración para indicadores proactivos.
        
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
            # IART
            nart_prog = np.random.randint(8, 15)
            nart_ejec = int(nart_prog * np.random.uniform(0.7, 1.0))
            
            # OPAS
            opas_prog = np.random.randint(10, 20)
            opas_real = int(opas_prog * np.random.uniform(0.7, 1.0))
            opas_prev = np.random.randint(30, 50)
            opas_conf = int(opas_prev * np.random.uniform(0.75, 0.95))
            
            # IDPS
            dps_plan = np.random.randint(4, 8)
            dps_real = int(dps_plan * np.random.uniform(0.75, 1.0))
            dps_prev = np.random.randint(20, 40)
            dps_asist = int(dps_prev * np.random.uniform(0.8, 1.0))
            
            # IDS
            ds_det = np.random.randint(5, 15)
            ds_elim = int(ds_det * np.random.uniform(0.7, 0.95))
            
            # IENTS
            ent_prog = np.random.randint(15, 30)
            ent_entr = int(ent_prog * np.random.uniform(0.75, 1.0))
            
            # IOSEA
            osea_apl = np.random.randint(10, 20)
            osea_cum = int(osea_apl * np.random.uniform(0.75, 0.98))
            
            # ICAI
            cai_prop = np.random.randint(3, 8)
            cai_impl = int(cai_prop * np.random.uniform(0.7, 1.0))
            
            # IEF
            ef_tot = np.random.randint(15, 25)
            ef_aud = int(ef_tot * np.random.uniform(0.75, 0.95))
            
            datos.append({
                'mes': mes,
                'anio': anio,
                'nart_prog': max(nart_prog, 1),
                'nart_ejec': nart_ejec,
                'opas_prog': max(opas_prog, 1),
                'opas_real': opas_real,
                'opas_personas_prev': max(opas_prev, 1),
                'opas_personas_conf': opas_conf,
                'dps_plan': max(dps_plan, 1),
                'dps_real': dps_real,
                'dps_previstos': max(dps_prev, 1),
                'dps_asistentes': dps_asist,
                'ds_detectadas': max(ds_det, 1),
                'ds_eliminadas': ds_elim,
                'ent_programados': max(ent_prog, 1),
                'ent_entrenados': ent_entr,
                'osea_aplicables': max(osea_apl, 1),
                'osea_cumplidos': osea_cum,
                'cai_propuestas': max(cai_prop, 1),
                'cai_implement': cai_impl,
                'ef_totales': max(ef_tot, 1),
                'ef_auditados': ef_aud,
            })
        
        return pd.DataFrame(datos)
