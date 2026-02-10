"""
Configuracion de Parametros
JAC Engineering SAS
VERSION CON OBSERVACIONES Y FIX STOCK MAXIMO
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
st.markdown("JAC Engineering SAS")
st.markdown("---")

def load_params():
    loader = DataLoader()
    df = loader.load_parameters()
    
    if df.empty:
        return pd.DataFrame()
    
    # Conversiones numéricas
    for col in ['stock_minimo', 'stock_maximo', 'lead_time', 'consumo_mensual']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # Conversiones de texto
    for col in ['nombre_tecnico', 'proveedor', 'observaciones']:
        if col in df.columns:
            df[col] = df[col].fillna('')
        else:
            df[col] = ''
    
    df = df[df['codigo'].notna()].copy()
    
    return df

# ============================================================
# CARGAR DATOS
# ============================================================

df_params = load_params()

if df_params.empty:
    st.error("No se pudieron cargar los parametros")
    st.stop()

# Agregar columna observaciones si no existe
if 'observaciones' not in df_params.columns:
    df_params['observaciones'] = ''

st.info("Total de registros configurados: " + str(len(df_params)))

# ============================================================
# BÚSQUEDA
# ============================================================

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

# ============================================================
# RESULTADOS Y EDICIÓN
# ============================================================

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
        
        # Construir opciones del selector
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
            
            # ============================================================
            # INFO DEL MATERIAL
            # ============================================================
            
            st.markdown("### 📋 Información del Material")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.info("**Código SAP:** " + str(material['codigo']))
                st.info("**Centro:** " + str(material['centro']))
            
            with col2:
                st.info("**Descripción SAP:** " + str(material['descripcion']))
            
            with col3:
                cat_actual = str(material.get('Categoria', 'SIN CATEGORIA'))
                if cat_actual == 'nan':
                    cat_actual = 'SIN CATEGORIA'
                st.info("**Categoría:** " + cat_actual)
            
            # Mostrar nombre técnico actual
            nombre_actual = str(material.get('nombre_tecnico', ''))
            if nombre_actual and nombre_actual not in ['nan', 'None', '']:
                st.success("📝 Nombre Técnico actual: **" + nombre_actual + "**")
            else:
                st.warning("⚠️ Este material no tiene Nombre Técnico configurado")
            
            # Mostrar observaciones actuales si existen
            obs_actual = str(material.get('observaciones', ''))
            if obs_actual and obs_actual not in ['nan', 'None', '']:
                st.info("💬 Observación actual: " + obs_actual)
            
            st.markdown("---")
            
            # ============================================================
            # LEER VALORES ACTUALES CORRECTAMENTE
            # ============================================================
            
            # Leer stock_minimo actual
            try:
                stock_min_actual = int(float(str(material.get('stock_minimo', 0)).replace(',', '.')))
            except:
                stock_min_actual = 0
            
            # Leer stock_maximo actual
            try:
                stock_max_actual = int(float(str(material.get('stock_maximo', 0)).replace(',', '.')))
            except:
                stock_max_actual = 0
            
            # Asegurar que max >= min
            if stock_max_actual < stock_min_actual:
                stock_max_actual = stock_min_actual
            
            # Leer lead_time actual
            try:
                lead_time_actual = int(float(str(material.get('lead_time', 30)).replace(',', '.')))
            except:
                lead_time_actual = 30
            
            # Leer consumo actual
            try:
                consumo_actual = float(str(material.get('consumo_mensual', 0)).replace(',', '.'))
            except:
                consumo_actual = 0.0
            
            # ============================================================
            # FORMULARIO DE EDICIÓN
            # ============================================================
            
            st.markdown("### ✏️ Editar Parámetros")
            
            # Mostrar valores actuales como referencia
            with st.expander("📊 Valores actuales en Google Sheets", expanded=False):
                st.write("Stock Mínimo guardado:", stock_min_actual)
                st.write("Stock Máximo guardado:", stock_max_actual)
                st.write("Lead Time guardado:", lead_time_actual)
                st.write("Consumo guardado:", consumo_actual)
            
            with st.form("form_edicion_" + str(idx_real)):
                
                # FILA 1: Nombre técnico y Categoría
                col_f1, col_f2 = st.columns(2)
                
                with col_f1:
                    nombre_tecnico_val = str(material.get('nombre_tecnico', ''))
                    if nombre_tecnico_val in ['nan', 'None']:
                        nombre_tecnico_val = ''
                    
                    nuevo_nombre_tecnico = st.text_area(
                        "Nombre Técnico (aplica a TODOS los centros con este código)",
                        value=nombre_tecnico_val,
                        height=80,
                        help="Se aplicará a todos los centros que tengan el mismo código de material"
                    )
                
                with col_f2:
                    categorias_disponibles = [
                        'VFD',
                        'MATERIAL_ELECTRICO',
                        'ESP',
                        'INSTRUMENTACION',
                        'CONTROL',
                        'OTROS'
                    ]
                    
                    cat_val = str(material.get('Categoria', 'VFD'))
                    if cat_val in ['nan', 'None', '']:
                        cat_val = 'VFD'
                    
                    if cat_val in categorias_disponibles:
                        idx_cat = categorias_disponibles.index(cat_val)
                    else:
                        idx_cat = 0
                    
                    nueva_categoria = st.selectbox(
                        "Categoría",
                        categorias_disponibles,
                        index=idx_cat
                    )
                
                # FILA 2: Stocks y Lead Time
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    nuevo_stock_minimo = st.number_input(
                        "Stock Mínimo",
                        min_value=0,
                        max_value=99999,
                        value=stock_min_actual,
                        step=1,
                        help="Cantidad mínima requerida en stock"
                    )
                
                with col_s2:
                    # CRÍTICO: usar max_value alto y value fijo
                    nuevo_stock_maximo = st.number_input(
                        "Stock Máximo",
                        min_value=0,
                        max_value=99999,
                        value=stock_max_actual,
                        step=1,
                        help="Cantidad máxima recomendada en stock"
                    )
                
                with col_s3:
                    nuevo_lead_time = st.number_input(
                        "Lead Time (días)",
                        min_value=1,
                        max_value=999,
                        value=max(1, lead_time_actual),
                        step=1
                    )
                
                # FILA 3: Consumo, Criticidad y Proveedor
                col_c1, col_c2, col_c3 = st.columns(3)
                
                with col_c1:
                    nuevo_consumo = st.number_input(
                        "Consumo Promedio Mensual",
                        min_value=0.0,
                        max_value=99999.0,
                        value=float(consumo_actual),
                        step=0.5
                    )
                
                with col_c2:
                    criticidades = ['A', 'B', 'C']
                    crit_val = str(material.get('criticidad', 'B'))
                    if crit_val in ['nan', 'None', '']:
                        crit_val = 'B'
                    if crit_val not in criticidades:
                        crit_val = 'B'
                    idx_crit = criticidades.index(crit_val)
                    
                    nueva_criticidad = st.selectbox(
                        "Criticidad",
                        criticidades,
                        index=idx_crit,
                        help="A=Alta, B=Media, C=Baja"
                    )
                
                with col_c3:
                    proveedor_val = str(material.get('proveedor', 'POR CONFIGURAR'))
                    if proveedor_val in ['nan', 'None', '']:
                        proveedor_val = 'POR CONFIGURAR'
                    
                    nuevo_proveedor = st.text_input(
                        "Proveedor",
                        value=proveedor_val
                    )
                
                # FILA 4: OBSERVACIONES (NUEVA)
                st.markdown("---")
                st.markdown("**💬 Observaciones del Material**")
                
                obs_val = str(material.get('observaciones', ''))
                if obs_val in ['nan', 'None']:
                    obs_val = ''
                
                nuevas_observaciones = st.text_area(
                    "Observaciones",
                    value=obs_val,
                    height=100,
                    placeholder="Ejemplo: Este material también aparece con el código 42780. "
                                "Mismo componente diferente referencia SAP. "
                                "Pendiente depuración en SAP...",
                    help="Notas adicionales: códigos duplicados, equivalencias, aclaraciones técnicas, etc."
                )
                
                submitted = st.form_submit_button(
                    "💾 GUARDAR CAMBIOS",
                    use_container_width=True,
                    type="primary"
                )
                
                if submitted:
                    with st.spinner("Guardando en Google Sheets..."):
                        
                        codigo_mat = str(material['codigo'])
                        centro_mat = str(material['centro'])
                        
                        # Validar stock máximo >= stock mínimo
                        if nuevo_stock_maximo < nuevo_stock_minimo:
                            st.error("❌ El Stock Máximo (" + str(nuevo_stock_maximo) + ") no puede ser menor que el Stock Mínimo (" + str(nuevo_stock_minimo) + ")")
                            st.stop()
                        
                        # Aplicar nombre técnico, categoría y observaciones
                        # a TODOS los centros con el mismo código
                        mask_global = df_params['codigo'].astype(str) == codigo_mat
                        registros_afectados = int(mask_global.sum())
                        
                        df_params.loc[mask_global, 'nombre_tecnico'] = nuevo_nombre_tecnico
                        df_params.loc[mask_global, 'Categoria'] = nueva_categoria
                        df_params.loc[mask_global, 'observaciones'] = nuevas_observaciones
                        
                        # Aplicar parámetros específicos al centro seleccionado
                        mask_especifico = (
                            (df_params['codigo'].astype(str) == codigo_mat) &
                            (df_params['centro'].astype(str) == centro_mat)
                        )
                        
                        df_params.loc[mask_especifico, 'stock_minimo'] = int(nuevo_stock_minimo)
                        df_params.loc[mask_especifico, 'stock_maximo'] = int(nuevo_stock_maximo)
                        df_params.loc[mask_especifico, 'lead_time'] = int(nuevo_lead_time)
                        df_params.loc[mask_especifico, 'consumo_mensual'] = float(nuevo_consumo)
                        df_params.loc[mask_especifico, 'criticidad'] = nueva_criticidad
                        df_params.loc[mask_especifico, 'proveedor'] = nuevo_proveedor
                        
                        # Mostrar resumen
                        st.markdown("##### 📊 Resumen de cambios:")
                        
                        st.write("**Cambios globales** (aplicados a " + str(registros_afectados) + " registros con código " + codigo_mat + "):")
                        st.write("- Nombre Técnico: **" + nuevo_nombre_tecnico + "**")
                        st.write("- Categoría: **" + nueva_categoria + "**")
                        if nuevas_observaciones:
                            st.write("- Observaciones: **" + nuevas_observaciones[:60] + "...**")
                        
                        st.write("**Cambios específicos** (solo centro " + centro_mat + "):")
                        st.write("- Stock Mínimo: **" + str(nuevo_stock_minimo) + "**")
                        st.write("- Stock Máximo: **" + str(nuevo_stock_maximo) + "**")
                        st.write("- Lead Time: **" + str(nuevo_lead_time) + " días**")
                        
                        st.write("Escribiendo en Google Sheets...")
                        
                        loader = DataLoader()
                        
                        try:
                            success = loader.save_parameters(df_params)
                            
                            if success:
                                st.success("✅ GUARDADO EXITOSO")
                                st.info("Stock Mín: " + str(nuevo_stock_minimo) + " | Stock Máx: " + str(nuevo_stock_maximo))
                                st.balloons()
                                st.cache_data.clear()
                                
                                import time
                                time.sleep(2)
                                st.rerun()
                            else:
                                st.error("❌ ERROR: No se pudo guardar en Google Sheets")
                        
                        except Exception as e:
                            st.error("❌ EXCEPCIÓN al guardar:")
                            st.code(str(e))
                            import traceback
                            st.code(traceback.format_exc())

st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); 
     color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
    <strong>JAC Engineering SAS</strong> - Electrical Systems & Data Intelligence<br>
    proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502
</div>
""", unsafe_allow_html=True)