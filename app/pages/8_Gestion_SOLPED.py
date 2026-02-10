"""
Gestion de Solicitudes de Pedido (SOLPED)
JAC Engineering SAS
VERSION CON GOOGLE SHEETS - MULTI USUARIO
"""

import streamlit as st
import pandas as pd
import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.google_sheets_handler import GoogleSheetsHandler
from config.google_config import SHEETS_CONFIG

st.set_page_config(
    page_title="Gestion SOLPED - JAC Engineering",
    page_icon="📋",
    layout="wide"
)

st.title("📋 Gestion de Solicitudes de Pedido (SOLPED)")
st.markdown("JAC Engineering SAS - Control de compras con carrito multi-material")
st.markdown("---")

# ============================================================
# FUNCIONES DE GOOGLE SHEETS
# ============================================================

def get_handler():
    return GoogleSheetsHandler()

def load_solped_from_sheets():
    """Carga historial de SOLPEDs desde Google Sheets"""
    try:
        handler = get_handler()
        config = SHEETS_CONFIG['solped']
        
        df = handler.read_sheet_to_dataframe(
            config['sheet_id'],
            config['sheet_name']
        )
        
        if df.empty:
            return pd.DataFrame(columns=[
                'SOLPED_Numero', 'Fecha', 'Codigo', 'Descripcion',
                'Nombre_Tecnico', 'Centro', 'Centro_Nombre',
                'Cantidad_Solicitada', 'Unidad', 'Precio_Unitario',
                'Valor_Total', 'Criticidad', 'Proveedor',
                'Solicitado_Por', 'Estado', 'Notas'
            ])
        
        return df
        
    except Exception as e:
        st.error("Error cargando SOLPEDs: " + str(e))
        return pd.DataFrame()

def save_solped_to_sheets(df):
    """Guarda SOLPEDs en Google Sheets"""
    try:
        handler = get_handler()
        config = SHEETS_CONFIG['solped']
        
        # Limpiar datos antes de guardar
        df_save = df.copy()
        df_save = df_save.fillna('')
        df_save = df_save.astype(str)
        df_save = df_save.replace('nan', '')
        
        success = handler.write_dataframe_to_sheet(
            df_save,
            config['sheet_id'],
            config['sheet_name']
        )
        
        return success
        
    except Exception as e:
        st.error("Error guardando SOLPEDs: " + str(e))
        return False

def get_next_solped_number(df_solped):
    """Genera el siguiente numero de SOLPED"""
    if df_solped.empty or 'SOLPED_Numero' not in df_solped.columns:
        return "SOLPED-2026-001"
    
    try:
        numeros = df_solped['SOLPED_Numero'].dropna().tolist()
        if not numeros:
            return "SOLPED-2026-001"
        
        # Extraer el numero secuencial del ultimo
        ultimo = str(numeros[-1])
        partes = ultimo.split('-')
        if len(partes) == 3:
            anio = datetime.now().year
            num = int(partes[-1]) + 1
            return "SOLPED-" + str(anio) + "-" + str(num).zfill(3)
        else:
            return "SOLPED-" + str(datetime.now().year) + "-" + str(len(numeros) + 1).zfill(3)
    except:
        return "SOLPED-" + str(datetime.now().year) + "-001"

def load_inventory():
    """Carga inventario para seleccionar materiales"""
    try:
        from src.data_loader_sheets import DataLoaderSheets
        loader = DataLoaderSheets()
        df = loader.merge_data()
        return df
    except Exception as e:
        st.error("Error cargando inventario: " + str(e))
        return pd.DataFrame()

# ============================================================
# INICIALIZAR CARRITO EN SESSION STATE
# ============================================================

if 'carrito_solped' not in st.session_state:
    st.session_state.carrito_solped = []

if 'solicitado_por' not in st.session_state:
    # Intentar obtener el nombre del usuario en sesión
    if 'usuario_nombre' in st.session_state:
        st.session_state.solicitado_por = st.session_state.usuario_nombre
    else:
        st.session_state.solicitado_por = ""

# ============================================================
# TABS PRINCIPALES
# ============================================================

tab1, tab2, tab3 = st.tabs([
    "🛒 Nueva SOLPED",
    "📊 Historial de SOLPEDs",
    "📈 Resumen"
])

# ============================================================
# TAB 1: NUEVA SOLPED
# ============================================================

