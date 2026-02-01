# -*- coding: utf-8 -*-
"""
Módulo de Validación de Datos SSO v2.0
Soporta validación diferenciada para datos Reactivos y Proactivos
"""

import pandas as pd
import numpy as np
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from enum import Enum


class TipoAnalisis(Enum):
    """Tipo de análisis a realizar"""
    REACTIVO = "reactivo"
    PROACTIVO = "proactivo"
    AMBOS = "ambos"


@dataclass
class ValidationError:
    """Representa un error de validación"""
    columna: str
    mensaje: str
    tipo: str  # 'error' | 'warning'
    fila: Optional[int] = None


@dataclass
class ValidationResult:
    """Resultado de la validación"""
    es_valido: bool
    errores: List[ValidationError] = field(default_factory=list)
    warnings: List[ValidationError] = field(default_factory=list)
    df_limpio: Optional[pd.DataFrame] = None
    resumen: Dict[str, Any] = field(default_factory=dict)
    
    def agregar_error(self, columna: str, mensaje: str, fila: Optional[int] = None):
        self.errores.append(ValidationError(columna, mensaje, 'error', fila))
        self.es_valido = False
    
    def agregar_warning(self, columna: str, mensaje: str, fila: Optional[int] = None):
        self.warnings.append(ValidationError(columna, mensaje, 'warning', fila))


