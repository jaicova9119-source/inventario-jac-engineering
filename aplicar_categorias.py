"""
Aplicar categorias desde archivo de mapeo
JAC Engineering SAS
"""

import pandas as pd
import os

print("="*70)
print("  APLICAR CATEGORIAS DESDE MAPEO MANUAL")
print("  JAC Engineering SAS")
print("="*70)
print()

try:
    params_file = 'config/parametros_stock_por_centro.xlsx'
    mapeo_file = 'config/mapeo_categorias.xlsx'
    
    if not os.path.exists(mapeo_file):
        print("ERROR: No existe " + mapeo_file)
        print("Primero ejecuta: python crear_categorias.py")
        input("\nPresiona Enter...")
        exit()
    
    print("[1/2] Leyendo archivos...")
    df_params = pd.read_excel(params_file)
    df_mapeo = pd.read_excel(mapeo_file)
    
    print("Parametros: " + str(len(df_params)) + " registros")
    print("Mapeo: " + str(len(df_mapeo)) + " categorias")
    print()
    
    print("[2/2] Aplicando categorias...")
    
    # Crear diccionario de mapeo
    mapeo_dict = dict(zip(df_mapeo['Codigo'].astype(str), df_mapeo['Categoria']))
    
    # Aplicar
    df_params['Categoria'] = df_params['Codigo'].astype(str).map(mapeo_dict)
    
    # Llenar valores faltantes
    df_params['Categoria'] = df_params['Categoria'].fillna('OTROS')
    
    # Guardar
    df_params.to_excel(params_file, index=False)
    
    print()
    print("="*70)
    print("  CATEGORIAS APLICADAS CON EXITO")
    print("="*70)
    print()
    
    resumen = df_params['Categoria'].value_counts()
    for cat, count in resumen.items():
        print("  " + cat + ": " + str(count))
    print()
    
except Exception as e:
    print("ERROR: " + str(e))
    import traceback
    traceback.print_exc()

input("\nPresiona Enter...")