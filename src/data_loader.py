"""
Módulo de carga y limpieza de datos SAP
JAC Engineering SAS - Adaptado para columnas en español
"""

import pandas as pd
import os
from datetime import datetime
import sys
import glob

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config.settings import RAW_DATA_DIR, CONFIG_DIR, SAP_FILE, PARAMS_FILE

class DataLoader:
    
    def __init__(self):
        self.sap_file_path = os.path.join(RAW_DATA_DIR, SAP_FILE)
        self.params_file_path = os.path.join(CONFIG_DIR, PARAMS_FILE)
        
        self.sap_downloads_dir = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            'data',
            'sap_descargas'
        )
        
        os.makedirs(self.sap_downloads_dir, exist_ok=True)
    
    def get_latest_sap_file(self):
        """Busca el archivo Excel más reciente"""
        try:
            excel_files = glob.glob(os.path.join(self.sap_downloads_dir, '*.xlsx'))
            excel_files.extend(glob.glob(os.path.join(self.sap_downloads_dir, '*.xls')))
            
            if not excel_files:
                return None
            
            latest_file = max(excel_files, key=os.path.getmtime)
            mod_time = datetime.fromtimestamp(os.path.getmtime(latest_file))
            
            print("Archivo SAP: " + os.path.basename(latest_file))
            print("Fecha: " + mod_time.strftime('%Y-%m-%d %H:%M:%S'))
            
            return latest_file
            
        except Exception as e:
            print("Error buscando archivo: " + str(e))
            return None
    
    def load_sap_data(self):
        """Carga datos desde archivo SAP"""
        try:
            latest_file = self.get_latest_sap_file()
            
            if latest_file is None:
                print("Usando archivo base: " + self.sap_file_path)
                if not os.path.exists(self.sap_file_path):
                    print("ERROR: No existe archivo")
                    return pd.DataFrame()
                file_to_read = self.sap_file_path
            else:
                file_to_read = latest_file
            
            df = pd.read_excel(file_to_read)
            print("Archivo leído: " + str(len(df)) + " filas")
            
            # Mapeo de columnas en español
            column_mapping = {
                'Codigo material': 'codigo',
                'Texto breve de material': 'descripcion',
                'Centro': 'centro',
                'Nombre centro de costo': 'centro_nombre',
                'Ubicacion': 'almacen',
                'Cantidad': 'stock_actual',
                'Unidad de medida': 'unidad',
                'Valor por unidad': 'precio_unitario',
                'Valor total': 'valor_total'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            # Verificar columnas esenciales
            if 'codigo' not in df.columns:
                print("ERROR: No se encontró columna de código")
                return pd.DataFrame()
            
            # Limpieza de datos
            df['stock_actual'] = pd.to_numeric(df['stock_actual'], errors='coerce').fillna(0)
            df['precio_unitario'] = pd.to_numeric(df['precio_unitario'], errors='coerce').fillna(0)
            
            # Calcular valor de stock si no existe
            if 'valor_stock' not in df.columns:
                df['valor_stock'] = df['stock_actual'] * df['precio_unitario']
            
            # Agregar columnas faltantes
            if 'unidad' not in df.columns:
                df['unidad'] = 'UND'
            if 'almacen' not in df.columns:
                df['almacen'] = 'ALM01'
            if 'fecha_actualizacion' not in df.columns:
                df['fecha_actualizacion'] = datetime.now().strftime('%Y-%m-%d')
            
            # Limpiar valores nulos
            df = df[df['codigo'].notna()]
            df['descripcion'] = df['descripcion'].fillna('SIN DESCRIPCION')
            
            print("Datos procesados: " + str(len(df)) + " registros")
            return df
            
        except Exception as e:
            print("ERROR: " + str(e))
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def load_parameters(self):
        """Carga parámetros de control"""
        try:
            if not os.path.exists(self.params_file_path):
                print("ERROR: No existe parametros_stock.xlsx")
                return pd.DataFrame()
            
            df = pd.read_excel(self.params_file_path)
            
            column_mapping = {
                'Codigo': 'codigo',
                'Descripcion': 'descripcion',
                'Stock_Minimo': 'stock_minimo',
                'Stock_Maximo': 'stock_maximo',
                'Lead_Time_dias': 'lead_time',
                'Criticidad': 'criticidad',
                'Consumo_Prom_Mensual': 'consumo_mensual',
                'Proveedor': 'proveedor'
            }
            
            df.rename(columns=column_mapping, inplace=True)
            
            df['criticidad'] = df['criticidad'].fillna('C').str.upper()
            df['criticidad'] = df['criticidad'].apply(lambda x: x if x in ['A', 'B', 'C'] else 'C')
            
            print("Parametros cargados: " + str(len(df)) + " materiales")
            return df
            
        except Exception as e:
            print("ERROR parametros: " + str(e))
            return pd.DataFrame()
    
    def merge_data(self):
        """Combina datos SAP con parámetros"""
        print("\n" + "="*60)
        print("ACTUALIZANDO INVENTARIO")
        print("="*60 + "\n")
        
        sap_data = self.load_sap_data()
        params = self.load_parameters()
        
        if sap_data.empty:
            print("ERROR: No hay datos SAP")
            return pd.DataFrame()
        
        if params.empty:
            print("AVISO: Sin parametros, usando datos SAP")
            sap_data['stock_minimo'] = 0
            sap_data['stock_maximo'] = 0
            sap_data['lead_time'] = 0
            sap_data['criticidad'] = 'C'
            sap_data['consumo_mensual'] = 0
            sap_data['proveedor'] = 'SIN CONFIGURAR'
            return sap_data
        
        merged = pd.merge(
            sap_data,
            params,
            on='codigo',
            how='left',
            suffixes=('', '_param')
        )
        
        merged['descripcion'] = merged['descripcion'].fillna(merged.get('descripcion_param', ''))
        if 'descripcion_param' in merged.columns:
            merged.drop('descripcion_param', axis=1, inplace=True)
        
        merged['stock_minimo'] = merged['stock_minimo'].fillna(0)
        merged['stock_maximo'] = merged['stock_maximo'].fillna(0)
        merged['lead_time'] = merged['lead_time'].fillna(0)
        merged['criticidad'] = merged['criticidad'].fillna('C')
        merged['consumo_mensual'] = merged['consumo_mensual'].fillna(0)
        merged['proveedor'] = merged['proveedor'].fillna('SIN CONFIGURAR')
        
        print("\nDATOS COMBINADOS: " + str(len(merged)) + " registros")
        print("="*60 + "\n")
        
        return merged