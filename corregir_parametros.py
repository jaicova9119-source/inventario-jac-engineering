import pandas as pd

print("Corrigiendo archivo de parametros...")

# Leer archivo actual
df = pd.read_excel('config/parametros_stock.xlsx')

print("Columnas actuales:", list(df.columns))

# Renombrar columnas al formato correcto
df.columns = [
    'Codigo',
    'Descripcion', 
    'Stock_Minimo',
    'Stock_Maximo',
    'Lead_Time_dias',
    'Criticidad',
    'Consumo_Prom_Mensual',
    'Proveedor'
]

# Guardar con nombres corregidos
df.to_excel('config/parametros_stock.xlsx', index=False)

print("LISTO! Archivo corregido")
print("Nuevas columnas:", list(df.columns))

input("Presiona Enter...")