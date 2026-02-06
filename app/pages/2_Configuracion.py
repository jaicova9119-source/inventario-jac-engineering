"""
Configuracion de Parametros
JAC Engineering SAS
VERSION CON GUARDADO VERIFICADO
"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_loader_sheets import DataLoaderSheets as DataLoader

st.set_page_config(
    page_title="Configuracion - JAC Engineering",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Configuracion de Parametros de Stock")
st.markdown("JAC Engineering SAS - Configuracion por centro y material")
st.markdown("---")

def load_params():
    loader = DataLoader()
    df = loader.load_parameters()
    
    if df.empty:
        return pd.DataFrame()
    
    if 'stock_minimo' in df.columns:
        df['stock_minimo'] = pd.to_numeric(df['stock_minimo'], errors='coerce').fillna(10)
    if 'stock_maximo' in df.columns:
        df['stock_maximo'] = pd.to_numeric(df['stock_maximo'], errors='coerce').fillna(50)
    if 'lead_time' in df.columns:
        df['lead_time'] = pd.to_numeric(df['lead_time'], errors='coerce').fillna(30)
    if 'consumo_mensual' in df.columns:
        df['consumo_mensual'] = pd.to_numeric(df['consumo_mensual'], errors='coerce').fillna(5.0)
    if 'nombre_tecnico' in df.columns:
        df['nombre_tecnico'] = df['nombre_tecnico'].fillna('')
    if 'proveedor' in df.columns:
        df['proveedor'] = df['proveedor'].fillna('POR CONFIGURAR')
    
    df = df[df['codigo'].notna()].copy()
    
    return df

# Cargar parámetros
df_params = load_params()

if df_params.empty:
    st.error("No se pudieron cargar los parametros")
    st.stop()

st.info("Total de registros configurados: " + str(len(df_params)))

# Búsqueda
col_search1, col_search2 = st.columns([3, 1])

with col_search1:
    busqueda = st.text_input(
        "Buscar material por codigo o descripcion",
        placeholder="Codigo o descripcion..."
    )

with col_search2:
    st.write("")
    st.write("")
    btn_buscar = st.button("Buscar", use_container_width=True)

if busqueda:
    termino = busqueda.lower().strip()
    
    mask = (
        df_params['codigo'].astype(str).str.lower().str.contains(termino, na=False) |
        df_params['descripcion'].astype(str).str.lower().str.contains(termino, na=False)
    )
    
    if 'nombre_tecnico' in df_params.columns:
        mask = mask | df_params['nombre_tecnico'].astype(str).str.lower().str.contains(termino, na=False)
    
    df_filtrado = df_params[mask].copy()
    
    if df_filtrado.empty:
        st.warning("No se encontraron materiales con: " + busqueda)
    else:
        st.success("Encontrados: " + str(len(df_filtrado)) + " materiales")
        
        if 'centro' in df_filtrado.columns:
            opciones = []
            indices_reales = []
            
            for idx in df_filtrado.index:
                codigo = str(df_filtrado.loc[idx, 'codigo'])
                desc = str(df_filtrado.loc[idx, 'descripcion'])[:40]
                centro = str(df_filtrado.loc[idx, 'centro'])
                
                texto = codigo + " [" + centro + "] - " + desc
                opciones.append(texto)
                indices_reales.append(idx)
            
            seleccion = st.selectbox(
                "Selecciona el material a configurar:",
                range(len(opciones)),
                format_func=lambda x: opciones[x]
            )
            
            if seleccion is not None:
                idx_real = indices_reales[seleccion]
                material = df_params.loc[idx_real]
                
                st.markdown("---")
                st.markdown("### Informacion del Material")
                
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.info("**Codigo:** " + str(material['codigo']))
                    st.info("**Centro:** " + str(material['centro']))
                
                with col2:
                    st.info("**Descripcion SAP:** " + str(material['descripcion']))
                
                with col3:
                    if 'Categoria' in material.index:
                        st.info("**Categoria:** " + str(material['Categoria']))
                
                # Mostrar valor actual de nombre técnico
                nombre_actual = str(material.get('nombre_tecnico', ''))
                if nombre_actual and nombre_actual != 'nan' and nombre_actual != '':
                    st.info("📝 Nombre Técnico actual: **" + nombre_actual + "**")
                else:
                    st.warning("⚠️ Este material no tiene Nombre Técnico configurado")
                
                st.markdown("---")
                st.markdown("### Editar Parametros")
                
                with st.form("form_edicion"):
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nombre_tecnico_actual = str(material.get('nombre_tecnico', ''))
                        if nombre_tecnico_actual == 'nan' or nombre_tecnico_actual == 'None':
                            nombre_tecnico_actual = ''
                        
                        nuevo_nombre_tecnico = st.text_area(
                            "Nombre Tecnico",
                            value=nombre_tecnico_actual,
                            height=100,
                            help="Nombre personalizado para identificar el material"
                        )
                        
                        categoria_actual = str(material.get('Categoria', 'SIN CATEGORIA'))
                        if categoria_actual == 'nan' or categoria_actual == 'None':
                            categoria_actual = 'SIN CATEGORIA'
                        
                        categorias_disponibles = [
                            'VFD',
                            'MATERIAL_ELECTRICO',
                            'ESP',
                            'INSTRUMENTACION',
                            'CONTROL',
                            'OTROS'
                        ]
                        
                        if categoria_actual in categorias_disponibles:
                            idx_cat = categorias_disponibles.index(categoria_actual)
                        else:
                            idx_cat = 0
                        
                        nueva_categoria = st.selectbox(
                            "Categoria",
                            categorias_disponibles,
                            index=idx_cat
                        )
                    
                    with col2:
                        stock_min_actual = int(float(material.get('stock_minimo', 10)))
                        nuevo_stock_minimo = st.number_input(
                            "Stock Minimo",
                            min_value=0,
                            value=stock_min_actual,
                            step=1,
                            help="Cantidad minima en stock"
                        )
                        
                        stock_max_actual = int(float(material.get('stock_maximo', 50)))
                        if stock_max_actual < nuevo_stock_minimo:
                            stock_max_actual = nuevo_stock_minimo + 10
                        
                        nuevo_stock_maximo = st.number_input(
                            "Stock Maximo",
                            min_value=nuevo_stock_minimo,
                            value=stock_max_actual,
                            step=1,
                            help="Cantidad maxima en stock"
                        )
                        
                        lead_time_actual = int(float(material.get('lead_time', 30)))
                        nuevo_lead_time = st.number_input(
                            "Lead Time (dias)",
                            min_value=1,
                            value=lead_time_actual,
                            step=1
                        )
                    
                    with col3:
                        consumo_actual = float(material.get('consumo_mensual', 5.0))
                        nuevo_consumo = st.number_input(
                            "Consumo Promedio Mensual",
                            min_value=0.0,
                            value=consumo_actual,
                            step=0.5
                        )
                        
                        criticidades = ['A', 'B', 'C']
                        crit_actual = str(material.get('criticidad', 'B'))
                        if crit_actual in criticidades:
                            idx_crit = criticidades.index(crit_actual)
                        else:
                            idx_crit = 1
                        
                        nueva_criticidad = st.selectbox(
                            "Criticidad",
                            criticidades,
                            index=idx_crit
                        )
                        
                        proveedor_actual = str(material.get('proveedor', 'POR CONFIGURAR'))
                        if proveedor_actual == 'nan' or proveedor_actual == 'None':
                            proveedor_actual = 'POR CONFIGURAR'
                        
                        nuevo_proveedor = st.text_input(
                            "Proveedor",
                            value=proveedor_actual
                        )
                    
                    submitted = st.form_submit_button(
                        "💾 GUARDAR CAMBIOS",
                        use_container_width=True,
                        type="primary"
                    )
                    
                    if submitted:
                        with st.spinner("Guardando cambios en Google Sheets..."):
                            
                            codigo_mat = str(material['codigo'])
                            centro_mat = str(material['centro'])
                            
                            # Aplicar nombre técnico y categoría a TODOS los centros
                            mask_global = df_params['codigo'] == codigo_mat
                            registros_afectados = int(mask_global.sum())
                            
                            df_params.loc[mask_global, 'nombre_tecnico'] = nuevo_nombre_tecnico
                            df_params.loc[mask_global, 'Categoria'] = nueva_categoria
                            
                            # Aplicar parámetros específicos solo al centro seleccionado
                            mask_especifico = (df_params['codigo'] == codigo_mat) & (df_params['centro'] == centro_mat)
                            
                            df_params.loc[mask_especifico, 'stock_minimo'] = float(nuevo_stock_minimo)
                            df_params.loc[mask_especifico, 'stock_maximo'] = float(nuevo_stock_maximo)
                            df_params.loc[mask_especifico, 'lead_time'] = float(nuevo_lead_time)
                            df_params.loc[mask_especifico, 'consumo_mensual'] = float(nuevo_consumo)
                            df_params.loc[mask_especifico, 'criticidad'] = nueva_criticidad
                            df_params.loc[mask_especifico, 'proveedor'] = nuevo_proveedor
                            
                            # Mostrar resumen de cambios
                            st.info("📊 Resumen de cambios:")
                            st.write("**Cambios globales** (aplicados a " + str(registros_afectados) + " registros con código " + codigo_mat + "):")
                            st.write("- Nombre Técnico: **" + nuevo_nombre_tecnico + "**")
                            st.write("- Categoría: **" + nueva_categoria + "**")
                            st.write("")
                            st.write("**Cambios específicos** (solo centro " + centro_mat + "):")
                            st.write("- Stock Mínimo: " + str(nuevo_stock_minimo))
                            st.write("- Stock Máximo: " + str(nuevo_stock_maximo))
                            
                            # Guardar en Google Sheets
                            st.write("Escribiendo en Google Sheets...")
                            
                            loader = DataLoader()
                            
                            try:
                                success = loader.save_parameters(df_params)
                                
                                if success:
                                    st.success("✅ GUARDADO EXITOSO")
                                    st.balloons()
                                    
                                    st.info("Recargando en 2 segundos para ver los cambios...")
                                    
                                    # Limpiar cache
                                    st.cache_data.clear()
                                    
                                    import time
                                    time.sleep(2)
                                    st.rerun()
                                else:
                                    st.error("❌ ERROR: No se pudo guardar")
                                    st.warning("Verifica:")
                                    st.write("- Conexión a Internet")
                                    st.write("- Permisos de la hoja de Google Sheets")
                                    st.write("- ID correcto en google_config.py")
                            
                            except Exception as e:
                                st.error("❌ EXCEPCIÓN al guardar:")
                                st.code(str(e))
                                import traceback
                                st.code(traceback.format_exc())
        else:
            st.error("Los datos no tienen columna de centro")

st.markdown("---")

st.markdown("""
<div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
    <strong>JAC Engineering SAS</strong> - Electrical Systems & Data Intelligence<br>
    proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502
</div>
""", unsafe_allow_html=True)