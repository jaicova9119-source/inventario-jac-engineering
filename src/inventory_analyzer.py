"""
Módulo de análisis de inventario
JAC Engineering SAS
"""

import pandas as pd
import numpy as np

class InventoryAnalyzer:
    
    def __init__(self, data):
        self.data = data
    
    def calculate_gaps(self):
        """Calcula brechas de inventario"""
        df = self.data.copy()
        
        df['brecha_minimo'] = df['stock_actual'] - df['stock_minimo']
        df['brecha_maximo'] = df['stock_maximo'] - df['stock_actual']
        df['cumplimiento_pct'] = (df['stock_actual'] / df['stock_minimo'] * 100).round(1)
        df['cumplimiento_pct'] = df['cumplimiento_pct'].replace([np.inf, -np.inf], 0)
        
        return df
    
    def classify_status(self, row):
        """Clasifica el estado del material"""
        if pd.isna(row['stock_minimo']):
            return 'SIN CONFIGURAR'
        
        brecha = row['brecha_minimo']
        
        if brecha < 0:
            return 'CRITICO'
        elif brecha < row['stock_minimo'] * 0.2:
            return 'BAJO'
        elif row['stock_actual'] > row['stock_maximo']:
            return 'SOBREINVENTARIO'
        else:
            return 'OK'
    
    def generate_actions(self, row):
        """Genera acciones recomendadas"""
        status = row['estado']
        
        actions = {
            'CRITICO': f"🔴 COMPRAR URGENTE - Faltante: {abs(row['brecha_minimo']):.0f} {row['unidad']}",
            'BAJO': f"🟡 SOLICITAR COMPRA - Recomendado: {row['brecha_maximo']:.0f} {row['unidad']}",
            'SOBREINVENTARIO': "🔵 REVISAR - Stock excesivo",
            'OK': "🟢 NORMAL - Monitoreo continuo",
            'SIN CONFIGURAR': "⚪ CONFIGURAR PARAMETROS"
        }
        
        return actions.get(status, "—")
    
    def calculate_purchase_qty(self, row):
        """Calcula cantidad a comprar"""
        if row['estado'] in ['CRITICO', 'BAJO']:
            qty = max(0, row['stock_maximo'] - row['stock_actual'])
            return int(np.ceil(qty))
        return 0
    
    def full_analysis(self):
        """Análisis completo de inventario"""
        df = self.calculate_gaps()
        
        df['estado'] = df.apply(self.classify_status, axis=1)
        df['accion'] = df.apply(self.generate_actions, axis=1)
        df['cantidad_comprar'] = df.apply(self.calculate_purchase_qty, axis=1)
        df['valor_compra'] = df['cantidad_comprar'] * df['precio_unitario']
        
        priority_map = {'A': 1, 'B': 2, 'C': 3}
        df['prioridad_num'] = df['criticidad'].map(priority_map).fillna(4)
        
        df = df.sort_values(['estado', 'prioridad_num', 'brecha_minimo'])
        
        return df
    
    def get_summary_metrics(self):
        """Métricas resumen del inventario"""
        df = self.full_analysis()
        
        metrics = {
            'total_materiales': len(df),
            'criticos': len(df[df['estado'] == 'CRITICO']),
            'bajo': len(df[df['estado'] == 'BAJO']),
            'ok': len(df[df['estado'] == 'OK']),
            'sobreinventario': len(df[df['estado'] == 'SOBREINVENTARIO']),
            'sin_configurar': len(df[df['estado'] == 'SIN CONFIGURAR']),
            'valor_total_stock': df['valor_stock'].sum(),
            'valor_compras_requeridas': df['valor_compra'].sum(),
            'materiales_categoria_a': len(df[df['criticidad'] == 'A']),
            'materiales_categoria_b': len(df[df['criticidad'] == 'B']),
            'materiales_categoria_c': len(df[df['criticidad'] == 'C'])
        }
        
        return metrics