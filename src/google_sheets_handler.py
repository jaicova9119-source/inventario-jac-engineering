"""
Manejador de Google Sheets
JAC Engineering SAS
VERSION COMPATIBLE CON RENDER, STREAMLIT CLOUD Y LOCAL
"""

import gspread
from google.oauth2.service_account import Credentials
import pandas as pd
import streamlit as st
import os

class GoogleSheetsHandler:
    
    def __init__(self):
        self.scopes = [
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/drive'
        ]
        self.client = None
        self._authenticate()
    
    def _authenticate(self):
        """Autentica con Google Sheets - Compatible con Render, Streamlit Cloud y Local"""
        try:
            # OPCION 1: Variables de entorno (Render/Heroku) - VERIFICAR PRIMERO
            if os.environ.get('GCP_PROJECT_ID'):
                print("Autenticando con variables de entorno (Render/Heroku)...")
                
                # Construir diccionario de credenciales desde env vars
                private_key = os.environ.get('GCP_PRIVATE_KEY', '')
                
                # Render/Heroku pueden escapar los saltos de linea, restaurarlos
                if '\\n' in private_key:
                    private_key = private_key.replace('\\n', '\n')
                
                credentials_dict = {
                    'type': os.environ.get('GCP_TYPE', 'service_account'),
                    'project_id': os.environ.get('GCP_PROJECT_ID'),
                    'private_key_id': os.environ.get('GCP_PRIVATE_KEY_ID'),
                    'private_key': private_key,
                    'client_email': os.environ.get('GCP_CLIENT_EMAIL'),
                    'client_id': os.environ.get('GCP_CLIENT_ID'),
                    'auth_uri': os.environ.get('GCP_AUTH_URI', 'https://accounts.google.com/o/oauth2/auth'),
                    'token_uri': os.environ.get('GCP_TOKEN_URI', 'https://oauth2.googleapis.com/token'),
                    'auth_provider_x509_cert_url': os.environ.get('GCP_AUTH_PROVIDER_CERT', 'https://www.googleapis.com/oauth2/v1/certs'),
                    'client_x509_cert_url': os.environ.get('GCP_CLIENT_CERT_URL'),
                    'universe_domain': os.environ.get('GCP_UNIVERSE_DOMAIN', 'googleapis.com')
                }
                
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=self.scopes
                )
            
            # OPCION 2: Streamlit secrets (Streamlit Cloud)
            elif hasattr(st, 'secrets'):
                try:
                    # Intentar acceder a secrets sin lanzar excepcion
                    secrets_dict = st.secrets.to_dict() if hasattr(st.secrets, 'to_dict') else {}
                    
                    if 'gcp_service_account' in secrets_dict:
                        print("Autenticando con Streamlit secrets...")
                        credentials_dict = dict(st.secrets['gcp_service_account'])
                        credentials = Credentials.from_service_account_info(
                            credentials_dict,
                            scopes=self.scopes
                        )
                    else:
                        raise ValueError("No se encontraron credenciales de GCP en Streamlit secrets")
                except Exception as e:
                    print("No se pudieron leer Streamlit secrets:", str(e))
                    # Intentar con archivo local como fallback
                    raise
            
            # OPCION 3: Archivo local (desarrollo)
            else:
                print("Autenticando con archivo local...")
                credentials_file = 'config/google_credentials.json'
                
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError(
                        "No se encontro google_credentials.json y no hay variables de entorno configuradas. "
                        "Por favor configura las variables de entorno GCP_* en Render."
                    )
                
                credentials = Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.scopes
                )
            
            self.client = gspread.authorize(credentials)
            print("✅ Autenticacion exitosa con Google Sheets")
            
        except Exception as e:
            error_msg = "Error de autenticacion con Google Sheets: " + str(e)
            print("❌", error_msg)
            st.error(error_msg)
            st.info("Verifica que las variables de entorno GCP_* esten configuradas correctamente en Render")
            raise
    
    def read_sheet_to_dataframe(self, sheet_id, sheet_name):
        """Lee Google Sheet y convierte a DataFrame"""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            data = worksheet.get_all_records()
            
            if not data:
                headers = worksheet.row_values(1)
                return pd.DataFrame(columns=headers)
            
            df = pd.DataFrame(data)
            return df
            
        except Exception as e:
            st.error("Error leyendo Google Sheet: " + str(e))
            print("ERROR leyendo sheet:", str(e))
            return pd.DataFrame()
    
    def write_dataframe_to_sheet(self, df, sheet_id, sheet_name):
        """Escribe DataFrame a Google Sheets"""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            worksheet.clear()
            
            values = [df.columns.tolist()] + df.values.tolist()
            worksheet.update('A1', values)
            
            return True
            
        except Exception as e:
            st.error("Error escribiendo a Google Sheet: " + str(e))
            print("ERROR escribiendo sheet:", str(e))
            return False
    
    def append_rows_to_sheet(self, df, sheet_id, sheet_name):
        """Agrega filas al final"""
        try:
            spreadsheet = self.client.open_by_key(sheet_id)
            worksheet = spreadsheet.worksheet(sheet_name)
            
            values = df.values.tolist()
            worksheet.append_rows(values)
            
            return True
            
        except Exception as e:
            st.error("Error agregando filas: " + str(e))
            print("ERROR agregando filas:", str(e))
            return False
    
    def update_rows_by_condition(self, df, sheet_id, sheet_name, key_column):
        """Actualiza filas basado en una columna clave"""
        try:
            # Leer datos actuales
            current_df = self.read_sheet_to_dataframe(sheet_id, sheet_name)
            
            if current_df.empty:
                # Si no hay datos, escribir todo
                return self.write_dataframe_to_sheet(df, sheet_id, sheet_name)
            
            # Actualizar o agregar filas
            for idx, row in df.iterrows():
                key_value = row[key_column]
                
                # Buscar si existe
                mask = current_df[key_column] == key_value
                
                if mask.any():
                    # Actualizar fila existente
                    current_df.loc[mask] = row
                else:
                    # Agregar nueva fila
                    current_df = pd.concat([current_df, pd.DataFrame([row])], ignore_index=True)
            
            # Escribir todo de vuelta
            return self.write_dataframe_to_sheet(current_df, sheet_id, sheet_name)
            
        except Exception as e:
            st.error("Error actualizando filas: " + str(e))
            print("ERROR actualizando filas:", str(e))
            return False