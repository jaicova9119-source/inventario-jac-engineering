"""
Sistema de Control de Inventario
JAC Engineering SAS
CON AUTENTICACION Y GOOGLE SHEETS
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import usuarios

if not usuarios.verificar_autenticacion():
    usuarios.mostrar_login()
    st.stop()

from src.data_loader_sheets import DataLoaderSheets as DataLoader
from src.inventory_analyzer import InventoryAnalyzer
from config.settings import COMPANY_INFO
import pandas as pd

st.set_page_config(
    page_title="Sistema de Inventario - JAC Engineering",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%);
        padding: 2rem;
        border-radius: 10px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .main-header h1 {
        color: white;
        font-size: 2.5rem;
        font-weight: bold;
        margin: 0;
    }
    .main-header p {
        color: #f0f0f0;
        font-size: 1.2rem;
        margin: 0.5rem 0 0 0;
    }
</style>
""", unsafe_allow_html=True)

col1, col2 = st.columns([1, 4])

with col1:
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo_jac.png')
    if os.path.exists(logo_path):
        st.image(logo_path, width=150)

with col2:
    st.markdown("""
    <div class="main-header">
        <h1>Sistema de Control de Inventario</h1>
        <p>JAC Engineering SAS - Electrical Systems & Data Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

usuarios.mostrar_info_usuario_sidebar()

with st.sidebar:
    st.markdown("---")
    st.markdown("### Configuracion")
    
    st.info("Datos sincronizados con Google Sheets")
    
    if st.button("Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("Los cambios se guardan automaticamente")
    
    st.markdown("---")
    st.markdown("### Contacto")
    
    st.markdown(COMPANY_INFO['nombre'])
    st.markdown("Email: " + COMPANY_INFO['email'])
    st.markdown("Web: " + COMPANY_INFO['website'])
    st.markdown("WhatsApp: " + COMPANY_INFO['whatsapp'])

def buscar_material(df, termino):
    if not termino:
        return df
    t = termino.lower().strip()
    
    mask = (
        df['codigo'].astype(str).str.lower().str.contains(t, na=False) |
        df['descripcion'].astype(str).str.lower().str.contains(t, na=False)
    )
    
    if 'nombre_tecnico' in df.columns:
        mask = mask | df['nombre_tecnico'].astype(str).str.lower().str.contains(t, na=False)
    
    if 'ubicacion' in df.columns:
        mask = mask | df['ubicacion'].astype(str).str.lower().str.contains(t, na=False)
    
    if 'centro' in df.columns:
        mask = mask | df['centro'].astype(str).str.lower().str.contains(t, na=False)
    
    if 'centro_nombre' in df.columns:
        mask = mask | df['centro_nombre'].astype(str).str.lower().str.contains(t, na=False)
    
    return df[mask]

@st.cache_data(ttl=300)
def load_data():
    loader = DataLoader()
    data = loader.merge_data()
    if data.empty:
        return None, None
    analyzer = InventoryAnalyzer(data)
    analysis = analyzer.full_analysis()
    metrics = analyzer.get_summary_metrics()
    return analysis, metrics

try:
    df, metrics = load_data()
    
    if df is None:
        st.error("No se pudieron cargar los datos")
        st.info("Verifica la conexion con Google Sheets")
        st.stop()
    
    st.markdown("### Busqueda de Materiales")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        termino = st.text_input(
            "buscar",
            placeholder="Codigo, descripcion, nombre tecnico, ubicacion...",
            label_visibility="collapsed"
        )
    with col_s2:
        btn_buscar = st.button("Buscar", use_container_width=True)
    
    if termino:
        resultados = buscar_material(df, termino)
        
        if not resultados.empty:
            st.success("Encontrados: " + str(len(resultados)) + " materiales")
            
            cols_d = ['codigo', 'descripcion', 'nombre_tecnico', 'centro', 'centro_nombre', 'ubicacion',
                     'stock_actual', 'stock_minimo', 'stock_maximo', 'estado', 
                     'criticidad', 'proveedor']
            
            cols_exist = [col for col in cols_d if col in resultados.columns]
            
            st.dataframe(resultados[cols_exist], use_container_width=True, height=400)
            
            csv_r = resultados.to_csv(index=False).encode('utf-8')
            st.download_button(
                "Descargar Resultados",
                csv_r,
                "busqueda_" + termino + ".csv",
                "text/csv",
                use_container_width=True
            )
            st.markdown("---")
        else:
            st.warning("No se encontraron materiales con: " + termino)
            st.markdown("---")
    
    st.markdown("### Indicadores Clave")
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    with c1:
        st.metric("Total", metrics['total_materiales'])
    with c2:
        st.metric("Criticos", metrics['criticos'])
    with c3:
        st.metric("Bajo", metrics['bajo'])
    with c4:
        st.metric("OK", metrics['ok'])
    with c5:
        st.metric("Valor", "${:,.0f}".format(metrics['valor_total_stock']))
    
    st.markdown("---")
    
    st.markdown("### Accion Inmediata")
    
    critical = df[df['estado'].isin(['CRITICO', 'BAJO'])].copy()
    
    if not critical.empty:
        critical = critical.sort_values(['estado', 'criticidad'])
        
        cols_c = ['codigo', 'descripcion', 'nombre_tecnico', 'centro', 'centro_nombre', 'ubicacion',
                 'stock_actual', 'stock_minimo', 'brecha_minimo', 
                 'estado', 'cantidad_comprar', 'proveedor']
        
        cols_exist_c = [col for col in cols_c if col in critical.columns]
        
        st.dataframe(critical[cols_exist_c], use_container_width=True, height=400)
        
        csv = critical.to_csv(index=False).encode('utf-8')
        st.download_button(
            "Descargar Lista de Compras",
            csv,
            "compras_" + pd.Timestamp.now().strftime('%Y%m%d') + ".csv",
            "text/csv",
            use_container_width=True
        )
    else:
        st.success("No hay materiales criticos")

except Exception as e:
    st.error("Error: " + str(e))
    import traceback
    st.code(traceback.format_exc())

st.markdown("---")
st.markdown("JAC Engineering SAS - Electrical Systems & Data Intelligence")
st.caption("proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502")
st.caption("v2.0 Google Sheets - 2026 JAC Engineering")