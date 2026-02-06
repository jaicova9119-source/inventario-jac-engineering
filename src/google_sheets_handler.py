"""
Manejador de Google Sheets
JAC Engineering SAS
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
        """Autentica con Google Sheets"""
        try:
            if hasattr(st, 'secrets') and 'gcp_service_account' in st.secrets:
                credentials_dict = dict(st.secrets['gcp_service_account'])
                credentials = Credentials.from_service_account_info(
                    credentials_dict,
                    scopes=self.scopes
                )
            else:
                credentials_file = 'config/google_credentials.json'
                if not os.path.exists(credentials_file):
                    raise FileNotFoundError("No se encontro google_credentials.json")
                
                credentials = Credentials.from_service_account_file(
                    credentials_file,
                    scopes=self.scopes
                )
            
            self.client = gspread.authorize(credentials)
            
        except Exception as e:
            st.error("Error de autenticacion: " + str(e))
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
            return False