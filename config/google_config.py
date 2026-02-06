"""
Configuracion de Google Sheets
JAC Engineering SAS
"""

# IDs de las hojas de Google Sheets
SHEETS_CONFIG = {
    'parametros': {
        'sheet_id': '1ZystDkRNpqaofy8HTMcDfJlWQNLxtoo4slyIJWpt8fY',  # Mantén el que ya tienes
        'sheet_name': 'JAC_Parametros_Stock'
    },
    'solped': {
        'sheet_id': '1rQY-RUiK7ot9ly62E3toSBOZwNH3eKFgfGFsvzpNa80',  # Mantén el que ya tienes
        'sheet_name': 'JAC_SOLPED_Historico'
    },
    'inventario_sap': {  # NUEVO
        'sheet_id': '1d959xhiNnQI48b-fhikFXWEvny8AkeGyF_aIzZbZ0wQ',  # ← ID nuevo que copiaste
        'sheet_name': 'JAC_Inventario_SAP'
    }
}

CREDENTIALS_FILE = 'config/google_credentials.json'