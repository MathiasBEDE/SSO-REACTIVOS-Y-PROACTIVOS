"""
Módulo de Cálculo de Indicadores SSO
Motor de cálculo de fórmulas según Normativa IESS CD 513

Este módulo implementa las 11 fórmulas de indicadores de Seguridad
y Salud Ocupacional requeridas por la normativa ecuatoriana.
"""

import pandas as pd
import numpy as np
from typing import Union


class SSOCalculator:
    """
    Calculadora de Indicadores de Seguridad y Salud Ocupacional.
    
    Implementa los 11 indicadores según la Normativa IESS CD 513:
    - IF: Índice de Frecuencia
    - IG: Índice de Gravedad
    - IART: Índice de Análisis de Riesgos de Tarea
    - OPAS: Observaciones Planeadas de Acciones Subestándar
    - IDPS: Índice de Diálogos Periódicos de Seguridad
    - IDS: Índice de Demanda de Seguridad
    - IENTS: Índice de Entrenamiento de Seguridad
    - IOSEA: Índice de Órdenes de Servicio Estandarizadas
    - ICAI: Índice de Control de Accidentes e Incidentes
    - IEF: Índice de Eficacia
    - IG_TOTAL: Índice de Gestión Total (Ponderado)
    
    Todos los métodos manejan división por cero retornando 0.
    """
    
    # Constante para cálculos de frecuencia y gravedad
    FACTOR_HHT = 200_000
    
    # Pesos para el índice ponderado IG_TOTAL
    PESOS = {
        'IART': 5,
        'OPAS': 3,
        'IDPS': 2,
        'IDS': 3,
        'IENTS': 1,
        'IOSEA': 4,
        'ICAI': 4
    }
    SUMA_PESOS = sum(PESOS.values())  # 22
    
    @staticmethod
    def _safe_divide(numerador: float, denominador: float) -> float:
        """
        Realiza una división segura manejando división por cero.
        
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
    
    @classmethod
    def calcular_if(cls, accidentes: float, horas_trabajadas: float) -> float:
        """
        Calcula el Índice de Frecuencia (IF).
        
        Fórmula: IF = (Accidentes * 200,000) / Horas_Trabajadas
        
        Mide la cantidad de accidentes por cada 200,000 horas trabajadas,
        equivalente aproximadamente a 100 trabajadores durante un año.
        
        Args:
            accidentes: Número de accidentes en el período
            horas_trabajadas: Total de horas hombre trabajadas
            
        Returns:
            float: Índice de frecuencia calculado
        """
        numerador = accidentes * cls.FACTOR_HHT
        return cls._safe_divide(numerador, horas_trabajadas)
    
    @classmethod
    def calcular_ig(cls, dias_perdidos: float, horas_trabajadas: float) -> float:
        """
        Calcula el Índice de Gravedad (IG).
        
        Fórmula: IG = (Días_Perdidos * 200,000) / Horas_Trabajadas
        
        Mide la severidad de los accidentes en términos de días perdidos
        por cada 200,000 horas trabajadas.
        
        Args:
            dias_perdidos: Total de días perdidos por accidentes
            horas_trabajadas: Total de horas hombre trabajadas
            
        Returns:
            float: Índice de gravedad calculado
        """
        numerador = dias_perdidos * cls.FACTOR_HHT
        return cls._safe_divide(numerador, horas_trabajadas)
    
    @classmethod
    def calcular_iart(cls, ejecutadas: float, programadas: float) -> float:
        """
        Calcula el Índice de Análisis de Riesgos de Tarea (IART).
        
        Fórmula: IART = (Ejecutadas / Programadas) * 100
        
        Mide el cumplimiento de los análisis de riesgos de tarea
        planificados versus ejecutados.
        
        Args:
            ejecutadas: Número de análisis ejecutados
            programadas: Número de análisis programados
            
        Returns:
            float: Porcentaje de cumplimiento IART
        """
        return cls._safe_divide(ejecutadas, programadas) * 100
    
    @classmethod
    def calcular_opas(cls, realizadas: float, personas_conformes: float,
                      programadas: float, personas_previstas: float) -> float:
        """
        Calcula el Índice de Observaciones Planeadas de Acciones Subestándar (OPAS).
        
        Fórmula: OPAS = ((Realizadas * Personas_Conformes) / 
                         (Programadas * Personas_Previstas)) * 100
        
        Mide la efectividad del programa de observaciones planeadas
        considerando tanto cantidad como calidad de participación.
        
        Args:
            realizadas: Observaciones realizadas
            personas_conformes: Personas que actuaron de forma conforme
            programadas: Observaciones programadas
            personas_previstas: Personas previstas a observar
            
        Returns:
            float: Porcentaje de cumplimiento OPAS
        """
        numerador = realizadas * personas_conformes
        denominador = programadas * personas_previstas
        return cls._safe_divide(numerador, denominador) * 100
    
    @classmethod
    def calcular_idps(cls, realizadas: float, asistentes: float,
                      planeadas: float, previstos: float) -> float:
        """
        Calcula el Índice de Diálogos Periódicos de Seguridad (IDPS).
        
        Fórmula: IDPS = ((Realizadas * Asistentes) / 
                         (Planeadas * Previstos)) * 100
        
        Mide el cumplimiento y participación en los diálogos
        periódicos de seguridad.
        
        Args:
            realizadas: Diálogos realizados
            asistentes: Número de asistentes reales
            planeadas: Diálogos planeados
            previstos: Asistentes previstos
            
        Returns:
            float: Porcentaje de cumplimiento IDPS
        """
        numerador = realizadas * asistentes
        denominador = planeadas * previstos
        return cls._safe_divide(numerador, denominador) * 100
    
    @classmethod
    def calcular_ids(cls, eliminadas: float, detectadas: float) -> float:
        """
        Calcula el Índice de Demanda de Seguridad (IDS).
        
        Fórmula: IDS = (Eliminadas / Detectadas) * 100
        
        Mide la capacidad de respuesta ante condiciones
        o actos subestándar detectados.
        
        Args:
            eliminadas: Demandas de seguridad eliminadas/resueltas
            detectadas: Demandas de seguridad detectadas
            
        Returns:
            float: Porcentaje de cumplimiento IDS
        """
        return cls._safe_divide(eliminadas, detectadas) * 100
    
    @classmethod
    def calcular_ients(cls, entrenados: float, programados: float) -> float:
        """
        Calcula el Índice de Entrenamiento de Seguridad (IENTS).
        
        Fórmula: IENTS = (Entrenados / Programados) * 100
        
        Mide el cumplimiento del programa de capacitación
        y entrenamiento en seguridad.
        
        Args:
            entrenados: Personal efectivamente entrenado
            programados: Personal programado para entrenamiento
            
        Returns:
            float: Porcentaje de cumplimiento IENTS
        """
        return cls._safe_divide(entrenados, programados) * 100
    
    @classmethod
    def calcular_iosea(cls, cumplidos: float, aplicables: float) -> float:
        """
        Calcula el Índice de Órdenes de Servicio Estandarizadas y Auditadas (IOSEA).
        
        Fórmula: IOSEA = (Cumplidos / Aplicables) * 100
        
        Mide el cumplimiento de las órdenes de servicio
        estandarizadas aplicables.
        
        Args:
            cumplidos: Estándares cumplidos
            aplicables: Estándares aplicables
            
        Returns:
            float: Porcentaje de cumplimiento IOSEA
        """
        return cls._safe_divide(cumplidos, aplicables) * 100
    
    @classmethod
    def calcular_icai(cls, implementadas: float, propuestas: float) -> float:
        """
        Calcula el Índice de Control de Accidentes e Incidentes (ICAI).
        
        Fórmula: ICAI = (Implementadas / Propuestas) * 100
        
        Mide la implementación de medidas correctivas
        derivadas de la investigación de accidentes/incidentes.
        
        Args:
            implementadas: Medidas correctivas implementadas
            propuestas: Medidas correctivas propuestas
            
        Returns:
            float: Porcentaje de cumplimiento ICAI
        """
        return cls._safe_divide(implementadas, propuestas) * 100
    
    @classmethod
    def calcular_ief(cls, auditados: float, totales: float) -> float:
        """
        Calcula el Índice de Eficacia (IEF).
        
        Fórmula: IEF = (Auditados / Totales) * 100
        
        Mide la eficacia del sistema de gestión mediante
        auditorías internas.
        
        Args:
            auditados: Elementos auditados conformes
            totales: Total de elementos a auditar
            
        Returns:
            float: Porcentaje de eficacia
        """
        return cls._safe_divide(auditados, totales) * 100
    
    @classmethod
    def calcular_ig_total(cls, iart: float, opas: float, idps: float,
                          ids: float, ients: float, iosea: float, 
                          icai: float) -> float:
        """
        Calcula el Índice de Gestión Total Ponderado (IG_TOTAL).
        
        Fórmula: IG_TOTAL = (5*IART + 3*OPAS + 2*IDPS + 3*IDS + 
                            1*IENTS + 4*IOSEA + 4*ICAI) / 22
        
        Es el indicador global que pondera todos los índices proactivos
        según su importancia relativa en el sistema de gestión.
        
        Args:
            iart: Índice IART calculado
            opas: Índice OPAS calculado
            idps: Índice IDPS calculado
            ids: Índice IDS calculado
            ients: Índice IENTS calculado
            iosea: Índice IOSEA calculado
            icai: Índice ICAI calculado
            
        Returns:
            float: Índice de gestión total ponderado
        """
        try:
            ponderado = (
                cls.PESOS['IART'] * iart +
                cls.PESOS['OPAS'] * opas +
                cls.PESOS['IDPS'] * idps +
                cls.PESOS['IDS'] * ids +
                cls.PESOS['IENTS'] * ients +
                cls.PESOS['IOSEA'] * iosea +
                cls.PESOS['ICAI'] * icai
            )
            return ponderado / cls.SUMA_PESOS
        except (TypeError, ValueError):
            return 0.0
    
    @classmethod
    def procesar_dataframe(cls, df: pd.DataFrame) -> pd.DataFrame:
        """
        Procesa un DataFrame completo calculando todos los indicadores.
        
        Añade columnas calculadas para cada uno de los 11 indicadores
        y una columna de estado de cumplimiento.
        
        Args:
            df: DataFrame con los datos crudos de entrada
            
        Returns:
            pd.DataFrame: DataFrame con todas las columnas calculadas
        """
        df = df.copy()
        
        # Calcular IF e IG (indicadores reactivos)
        df['IF'] = df.apply(
            lambda row: cls.calcular_if(
                row.get('accidentes', 0),
                row.get('horas_trabajadas', 0)
            ), axis=1
        )
        
        df['IG'] = df.apply(
            lambda row: cls.calcular_ig(
                row.get('dias_perdidos', 0),
                row.get('horas_trabajadas', 0)
            ), axis=1
        )
        
        # Calcular IART
        df['IART'] = df.apply(
            lambda row: cls.calcular_iart(
                row.get('nart_ejec', 0),
                row.get('nart_prog', 0)
            ), axis=1
        )
        
        # Calcular OPAS
        df['OPAS'] = df.apply(
            lambda row: cls.calcular_opas(
                row.get('opas_real', 0),
                row.get('opas_personas_conf', 0),
                row.get('opas_prog', 0),
                row.get('opas_personas_prev', 0)
            ), axis=1
        )
        
        # Calcular IDPS
        df['IDPS'] = df.apply(
            lambda row: cls.calcular_idps(
                row.get('dps_real', 0),
                row.get('dps_asistentes', 0),
                row.get('dps_plan', 0),
                row.get('dps_previstos', 0)
            ), axis=1
        )
        
        # Calcular IDS
        df['IDS'] = df.apply(
            lambda row: cls.calcular_ids(
                row.get('ds_eliminadas', 0),
                row.get('ds_detectadas', 0)
            ), axis=1
        )
        
        # Calcular IENTS
        df['IENTS'] = df.apply(
            lambda row: cls.calcular_ients(
                row.get('ent_entrenados', 0),
                row.get('ent_programados', 0)
            ), axis=1
        )
        
        # Calcular IOSEA
        df['IOSEA'] = df.apply(
            lambda row: cls.calcular_iosea(
                row.get('osea_cumplidos', 0),
                row.get('osea_aplicables', 0)
            ), axis=1
        )
        
        # Calcular ICAI
        df['ICAI'] = df.apply(
            lambda row: cls.calcular_icai(
                row.get('cai_implement', 0),
                row.get('cai_propuestas', 0)
            ), axis=1
        )
        
        # Calcular IEF
        df['IEF'] = df.apply(
            lambda row: cls.calcular_ief(
                row.get('ef_auditados', 0),
                row.get('ef_totales', 0)
            ), axis=1
        )
        
        # Calcular IG_TOTAL
        df['IG_TOTAL'] = df.apply(
            lambda row: cls.calcular_ig_total(
                row['IART'], row['OPAS'], row['IDPS'],
                row['IDS'], row['IENTS'], row['IOSEA'], row['ICAI']
            ), axis=1
        )
        
        return df
    
    @staticmethod
    def evaluar_cumplimiento(valor: float, meta: float = 80.0) -> str:
        """
        Evalúa si un indicador cumple con la meta establecida.
        
        Args:
            valor: Valor del indicador
            meta: Meta mínima de cumplimiento (default 80%)
            
        Returns:
            str: 'CUMPLE' o 'NO CUMPLE'
        """
        return 'CUMPLE' if valor >= meta else 'NO CUMPLE'
    
    @classmethod
    def agregar_estado_cumplimiento(cls, df: pd.DataFrame, 
                                     meta: float = 80.0) -> pd.DataFrame:
        """
        Agrega columna de estado de cumplimiento basado en IG_TOTAL.
        
        Args:
            df: DataFrame con indicadores calculados
            meta: Meta de cumplimiento (default 80%)
            
        Returns:
            pd.DataFrame: DataFrame con columna 'Estado' añadida
        """
        df = df.copy()
        df['Estado'] = df['IG_TOTAL'].apply(
            lambda x: cls.evaluar_cumplimiento(x, meta)
        )
        return df
