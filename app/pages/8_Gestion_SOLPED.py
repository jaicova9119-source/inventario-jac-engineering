"""
Gestion de Solicitudes de Pedido (SOLPED) Multi-Material
JAC Engineering SAS
"""

import streamlit as st
import sys
import os
import pandas as pd
from datetime import datetime, timedelta

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.data_loader_sheets import DataLoaderSheets as DataLoader
from src.inventory_analyzer import InventoryAnalyzer

st.set_page_config(
    page_title="Gestion SOLPED - JAC Engineering",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Gestion de Solicitudes de Pedido (SOLPED)")
st.markdown("JAC Engineering SAS - Control de compras con carrito multi-material")
st.markdown("---")

solped_file = 'config/solped_historico.xlsx'

if 'carrito_solped' not in st.session_state:
    st.session_state.carrito_solped = []

def load_solpeds():
    try:
        if not os.path.exists(solped_file):
            return pd.DataFrame()
        
        df = pd.read_excel(solped_file)
        
        if 'Fecha_Solicitud' in df.columns:
            df['Fecha_Solicitud'] = pd.to_datetime(df['Fecha_Solicitud'], errors='coerce')
        if 'Fecha_Estimada_Llegada' in df.columns:
            df['Fecha_Estimada_Llegada'] = pd.to_datetime(df['Fecha_Estimada_Llegada'], errors='coerce')
        if 'Fecha_Recepcion_Real' in df.columns:
            df['Fecha_Recepcion_Real'] = pd.to_datetime(df['Fecha_Recepcion_Real'], errors='coerce')
        
        return df
    except Exception as e:
        st.error("Error cargando SOLPEDs: " + str(e))
        return pd.DataFrame()

def save_solpeds(df):
    try:
        df.to_excel(solped_file, index=False)
        return True
    except Exception as e:
        st.error("Error guardando: " + str(e))
        return False

def generar_numero_solped():
    df = load_solpeds()
    
    if df.empty:
        return "SOLPED-2026-001"
    
    numeros = df['SOLPED_Numero'].unique().tolist()
    
    try:
        nums = [int(n.split('-')[-1]) for n in numeros if isinstance(n, str)]
        ultimo = max(nums) if nums else 0
        nuevo = ultimo + 1
        return "SOLPED-2026-" + str(nuevo).zfill(3)
    except:
        return "SOLPED-2026-001"

def agregar_al_carrito(material, cantidad):
    item = {
        'codigo': str(material['codigo']),
        'centro': str(material['centro']),
        'descripcion': str(material['descripcion']),
        'nombre_tecnico': str(material.get('nombre_tecnico', '')),
        'categoria': str(material.get('Categoria', '')),
        'stock_actual': int(material['stock_actual']),
        'stock_minimo': int(material['stock_minimo']),
        'cantidad': cantidad,
        'proveedor': str(material.get('proveedor', 'POR CONFIGURAR'))
    }
    
    existe = False
    for i, item_carrito in enumerate(st.session_state.carrito_solped):
        if item_carrito['codigo'] == item['codigo'] and item_carrito['centro'] == item['centro']:
            st.session_state.carrito_solped[i]['cantidad'] = cantidad
            existe = True
            break
    
    if not existe:
        st.session_state.carrito_solped.append(item)

def eliminar_del_carrito(codigo, centro):
    st.session_state.carrito_solped = [
        item for item in st.session_state.carrito_solped 
        if not (item['codigo'] == codigo and item['centro'] == centro)
    ]

@st.cache_data
def load_inventory():
    loader = DataLoader()
    data = loader.merge_data()
    if data.empty:
        return None
    analyzer = InventoryAnalyzer(data)
    return analyzer.full_analysis()

if not os.path.exists(solped_file):
    st.warning("⚠️ No existe el archivo de SOLPEDs")
    st.info("Ejecuta el script para crear el sistema:")
    st.code("python crear_solped_sistema.py", language="bash")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["🛒 Crear SOLPED", "📑 SOLPEDs Activas", "📊 Historial", "📈 Estadísticas"])

