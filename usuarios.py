"""
Sistema de Autenticación
JAC Engineering SAS
"""

import streamlit as st
import hashlib

# Base de datos de usuarios (contraseñas encriptadas con SHA-256)
USUARIOS = {
    'jaime.cordoba': {
        'password_hash': hashlib.sha256('JAC2026!'.encode()).hexdigest(),
        'nombre': 'Jaime Alveiro Córdoba',
        'rol': 'Administrador',
        'email': 'proyectos@jacengineering.com.co'
    },
    'operador1': {
        'password_hash': hashlib.sha256('Operador1!'.encode()).hexdigest(),
        'nombre': 'Operador Campo 1',
        'rol': 'Operador',
        'email': 'operador1@jacengineering.com.co'
    },
    'operador2': {
        'password_hash': hashlib.sha256('Operador2!'.encode()).hexdigest(),
        'nombre': 'Operador Campo 2',
        'rol': 'Operador',
        'email': 'operador2@jacengineering.com.co'
    },
    'bodeguero': {
        'password_hash': hashlib.sha256('Bodega2026!'.encode()).hexdigest(),
        'nombre': 'Bodeguero Principal',
        'rol': 'Bodeguero',
        'email': 'bodega@jacengineering.com.co'
    }
}

def verificar_credenciales(usuario, password):
    """
    Verifica si usuario y contraseña son correctos
    Retorna True si las credenciales son válidas
    """
    if usuario not in USUARIOS:
        return False
    
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    return USUARIOS[usuario]['password_hash'] == password_hash

def obtener_info_usuario(usuario):
    """
    Obtiene información completa del usuario
    Retorna dict con nombre, rol, email
    """
    return USUARIOS.get(usuario, None)

def mostrar_login():
    """
    Muestra la pantalla de inicio de sesión
    """
    
    # Header con branding
    st.markdown("""
    <div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); padding: 3rem; border-radius: 15px; text-align: center; margin-bottom: 2rem; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
        <h1 style="color: white; margin: 0; font-size: 2.5rem;">⚡ JAC Engineering SAS</h1>
        <p style="color: #f0f0f0; font-size: 1.3rem; margin-top: 0.5rem;">Sistema de Control de Inventario</p>
        <p style="color: #e0e0e0; font-size: 1rem; margin-top: 0.3rem;">Electrical Systems & Data Intelligence</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Centrar el formulario
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown("""
        <div style="background: white; padding: 2rem; border-radius: 10px; box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);">
        """, unsafe_allow_html=True)
        
        st.markdown("### 🔐 Inicio de Sesión")
        st.markdown("Ingresa tus credenciales para acceder al sistema")
        
        # Formulario de login
        with st.form("login_form"):
            usuario = st.text_input(
                "👤 Usuario",
                placeholder="Ingresa tu usuario",
                help="Usuario asignado por el administrador"
            )
            
            password = st.text_input(
                "🔑 Contraseña",
                type="password",
                placeholder="Ingresa tu contraseña",
                help="Contraseña personal"
            )
            
            st.markdown("")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button(
                    "🚀 Iniciar Sesión",
                    use_container_width=True,
                    type="primary"
                )
            
            with col_btn2:
                ayuda = st.form_submit_button(
                    "❓ Ayuda",
                    use_container_width=True
                )
            
            if submit:
                if not usuario or not password:
                    st.error("⚠️ Por favor completa todos los campos")
                elif verificar_credenciales(usuario, password):
                    # Credenciales correctas
                    st.session_state['autenticado'] = True
                    st.session_state['usuario'] = usuario
                    st.session_state['info_usuario'] = obtener_info_usuario(usuario)
                    
                    info = obtener_info_usuario(usuario)
                    st.success("✅ Bienvenido " + info['nombre'])
                    st.balloons()
                    
                    import time
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Usuario o contraseña incorrectos")
                    st.warning("Verifica tus credenciales e intenta nuevamente")
            
            if ayuda:
                st.info("""
                **¿Necesitas ayuda?**
                
                Contacta al administrador:
                - 📧 proyectos@jacengineering.com.co
                - 📱 WhatsApp: +57 322 701 8502
                - 🌐 https://jacengineering.com.co
                """)
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        # Footer
        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #666;">
            <p style="margin: 0.5rem 0;"><strong>JAC Engineering SAS</strong></p>
            <p style="margin: 0.3rem 0; font-size: 0.9rem;">proyectos@jacengineering.com.co</p>
            <p style="margin: 0.3rem 0; font-size: 0.9rem;">+57 322 701 8502</p>
            <p style="margin: 0.3rem 0; font-size: 0.8rem;">© 2026 JAC Engineering - Todos los derechos reservados</p>
        </div>
        """, unsafe_allow_html=True)

