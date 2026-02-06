"""
Gestion por Centros
JAC Engineering SAS
"""

import streamlit as st
import sys
import os
import pandas as pd

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_loader_sheets import DataLoaderSheets as DataLoader
from src.inventory_analyzer import InventoryAnalyzer

st.set_page_config(
    page_title="Gestion Centros - JAC Engineering",
    page_icon="🏭",
    layout="wide"
)

st.title("🏭 Gestion por Centros de Costo")
st.markdown("JAC Engineering SAS - Analisis individual por bodega")
st.markdown("---")

@st.cache_data(ttl=300)
def load_data():
    loader = DataLoader()
    data = loader.merge_data()
    if data.empty:
        return None
    analyzer = InventoryAnalyzer(data)
    return analyzer.full_analysis()

df = load_data()

if df is None or df.empty:
    st.error("No se pudieron cargar los datos")
    st.stop()

if 'centro' not in df.columns:
    st.error("Los datos no tienen columna de centro")
    st.stop()

centros_unicos = sorted(df['centro'].unique().tolist())

col_select1, col_select2 = st.columns([2, 2])

with col_select1:
    centro_seleccionado = st.selectbox(
        "Selecciona el Centro:",
        centros_unicos,
        format_func=lambda x: x + " - " + df[df['centro'] == x]['centro_nombre'].iloc[0] if 'centro_nombre' in df.columns else x
    )

with col_select2:
    if 'Categoria' in df.columns:
        categorias = ['Todas'] + sorted(df['Categoria'].unique().tolist())
        categoria_seleccionada = st.selectbox("Categoria:", categorias)
    else:
        categoria_seleccionada = 'Todas'

df_centro = df[df['centro'] == centro_seleccionado].copy()

if categoria_seleccionada != 'Todas':
    df_centro = df_centro[df_centro['Categoria'] == categoria_seleccionada].copy()

if df_centro.empty:
    st.warning("No hay datos para este centro y categoria")
    st.stop()

nombre_centro = df_centro['centro_nombre'].iloc[0] if 'centro_nombre' in df_centro.columns else centro_seleccionado

if categoria_seleccionada != 'Todas':
    st.markdown("## " + centro_seleccionado + " - " + nombre_centro + " | Categoria: " + categoria_seleccionada)
else:
    st.markdown("## " + centro_seleccionado + " - " + nombre_centro)

st.markdown("---")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    st.metric("Total Materiales", len(df_centro))
with col2:
    criticos = len(df_centro[df_centro['estado'] == 'CRITICO'])
    st.metric("Criticos", criticos)
with col3:
    bajo = len(df_centro[df_centro['estado'] == 'BAJO'])
    st.metric("Bajo", bajo)
with col4:
    ok = len(df_centro[df_centro['estado'] == 'OK'])
    st.metric("OK", ok)
with col5:
    valor_total = df_centro['valor_stock'].sum() if 'valor_stock' in df_centro.columns else 0
    st.metric("Valor Total", "${:,.0f}".format(valor_total))

st.markdown("---")

if categoria_seleccionada == 'Todas' and 'Categoria' in df_centro.columns:
    st.markdown("### Resumen por Categoria")
    
    resumen_cat = df_centro.groupby('Categoria').agg({
        'codigo': 'count',
        'estado': lambda x: (x == 'CRITICO').sum()
    }).reset_index()
    
    resumen_cat.columns = ['Categoria', 'Total Materiales', 'Criticos']
    
    st.dataframe(resumen_cat, use_container_width=True)
    
    st.markdown("---")

df_criticos_centro = df_centro[df_centro['estado'].isin(['CRITICO', 'BAJO'])].copy()

if not df_criticos_centro.empty:
    st.markdown("### Materiales Criticos y Bajos")
    
    df_criticos_centro = df_criticos_centro.sort_values('estado')
    
    cols_mostrar = ['codigo', 'descripcion', 'nombre_tecnico', 'ubicacion', 'stock_actual', 
                   'stock_minimo', 'estado', 'cantidad_comprar', 'proveedor']
    
    if 'Categoria' in df_criticos_centro.columns:
        cols_mostrar.insert(2, 'Categoria')
    
    cols_exist = [col for col in cols_mostrar if col in df_criticos_centro.columns]
    
    st.dataframe(df_criticos_centro[cols_exist], use_container_width=True, height=400)
    
    csv = df_criticos_centro.to_csv(index=False).encode('utf-8')
    
    if categoria_seleccionada != 'Todas':
        filename = "compras_" + centro_seleccionado + "_" + categoria_seleccionada + "_" + pd.Timestamp.now().strftime('%Y%m%d') + ".csv"
    else:
        filename = "compras_" + centro_seleccionado + "_" + pd.Timestamp.now().strftime('%Y%m%d') + ".csv"
    
    st.download_button(
        "Descargar Lista de Compras",
        csv,
        filename,
        "text/csv",
        use_container_width=True
    )
else:
    st.success("No hay materiales criticos en este centro")

st.markdown("---")

st.markdown("### Inventario Completo del Centro")

cols_inventario = ['codigo', 'descripcion', 'nombre_tecnico', 'ubicacion', 'stock_actual',
                  'stock_minimo', 'stock_maximo', 'estado', 'proveedor']

if 'Categoria' in df_centro.columns:
    cols_inventario.insert(2, 'Categoria')

cols_exist_inv = [col for col in cols_inventario if col in df_centro.columns]

st.dataframe(df_centro[cols_exist_inv], use_container_width=True, height=400)

csv_completo = df_centro.to_csv(index=False).encode('utf-8')

if categoria_seleccionada != 'Todas':
    filename_completo = "inventario_" + centro_seleccionado + "_" + categoria_seleccionada + "_" + pd.Timestamp.now().strftime('%Y%m%d') + ".csv"
else:
    filename_completo = "inventario_" + centro_seleccionado + "_" + pd.Timestamp.now().strftime('%Y%m%d') + ".csv"

st.download_button(
    "Descargar Inventario Completo",
    csv_completo,
    filename_completo,
    "text/csv",
    use_container_width=True
)

st.markdown("---")

st.markdown("""
<div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
    <strong>JAC Engineering SAS</strong> - Electrical Systems & Data Intelligence<br>
    proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502
</div>
""", unsafe_allow_html=True)