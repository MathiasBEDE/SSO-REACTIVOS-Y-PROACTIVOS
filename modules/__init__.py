# -*- coding: utf-8 -*-
"""
PROYECTO SSO - Módulo Principal v2.0
Dashboard de Seguridad y Salud Ocupacional
Arquitectura separada: Motores Reactivo y Proactivo

Autor: Arquitecto de Software Senior
Normativa: IESS CD 513 Ecuador
"""

from .reactive_engine import ReactiveAnalyzer, ConstantesK
from .proactive_engine import ProactiveCalculator, IndicadorConfig
from .validator import DataValidator, TipoAnalisis, ValidationResult
from .visualizer import SSOVisualizer

__all__ = [
    # Motor Reactivo
    'ReactiveAnalyzer',
    'ConstantesK',
    # Motor Proactivo
    'ProactiveCalculator',
    'IndicadorConfig',
    # Validador
    'DataValidator',
    'TipoAnalisis',
    'ValidationResult',
    # Visualizador
    'SSOVisualizer',
]

__version__ = '2.0.0'
__author__ = 'Arquitecto de Software Senior'