with tab1:
    st.markdown("### 🛒 Crear Nueva Solicitud de Pedido")
    
    # Datos del solicitante
    col1, col2 = st.columns(2)
    
    with col1:
        solicitado_por = st.text_input(
            "Solicitado por",
            value=st.session_state.solicitado_por,
            placeholder="Nombre del solicitante"
        )
        st.session_state.solicitado_por = solicitado_por
    
    with col2:
        notas_generales = st.text_area(
            "Notas generales",
            placeholder="Observaciones de la solicitud...",
            height=80
        )
    
    st.markdown("---")
    
    # Buscar materiales para agregar al carrito
    st.markdown("### 🔍 Buscar y Agregar Materiales")
    
    col_busq1, col_busq2 = st.columns([4, 1])
    
    with col_busq1:
        busqueda = st.text_input(
            "Buscar material",
            placeholder="Código, descripción o nombre técnico..."
        )
    
    with col_busq2:
        st.write("")
        st.write("")
        btn_buscar = st.button("🔍 Buscar", use_container_width=True)
    
    if busqueda:
        with st.spinner("Buscando materiales..."):
            df_inventario = load_inventory()
        
        if not df_inventario.empty:
            termino = busqueda.lower().strip()
            
            mask = (
                df_inventario['codigo'].astype(str).str.lower().str.contains(termino, na=False) |
                df_inventario['descripcion'].astype(str).str.lower().str.contains(termino, na=False)
            )
            
            if 'nombre_tecnico' in df_inventario.columns:
                mask = mask | df_inventario['nombre_tecnico'].astype(str).str.lower().str.contains(termino, na=False)
            
            df_resultado = df_inventario[mask].copy()
            
            if df_resultado.empty:
                st.warning("No se encontraron materiales con: " + busqueda)
            else:
                st.success("Encontrados: " + str(len(df_resultado)) + " materiales")
                
                # Mostrar resultados
                for idx, row in df_resultado.head(10).iterrows():
                    with st.expander(
                        str(row['codigo']) + " - " + str(row['descripcion'])[:60] + " | Centro: " + str(row.get('centro', '')) + " | Stock: " + str(row.get('stock_actual', 0))
                    ):
                        col_info1, col_info2, col_info3 = st.columns(3)
                        
                        with col_info1:
                            st.write("**Código:** " + str(row['codigo']))
                            st.write("**Centro:** " + str(row.get('centro', 'N/A')))
                            st.write("**Stock actual:** " + str(row.get('stock_actual', 0)))
                        
                        with col_info2:
                            nombre_tec = str(row.get('nombre_tecnico', ''))
                            if nombre_tec and nombre_tec != 'nan':
                                st.write("**Nombre técnico:** " + nombre_tec)
                            st.write("**Criticidad:** " + str(row.get('criticidad', 'N/A')))
                            st.write("**Unidad:** " + str(row.get('unidad', 'UND')))
                        
                        with col_info3:
                            precio = float(row.get('precio_unitario', 0)) if row.get('precio_unitario', 0) else 0
                            st.write("**Precio unit.:** $" + "{:,.0f}".format(precio))
                            st.write("**Proveedor:** " + str(row.get('proveedor', 'N/A')))
                        
                        # Cantidad a solicitar
                        col_cant, col_btn = st.columns([2, 1])
                        
                        with col_cant:
                            cantidad = st.number_input(
                                "Cantidad a solicitar",
                                min_value=1,
                                value=1,
                                step=1,
                                key="cant_" + str(idx)
                            )
                        
                        with col_btn:
                            st.write("")
                            st.write("")
                            if st.button(
                                "➕ Agregar al carrito",
                                key="btn_" + str(idx),
                                use_container_width=True
                            ):
                                # Verificar si ya está en el carrito
                                ya_existe = False
                                for item in st.session_state.carrito_solped:
                                    if item['codigo'] == str(row['codigo']) and item['centro'] == str(row.get('centro', '')):
                                        item['cantidad'] += cantidad
                                        ya_existe = True
                                        break
                                
                                if not ya_existe:
                                    nombre_tecnico = str(row.get('nombre_tecnico', ''))
                                    if nombre_tecnico == 'nan' or nombre_tecnico == 'None':
                                        nombre_tecnico = ''
                                    
                                    st.session_state.carrito_solped.append({
                                        'codigo': str(row['codigo']),
                                        'descripcion': str(row['descripcion']),
                                        'nombre_tecnico': nombre_tecnico,
                                        'centro': str(row.get('centro', '')),
                                        'centro_nombre': str(row.get('centro_nombre', '')),
                                        'cantidad': cantidad,
                                        'unidad': str(row.get('unidad', 'UND')),
                                        'precio_unitario': float(row.get('precio_unitario', 0) or 0),
                                        'criticidad': str(row.get('criticidad', 'C')),
                                        'proveedor': str(row.get('proveedor', 'POR DEFINIR'))
                                    })
                                
                                st.success("✅ Agregado al carrito")
                                st.rerun()
    
    st.markdown("---")
    
    # CARRITO
    st.markdown("### 🛒 Carrito de Compras")
    
    if not st.session_state.carrito_solped:
        st.info("El carrito está vacío. Busca y agrega materiales.")
    else:
        st.success("**" + str(len(st.session_state.carrito_solped)) + " materiales en el carrito**")
        
        total_general = 0
        items_a_eliminar = []
        
        for i, item in enumerate(st.session_state.carrito_solped):
            valor_total = item['cantidad'] * item['precio_unitario']
            total_general += valor_total
            
            with st.container():
                col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 2, 1])
                
                with col1:
                    desc_display = item['nombre_tecnico'] if item['nombre_tecnico'] else item['descripcion']
                    st.write("**" + item['codigo'] + "** - " + desc_display[:50])
                    st.caption("Centro: " + item['centro'] + " | " + item['centro_nombre'][:30])
                
                with col2:
                    nueva_cantidad = st.number_input(
                        "Cant.",
                        min_value=1,
                        value=item['cantidad'],
                        step=1,
                        key="carrito_cant_" + str(i)
                    )
                    st.session_state.carrito_solped[i]['cantidad'] = nueva_cantidad
                
                with col3:
                    st.write("**Unid:**")
                    st.write(item['unidad'])
                
                with col4:
                    st.write("**Valor:**")
                    valor = nueva_cantidad * item['precio_unitario']
                    st.write("$" + "{:,.0f}".format(valor))
                
                with col5:
                    if st.button("🗑️", key="del_" + str(i), help="Eliminar del carrito"):
                        items_a_eliminar.append(i)
                
                st.markdown("---")
        
        # Eliminar items marcados
        if items_a_eliminar:
            for i in sorted(items_a_eliminar, reverse=True):
                st.session_state.carrito_solped.pop(i)
            st.rerun()
        
        # Total
        st.markdown("### 💰 Total: **$" + "{:,.0f}".format(total_general) + " COP**")
        
        st.markdown("---")
        
        # Botones de acción
        col_acc1, col_acc2, col_acc3 = st.columns(3)
        
        with col_acc1:
            if st.button("🗑️ Limpiar carrito", use_container_width=True):
                st.session_state.carrito_solped = []
                st.rerun()
        
        with col_acc2:
            # Descargar como Excel
            df_carrito = pd.DataFrame(st.session_state.carrito_solped)
            csv = df_carrito.to_csv(index=False).encode('utf-8')
            
            st.download_button(
                label="📥 Descargar lista",
                data=csv,
                file_name="solped_" + datetime.now().strftime('%Y%m%d_%H%M') + ".csv",
                mime="text/csv",
                use_container_width=True
            )
        
        with col_acc3:
            if st.button(
                "✅ GENERAR SOLPED",
                use_container_width=True,
                type="primary"
            ):
                if not solicitado_por:
                    st.error("❌ Ingresa el nombre del solicitante")
                else:
                    with st.spinner("Generando SOLPED en Google Sheets..."):
                        # Cargar historial actual
                        df_solped = load_solped_from_sheets()
                        
                        # Generar numero de SOLPED
                        numero_solped = get_next_solped_number(df_solped)
                        fecha_actual = datetime.now().strftime('%Y-%m-%d %H:%M')
                        
                        # Crear filas para cada item
                        nuevas_filas = []
                        for item in st.session_state.carrito_solped:
                            valor_total = item['cantidad'] * item['precio_unitario']
                            
                            nuevas_filas.append({
                                'SOLPED_Numero': numero_solped,
                                'Fecha': fecha_actual,
                                'Codigo': item['codigo'],
                                'Descripcion': item['descripcion'],
                                'Nombre_Tecnico': item['nombre_tecnico'],
                                'Centro': item['centro'],
                                'Centro_Nombre': item['centro_nombre'],
                                'Cantidad_Solicitada': item['cantidad'],
                                'Unidad': item['unidad'],
                                'Precio_Unitario': item['precio_unitario'],
                                'Valor_Total': valor_total,
                                'Criticidad': item['criticidad'],
                                'Proveedor': item['proveedor'],
                                'Solicitado_Por': solicitado_por,
                                'Estado': 'PENDIENTE',
                                'Notas': notas_generales
                            })
                        
                        df_nuevas = pd.DataFrame(nuevas_filas)
                        
                        # Agregar al historial
                        if df_solped.empty:
                            df_actualizado = df_nuevas
                        else:
                            df_actualizado = pd.concat([df_solped, df_nuevas], ignore_index=True)
                        
                        # Guardar en Google Sheets
                        success = save_solped_to_sheets(df_actualizado)
                        
                        if success:
                            st.success("✅ SOLPED **" + numero_solped + "** generada exitosamente")
                            st.info("📊 " + str(len(nuevas_filas)) + " materiales | Total: $" + "{:,.0f}".format(sum([i['cantidad'] * i['precio_unitario'] for i in st.session_state.carrito_solped])))
                            st.balloons()
                            
                            # Limpiar carrito
                            st.session_state.carrito_solped = []
                            st.rerun()
                        else:
                            st.error("❌ Error generando SOLPED")

