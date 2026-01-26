import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from config.settings import CONFIG_DIR, PARAMS_FILE

st.set_page_config(
    page_title="Configuracion - JAC Engineering",
    page_icon="⚙️",
    layout="wide"
)

st.title("Configuracion de Parametros de Stock")
st.markdown("JAC Engineering SAS")
st.markdown("---")

params_file_path = os.path.join(CONFIG_DIR, PARAMS_FILE)

def load_params():
    try:
        df = pd.read_excel(params_file_path)
        df['Codigo'] = df['Codigo'].astype(str)
        return df
    except Exception as e:
        st.error("Error: " + str(e))
        return pd.DataFrame()

def save_params(df):
    try:
        df.to_excel(params_file_path, index=False)
        return True
    except Exception as e:
        st.error("Error: " + str(e))
        return False

tab1, tab2 = st.tabs(["Editar Individual", "Editar Tabla"])

with tab1:
    st.subheader("Buscar y Editar Material")
    
    df_params = load_params()
    
    if not df_params.empty:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            buscar = st.text_input("Buscar", placeholder="Codigo o descripcion")
        
        with col2:
            st.write("")
            st.write("")
            buscar_btn = st.button("Buscar", use_container_width=True)
        
        if buscar:
            mask = (
                df_params['Codigo'].astype(str).str.contains(buscar, case=False, na=False) |
                df_params['Descripcion'].astype(str).str.contains(buscar, case=False, na=False)
            )
            resultados = df_params[mask]
            
            if not resultados.empty:
                st.success("Encontrados: " + str(len(resultados)))
                
                opciones = []
                for idx in resultados.index:
                    codigo = str(resultados.loc[idx, 'Codigo'])
                    desc = str(resultados.loc[idx, 'Descripcion'])[:50]
                    opciones.append(codigo + " - " + desc)
                
                seleccion = st.selectbox("Material:", options=range(len(opciones)), format_func=lambda x: opciones[x])
                
                if seleccion is not None:
                    material_idx = resultados.index[seleccion]
                    material = resultados.iloc[seleccion]
                    
                    st.markdown("---")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        st.info("Codigo: " + str(material['Codigo']))
                        st.info("Material: " + str(material['Descripcion']))
                        
                        nuevo_minimo = st.number_input("Stock Minimo", min_value=0, value=int(material['Stock_Minimo']), step=1)
                        nuevo_maximo = st.number_input("Stock Maximo", min_value=0, value=int(material['Stock_Maximo']), step=1)
                    
                    with col2:
                        crit_actual = str(material['Criticidad']).upper()
                        if crit_actual not in ['A', 'B', 'C']:
                            crit_actual = 'B'
                        
                        nueva_criticidad = st.selectbox("Criticidad", options=['A', 'B', 'C'], index=['A', 'B', 'C'].index(crit_actual))
                        nuevo_proveedor = st.text_input("Proveedor", value=str(material['Proveedor']))
                    
                    if nuevo_minimo > nuevo_maximo:
                        st.warning("Minimo no puede ser mayor que maximo")
                    
                    col_btn1, col_btn2 = st.columns(2)
                    
                    with col_btn1:
                        if st.button("Guardar", type="primary", use_container_width=True):
                            if nuevo_minimo <= nuevo_maximo:
                                df_params.loc[material_idx, 'Stock_Minimo'] = nuevo_minimo
                                df_params.loc[material_idx, 'Stock_Maximo'] = nuevo_maximo
                                df_params.loc[material_idx, 'Criticidad'] = nueva_criticidad
                                df_params.loc[material_idx, 'Proveedor'] = nuevo_proveedor
                                
                                if save_params(df_params):
                                    st.success("Guardado")
                                    st.balloons()
                            else:
                                st.error("Minimo no puede ser mayor que maximo")
                    
                    with col_btn2:
                        if st.button("Cancelar", use_container_width=True):
                            st.rerun()
            else:
                st.warning("No encontrado: " + buscar)

with tab2:
    st.subheader("Editar Tabla Completa")
    
    df_params = load_params()
    
    if not df_params.empty:
        edited_df = st.data_editor(
            df_params,
            use_container_width=True,
            num_rows="fixed",
            column_config={
                "Codigo": st.column_config.TextColumn("Codigo", disabled=True),
                "Descripcion": st.column_config.TextColumn("Descripcion", disabled=True),
                "Stock_Minimo": st.column_config.NumberColumn("Stock Minimo", min_value=0),
                "Stock_Maximo": st.column_config.NumberColumn("Stock Maximo", min_value=0),
                "Criticidad": st.column_config.SelectboxColumn("Criticidad", options=['A', 'B', 'C'])
            },
            height=500
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Guardar Todo", type="primary", use_container_width=True):
                if save_params(edited_df):
                    st.success("Guardado")
                    st.balloons()
        
        with col2:
            csv = edited_df.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar CSV", csv, "parametros.csv", use_container_width=True)

st.markdown("---")
st.info("Despues de guardar, actualiza los datos en la pagina principal")