# -*- coding: utf-8 -*-
"""
Módulo de Visualización SSO v2.0
Métodos separados para dashboards Reactivo y Proactivo

Características:
- render_reactive_dashboard(): Tabla con filas de resumen trimestral + gráficos de línea
- render_proactive_dashboard(): Gráfico combo con barras de cumplimiento y línea de meta
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from typing import Optional, Dict, List, Tuple, Any


class SSOVisualizer:
    """
    Visualizador de Dashboard SSO v2.0
    Renderiza dashboards separados para indicadores Reactivos y Proactivos
    """
    
    # Paleta de colores corporativa
    COLORES = {
        'primario': '#1f77b4',
        'secundario': '#ff7f0e',
        'exito': '#2ecc71',
        'peligro': '#e74c3c',
        'warning': '#f39c12',
        'info': '#3498db',
        'gris': '#95a5a6',
        'oscuro': '#2c3e50',
        'claro': '#ecf0f1',
        # Colores para indicadores reactivos
        'if_color': '#e74c3c',      # Rojo - Índice de Frecuencia
        'ig_color': '#f39c12',      # Naranja - Índice de Gravedad
        'tr_color': '#9b59b6',      # Púrpura - Tasa de Riesgo
        # Colores para trimestres
        'trimestre_bg': '#d5d5d5',  # Gris claro para filas trimestre
        'anual_bg': '#a0a0a0',      # Gris medio para fila anual
    }
    
    # Nombres de meses en español
    MESES_ES = {
        1: 'Enero', 2: 'Febrero', 3: 'Marzo', 4: 'Abril',
        5: 'Mayo', 6: 'Junio', 7: 'Julio', 8: 'Agosto',
        9: 'Septiembre', 10: 'Octubre', 11: 'Noviembre', 12: 'Diciembre'
    }
    
    def __init__(self):
        """Inicializa el visualizador"""
        self._configurar_plotly()
    
    def _configurar_plotly(self):
        """Configura opciones globales de Plotly"""
        self.layout_base = dict(
            font=dict(family="Inter, Segoe UI, Arial, sans-serif", size=12),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(248,249,250,1)',
            margin=dict(l=60, r=40, t=60, b=60),
            hovermode='x unified'
        )
    
    def _badge_html(self, text: str, type: str = 'neutral', icon: str = None) -> str:
        """Helper local para badges HTML"""
        icon_html = f'<iconify-icon icon="{icon}"></iconify-icon>' if icon else ''
        return f'<span class="sso-badge badge-{type}">{icon_html} {text}</span>'

    # =========================================================================
    # DASHBOARD REACTIVO
    # =========================================================================
    
    def render_reactive_dashboard(
        self,
        df_reporte: pd.DataFrame,
        df_charts: pd.DataFrame,
        titulo: str = "Dashboard de Indicadores Reactivos",
        mostrar_tabla: bool = True,
        mostrar_graficos: bool = True
    ) -> None:
        """Renderiza el dashboard de indicadores reactivos"""
        st.markdown(f"## {titulo}", unsafe_allow_html=True)
        st.markdown("---")
        
        if mostrar_tabla:
            self._render_tabla_reactiva(df_reporte)
        
        if mostrar_graficos:
            st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:trending-up'></iconify-icon> Evolución</div>", unsafe_allow_html=True)
            self._render_graficos_reactivos(df_charts)
    
    def _render_tabla_reactiva(self, df: pd.DataFrame) -> None:
        """Renderiza la tabla de indicadores reactivos con estilos"""
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:table'></iconify-icon> Detalle de Datos</div>", unsafe_allow_html=True)
        
        # Preparar DataFrame para mostrar
        df_display = df.copy()
        
        # Redondear valores numéricos
        cols_numericas = ['total_horas', 'total_lesiones', 'dias_perdidos', 
                         'IF', 'IG', 'TR']
        for col in cols_numericas:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: f"{x:,.2f}" if pd.notna(x) and x != 0 else "-"
                )
        
        # Renombrar columnas para mejor presentación
        rename_cols = {
            'mes': 'Período',
            'total_horas': 'Horas H/H',
            'total_lesiones': 'Lesiones',
            'dias_perdidos': 'Días Perdidos',
            'IF': 'Índ. Frecuencia',
            'IG': 'Índ. Gravedad',
            'TR': 'Tasa Riesgo'
        }
        df_display = df_display.rename(columns=rename_cols)
        
        # Identificar filas especiales (trimestres y total)
        # Aplicar estilos con Pandas Styler
        def highlight_rows(row):
            periodo = row['Período'] if 'Período' in row.index else ''
            if 'TOTAL' in str(periodo).upper():
                return ['background-color: #a0a0a0; font-weight: bold; color: white'] * len(row)
            elif 'TRIMESTRE' in str(periodo).upper():
                return ['background-color: #d5d5d5; font-weight: bold'] * len(row)
            return [''] * len(row)
        
        styled_df = df_display.style.apply(highlight_rows, axis=1)
        styled_df = styled_df.set_properties(**{
            'text-align': 'center',
            'border': '1px solid #ddd'
        })
        
        # Mostrar tabla
        st.dataframe(
            styled_df,
            use_container_width=True,
            hide_index=True,
            height=min(600, 50 + len(df_display) * 35)
        )
        
        # Leyenda
        st.markdown("""
        <div style="display: flex; gap: 15px; font-size: 0.9rem; color: #555; margin-top: 10px;">
            <span><strong style="color: #e74c3c">IF</strong>: Índice de Frecuencia</span>
            <span><strong style="color: #f39c12">IG</strong>: Índice de Gravedad</span>
            <span><strong style="color: #9b59b6">TR</strong>: Tasa de Riesgo</span>
        </div>
        """, unsafe_allow_html=True)
    
    def _render_graficos_reactivos(self, df: pd.DataFrame) -> None:
        """Renderiza los gráficos de línea para indicadores reactivos"""
        if df.empty or 'mes' not in df.columns:
            st.warning("No hay datos suficientes para generar gráficos")
            return
        
        # Crear tres columnas para los gráficos
        col1, col2, col3 = st.columns(3)
        
        with col1:
            fig_if = self._crear_grafico_linea(
                df=df, columna='IF', titulo='Índice de Frecuencia (IF)',
                color=self.COLORES['if_color'], formato_hover='.2f'
            )
            st.plotly_chart(fig_if, use_container_width=True)
        
        with col2:
            fig_ig = self._crear_grafico_linea(
                df=df, columna='IG', titulo='Índice de Gravedad (IG)',
                color=self.COLORES['ig_color'], formato_hover='.2f'
            )
            st.plotly_chart(fig_ig, use_container_width=True)
        
        with col3:
            fig_tr = self._crear_grafico_linea(
                df=df, columna='TR', titulo='Tasa de Riesgo (TR)',
                color=self.COLORES['tr_color'], formato_hover='.2f'
            )
            st.plotly_chart(fig_tr, use_container_width=True)
        
        # Gráfico combinado grande
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:bar-chart-2'></iconify-icon> Comparativa Reactiva</div>", unsafe_allow_html=True)
        fig_combo = self._crear_grafico_reactivo_combinado(df)
        st.plotly_chart(fig_combo, use_container_width=True)
    
    def _crear_grafico_linea(
        self, df: pd.DataFrame, columna: str, titulo: str, color: str, formato_hover: str = '.2f'
    ) -> go.Figure:
        """Crea un gráfico de línea individual"""
        fig = go.Figure()
        
        if columna not in df.columns:
            return fig
        
        fig.add_trace(go.Scatter(
            x=df['mes'], y=df[columna], mode='lines+markers', name=titulo,
            line=dict(color=color, width=3), marker=dict(size=10, color=color),
            hovertemplate=f'%{{x}}<br>{titulo}: %{{y:{formato_hover}}}<extra></extra>'
        ))
        
        fig.update_layout(
            **self.layout_base,
            title=dict(text=titulo, x=0.5, font=dict(size=14)),
            xaxis=dict(title='', tickangle=-45),
            yaxis=dict(title='', gridcolor='rgba(0,0,0,0.1)'),
            showlegend=False, height=300
        )
        return fig
    
    def _crear_grafico_reactivo_combinado(self, df: pd.DataFrame) -> go.Figure:
        """Crea un gráfico combinado con todos los indicadores reactivos"""
        fig = make_subplots(rows=1, cols=1, specs=[[{"secondary_y": True}]])
        
        if 'IF' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['mes'], y=df['IF'], name='Índice de Frecuencia',
                mode='lines+markers', line=dict(color=self.COLORES['if_color'], width=3),
                marker=dict(size=8)
            ), secondary_y=False)
        
        if 'IG' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['mes'], y=df['IG'], name='Índice de Gravedad',
                mode='lines+markers', line=dict(color=self.COLORES['ig_color'], width=3),
                marker=dict(size=8)
            ), secondary_y=False)
        
        if 'TR' in df.columns:
            fig.add_trace(go.Scatter(
                x=df['mes'], y=df['TR'], name='Tasa de Riesgo',
                mode='lines+markers', line=dict(color=self.COLORES['tr_color'], width=3, dash='dash'),
                marker=dict(size=8)
            ), secondary_y=True)
        
        fig.update_layout(
            **self.layout_base,
            title=dict(text='Evolución de Indicadores Reactivos', x=0.5, font=dict(size=16)),
            xaxis=dict(title='Período', tickangle=-45),
            legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='center', x=0.5),
            height=450
        )
        fig.update_yaxes(title_text="IF / IG", secondary_y=False)
        fig.update_yaxes(title_text="Tasa de Riesgo", secondary_y=True)
        return fig
    
    # =========================================================================
    # DASHBOARD PROACTIVO
    # =========================================================================
    
    def render_proactive_dashboard(
        self,
        df: pd.DataFrame,
        metas: Dict[str, float],
        titulo: str = "Dashboard de Indicadores Proactivos",
        mostrar_tabla: bool = True,
        mostrar_graficos: bool = True
    ) -> None:
        """Renderiza el dashboard de indicadores proactivos"""
        st.markdown(f"## {titulo}", unsafe_allow_html=True)
        st.markdown("---")
        
        if mostrar_tabla:
            self._render_tabla_proactiva(df, metas)
        
        if mostrar_graficos:
            st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:bar-chart'></iconify-icon> Cumplimiento Gráfico</div>", unsafe_allow_html=True)
            self._render_graficos_proactivos(df, metas)
    
    def _render_tabla_proactiva(self, df: pd.DataFrame, metas: Dict[str, float]) -> None:
        """Renderiza la tabla de indicadores proactivos"""
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:list'></iconify-icon> Tabla de Detalle</div>", unsafe_allow_html=True)
        
        df_display = df.copy()
        cols_porcentaje = ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai', 'ig_total']
        
        for col in cols_porcentaje:
            if col in df_display.columns:
                df_display[col] = df_display[col].apply(
                    lambda x: f"{x:.1f}%" if pd.notna(x) else "-"
                )
        
        rename_cols = {
            'mes': 'Mes', 'iart': 'IART', 'opas': 'OPAS', 'idps': 'IDPS',
            'ids': 'IDS', 'ients': 'IENTS', 'iosea': 'IOSEA',
            'icai': 'ICAI', 'ig_total': 'IG Total'
        }
        df_display = df_display.rename(columns={k: v for k, v in rename_cols.items() if k in df_display.columns})
        st.dataframe(df_display, use_container_width=True, hide_index=True)
        
        # Metas
        metas_items = [f"<strong>{k.upper()}:</strong> {v}%" for k, v in metas.items()]
        st.markdown(
            f"<div style='font-size: 0.9rem; color: #666; margin-top:10px;'>Meta Configurada: {' | '.join(metas_items)}</div>", 
            unsafe_allow_html=True
        )
    
    def _render_graficos_proactivos(self, df: pd.DataFrame, metas: Dict[str, float]) -> None:
        """Renderiza gráficos de indicadores proactivos con filtros mejorados"""
        indicadores = ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai', 'ief']
        indicadores_presentes = [ind for ind in indicadores if ind in df.columns]
        
        if not indicadores_presentes:
            st.warning("No hay indicadores proactivos para graficar")
            return
        
        # --- GRÁFICO 1: Barras por indicador (meses en eje X) ---
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:bar-chart-2'></iconify-icon> Evolución por Indicador</div>", unsafe_allow_html=True)
        
        indicador_seleccionado = st.selectbox(
            "Seleccionar Indicador",
            options=indicadores_presentes,
            format_func=lambda x: x.upper(),
            key="select_indicador_proactivo"
        )
        
        fig_barras = self._crear_grafico_barras_por_indicador(df, indicador_seleccionado, metas)
        st.plotly_chart(fig_barras, use_container_width=True)
        
        st.markdown("---")
        
        # --- GRÁFICO 2: Radar por mes ---
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:radar'></iconify-icon> Radar de Cumplimiento</div>", unsafe_allow_html=True)
        
        meses_disponibles = list(df['mes'].unique())
        opciones_mes = ["Anual (Promedio)"] + meses_disponibles
        
        mes_radar = st.selectbox(
            "Seleccionar Período",
            options=opciones_mes,
            index=0,  # Por defecto: Anual
            key="select_mes_radar"
        )
        
        fig_radar = self._crear_grafico_radar(df, indicadores_presentes, metas, mes_radar)
        st.plotly_chart(fig_radar, use_container_width=True)
        
        st.markdown("---")
        
        # --- GRÁFICO 3: Evolución IG Total ---
        st.markdown(f"### <div class='flex-center'><iconify-icon icon='lucide:activity'></iconify-icon> Tendencia IG Total</div>", unsafe_allow_html=True)
        fig_evol = self._crear_grafico_evolucion_ig(df, metas.get('ig_total', 80))
        st.plotly_chart(fig_evol, use_container_width=True)
    
    def _crear_grafico_barras_por_indicador(
        self, df: pd.DataFrame, indicador: str, metas: Dict[str, float]
    ) -> go.Figure:
        """Crea gráfico de barras con meses en eje X para un indicador específico"""
        fig = go.Figure()
        
        meta = metas.get(indicador, metas.get('general', 80))
        valores = df[indicador].tolist()
        meses = df['mes'].tolist()
        
        # Colores según cumplimiento
        colores = [self.COLORES['exito'] if v >= meta else self.COLORES['peligro'] for v in valores]
        
        fig.add_trace(go.Bar(
            x=meses, y=valores, marker_color=colores,
            text=[f"{v:.1f}%" for v in valores], textposition='outside',
            name=indicador.upper(),
            hovertemplate='%{x}<br>Cumplimiento: %{y:.1f}%<extra></extra>'
        ))
        
        # Línea de meta
        fig.add_hline(
            y=meta, line_dash="dash", line_color=self.COLORES['oscuro'],
            annotation_text=f"Meta: {meta}%", annotation_position="right"
        )
        
        # Área de cumplimiento
        fig.add_hrect(
            y0=meta, y1=120, fillcolor=self.COLORES['exito'], opacity=0.1, line_width=0
        )
        
        fig.update_layout(
            **self.layout_base,
            title=dict(text=f'Evolución {indicador.upper()} por Mes', x=0.5, font=dict(size=16)),
            xaxis=dict(title='Mes', tickangle=-45),
            yaxis=dict(title='Porcentaje (%)', range=[0, 120]),
            showlegend=False, height=400, bargap=0.3
        )
        return fig
    
    def _crear_grafico_radar(
        self, df: pd.DataFrame, indicadores: List[str], metas: Dict[str, float], mes_seleccionado: str
    ) -> go.Figure:
        """Crea gráfico radar/spider para visualizar cumplimiento de indicadores"""
        fig = go.Figure()
        
        # Obtener valores según selección
        if mes_seleccionado == "Anual (Promedio)":
            valores = [df[ind].mean() for ind in indicadores]
            titulo = "Cumplimiento Anual (Promedio)"
        else:
            df_mes = df[df['mes'] == mes_seleccionado]
            if df_mes.empty:
                valores = [0] * len(indicadores)
            else:
                valores = [df_mes[ind].iloc[0] for ind in indicadores]
            titulo = f"Cumplimiento - {mes_seleccionado}"
        
        etiquetas = [ind.upper() for ind in indicadores]
        meta_general = metas.get('general', 80)
        metas_valores = [metas.get(ind, meta_general) for ind in indicadores]
        
        # Cerrar el polígono (repetir primer valor)
        valores_cerrado = valores + [valores[0]]
        etiquetas_cerrado = etiquetas + [etiquetas[0]]
        metas_cerrado = metas_valores + [metas_valores[0]]
        
        # Área de valores reales
        fig.add_trace(go.Scatterpolar(
            r=valores_cerrado,
            theta=etiquetas_cerrado,
            fill='toself',
            fillcolor='rgba(31, 119, 180, 0.3)',
            line=dict(color=self.COLORES['primario'], width=2),
            name='Cumplimiento Real',
            hovertemplate='%{theta}: %{r:.1f}%<extra></extra>'
        ))
        
        # Línea de meta (80%)
        fig.add_trace(go.Scatterpolar(
            r=metas_cerrado,
            theta=etiquetas_cerrado,
            fill=None,
            line=dict(color=self.COLORES['peligro'], width=2, dash='dash'),
            name='Meta',
            hovertemplate='Meta %{theta}: %{r:.0f}%<extra></extra>'
        ))
        
        # Marcar indicadores que no cumplen
        for i, (val, meta, etiq) in enumerate(zip(valores, metas_valores, etiquetas)):
            if val < meta:
                fig.add_trace(go.Scatterpolar(
                    r=[val], theta=[etiq],
                    mode='markers',
                    marker=dict(color=self.COLORES['peligro'], size=12, symbol='x'),
                    name=f'{etiq} (No cumple)',
                    showlegend=False,
                    hovertemplate=f'{etiq}: {val:.1f}% (< Meta {meta}%)<extra></extra>'
                ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 120],
                    ticksuffix='%',
                    tickfont=dict(size=10)
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, weight='bold')
                ),
                bgcolor='rgba(255,255,255,0.9)'
            ),
            showlegend=True,
            legend=dict(orientation='h', yanchor='bottom', y=-0.2, xanchor='center', x=0.5),
            title=dict(text=titulo, x=0.5, font=dict(size=16)),
            height=500,
            paper_bgcolor='white',
            font=dict(family='Inter, sans-serif')
        )
        return fig
    
    def _crear_grafico_evolucion_ig(self, df: pd.DataFrame, meta_ig: float) -> go.Figure:
        """Crea gráfico de evolución del IG Total"""
        fig = go.Figure()
        
        if 'ig_total' not in df.columns:
            return fig
        
        fig.add_trace(go.Scatter(
            x=df['mes'], y=df['ig_total'], mode='lines+markers+text', name='IG Total',
            line=dict(color=self.COLORES['primario'], width=3),
            marker=dict(size=12), text=[f"{v:.1f}%" for v in df['ig_total']],
            textposition='top center', hovertemplate='%{x}<br>IG Total: %{y:.1f}%<extra></extra>'
        ))
        
        fig.add_hline(
            y=meta_ig, line_dash="dash", line_color=self.COLORES['oscuro'],
            annotation_text=f"Meta: {meta_ig}%", annotation_position="right"
        )
        
        fig.add_hrect(
            y0=meta_ig, y1=100, fillcolor=self.COLORES['exito'], opacity=0.1, line_width=0
        )
        
        fig.update_layout(
            **self.layout_base,
            title=dict(text='Evolución del Índice de Gestión Total', x=0.5, font=dict(size=16)),
            xaxis=dict(title='Mes', tickangle=-45),
            yaxis=dict(title='IG Total (%)', range=[0, 110]),
            showlegend=True, height=400
        )
        return fig

    # =========================================================================
    # GENERACIÓN DE GRÁFICOS ESTÁTICOS (MATPLOTLIB) PARA PDF
    # =========================================================================
    
    def generar_imagenes_reactivas(self, df: pd.DataFrame) -> Dict[str, bytes]:
        """Genera gráficos estáticos para el reporte PDF reactivo"""
        import matplotlib.pyplot as plt
        import io
        
        imagenes = {}
        
        if df.empty or 'mes' not in df.columns:
            return imagenes
            
        # Configurar estilo
        plt.style.use('default')
        plt.rcParams.update({'font.size': 9, 'figure.figsize': (8, 4)})
        
        # 1. Índice de Frecuencia
        if 'IF' in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df['mes'], df['IF'], marker='o', linestyle='-', color='#e74c3c', linewidth=2)
            ax.set_title('Evolución Índice de Frecuencia (IF)')
            ax.set_ylabel('Índice')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            imagenes['IF'] = buf
            plt.close(fig)
            
        # 2. Índice de Gravedad
        if 'IG' in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df['mes'], df['IG'], marker='s', linestyle='-', color='#f39c12', linewidth=2)
            ax.set_title('Evolución Índice de Gravedad (IG)')
            ax.set_ylabel('Índice')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            imagenes['IG'] = buf
            plt.close(fig)
            
        # 3. Tasa de Riesgo
        if 'TR' in df.columns:
            fig, ax = plt.subplots()
            ax.plot(df['mes'], df['TR'], marker='^', linestyle='-', color='#9b59b6', linewidth=2)
            ax.set_title('Evolución Tasa de Riesgo (TR)')
            ax.set_ylabel('Días / Accidente')
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            imagenes['TR'] = buf
            plt.close(fig)
            
        return imagenes

    def generar_imagenes_proactivas(self, df: pd.DataFrame, metas: Dict[str, float]) -> Dict[str, bytes]:
        """Genera gráficos estáticos para el reporte PDF proactivo"""
        import matplotlib.pyplot as plt
        import io
        
        imagenes = {}
        indicadores = ['iart', 'opas', 'idps', 'ids', 'ients', 'iosea', 'icai', 'ig_total']
        presentes = [ind for ind in indicadores if ind in df.columns]
        
        if not presentes:
            return imagenes
            
        plt.style.use('default')
        plt.rcParams.update({'font.size': 9})
        
        # 1. Barras de Cumplimiento Promedio vs Meta
        fig, ax = plt.subplots(figsize=(8, 4))
        
        promedios = [df[ind].mean() for ind in presentes]
        nombres = [ind.upper() for ind in presentes]
        metas_vals = [metas.get(ind, metas.get('general', 80)) for ind in presentes]
        
        colores = ['#2ecc71' if p >= m else '#e74c3c' for p, m in zip(promedios, metas_vals)]
        
        bars = ax.bar(nombres, promedios, color=colores, alpha=0.7)
        
        # Líneas de meta
        for i, meta in enumerate(metas_vals):
            ax.hlines(y=meta, xmin=i-0.4, xmax=i+0.4, colors='gray', linestyles='--', linewidth=1.5)
            
        ax.set_title('Cumplimiento Promedio por Indicador')
        ax.set_ylabel('Cumplimiento (%)')
        ax.set_ylim(0, 110)
        
        # Etiquetas
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}%', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=100)
        buf.seek(0)
        imagenes['barras_resumen'] = buf
        plt.close(fig)
        
        # 2. Evolución IG Total
        if 'ig_total' in df.columns:
            fig, ax = plt.subplots(figsize=(8, 4))
            ax.plot(df['mes'], df['ig_total'], marker='o', linestyle='-', color='#1f77b4', linewidth=2)
            
            meta_ig = metas.get('ig_total', 80)
            ax.axhline(y=meta_ig, color='gray', linestyle='--', alpha=0.7, label=f'Meta {meta_ig}%')
            
            ax.set_title('Evolución Índice de Gestión Total (IG Total)')
            ax.set_ylabel('Cumplimiento (%)')
            ax.legend()
            ax.grid(True, alpha=0.3)
            plt.xticks(rotation=45)
            plt.ylim(0, 110)
            plt.tight_layout()
            
            buf = io.BytesIO()
            plt.savefig(buf, format='png', dpi=100)
            buf.seek(0)
            imagenes['evolucion_ig'] = buf
            plt.close(fig)
            
        return imagenes
    
    # =========================================================================
    # UTILIDADES COMUNES
    # =========================================================================
    
    def render_metricas_resumen(
        self, metricas: Dict[str, Any], tipo: str = "reactivo"
    ) -> None:
        """Renderiza tarjetas de métricas resumen con estilo mejorado"""
        
        if tipo == "reactivo":
            # 5 métricas en una fila
            col1, col2, col3, col4, col5 = st.columns(5)
            
            with col1:
                st.metric(
                    label="Lesiones Totales",
                    value=f"{metricas.get('total_lesiones', 0):,.0f}"
                )
            with col2:
                st.metric(
                    label="Días Perdidos",
                    value=f"{metricas.get('total_dias', 0):,.0f}"
                )
            with col3:
                st.metric(
                    label="IF Promedio",
                    value=f"{metricas.get('if_promedio', 0):.2f}"
                )
            with col4:
                st.metric(
                    label="IG Promedio",
                    value=f"{metricas.get('ig_promedio', 0):.2f}"
                )
            with col5:
                st.metric(
                    label="TR Promedio",
                    value=f"{metricas.get('tr_promedio', 0):.2f}"
                )
        else:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    label="IG Total Promedio",
                    value=f"{metricas.get('ig_promedio', 0):.1f}%"
                )
            with col2:
                cumple = metricas.get('cumplimiento_general', 0) >= 80
                st.metric(
                    label="Cumplimiento",
                    value=f"{metricas.get('cumplimiento_general', 0):.1f}%",
                    delta="Cumple" if cumple else "No cumple",
                    delta_color="normal" if cumple else "inverse"
                )
            with col3:
                st.metric(
                    label="Meses Analizados",
                    value=f"{metricas.get('meses', 0)}"
                )

    def exportar_a_excel(
        self,
        df_reactivo: Optional[pd.DataFrame] = None,
        df_proactivo: Optional[pd.DataFrame] = None,
        nombre_archivo: str = "reporte_sso.xlsx"
    ) -> bytes:
        """Exporta los datos a Excel"""
        import io
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            if df_reactivo is not None:
                df_reactivo.to_excel(writer, sheet_name='Indicadores Reactivos', index=False)
            if df_proactivo is not None:
                df_proactivo.to_excel(writer, sheet_name='Indicadores Proactivos', index=False)
        output.seek(0)
        return output.getvalue()
