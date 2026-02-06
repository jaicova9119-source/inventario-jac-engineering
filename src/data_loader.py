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
            print("Archivo leido: " + str(len(df)) + " filas")
            
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
                print("ERROR: No se encontro columna de codigo")
                return pd.DataFrame()
            
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
            
            df = df[df['codigo'].notna()]
            df['descripcion'] = df['descripcion'].fillna('SIN DESCRIPCION')
            
            df['codigo'] = df['codigo'].astype(float).astype(int).astype(str)
            
            print("Datos procesados: " + str(len(df)) + " registros")
            return df
            
        except Exception as e:
            print("ERROR: " + str(e))
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def load_parameters(self):
        try:
            params_file_centro = os.path.join(
                os.path.dirname(self.params_file_path), 
                'parametros_stock_por_centro.xlsx'
            )
            
            if os.path.exists(params_file_centro):
                print("Usando parametros por centro")
                print("Archivo: " + params_file_centro)
                df = pd.read_excel(params_file_centro)
                
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
                
                print("  Registros antes de limpiar: " + str(len(df)))
                df = df[df['codigo'].notna()]
                print("  Registros despues de limpiar: " + str(len(df)))
                
                df['codigo'] = df['codigo'].astype(float).astype(int).astype(str)
                
                print("Parametros cargados (con centro): " + str(len(df)) + " registros")
                
            else:
                print("Usando parametros sin centro")
                if not os.path.exists(self.params_file_path):
                    print("ERROR: No existe parametros_stock.xlsx")
                    return pd.DataFrame()
                
                df = pd.read_excel(self.params_file_path)
                
                column_mapping = {
                    'Codigo': 'codigo',
                    'Descripcion': 'descripcion',
                    'Nombre_Tecnico': 'nombre_tecnico',
                    'Stock_Minimo': 'stock_minimo',
                    'Stock_Maximo': 'stock_maximo',
                    'Lead_Time_dias': 'lead_time',
                    'Criticidad': 'criticidad',
                    'Consumo_Prom_Mensual': 'consumo_mensual',
                    'Proveedor': 'proveedor',
                    'Categoria': 'Categoria'
                }
                
                df.rename(columns=column_mapping, inplace=True)
                
                df = df[df['codigo'].notna()]
                df['codigo'] = df['codigo'].astype(float).astype(int).astype(str)
                
                print("Parametros cargados (sin centro): " + str(len(df)) + " registros")
            
            df['criticidad'] = df['criticidad'].fillna('C').str.upper()
            df['criticidad'] = df['criticidad'].apply(lambda x: x if x in ['A', 'B', 'C'] else 'C')
            
            if 'nombre_tecnico' in df.columns:
                df['nombre_tecnico'] = df['nombre_tecnico'].fillna('')
            
            return df
            
        except Exception as e:
            print("ERROR parametros: " + str(e))
            import traceback
            traceback.print_exc()
            return pd.DataFrame()
    
    def merge_data(self):
        print("\n" + "="*70)
        print("  ACTUALIZANDO INVENTARIO")
        print("="*70 + "\n")
        
        print("[1/4] Cargando datos SAP...")
        sap_data = self.load_sap_data()
        
        if sap_data.empty:
            print("ERROR: No hay datos SAP")
            return pd.DataFrame()
        
        print("  SAP cargado: " + str(len(sap_data)) + " registros")
        print()
        
        print("[2/4] Cargando parametros...")
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
        
        print("  Centro en SAP: " + str(tiene_centro_sap))
        print("  Centro en Params: " + str(tiene_centro_params))
        
        if tiene_centro_params and tiene_centro_sap:
            print("  Merge por codigo + centro")
            
            sap_data['centro'] = sap_data['centro'].astype(str)
            params['centro'] = params['centro'].astype(str)
            
            merged = pd.merge(
                sap_data,
                params,
                on=['codigo', 'centro'],
                how='left',
                suffixes=('', '_param')
            )
            
            print("  Merge completado: " + str(len(merged)) + " registros")
            
            con_params = merged['stock_minimo'].notna().sum()
            sin_params = merged['stock_minimo'].isna().sum()
            
            print("  Con parametros: " + str(con_params))
            print("  Sin parametros: " + str(sin_params))
            
        else:
            print("  Merge solo por codigo")
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
        print("="*70 + "\n")
        
        return merged