def verificar_autenticacion():
    """
    Verifica si el usuario está autenticado
    Retorna True si está autenticado
    """
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False
    
    return st.session_state['autenticado']

def cerrar_sesion():
    """
    Cierra la sesión del usuario actual
    Limpia todas las variables de sesión
    """
    st.session_state['autenticado'] = False
    st.session_state['usuario'] = None
    st.session_state['info_usuario'] = None
    
    # Limpiar carrito si existe
    if 'carrito_solped' in st.session_state:
        st.session_state['carrito_solped'] = []
    
    st.rerun()

def mostrar_info_usuario_sidebar():
    """
    Muestra la información del usuario en el sidebar
    """
    with st.sidebar:
        st.markdown("---")
        st.markdown("### 👤 Sesión Activa")
        
        info = st.session_state.get('info_usuario', {})
        
        st.markdown("""
        <div style="background: linear-gradient(135deg, #134B70 0%, #1B8E9E 100%); padding: 1rem; border-radius: 8px; margin-bottom: 1rem;">
            <p style="color: white; margin: 0; font-weight: bold;">{nombre}</p>
            <p style="color: #e0e0e0; margin: 0.3rem 0 0 0; font-size: 0.9rem;">{rol}</p>
        </div>
        """.format(
            nombre=info.get('nombre', 'Usuario'),
            rol=info.get('rol', 'Rol')
        ), unsafe_allow_html=True)
        
        st.caption("📧 " + info.get('email', ''))
        st.caption("👤 Usuario: " + st.session_state.get('usuario', ''))
        
        st.markdown("")
        
        if st.button("🚪 Cerrar Sesión", use_container_width=True, type="primary"):
            cerrar_sesion()

def verificar_permisos(rol_requerido):
    """
    Verifica si el usuario tiene el rol requerido
    Roles: Administrador > Bodeguero > Operador
    """
    if not verificar_autenticacion():
        return False
    
    info = st.session_state.get('info_usuario', {})
    rol_usuario = info.get('rol', '')
    
    jerarquia = {
        'Administrador': 3,
        'Bodeguero': 2,
        'Operador': 1
    }
    
    nivel_usuario = jerarquia.get(rol_usuario, 0)
    nivel_requerido = jerarquia.get(rol_requerido, 0)
    
    return nivel_usuario >= nivel_requerido

# Funciones de utilidad para agregar/modificar usuarios

def agregar_usuario(usuario, password, nombre, rol, email):
    """
    Agrega un nuevo usuario al sistema
    NOTA: En producción esto debería guardar en base de datos
    """
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    USUARIOS[usuario] = {
        'password_hash': password_hash,
        'nombre': nombre,
        'rol': rol,
        'email': email
    }
    
    return True

def listar_usuarios():
    """
    Lista todos los usuarios del sistema
    Retorna lista de diccionarios con info de usuarios
    """
    usuarios_lista = []
    
    for usuario, info in USUARIOS.items():
        usuarios_lista.append({
            'usuario': usuario,
            'nombre': info['nombre'],
            'rol': info['rol'],
            'email': info['email']
        })
    
    return usuarios_lista