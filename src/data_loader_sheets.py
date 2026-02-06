"""
Data Loader con Google Sheets
JAC Engineering SAS
VERSION QUE LEE TODO DESDE GOOGLE SHEETS
"""

import pandas as pd
import streamlit as st
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.google_sheets_handler import GoogleSheetsHandler
from config.google_config import SHEETS_CONFIG

class DataLoaderSheets:
    
    def __init__(self):
        self.sheets_handler = GoogleSheetsHandler()
    
    def load_sap_data(self):
        """
        Carga datos SAP desde Google Sheets
        VERSION MULTI-USUARIO
        """
        try:
            print("Cargando inventario SAP desde Google Sheets...")
            
            config = SHEETS_CONFIG['inventario_sap']
            
            df = self.sheets_handler.read_sheet_to_dataframe(
                config['sheet_id'],
                config['sheet_name']
            )
            
            if df.empty:
                st.warning("Google Sheet de inventario SAP esta vacia")
                st.info("Sube tu archivo SAP a Google Sheets")
                return pd.DataFrame()
            
            print("Registros leidos: " + str(len(df)))
            
            # Mapeo de columnas
            column_mapping = {
                'Codigo material': 'codigo',
                'Texto breve de material': 'descripcion',
                'Centro': 'centro',
                'Nombre centro de costo': 'centro_nombre',
                'Ubicacion': 'ubicacion',
                'Cantidad': 'stock_actual',
                'Unidad de medida': 'unidad',
                'Valor por unidad': 'precio_unitario',
                'Valor total': 'valor_total'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            if 'codigo' not in df.columns:
                st.error("No se encontro columna de codigo")
                return pd.DataFrame()
            
            # Limpiar y convertir tipos
            df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0)
            df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce').fillna(0)
            
            if 'valor_stock' not in df.columns:
                df['valor_stock'] = df['stock_actual'] * df['precio_unitario']
            
            if 'unidad' not in df.columns:
                df['unidad'] = 'UND'
            if 'almacen' not in df.columns:
                df['almacen'] = 'ALM01'
            if 'fecha_actualizacion' not in df.columns:
                df['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
            
            # Limpiar datos
            df = df[df['codigo'].notna()].copy()
            df['descripcion'] = df['descripcion'].fillna('SIN DESCRIPCION')
            
            # Convertir codigo a string
            df['codigo'] = df['codigo'].astype(str)
            
            # Remover .0 si es numero entero
            df['codigo'] = df['codigo'].apply(lambda x: x.replace('.0', '') if '.0' in x else x)
            
            print("SAP cargado exitosamente: " + str(len(df)) + " registros")
            
            return df
            
        except Exception as e:
            st.error("ERROR cargando inventario SAP: " + str(e))
            import traceback
            st.code(traceback.format_exc())
            return pd.DataFrame()
    
    def load_parameters(self):
        """Carga parametros desde Google Sheets"""
        try:
            config = SHEETS_CONFIG['parametros']
            
            df = self.sheets_handler.read_sheet_to_dataframe(
                config['sheet_id'],
                config['sheet_name']
            )
            
            if df.empty:
                st.warning("Google Sheet de parametros esta vacia")
                return pd.DataFrame()
            
            if 'Codigo' in df.columns:
                df = df[df['Codigo'].notna()].copy()
                df['Codigo'] = df['Codigo'].astype(str)
                df['Codigo'] = df['Codigo'].apply(lambda x: x.replace('.0', '') if '.0' in x else x)
            
            if 'Centro' in df.columns:
                df = df[df['Centro'].notna()].copy()
                df['Centro'] = df['Centro'].astype(str)
            
            column_mapping = {
                'Codigo': 'codigo',
                'Centro': 'centro',
                'Descripcion': 'descripcion',
                'Nombre_Tecnico': 'nombre_tecnico',
                'Centro_Nombre': 'centro_nombre_param',
                'Stock_Minimo': 'stock_minimo',
                'Stock_Maximo': 'stock_maximo',
                'Lead_Time_dias': 'lead_time',
                'Criticidad': 'criticidad',
                'Consumo_Prom_Mensual': 'consumo_mensual',
                'Proveedor': 'proveedor',
                'Categoria': 'Categoria'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            if 'stock_minimo' in df.columns:
                df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(10)
            
            if 'stock_maximo' in df.columns:
                df['stock_maximo'] = pd.to_numeric(df['stock_maximo'], errors='coerce').fillna(50)
            
            if 'lead_time' in df.columns:
                df['lead_time'] = pd.to_numeric(df['lead_time'], errors='coerce').fillna(30)
            
            if 'consumo_mensual' in df.columns:
                df['consumo_mensual'] = pd.to_numeric(df['consumo_mensual'], errors='coerce').fillna(5.0)
            
            if 'nombre_tecnico' in df.columns:
                df['nombre_tecnico'] = df['nombre_tecnico'].fillna('')
            
            if 'proveedor' in df.columns:
                df['proveedor'] = df['proveedor'].fillna('POR CONFIGURAR')
            
            if 'criticidad' in df.columns:
                df['criticidad'] = df['criticidad'].fillna('B')
            
            return df
            
        except Exception as e:
            st.error("ERROR cargando parametros: " + str(e))
            return pd.DataFrame()
    
    def save_parameters(self, df):
        """Guarda parametros a Google Sheets"""
        try:
            config = SHEETS_CONFIG['parametros']
            
            column_mapping_reverse = {
                'codigo': 'Codigo',
                'centro': 'Centro',
                'descripcion': 'Descripcion',
                'nombre_tecnico': 'Nombre_Tecnico',
                'centro_nombre_param': 'Centro_Nombre',
                'stock_minimo': 'Stock_Minimo',
                'stock_maximo': 'Stock_Maximo',
                'lead_time': 'Lead_Time_dias',
                'criticidad': 'Criticidad',
                'consumo_mensual': 'Consumo_Prom_Mensual',
                'proveedor': 'Proveedor',
                'Categoria': 'Categoria'
            }
            
            df_save = df.copy()
            df_save.rename(columns=column_mapping_reverse, inplace=True)
            
            return self.sheets_handler.write_dataframe_to_sheet(
                df_save,
                config['sheet_id'],
                config['sheet_name']
            )
            
        except Exception as e:
            st.error("ERROR guardando parametros: " + str(e))
            return False
    
    def merge_data(self):
        """Combina datos SAP con parametros - TODO DESDE GOOGLE SHEETS"""
        print("\n" + "="*70)
        print("  ACTUALIZANDO INVENTARIO - MODO MULTI-USUARIO")
        print("  Todo desde Google Sheets")
        print("="*70 + "\n")
        
        print("[1/4] Cargando inventario SAP desde Google Sheets...")
        sap_data = self.load_sap_data()
        
        if sap_data.empty:
            print("ERROR: No hay datos SAP en Google Sheets")
            return pd.DataFrame()
        
        print("  SAP cargado: " + str(len(sap_data)) + " registros")
        print()
        
        print("[2/4] Cargando parametros desde Google Sheets...")
        params = self.load_parameters()
        
        if params.empty:
            print("  Sin parametros, usando valores por defecto")
            sap_data['stock_minimo'] = 0
            sap_data['stock_maximo'] = 0
            sap_data['lead_time'] = 0
            sap_data['criticidad'] = 'C'
            sap_data['consumo_mensual'] = 0
            sap_data['proveedor'] = 'SIN CONFIGURAR'
            sap_data['nombre_tecnico'] = ''
            return sap_data
        
        print("  Parametros cargados: " + str(len(params)) + " registros")
        print()
        
        print("[3/4] Realizando merge...")
        
        tiene_centro_sap = 'centro' in sap_data.columns
        tiene_centro_params = 'centro' in params.columns
        
        if tiene_centro_params and tiene_centro_sap:
            sap_data['centro'] = sap_data['centro'].astype(str)
            params['centro'] = params['centro'].astype(str)
            
            merged = pd.merge(
                sap_data,
                params,
                on=['codigo', 'centro'],
                how='left',
                suffixes=('', '_param')
            )
        else:
            merged = pd.merge(
                sap_data,
                params,
                on='codigo',
                how='left',
                suffixes=('', '_param')
            )
        
        print("  Merge completado: " + str(len(merged)) + " registros")
        print()
        
        print("[4/4] Limpiando datos...")
        
        merged['descripcion'] = merged['descripcion'].fillna(merged.get('descripcion_param', ''))
        if 'descripcion_param' in merged.columns:
            merged.drop('descripcion_param', axis=1, inplace=True)
        
        merged['stock_minimo'] = merged['stock_minimo'].fillna(0)
        merged['stock_maximo'] = merged['stock_maximo'].fillna(0)
        merged['lead_time'] = merged['lead_time'].fillna(0)
        merged['criticidad'] = merged['criticidad'].fillna('C')
        merged['consumo_mensual'] = merged['consumo_mensual'].fillna(0)
        merged['proveedor'] = merged['proveedor'].fillna('SIN CONFIGURAR')
        
        if 'nombre_tecnico' in merged.columns:
            merged['nombre_tecnico'] = merged['nombre_tecnico'].fillna('')
        else:
            merged['nombre_tecnico'] = ''
        
        print()
        print("="*70)
        print("  DATOS COMBINADOS: " + str(len(merged)) + " registros")
        print("  Fuente: 100% Google Sheets (multi-usuario)")
        print("="*70 + "\n")
        
        return merged