with tab1:
    st.subheader("🛒 Crear SOLPED Multi-Material")
    
    df_inventory = load_inventory()
    
    if df_inventory is None or df_inventory.empty:
        st.error("No se pudo cargar el inventario")
        st.stop()
    
    df_criticos = df_inventory[df_inventory['estado'].isin(['CRITICO', 'BAJO'])].copy()
    
    df_solpeds_activas = load_solpeds()
    if not df_solpeds_activas.empty:
        solpeds_activas = df_solpeds_activas[
            df_solpeds_activas['Estado'].isin(['PENDIENTE', 'APROBADA', 'EN_TRANSITO'])
        ]
        
        if not solpeds_activas.empty:
            codigos_con_solped = solpeds_activas.groupby(['Codigo', 'Centro']).size().reset_index(name='tiene_solped')
            
            df_criticos = df_criticos.merge(
                codigos_con_solped,
                left_on=['codigo', 'centro'],
                right_on=['Codigo', 'Centro'],
                how='left'
            )
            
            df_criticos['tiene_solped'] = df_criticos['tiene_solped'].notna()
    else:
        df_criticos['tiene_solped'] = False
    
    sin_solped = df_criticos[df_criticos['tiene_solped'] == False]
    con_solped = df_criticos[df_criticos['tiene_solped'] == True]
    
    col_info1, col_info2, col_info3 = st.columns(3)
    
    with col_info1:
        st.metric("Materiales Críticos Total", len(df_criticos))
    
    with col_info2:
        st.metric("Sin SOLPED", len(sin_solped))
    
    with col_info3:
        st.metric("Con SOLPED Activa", len(con_solped))
    
    st.markdown("---")
    
    # BÚSQUEDA Y FILTROS MEJORADOS
    col_search, col_f1, col_f2, col_f3 = st.columns([3, 2, 2, 1])
    
    with col_search:
        busqueda = st.text_input(
            "🔍 Buscar material",
            placeholder="Codigo, nombre tecnico, descripcion...",
            key="buscar_material",
            help="Busca por codigo, nombre tecnico o cualquier palabra en la descripcion"
        )
    
    with col_f1:
        if 'centro' in sin_solped.columns:
            centros = ['Todos'] + sorted(sin_solped['centro'].unique().tolist())
            centro_filtro = st.selectbox("Centro:", centros, key="filtro_centro")
        else:
            centro_filtro = 'Todos'
    
    with col_f2:
        if 'Categoria' in sin_solped.columns:
            categorias = ['Todas'] + sorted(sin_solped['Categoria'].unique().tolist())
            categoria_filtro = st.selectbox("Categoría:", categorias, key="filtro_cat")
        else:
            categoria_filtro = 'Todas'
    
    with col_f3:
        st.write("")
        st.write("")
        if st.button("🗑️ Limpiar", use_container_width=True):
            st.session_state.carrito_solped = []
            st.rerun()
    
    # Aplicar filtros
    df_mostrar = sin_solped.copy()
    
    # BÚSQUEDA FLEXIBLE
    if busqueda:
        busqueda_lower = busqueda.lower().strip()
        
        mask_busqueda = (
            df_mostrar['codigo'].astype(str).str.lower().str.contains(busqueda_lower, na=False) |
            df_mostrar['descripcion'].astype(str).str.lower().str.contains(busqueda_lower, na=False)
        )
        
        if 'nombre_tecnico' in df_mostrar.columns:
            mask_busqueda = mask_busqueda | df_mostrar['nombre_tecnico'].astype(str).str.lower().str.contains(busqueda_lower, na=False)
        
        if 'centro_nombre' in df_mostrar.columns:
            mask_busqueda = mask_busqueda | df_mostrar['centro_nombre'].astype(str).str.lower().str.contains(busqueda_lower, na=False)
        
        df_mostrar = df_mostrar[mask_busqueda]
        
        if not df_mostrar.empty:
            st.success("✅ Encontrados: " + str(len(df_mostrar)) + " materiales con '" + busqueda + "'")
        else:
            st.warning("⚠️ No se encontraron materiales con: " + busqueda)
    
    # CENTRO
    if centro_filtro != 'Todos':
        df_mostrar = df_mostrar[df_mostrar['centro'] == centro_filtro]
    
    # CATEGORÍA
    if categoria_filtro != 'Todas':
        df_mostrar = df_mostrar[df_mostrar['Categoria'] == categoria_filtro]
    
    st.markdown("---")
    st.markdown("### 📦 Materiales Disponibles para Solicitud")
    
    if df_mostrar.empty:
        st.info("No hay materiales con estos filtros")
    else:
        st.caption("Mostrando " + str(len(df_mostrar)) + " materiales")
        
        for idx in df_mostrar.index:
            material = df_mostrar.loc[idx]
            
            col1, col2, col3, col4, col5, col6 = st.columns([1, 2, 2, 1, 1, 1])
            
            with col1:
                st.write("**" + str(material['codigo']) + "**")
            
            with col2:
                desc = str(material['descripcion'])[:40]
                st.write(desc)
                if material.get('nombre_tecnico', ''):
                    st.caption("🏷️ " + str(material['nombre_tecnico']))
            
            with col3:
                st.write(str(material['centro']) + " - " + str(material.get('centro_nombre', '')))
                if material.get('Categoria', ''):
                    st.caption("📂 " + str(material['Categoria']))
            
            with col4:
                st.metric("Stock", int(material['stock_actual']))
            
            with col5:
                cant_sugerida = int(material.get('cantidad_comprar', 0))
                cantidad = st.number_input(
                    "Cant",
                    min_value=1,
                    value=cant_sugerida,
                    step=1,
                    key="cant_" + str(idx),
                    label_visibility="collapsed"
                )
            
            with col6:
                if st.button("➕", key="add_" + str(idx), use_container_width=True):
                    agregar_al_carrito(material, cantidad)
                    st.success("✅")
                    st.rerun()
            
            st.markdown("---")
    
    # CARRITO
    st.markdown("### 🛒 Carrito de SOLPED")
    
    if not st.session_state.carrito_solped:
        st.info("El carrito está vacío. Agrega materiales desde la lista superior.")
    else:
        st.success("📦 Materiales en el carrito: " + str(len(st.session_state.carrito_solped)))
        
        for i, item in enumerate(st.session_state.carrito_solped):
            col1, col2, col3, col4, col5 = st.columns([2, 3, 2, 1, 1])
            
            with col1:
                st.write("**" + item['codigo'] + "** [" + item['centro'] + "]")
            
            with col2:
                st.write(item['descripcion'][:40])
                if item['nombre_tecnico']:
                    st.caption("🏷️ " + item['nombre_tecnico'])
            
            with col3:
                st.write("Proveedor: " + item['proveedor'])
            
            with col4:
                st.metric("Cantidad", item['cantidad'])
            
            with col5:
                if st.button("🗑️", key="del_" + str(i), use_container_width=True):
                    eliminar_del_carrito(item['codigo'], item['centro'])
                    st.rerun()
        
        st.markdown("---")
        
        st.markdown("### 📝 Detalles de la Solicitud")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            numero_solped = generar_numero_solped()
            st.text_input("Numero SOLPED", value=numero_solped, disabled=True)
            
            solicitante = st.text_input("Solicitante", value="Jaime Córdoba")
        
        with col2:
            fecha_solicitud = st.date_input("Fecha Solicitud", value=datetime.now())
            
            lead_time_general = st.number_input("Lead Time (dias)", min_value=1, value=30, step=1)
            
            fecha_estimada = fecha_solicitud + timedelta(days=lead_time_general)
            st.info("Fecha Estimada: " + fecha_estimada.strftime('%Y-%m-%d'))
        
        with col3:
            estado_inicial = st.selectbox("Estado Inicial", ['PENDIENTE', 'APROBADA'])
            
            precio_global = st.number_input("Precio Unitario Global (opcional)", min_value=0.0, value=0.0, step=1000.0)
        
        notas_general = st.text_area("Notas Generales", height=100)
        
        st.markdown("---")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✅ CREAR SOLPED COMPLETA", type="primary", use_container_width=True):
                
                nuevos_registros = []
                
                for item in st.session_state.carrito_solped:
                    registro = {
                        'SOLPED_Numero': numero_solped,
                        'Codigo': item['codigo'],
                        'Centro': item['centro'],
                        'Descripcion': item['descripcion'],
                        'Nombre_Tecnico': item['nombre_tecnico'],
                        'Categoria': item['categoria'],
                        'Cantidad_Solicitada': item['cantidad'],
                        'Fecha_Solicitud': fecha_solicitud,
                        'Estado': estado_inicial,
                        'Fecha_Estimada_Llegada': fecha_estimada,
                        'Fecha_Recepcion_Real': None,
                        'Proveedor': item['proveedor'],
                        'Precio_Unitario': precio_global,
                        'Valor_Total': precio_global * item['cantidad'],
                        'Solicitante': solicitante,
                        'Notas': notas_general
                    }
                    
                    nuevos_registros.append(registro)
                
                df_solpeds = load_solpeds()
                df_nuevos = pd.DataFrame(nuevos_registros)
                df_solpeds = pd.concat([df_solpeds, df_nuevos], ignore_index=True)
                
                if save_solpeds(df_solpeds):
                    st.success("✅ SOLPED " + numero_solped + " creada con " + str(len(nuevos_registros)) + " materiales")
                    st.balloons()
                    
                    st.session_state.carrito_solped = []
                    
                    import time
                    time.sleep(2)
                    st.rerun()
        
        with col_btn2:
            st.caption("Total materiales: " + str(len(st.session_state.carrito_solped)))

