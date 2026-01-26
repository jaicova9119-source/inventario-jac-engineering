"""
Sistema de Control de Inventario
JAC Engineering SAS
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.data_loader import DataLoader
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
    .stButton > button {
        background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 2rem;
        font-weight: bold;
    }
    .section-card {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        border-left: 4px solid #1B8E9E;
        margin-bottom: 1rem;
    }
    .section-title {
        color: #134B70;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .search-box {
        background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%);
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1.5rem;
    }
    .footer {
        background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%);
        color: white;
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-top: 3rem;
    }
    .footer a {
        color: #F39C12;
        text-decoration: none;
        font-weight: bold;
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
        <h1>📦 Sistema de Control de Inventario</h1>
        <p>JAC Engineering SAS - Electrical Systems & Data Intelligence</p>
    </div>
    """, unsafe_allow_html=True)

with st.sidebar:
    logo_path = os.path.join(os.path.dirname(__file__), 'assets', 'logo_jac.png')
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    
    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    
    st.info("💡 Coloca tu archivo SAP en: data/sap_descargas/")
    
    if st.button("🔄 Actualizar Datos", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.caption("El sistema lee el archivo más reciente")
    
    st.markdown("---")
    st.markdown("### 📞 Contacto")
    
    company_name = COMPANY_INFO['nombre']
    company_email = COMPANY_INFO['email']
    company_website = COMPANY_INFO['website']
    company_phone = COMPANY_INFO['whatsapp']
    
    st.markdown(company_name)
    st.markdown("📧 " + company_email)
    st.markdown("🌐 " + company_website)
    st.markdown("📱 " + company_phone)
    
    st.markdown("---")
    st.markdown("### ⚡ Especialidades")
    st.markdown("""
    - Sistemas Eléctricos
    - Análisis de Datos
    - VFD & ESP Systems
    - Calidad de Energía
    """)

def buscar_material(df, termino):
    if not termino:
        return df
    t = termino.lower().strip()
    mask = (
        df['codigo'].astype(str).str.lower().str.contains(t, na=False) |
        df['descripcion'].astype(str).str.lower().str.contains(t, na=False)
    )
    return df[mask]

@st.cache_data
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
        st.error("❌ No se pudieron cargar los datos")
        st.info("📁 Verifica: data/sap_descargas/ o data/raw/sap_export.xlsx")
        st.stop()
    
    st.markdown('<div class="search-box">', unsafe_allow_html=True)
    st.markdown("### 🔍 Búsqueda de Materiales")
    
    col_s1, col_s2 = st.columns([3, 1])
    with col_s1:
        termino = st.text_input(
            "buscar",
            placeholder="Código o descripción...",
            label_visibility="collapsed"
        )
    with col_s2:
        btn_buscar = st.button("🔍 Buscar", use_container_width=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    if termino:
        resultados = buscar_material(df, termino)
        
        if not resultados.empty:
            num_resultados = len(resultados)
            st.success("✅ " + str(num_resultados) + " materiales encontrados")
            
            st.markdown('<div class="section-card">', unsafe_allow_html=True)
            st.markdown('<p class="section-title">🎯 Resultados</p>', unsafe_allow_html=True)
            
            cols_d = ['codigo', 'descripcion', 'stock_actual', 'stock_minimo', 
                     'stock_maximo', 'estado', 'criticidad', 'proveedor']
            
            st.dataframe(resultados[cols_d], use_container_width=True, height=400)
            
            csv_r = resultados.to_csv(index=False).encode('utf-8')
            filename_busqueda = "busqueda_" + termino + ".csv"
            st.download_button(
                "📥 Descargar Resultados",
                csv_r,
                filename_busqueda,
                "text/csv",
                use_container_width=True
            )
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("---")
        else:
            st.warning("⚠️ No se encontraron materiales con: " + termino)
            st.markdown("---")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📊 Indicadores Clave</p>', unsafe_allow_html=True)
    
    c1, c2, c3, c4, c5 = st.columns(5)
    
    total_mat = metrics['total_materiales']
    criticos = metrics['criticos']
    bajo = metrics['bajo']
    ok = metrics['ok']
    valor_total = metrics['valor_total_stock']
    
    with c1:
        st.metric("📦 Total", total_mat)
    with c2:
        st.metric("🔴 Críticos", criticos)
    with c3:
        st.metric("🟡 Bajo", bajo)
    with c4:
        st.metric("🟢 OK", ok)
    with c5:
        valor_formateado = "${:,.0f}".format(valor_total)
        st.metric("💰 Valor", valor_formateado)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">📈 Distribución</p>', unsafe_allow_html=True)
    
    co1, co2 = st.columns(2)
    
    with co1:
        st.markdown("#### Estados")
        status = df['estado'].value_counts()
        total = len(df)
        
        for estado in ['CRITICO', 'BAJO', 'OK']:
            if estado in status.index:
                count = status[estado]
                pct = (count / total) * 100
                pct_str = "{:.1f}".format(pct)
                
                if estado == 'CRITICO':
                    texto = "🔴 **" + estado + "**: " + str(count) + " (" + pct_str + "%)"
                    st.markdown(texto)
                elif estado == 'BAJO':
                    texto = "🟡 **" + estado + "**: " + str(count) + " (" + pct_str + "%)"
                    st.markdown(texto)
                else:
                    texto = "🟢 **" + estado + "**: " + str(count) + " (" + pct_str + "%)"
                    st.markdown(texto)
                
                st.progress(pct / 100)
    
    with co2:
        st.markdown("#### Criticidad")
        crit = df['criticidad'].value_counts()
        total_c = len(df[df['criticidad'].notna()])
        
        if total_c > 0:
            for c in ['A', 'B', 'C']:
                if c in crit.index:
                    count = crit[c]
                    pct = (count / total_c) * 100
                    pct_str = "{:.1f}".format(pct)
                    texto = "**Categoría " + c + "**: " + str(count) + " (" + pct_str + "%)"
                    st.markdown(texto)
                    st.progress(pct / 100)
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.markdown('<p class="section-title">🚨 Acción Inmediata</p>', unsafe_allow_html=True)
    
    critical = df[df['estado'].isin(['CRITICO', 'BAJO'])].copy()
    
    if not critical.empty:
        critical = critical.sort_values(['estado', 'criticidad'])
        
        cols_c = ['codigo', 'descripcion', 'stock_actual', 'stock_minimo',
                 'brecha_minimo', 'estado', 'cantidad_comprar', 'proveedor']
        
        st.dataframe(critical[cols_c], use_container_width=True, height=400)
        
        cx1, cx2 = st.columns(2)
        with cx1:
            num_critical = len(critical)
            st.info("📦 Total: " + str(num_critical))
        with cx2:
            valor_compra = critical['valor_compra'].sum()
            valor_compra_str = "${:,.0f}".format(valor_compra)
            st.info("💰 Valor: " + valor_compra_str)
        
        csv = critical.to_csv(index=False).encode('utf-8')
        fecha_hoy = pd.Timestamp.now().strftime('%Y%m%d')
        filename_compras = "compras_" + fecha_hoy + ".csv"
        st.download_button(
            "📥 Descargar Lista de Compras",
            csv,
            filename_compras,
            "text/csv",
            use_container_width=True
        )
    else:
        st.success("✅ No hay materiales críticos")
    
    st.markdown('</div>', unsafe_allow_html=True)
    st.markdown("---")
    
    with st.expander("📋 Inventario Completo"):
        st.dataframe(
            df[['codigo', 'descripcion', 'stock_actual', 'stock_minimo', 
                'stock_maximo', 'estado', 'criticidad', 'proveedor']],
            use_container_width=True,
            height=500
        )
        
        csv_full = df.to_csv(index=False).encode('utf-8')
        fecha_inv = pd.Timestamp.now().strftime('%Y%m%d')
        filename_inv = "inventario_" + fecha_inv + ".csv"
        st.download_button(
            "📥 Descargar Todo",
            csv_full,
            filename_inv,
            "text/csv"
        )

except Exception as e:
    st.error("❌ Error: " + str(e))
    import traceback
    st.code(traceback.format_exc())

footer_html = """
<div class="footer">
    <h3>⚡ """ + COMPANY_INFO['nombre'] + """</h3>
    <p><strong>Electrical Systems & Data Intelligence</strong></p>
    <p>
        📧 <a href="mailto:""" + COMPANY_INFO['email'] + """">""" + COMPANY_INFO['email'] + """</a> | 
        🌐 <a href\"""" + COMPANY_INFO['website'] + """">""" + COMPANY_INFO['website'] + """</a> | 
        📱 """ + COMPANY_INFO['whatsapp'] + """
    </p>
    <p style="font-size: 0.9rem; margin-top: 1rem;">v1.1 | © 2026 JAC Engineering</p>
</div>
"""

st.markdown(footer_html, unsafe_allow_html=True)