# ============================================================
# TAB 2: HISTORIAL
# ============================================================

with tab2:
    st.markdown("### 📊 Historial de SOLPEDs")
    
    with st.spinner("Cargando historial..."):
        df_historial = load_solped_from_sheets()
    
    if df_historial.empty:
        st.info("No hay SOLPEDs registradas aún. Crea tu primera SOLPED en la pestaña 'Nueva SOLPED'.")
    else:
        # Filtros
        col_f1, col_f2, col_f3 = st.columns(3)
        
        with col_f1:
            if 'SOLPED_Numero' in df_historial.columns:
                solpeds_disponibles = ['Todas'] + sorted(df_historial['SOLPED_Numero'].unique().tolist())
                filtro_numero = st.selectbox("Filtrar por SOLPED", solpeds_disponibles)
        
        with col_f2:
            if 'Estado' in df_historial.columns:
                estados_disponibles = ['Todos'] + sorted(df_historial['Estado'].unique().tolist())
                filtro_estado = st.selectbox("Filtrar por Estado", estados_disponibles)
        
        with col_f3:
            if 'Centro' in df_historial.columns:
                centros_disponibles = ['Todos'] + sorted(df_historial['Centro'].unique().tolist())
                filtro_centro = st.selectbox("Filtrar por Centro", centros_disponibles)
        
        # Aplicar filtros
        df_filtrado = df_historial.copy()
        
        if filtro_numero != 'Todas' and 'SOLPED_Numero' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['SOLPED_Numero'] == filtro_numero]
        
        if filtro_estado != 'Todos' and 'Estado' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Estado'] == filtro_estado]
        
        if filtro_centro != 'Todos' and 'Centro' in df_filtrado.columns:
            df_filtrado = df_filtrado[df_filtrado['Centro'] == filtro_centro]
        
        st.info("Mostrando " + str(len(df_filtrado)) + " de " + str(len(df_historial)) + " registros")
        
        st.dataframe(df_filtrado, use_container_width=True, height=400)
        
        # Descargar historial
        csv_historial = df_filtrado.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Descargar historial",
            data=csv_historial,
            file_name="historial_solped_" + datetime.now().strftime('%Y%m%d') + ".csv",
            mime="text/csv"
        )