with tab2:
    st.subheader("📑 SOLPEDs Activas")
    
    df_solpeds = load_solpeds()
    
    if df_solpeds.empty:
        st.info("No hay SOLPEDs registradas")
    else:
        df_activas = df_solpeds[df_solpeds['Estado'].isin(['PENDIENTE', 'APROBADA', 'EN_TRANSITO'])].copy()
        
        if df_activas.empty:
            st.success("✅ No hay SOLPEDs activas")
        else:
            solpeds_unicas = df_activas['SOLPED_Numero'].unique()
            
            st.info("SOLPEDs activas: " + str(len(solpeds_unicas)))
            
            for solped_num in solpeds_unicas:
                materiales_solped = df_activas[df_activas['SOLPED_Numero'] == solped_num]
                
                with st.expander(solped_num + " (" + str(len(materiales_solped)) + " materiales) - Estado: " + materiales_solped.iloc[0]['Estado']):
                    
                    st.write("**Fecha Solicitud:** " + str(materiales_solped.iloc[0]['Fecha_Solicitud']))
                    st.write("**Solicitante:** " + str(materiales_solped.iloc[0].get('Solicitante', 'N/A')))
                    st.write("**Fecha Estimada:** " + str(materiales_solped.iloc[0]['Fecha_Estimada_Llegada']))
                    
                    st.markdown("---")
                    
                    st.dataframe(
                        materiales_solped[['Codigo', 'Centro', 'Descripcion', 'Cantidad_Solicitada', 'Proveedor']],
                        use_container_width=True
                    )
                    
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        nuevo_estado = st.selectbox(
                            "Cambiar Estado:",
                            ['PENDIENTE', 'APROBADA', 'EN_TRANSITO', 'RECIBIDA', 'CANCELADA'],
                            key="estado_" + solped_num
                        )
                    
                    with col2:
                        if nuevo_estado == 'RECIBIDA':
                            fecha_rec = st.date_input("Fecha Recepción", value=datetime.now(), key="fecha_" + solped_num)
                        else:
                            fecha_rec = None
                    
                    with col3:
                        st.write("")
                        if st.button("💾 Actualizar", key="update_" + solped_num):
                            df_solpeds.loc[df_solpeds['SOLPED_Numero'] == solped_num, 'Estado'] = nuevo_estado
                            
                            if fecha_rec and nuevo_estado == 'RECIBIDA':
                                df_solpeds.loc[df_solpeds['SOLPED_Numero'] == solped_num, 'Fecha_Recepcion_Real'] = fecha_rec
                            
                            if save_solpeds(df_solpeds):
                                st.success("✅ Actualizado")
                                st.rerun()

