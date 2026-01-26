"""
Verificar archivos Excel
JAC Engineering SAS
"""

import pandas as pd
import os

print("="*60)
print("  VERIFICACION DE ARCHIVOS")
print("="*60)
print()

# Verificar archivo SAP
print("[1/2] Verificando sap_export.xlsx...")
sap_path = 'data/raw/sap_export.xlsx'

if os.path.exists(sap_path):
    print(f"✓ Archivo existe: {sap_path}")
    try:
        df_sap = pd.read_excel(sap_path)
        print(f"✓ Se pudo leer correctamente")
        print(f"✓ Numero de filas: {len(df_sap)}")
        print(f"✓ Columnas encontradas: {list(df_sap.columns)}")
        print()
        print("Primeras 3 filas:")
        print(df_sap.head(3))
    except Exception as e:
        print(f"✗ ERROR al leer archivo: {e}")
else:
    print(f"✗ Archivo NO existe: {sap_path}")

print()
print("-"*60)
print()

# Verificar archivo de parametros
print("[2/2] Verificando parametros_stock.xlsx...")
params_path = 'config/parametros_stock.xlsx'

if os.path.exists(params_path):
    print(f"✓ Archivo existe: {params_path}")
    try:
        df_params = pd.read_excel(params_path)
        print(f"✓ Se pudo leer correctamente")
        print(f"✓ Numero de filas: {len(df_params)}")
        print(f"✓ Columnas encontradas: {list(df_params.columns)}")
        print()
        print("Primeras 3 filas:")
        print(df_params.head(3))
    except Exception as e:
        print(f"✗ ERROR al leer archivo: {e}")
else:
    print(f"✗ Archivo NO existe: {params_path}")

print()
print("="*60)
input("Presiona Enter para cerrar...")