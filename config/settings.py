"""
Configuración general del sistema
JAC Engineering SAS
"""

import os
from datetime import datetime

# Rutas principales
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')
RAW_DATA_DIR = os.path.join(DATA_DIR, 'raw')
PROCESSED_DATA_DIR = os.path.join(DATA_DIR, 'processed')
CONFIG_DIR = os.path.join(BASE_DIR, 'config')
OUTPUTS_DIR = os.path.join(BASE_DIR, 'outputs')

# Archivos
SAP_FILE = 'sap_export.xlsx'
PARAMS_FILE = 'parametros_stock.xlsx'

# Configuración de alertas
ALERT_THRESHOLDS = {
    'critico': 0,
    'bajo': 0.2,
    'ok': 0.5
}

# Información de la empresa
COMPANY_INFO = {
    'nombre': 'JAC Engineering SAS',
    'email': 'proyectos@jacengineering.com.co',
    'website': 'https://jacengineering.com.co',
    'whatsapp': '+57 322 701 8502'
}

# Formato de fecha
DATE_FORMAT = '%Y-%m-%d'
DATETIME_FORMAT = '%Y-%m-%d %H:%M:%S'