with tab3:
    st.subheader("📊 Historial Completo")
    
    df_solpeds = load_solpeds()
    
    if not df_solpeds.empty:
        st.metric("Total Registros", len(df_solpeds))
        
        st.dataframe(
            df_solpeds.sort_values('Fecha_Solicitud', ascending=False),
            use_container_width=True,
            height=500
        )
        
        csv = df_solpeds.to_csv(index=False).encode('utf-8')
        st.download_button(
            "📥 Descargar",
            csv,
            "historial_solped.csv",
            "text/csv"
        )

with tab4:
    st.subheader("📈 Estadísticas")
    
    df_solpeds = load_solpeds()
    
    if not df_solpeds.empty:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("Total Materiales", len(df_solpeds))
        
        with col2:
            solpeds_unicas = df_solpeds['SOLPED_Numero'].nunique()
            st.metric("SOLPEDs Únicas", solpeds_unicas)
        
        with col3:
            pendientes = len(df_solpeds[df_solpeds['Estado'] == 'PENDIENTE'])
            st.metric("Pendientes", pendientes)
        
        with col4:
            if 'Valor_Total' in df_solpeds.columns:
                valor = df_solpeds['Valor_Total'].sum()
                st.metric("Valor Total", "${:,.0f}".format(valor))

st.markdown("---")

st.markdown("""
<div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); color: white; padding: 1.5rem; border-radius: 10px; text-align: center; margin-top: 2rem;">
    <strong>JAC Engineering SAS</strong> - Electrical Systems & Data Intelligence<br>
    proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502
</div>
""", unsafe_allow_html=True)