class DataValidator:
    """
    Validador de datos para el Dashboard SSO v2.0
    Soporta validación diferenciada para datos Reactivos y Proactivos
    """
    
    # Columnas requeridas para análisis REACTIVO
    COLUMNAS_REACTIVO: Dict[str, str] = {
        'mes': 'Mes (texto o número)',
        'horas_trabajadas': 'Horas Hombre Trabajadas',
        'num_lesiones': 'Número de Lesiones/Accidentes',
        'dias_perdidos': 'Días Perdidos por Incapacidad'
    }
    
    # Columnas requeridas para análisis PROACTIVO
    COLUMNAS_PROACTIVO: Dict[str, str] = {
        'mes': 'Mes (texto o número)',
        'iart_real': 'IART - Análisis de Riesgos de Tareas (Real)',
        'iart_programado': 'IART - Análisis de Riesgos de Tareas (Programado)',
        'opas_real': 'OPAS - Observación Planeada de Acciones (Real)',
        'opas_programado': 'OPAS - Observación Planeada de Acciones (Programado)',
        'idps_real': 'IDPS - Diálogo Periódico de Seguridad (Real)',
        'idps_programado': 'IDPS - Diálogo Periódico de Seguridad (Programado)',
        'ids_real': 'IDS - Demanda de Seguridad (Real)',
        'ids_programado': 'IDS - Demanda de Seguridad (Programado)',
        'ients_real': 'IENTS - Entrenamiento de Seguridad (Real)',
        'ients_programado': 'IENTS - Entrenamiento de Seguridad (Programado)',
        'iosea_real': 'IOSEA - Órdenes de Servicios Estandarizados (Real)',
        'iosea_programado': 'IOSEA - Órdenes de Servicios Estandarizados (Programado)',
        'icai_real': 'ICAI - Control de Accidentes e Incidentes (Real)',
        'icai_programado': 'ICAI - Control de Accidentes e Incidentes (Programado)'
    }
    
    # Mapeo de nombres alternativos para columnas reactivas
    ALIAS_REACTIVO: Dict[str, List[str]] = {
        'mes': ['mes', 'month', 'periodo', 'fecha', 'meses'],
        'horas_trabajadas': ['horas_trabajadas', 'horas', 'horas_hombre', 'hh', 
                             'horas trabajadas', 'total_horas', 'h/h'],
        'num_lesiones': ['num_lesiones', 'lesiones', 'accidentes', 'num_accidentes',
                         'numero_lesiones', 'número de lesiones', 'n_lesiones'],
        'dias_perdidos': ['dias_perdidos', 'dias', 'días perdidos', 'días_perdidos',
                          'dias_incapacidad', 'jornadas_perdidas', 'd_perdidos']
    }
    
    # Mapeo de nombres alternativos para columnas proactivas
    ALIAS_PROACTIVO: Dict[str, List[str]] = {
        'mes': ['mes', 'month', 'periodo', 'fecha', 'meses'],
        'iart_real': ['iart_real', 'iart real', 'art_real', 'iart_r'],
        'iart_programado': ['iart_programado', 'iart programado', 'art_prog', 'iart_p'],
        'opas_real': ['opas_real', 'opas real', 'opas_r'],
        'opas_programado': ['opas_programado', 'opas programado', 'opas_p'],
        'idps_real': ['idps_real', 'idps real', 'dps_real', 'idps_r'],
        'idps_programado': ['idps_programado', 'idps programado', 'dps_prog', 'idps_p'],
        'ids_real': ['ids_real', 'ids real', 'ds_real', 'ids_r'],
        'ids_programado': ['ids_programado', 'ids programado', 'ds_prog', 'ids_p'],
        'ients_real': ['ients_real', 'ients real', 'ents_real', 'ients_r'],
        'ients_programado': ['ients_programado', 'ients programado', 'ents_prog', 'ients_p'],
        'iosea_real': ['iosea_real', 'iosea real', 'osea_real', 'iosea_r'],
        'iosea_programado': ['iosea_programado', 'iosea programado', 'osea_prog', 'iosea_p'],
        'icai_real': ['icai_real', 'icai real', 'cai_real', 'icai_r'],
        'icai_programado': ['icai_programado', 'icai programado', 'cai_prog', 'icai_p']
    }
    
    MESES_VALIDOS = [
        'enero', 'febrero', 'marzo', 'abril', 'mayo', 'junio',
        'julio', 'agosto', 'septiembre', 'octubre', 'noviembre', 'diciembre',
        'jan', 'feb', 'mar', 'apr', 'may', 'jun', 
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec'
    ]
    
    def __init__(self, tipo_analisis: TipoAnalisis = TipoAnalisis.REACTIVO):
        """
        Inicializa el validador
        
        Args:
            tipo_analisis: Tipo de análisis (REACTIVO, PROACTIVO, AMBOS)
        """
        self.tipo_analisis = tipo_analisis
    
    def validar(self, df: pd.DataFrame) -> ValidationResult:
        """
        Valida el DataFrame según el tipo de análisis configurado
        
        Args:
            df: DataFrame a validar
            
        Returns:
            ValidationResult con el resultado de la validación
        """
        resultado = ValidationResult(es_valido=True)
        
        if df is None or df.empty:
            resultado.agregar_error('general', 'El DataFrame está vacío o es nulo')
            return resultado
        
        # Normalizar nombres de columnas
        df_normalizado = self._normalizar_columnas(df.copy())
        
        # Validar según tipo
        if self.tipo_analisis == TipoAnalisis.REACTIVO:
            resultado = self._validar_reactivo(df_normalizado, resultado)
        elif self.tipo_analisis == TipoAnalisis.PROACTIVO:
            resultado = self._validar_proactivo(df_normalizado, resultado)
        else:  # AMBOS
            resultado = self._validar_reactivo(df_normalizado, resultado)
            if resultado.es_valido:
                resultado = self._validar_proactivo(df_normalizado, resultado)
        
        if resultado.es_valido:
            resultado.df_limpio = df_normalizado
            resultado.resumen = self._generar_resumen(df_normalizado)
        
        return resultado
    
    def _normalizar_columnas(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normaliza los nombres de las columnas"""
        # Convertir a minúsculas y limpiar espacios
        df.columns = df.columns.str.lower().str.strip().str.replace(' ', '_')
        
        # Seleccionar alias según tipo
        alias_map = {}
        if self.tipo_analisis in [TipoAnalisis.REACTIVO, TipoAnalisis.AMBOS]:
            alias_map.update(self.ALIAS_REACTIVO)
        if self.tipo_analisis in [TipoAnalisis.PROACTIVO, TipoAnalisis.AMBOS]:
            alias_map.update(self.ALIAS_PROACTIVO)
        
        # Mapear columnas usando alias
        rename_map = {}
        for col_std, aliases in alias_map.items():
            for alias in aliases:
                alias_norm = alias.lower().strip().replace(' ', '_')
                if alias_norm in df.columns and col_std not in df.columns:
                    rename_map[alias_norm] = col_std
                    break
        
        return df.rename(columns=rename_map)
    
    def _validar_reactivo(self, df: pd.DataFrame, resultado: ValidationResult) -> ValidationResult:
        """Valida datos para análisis reactivo"""
        # Verificar columnas requeridas
        columnas_faltantes = []
        for col_std in self.COLUMNAS_REACTIVO.keys():
            if col_std not in df.columns:
                columnas_faltantes.append(f"{col_std} ({self.COLUMNAS_REACTIVO[col_std]})")
        
        if columnas_faltantes:
            resultado.agregar_error(
                'columnas',
                f"Columnas faltantes para análisis REACTIVO: {', '.join(columnas_faltantes)}"
            )
            return resultado
        
        # Validar datos numéricos
        for col in ['horas_trabajadas', 'num_lesiones', 'dias_perdidos']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            nulos = df[col].isna().sum()
            if nulos > 0:
                resultado.agregar_warning(col, f"{nulos} valores no numéricos convertidos a NaN")
        
        # Validar valores negativos
        for col in ['horas_trabajadas', 'num_lesiones', 'dias_perdidos']:
            negativos = (df[col] < 0).sum()
            if negativos > 0:
                resultado.agregar_error(col, f"{negativos} valores negativos encontrados")
        
        # Validar horas trabajadas > 0
        ceros_horas = (df['horas_trabajadas'] == 0).sum()
        if ceros_horas > 0:
            resultado.agregar_warning('horas_trabajadas', f"{ceros_horas} meses con 0 horas trabajadas")
        
        return resultado
    
    def _validar_proactivo(self, df: pd.DataFrame, resultado: ValidationResult) -> ValidationResult:
        """Valida datos para análisis proactivo"""
        # Verificar columnas requeridas mínimas
        columnas_minimas = ['mes', 'iart_real', 'iart_programado']
        columnas_faltantes = [col for col in columnas_minimas if col not in df.columns]
        
        if columnas_faltantes:
            resultado.agregar_error(
                'columnas',
                f"Columnas mínimas faltantes para análisis PROACTIVO: {', '.join(columnas_faltantes)}"
            )
            return resultado
        
        # Validar que todos los pares real/programado existan
        indicadores = ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai']
        for ind in indicadores:
            col_real = f"{ind}_real"
            col_prog = f"{ind}_programado"
            
            if col_real in df.columns and col_prog not in df.columns:
                resultado.agregar_warning(col_prog, f"Falta columna programada para {ind.upper()}")
            elif col_prog in df.columns and col_real not in df.columns:
                resultado.agregar_warning(col_real, f"Falta columna real para {ind.upper()}")
            
            # Convertir a numérico si existe
            for col in [col_real, col_prog]:
                if col in df.columns:
                    df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
        
        return resultado
    
    def _generar_resumen(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Genera un resumen de los datos validados"""
        resumen = {
            'total_registros': len(df),
            'tipo_analisis': self.tipo_analisis.value
        }
        
        if self.tipo_analisis in [TipoAnalisis.REACTIVO, TipoAnalisis.AMBOS]:
            if 'horas_trabajadas' in df.columns:
                resumen['total_horas'] = df['horas_trabajadas'].sum()
            if 'num_lesiones' in df.columns:
                resumen['total_lesiones'] = df['num_lesiones'].sum()
            if 'dias_perdidos' in df.columns:
                resumen['total_dias_perdidos'] = df['dias_perdidos'].sum()
        
        return resumen
    
    @staticmethod
    def detectar_tipo_datos(df: pd.DataFrame) -> TipoAnalisis:
        """
        Detecta automáticamente el tipo de datos en el DataFrame
        
        Args:
            df: DataFrame a analizar
            
        Returns:
            TipoAnalisis detectado
        """
        cols_lower = [c.lower().strip().replace(' ', '_') for c in df.columns]
        
        tiene_reactivo = any(col in cols_lower for col in ['horas_trabajadas', 'horas', 'num_lesiones', 'lesiones'])
        tiene_proactivo = any(col in cols_lower for col in ['iart_real', 'iart_programado', 'opas_real'])
        
        if tiene_reactivo and tiene_proactivo:
            return TipoAnalisis.AMBOS
        elif tiene_proactivo:
            return TipoAnalisis.PROACTIVO
        else:
            return TipoAnalisis.REACTIVO
