import pandas as pd 
import os 
 
print("Verificando archivos...") 
print("") 
try: 
    df = pd.read_excel('data/raw/sap_export.xlsx') 
    print("SAP OK - Filas:", len(df)) 
    print("Columnas:", list(df.columns)) 
except Exception as e: 
    print("ERROR SAP:", e) 
 
try: 
    df2 = pd.read_excel('config/parametros_stock.xlsx') 
    print("PARAMS OK - Filas:", len(df2)) 
    print("Columnas:", list(df2.columns)) 
except Exception as e: 
    print("ERROR PARAMS:", e) 