# ============================================================
# TAB 3: RESUMEN
# ============================================================

with tab3:
    st.markdown("### 📈 Resumen de SOLPEDs")
    
    with st.spinner("Calculando resumen..."):
        df_resumen = load_solped_from_sheets()
    
    if df_resumen.empty:
        st.info("No hay datos suficientes para mostrar el resumen.")
    else:
        # Métricas generales
        col_m1, col_m2, col_m3, col_m4 = st.columns(4)
        
        total_solpeds = df_resumen['SOLPED_Numero'].nunique() if 'SOLPED_Numero' in df_resumen.columns else 0
        total_items = len(df_resumen)
        
        if 'Valor_Total' in df_resumen.columns:
            df_resumen['Valor_Total'] = pd.to_numeric(df_resumen['Valor_Total'], errors='coerce').fillna(0)
            valor_total = df_resumen['Valor_Total'].sum()
        else:
            valor_total = 0
        
        pendientes = len(df_resumen[df_resumen.get('Estado', '') == 'PENDIENTE']) if 'Estado' in df_resumen.columns else 0
        
        with col_m1:
            st.metric("Total SOLPEDs", total_solpeds)
        
        with col_m2:
            st.metric("Total Items", total_items)
        
        with col_m3:
            st.metric("Valor Total", "$" + "{:,.0f}".format(valor_total))
        
        with col_m4:
            st.metric("Pendientes", pendientes)

# Footer
st.markdown("---")
st.markdown("""
<div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); 
     color: white; padding: 1.5rem; border-radius: 10px; text-align: center;">
    <strong>JAC Engineering SAS</strong> - Electrical Systems & Data Intelligence<br>
    proyectos@jacengineering.com.co | https://jacengineering.com.co | +57 322 701 8502
</div>
""", unsafe_allow_html=True)