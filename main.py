# -*- coding: utf-8 -*-
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import logging
from datetime import datetime
import time
import os
from typing import Optional
from pydantic import BaseModel

# Modelos Pydantic
class SucursalUpdate(BaseModel):
    nombre: str = ""
    direccion: str = ""
    telefono: str = ""

class EmpleadoUpdate(BaseModel):
    nombre_completo: str = None
    email: str = None
    rol: str = None
    sucursal_id: int = None
    telefono: str = None
    codigo_empleado: str = None
    activo: bool = True

from config import settings
from database import DatabasePool, get_db
import bcrypt
import hashlib
import uvicorn

logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Sesiones activas: {usuario_id: {"username": "", "nombre": "", "rol": "", "departamento": "", "ultima_actividad": timestamp}}
ACTIVE_SESSIONS = {}

app = FastAPI(title=settings.API_TITLE, version=settings.API_VERSION, description="API PaintFlow 2")

# Dynamic CORS configuration for development and production
cors_origins = [
    "http://127.0.0.1:8001",
    "http://localhost:8001",
    "https://paintflow.onrender.com",  # Production Render URL
    "https://paintflow.onrender.com/",
]

# Add production URL if available via environment variable
render_url = os.getenv('RENDER_EXTERNAL_URL')
if render_url and render_url not in cors_origins:
    cors_origins.append(render_url)
    if not render_url.endswith('/'):
        cors_origins.append(render_url + '/')

app.add_middleware(CORSMiddleware, 
    allow_origins=cors_origins,
    allow_credentials=True, 
    allow_methods=["*"], 
    allow_headers=["*"]
)

# Servir archivos estáticos con ruta absoluta
static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")
else:
    logger.warning(f"Static directory not found at: {static_dir}")

@app.on_event("startup")
async def startup_event():
    logger.info("Starting PaintFlow 2 API...")
    DatabasePool.init_pool()

@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Shutting down PaintFlow 2 API...")
    DatabasePool.close_pool()

@app.get("/")
async def root():
    """Servir interfaz HTML"""
    html_path = os.path.join(os.path.dirname(__file__), "index.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Index not found")

@app.get("/employees")
async def employees_page():
    """Servir interfaz de gestión de empleados para analistas"""
    html_path = os.path.join(os.path.dirname(__file__), "employees.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Employees page not found")

@app.get("/employees.html")
async def employees_html():
    """Alias para acceso directo a employees.html"""
    html_path = os.path.join(os.path.dirname(__file__), "employees.html")
    if os.path.exists(html_path):
        return FileResponse(html_path, media_type="text/html")
    raise HTTPException(status_code=404, detail="Employees page not found")


@app.get("/health")
async def health_check():
    """Estado de la API"""
    return {"status": "healthy", "version": settings.API_VERSION, "timestamp": datetime.now().isoformat()}

@app.get("/logo.png")
async def serve_logo():
    """Servir logo"""
    logo_path = os.path.join(os.path.dirname(__file__), "static", "logo.png")
    if os.path.exists(logo_path):
        return FileResponse(logo_path, media_type="image/png")
    raise HTTPException(status_code=404, detail="Logo not found")


# ============================================================
# LOGIN ENDPOINT
# ============================================================

def get_departamento(rol):
    """Mapear rol a departamento"""
    if rol and rol.lower() == 'administrador':
        return "Departamento TI"
    elif rol and rol.lower() in ['gerente', 'contabilidad']:
        return "Finanzas"
    elif rol and rol.lower() in ['facturador', 'colorista', 'analista']:
        return "Tienda"
    return "Otros"

@app.post("/api/v1/login")
async def login(username: str, password: str, db=Depends(get_db)):
    try:
        cur = db.cursor()
        cur.execute(
            "SELECT id, username, nombre_completo, email, password_hash, rol, sucursal_id, telefono, activo FROM usuarios WHERE username = %s",
            (username,)
        )
        usuario = cur.fetchone()
        
        if not usuario:
            raise HTTPException(status_code=401, detail="Usuario o contraseña inválida")
        
        usuario_id, db_username, nombre_completo, email, password_hash, rol, sucursal_id, telefono, activo = usuario
        
        # Verificar contraseña con SHA256
        password_check = hashlib.sha256(password.encode()).hexdigest()
        if password_check != password_hash:
            raise HTTPException(status_code=401, detail="Usuario o contraseña inválida")
        
        # Verificar que esté activo
        if not activo:
            raise HTTPException(status_code=403, detail="Esta cuenta está inactiva")
        
        # Verificar que sea administrador o analista
        allowed_roles = ['administrador', 'analista']
        if not rol or rol.lower() not in allowed_roles:
            raise HTTPException(status_code=403, detail="Acceso restringido a administradores y analistas")
        
        # Registrar login en login_audits
        try:
            # Obtener nombre de sucursal
            cur2 = db.cursor()
            cur2.execute("SELECT nombre FROM sucursales WHERE id = %s", (sucursal_id,))
            sucursal_row = cur2.fetchone()
            sucursal_nombre = sucursal_row[0] if sucursal_row else ""
            
            # Registrar en login_audits
            cur.execute(
                "INSERT INTO login_audits (usuario_id, username, nombre_completo, rol, sucursal, fecha_hora_login, created_at) VALUES (%s, %s, %s, %s, %s, NOW(), NOW())",
                (usuario_id, db_username, nombre_completo, rol, sucursal_nombre)
            )
            db.commit()
        except Exception as log_error:
            logger.warning(f"Error registering login audit: {log_error}")
        
        # Registrar sesión activa
        ACTIVE_SESSIONS[usuario_id] = {
            "username": db_username,
            "nombre_completo": nombre_completo,
            "email": email,
            "rol": rol,
            "sucursal_id": sucursal_id,
            "departamento": get_departamento(rol),
            "ultima_actividad": time.time()
        }
        
        return {
            "id": usuario_id,
            "username": db_username,
            "nombre_completo": nombre_completo,
            "email": email,
            "rol": rol,
            "sucursal_id": sucursal_id,
            "telefono": telefono,
            "activo": activo
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in login: {e}")
        raise HTTPException(status_code=500, detail="Error de autenticacion")

# ============================================================
# ROLES ENDPOINTS
# ============================================================

@app.get("/api/v1/roles")
async def list_roles(db=Depends(get_db)):
    """Listar roles disponibles"""
    try:
        cur = db.cursor()
        cur.execute("SELECT id, nombre, descripcion FROM roles ORDER BY nombre")
        roles = cur.fetchall()
        return {
            "total": len(roles),
            "roles": [{"id": r[0], "nombre": r[1], "descripcion": r[2]} for r in roles]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error listing roles: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# EMPLEADOS ENDPOINTS
# ============================================================

@app.get("/api/v1/empleados")
async def list_empleados(skip: int = 0, limit: int = 200, db=Depends(get_db)):
    """Listar empleados desde tablas coloristas y encargados"""
    try:
        cur = db.cursor()
        
        # Mapeo de sucursales
        mapeo_sucursal = {
            'Arroyohondo': 'Arroyo Hondo',
            'Bellavista': 'Bella Vista',
            'Puertoplata': 'Puerto Plata',
            'Puntacana': 'Punta Cana',
            'Rafaelvidal': 'Rafael Vidal',
            'Sanfrancisco': 'San Francisco',
            'Sanmartin': 'San Martin',
            'Santiago1': 'Santiago Bartolome Colon',
            'Test': 'test',
            'Villamella': 'Villa Mella',
            'Zonaoriental': 'Zona Oriental',
            'Bavaro': 'Bavaro'
        }
        
        # Consultar coloristas
        cur.execute("""
            SELECT 
                c.id, 
                c.nombre, 
                c.sucursal, 
                c.activo,
                c.rol,
                u.email,
                u.telefono,
                c.codigo_empleado
            FROM coloristas c
            LEFT JOIN usuarios u ON u.id = c.id
            WHERE c.activo = true
            ORDER BY c.nombre
        """)
        coloristas = cur.fetchall()
        
        # Consultar encargados
        cur.execute("""
            SELECT 
                e.id, 
                e.nombre, 
                e.sucursal, 
                e.activo,
                e.rol,
                NULL as email,
                NULL as telefono,
                NULL as codigo_empleado
            FROM encargados e
            WHERE e.activo = true
            ORDER BY e.nombre
        """)
        encargados = cur.fetchall()
        
        # Combinar resultados
        todos = list(coloristas) + list(encargados)
        
        # Ordenar por nombre
        todos.sort(key=lambda x: x[1] if x[1] else "")
        
        # Aplicar LIMIT y OFFSET después de combinar
        todos_paginados = todos[skip:skip + limit]

        # OPTIMIZACIÓN: Cargar todas las sucursales UNA SOLA VEZ
        cur.execute("SELECT id, nombre FROM sucursales")
        all_sucursales = cur.fetchall()
        sucursal_dict = {s[1]: s[0] for s in all_sucursales}
        
        result = []
        for e in todos_paginados:
            sucursal_nombre = e[2] or ""
            # Mapear nombre de sucursal
            sucursal_mapped = mapeo_sucursal.get(sucursal_nombre, sucursal_nombre)
            
            # OPTIMIZACIÓN: Lookup en diccionario
            sucursal_id = sucursal_dict.get(sucursal_mapped, None)
            
            result.append({
                "id": e[0],
                "nombre_completo": e[1] or "",
                "email": e[5] or "",
                "posicion": e[4] or "colorista",
                "sucursal_id": sucursal_id,
                "sucursal_nombre": sucursal_mapped,
                "telefono": e[6] or "",
                "codigo_empleado": e[7] or "",
                "activo": e[3] if e[3] is not None else True
            })
        
        logger.info(f"[GET EMPLEADOS] Retrieved {len(result)} empleados from coloristas and encargados tables")
        
        return {
            "total": len(result),
            "empleados": result
        }
    except Exception as e:
        logger.error(f"Error listing empleados: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/sucursales")
async def list_sucursales(skip: int = 0, limit: int = 200, activo: Optional[bool] = None, db=Depends(get_db)):
    """Listar sucursales"""
    try:
        cur = db.cursor()
        if activo is not None:
            cur.execute("SELECT id, nombre, direccion, telefono, codigo, extension, activo, zona FROM sucursales WHERE activo = %s LIMIT %s OFFSET %s", (activo, limit, skip))
        else:
            cur.execute("SELECT id, nombre, direccion, telefono, codigo, extension, activo, zona FROM sucursales LIMIT %s OFFSET %s", (limit, skip))
        
        sucursales = cur.fetchall()
        return {
            "total": len(sucursales),
            "sucursales": [
                {
                    "id": s[0],
                    "nombre": s[1],
                    "direccion": s[2] or "",
                    "telefono": s[3] or "",
                    "codigo": s[4] or "",
                    "extension": s[5] or "",
                    "estado": "activa" if s[6] else "inactiva",
                    "zona": s[7] or "Santo_Domingo"
                }
                for s in sucursales
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error listing sucursales: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/sucursales")
async def create_sucursal(nombre: str, direccion: str = "", telefono: str = "", zona: str = "Santo_Domingo", db=Depends(get_db)):
    """Crear sucursal"""
    try:
        cur = db.cursor()
        cur.execute("INSERT INTO sucursales (nombre, direccion, telefono, zona, activo, fecha_creacion) VALUES (%s, %s, %s, %s, true, NOW()) RETURNING id", 
                   (nombre, direccion if direccion else None, telefono if telefono else None, zona))
        sucursal_id = cur.fetchone()[0]
        db.commit()
        return {"id": sucursal_id, "nombre": nombre, "direccion": direccion, "telefono": telefono, "zona": zona, "estado": "activa"}
    except Exception as e:
        logger.error(f"Error creating sucursal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/sucursales/{sucursal_id}")
async def update_sucursal(sucursal_id: int, nombre: str, direccion: str = "", telefono: str = "", zona: str = "", db=Depends(get_db)):
    """Actualizar sucursal"""
    try:
        cur = db.cursor()
        if zona:
            cur.execute("UPDATE sucursales SET nombre = %s, direccion = %s, telefono = %s, zona = %s WHERE id = %s", 
                       (nombre, direccion if direccion else None, telefono if telefono else None, zona, sucursal_id))
        else:
            cur.execute("UPDATE sucursales SET nombre = %s, direccion = %s, telefono = %s WHERE id = %s", 
                       (nombre, direccion if direccion else None, telefono if telefono else None, sucursal_id))
        db.commit()
        return {"id": sucursal_id, "nombre": nombre, "direccion": direccion, "telefono": telefono, "zona": zona, "message": "Sucursal actualizada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error updating sucursal: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/v1/sucursales/{sucursal_id}/estado")
async def update_sucursal_estado(sucursal_id: int, activo: bool, db=Depends(get_db)):
    """Cambiar estado de sucursal"""
    try:
        cur = db.cursor()
        cur.execute("UPDATE sucursales SET activo = %s WHERE id = %s", (activo, sucursal_id))
        db.commit()
        return {"id": sucursal_id, "activo": activo, "message": "Estado actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error updating sucursal estado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# USUARIOS ENDPOINTS (Organized by Sucursal)
# ============================================================

@app.get("/api/v1/usuarios")
async def list_usuarios(sucursal_id: int = None, skip: int = 0, limit: int = 200, db=Depends(get_db)):
    """Listar usuarios, opcionalmente filtrados por sucursal"""
    try:
        cur = db.cursor()
        if sucursal_id:
            cur.execute("SELECT id, username, nombre_completo, email, rol, sucursal_id, telefono, activo FROM usuarios WHERE sucursal_id = %s LIMIT %s OFFSET %s", (sucursal_id, limit, skip))
        else:
            cur.execute("SELECT id, username, nombre_completo, email, rol, sucursal_id, telefono, activo FROM usuarios LIMIT %s OFFSET %s", (limit, skip))
        
        usuarios = cur.fetchall()
        return {
            "total": len(usuarios),
            "usuarios": [
                {
                    "id": u[0],
                    "username": u[1],
                    "nombre_completo": u[2],
                    "email": u[3],
                    "rol": u[4],
                    "sucursal_id": u[5],
                    "telefono": u[6],
                    "activo": u[7]
                }
                for u in usuarios
            ]
        }
    except Exception as e:
        logger.error(f"Error listing usuarios: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/usuarios")
async def create_usuario(nombre_completo: str, email: str, password: str = None, username: str = None, rol: str = "Empleado", sucursal_id: int = None, telefono: str = "", db=Depends(get_db)):
    """Crear usuario con contraseña hasheada (genera temporal si no se proporciona)"""
    try:
        # Normalizar rol
        if rol and rol.lower() == 'contabilidad':
            rol = 'Contabilidad'
        
        # Generar contraseña temporal si no se proporciona
        if not password:
            password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        
        # Usar username si se proporciona, si no generarlo del email
        if not username:
            username = email.split('@')[0] if email else f"user_{sucursal_id}"
        
        cur = db.cursor()
        
        # Hash usando SHA256 (consistente con BD)
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        cur.execute(
            "INSERT INTO usuarios (username, password_hash, nombre_completo, email, telefono, rol, sucursal_id, activo, fecha_creacion) VALUES (%s, %s, %s, %s, %s, %s, %s, true, NOW()) RETURNING id",
            (username, password_hash, nombre_completo, email if email else None, telefono if telefono else None, rol or "Empleado", sucursal_id)
        )
        usuario_id = cur.fetchone()[0]
        db.commit()
        return {"id": usuario_id, "nombre_completo": nombre_completo, "email": email, "rol": rol or "Empleado", "sucursal_id": sucursal_id, "username": username, "temporal_password": password, "estado": "activo"}
    except Exception as e:
        logger.error(f"Error creating usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))
@app.put("/api/v1/usuarios/{usuario_id}")
async def update_usuario(usuario_id: int, nombre_completo: str = "", email: str = "", rol: str = "", telefono: str = "", sucursal_id: int = None, password: str = None, db=Depends(get_db)):
    """Actualizar usuario con soporte para cambio de contrasena"""
    try:
        cur = db.cursor()
        updates = []
        values = []
        
        if nombre_completo:
            updates.append("nombre_completo = %s")
            values.append(nombre_completo)
        if email:
            updates.append("email = %s")
            values.append(email)
        if rol:
            # Normalizar rol: "contabilidad" -> "Contabilidad"
            if rol.lower() == 'contabilidad':
                rol = 'Contabilidad'
            updates.append("rol = %s")
            values.append(rol)
        if telefono:
            updates.append("telefono = %s")
            values.append(telefono)
        if sucursal_id:
            updates.append("sucursal_id = %s")
            values.append(sucursal_id)
        if password:
            # Usar SHA256 (consistente con login y creación)
            password_hash = hashlib.sha256(password.encode()).hexdigest()
            updates.append("password_hash = %s")
            values.append(password_hash)
        
        if updates:
            updates.append("fecha_modificacion = NOW()")
            values.append(usuario_id)
            query = f"UPDATE usuarios SET {', '.join(updates)} WHERE id = %s"
            cur.execute(query, values)
            db.commit()
        
        return {"id": usuario_id, "message": "Usuario actualizado"}
    except Exception as e:
        logger.error(f"Error updating usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/usuarios/{usuario_id}")
async def delete_usuario(usuario_id: int, db=Depends(get_db)):
    """Eliminar usuario"""
    try:
        cur = db.cursor()
        cur.execute("DELETE FROM usuarios WHERE id = %s", (usuario_id,))
        db.commit()
        return {"id": usuario_id, "message": "Usuario eliminado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
        logger.error(f"Error deleting usuario: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.patch("/api/v1/usuarios/{usuario_id}/estado")
async def toggle_usuario_estado(usuario_id: int, activo: bool, db=Depends(get_db)):
    """Cambiar estado de usuario"""
    try:
        cur = db.cursor()
        cur.execute("UPDATE usuarios SET activo = %s, fecha_modificacion = NOW() WHERE id = %s", (activo, usuario_id))
        db.commit()
        return {"id": usuario_id, "activo": activo, "message": "Estado actualizado"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))



# ============================================================
# EMPLEADOS ENDPOINTS (Using usuarios table)
# ============================================================

@app.get("/api/v1/debug/empleados")
async def debug_empleados(db=Depends(get_db)):
    """DEBUG: Ver todos los empleados en BD sin filtro"""
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT id, nombre_completo, rol, sucursal_id, email
            FROM usuarios
            WHERE rol IN ('colorista', 'facturador', 'encargado', 'operador', 'auxiliar_almacen', 'administrador', 'analista')
            ORDER BY id
            LIMIT 50
        """)
        empleados = cur.fetchall()
        return {
            "total": len(empleados),
            "empleados": [
                {
                    "id": e[0],
                    "nombre_completo": e[1],
                    "rol": e[2],
                    "sucursal_id": e[3],
                    "email": e[4]
                }
                for e in empleados
            ]
        }
    except Exception as e:
        logger.error(f"Debug error: {e}")
        return {"error": str(e)}

@app.post("/api/v1/empleados")
async def create_empleado(data: EmpleadoUpdate, db=Depends(get_db)):
    """Crear empleado en coloristas"""
    try:
        cur = db.cursor()
        
        mapeo_inverso = {
            "Arroyo Hondo": "Arroyohondo",
            "Bella Vista": "Bellavista",
            "Puerto Plata": "Puertoplata",
            "Punta Cana": "Puntacana",
            "Rafael Vidal": "Rafaelvidal",
            "San Francisco": "Sanfrancisco",
            "San Martin": "Sanmartin",
            "Santiago Bartolome Colon": "Santiago1",
            "test": "Test",
            "Villa Mella": "Villamella",
            "Zona Oriental": "Zonaoriental",
            "Bavaro": "Bavaro"
        }
        
        sucursal_nombre = ""
        if data.sucursal_id:
            cur.execute("SELECT nombre FROM sucursales WHERE id = %s", (data.sucursal_id,))
            sucursal_row = cur.fetchone()
            if sucursal_row:
                sucursal_nombre = sucursal_row[0]
        
        sucursal_code = mapeo_inverso.get(sucursal_nombre, sucursal_nombre)
        
        codigo_empleado = data.codigo_empleado or data.nombre_completo.replace(" ", "_").lower()
        cur.execute(
            "INSERT INTO coloristas (nombre, sucursal, rol, activo, creado_en, codigo_empleado) VALUES (%s, %s, %s, true, NOW(), %s) RETURNING id",
            (data.nombre_completo, sucursal_code, data.rol or "colorista", codigo_empleado)
        )
        empleado_id = cur.fetchone()[0]
        db.commit()
        
        logger.info(f"[CREATE EMPLEADO] ID={empleado_id}, Nombre={data.nombre_completo}")
        
        return {
            "id": empleado_id,
            "nombre_completo": data.nombre_completo,
            "email": data.email or "",
            "posicion": data.rol or "colorista",
            "sucursal_id": data.sucursal_id,
            "sucursal_nombre": sucursal_nombre,
            "telefono": data.telefono or "",
            "activo": True,
            "message": "Empleado creado exitosamente"
        }
    except Exception as e:
        logger.error(f"Error creating empleado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.put("/api/v1/empleados/{empleado_id}")
async def update_empleado(empleado_id: int, data: EmpleadoUpdate, db=Depends(get_db)):
    """Actualizar empleado en coloristas"""
    try:
        cur = db.cursor()
        
        # Actualizar coloristas (nombre, sucursal, rol)
        coloristas_updates = []
        coloristas_params = []
        
        if data.nombre_completo:
            coloristas_updates.append("nombre = %s")
            coloristas_params.append(data.nombre_completo)
        
        if data.sucursal_id:
            # Obtener nombre de sucursal
            cur.execute("SELECT nombre FROM sucursales WHERE id = %s", (data.sucursal_id,))
            sucursal_row = cur.fetchone()
            if sucursal_row:
                sucursal_nombre = sucursal_row[0]
                # Aplicar mapeo inverso
                mapeo_inverso = {
                    "Arroyo Hondo": "Arroyohondo",
                    "Bella Vista": "Bellavista",
                    "Puerto Plata": "Puertoplata",
                    "Punta Cana": "Puntacana",
                    "Rafael Vidal": "Rafaelvidal",
                    "San Francisco": "Sanfrancisco",
                    "San Martin": "Sanmartin",
                    "Santiago Bartolome Colon": "Santiago1",
                    "test": "Test",
                    "Villa Mella": "Villamella",
                    "Zona Oriental": "Zonaoriental",
                    "Bavaro": "Bavaro"
                }
                sucursal_code = mapeo_inverso.get(sucursal_nombre, sucursal_nombre)
                coloristas_updates.append("sucursal = %s")
                coloristas_params.append(sucursal_code)
        
        # Agregar rol a coloristas
        if data.rol:
            coloristas_updates.append("rol = %s")
            coloristas_params.append(data.rol)
        
        # Agregar codigo_empleado a coloristas
        if data.codigo_empleado:
            coloristas_updates.append("codigo_empleado = %s")
            coloristas_params.append(data.codigo_empleado)
        
        # Ejecutar actualización en coloristas
        if coloristas_updates:
            coloristas_params.append(empleado_id)
            coloristas_query = "UPDATE coloristas SET " + ", ".join(coloristas_updates) + " WHERE id = %s"
            logger.info(f"[UPDATE COLORISTAS] ID={empleado_id}, Query={coloristas_query}")
            cur.execute(coloristas_query, coloristas_params)
            db.commit()
            logger.info(f"[UPDATE COLORISTAS] OK - {cur.rowcount} filas actualizadas")
        
        # Actualizar usuarios si existe (email, telefono, sucursal_id) - sincronización opcional
        usuarios_updates = []
        usuarios_params = []
        
        if data.email:
            usuarios_updates.append("email = %s")
            usuarios_params.append(data.email)
        if data.telefono is not None:
            usuarios_updates.append("telefono = %s")
            usuarios_params.append(data.telefono)
        if data.sucursal_id:
            usuarios_updates.append("sucursal_id = %s")
            usuarios_params.append(data.sucursal_id)
        
        if usuarios_updates:
            usuarios_params.append(empleado_id)
            usuarios_query = "UPDATE usuarios SET " + ", ".join(usuarios_updates) + " WHERE id = %s"
            logger.info(f"[SYNC USUARIOS] ID={empleado_id}")
            cur.execute(usuarios_query, usuarios_params)
            db.commit()
        
        return {"id": empleado_id, "message": "Empleado actualizado"}
        
        return {"id": empleado_id, "message": "Empleado actualizado"}
    except Exception as e:
        logger.error(f"Error updating empleado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/v1/empleados/{empleado_id}")
async def delete_empleado(empleado_id: int, db=Depends(get_db)):
    """Eliminar empleado de coloristas o encargados"""
    try:
        cur = db.cursor()
        # Intenta eliminar de coloristas primero
        cur.execute("DELETE FROM coloristas WHERE id = %s", (empleado_id,))
        deleted_from_coloristas = cur.rowcount > 0
        
        # Si no estaba en coloristas, intenta de encargados
        if not deleted_from_coloristas:
            cur.execute("DELETE FROM encargados WHERE id = %s", (empleado_id,))
        
        db.commit()
        logger.info(f"[DELETE EMPLEADO] ID={empleado_id}")
        return {"id": empleado_id, "message": "Empleado eliminado"}
    except Exception as e:
        logger.error(f"Error deleting empleado: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ============================================================
# USUARIOS ONLINE (ACTIVIDAD)
# ============================================================


@app.post("/api/v1/desktop/register")
async def register_desktop_app(nombre_programa: str, version: str = "", maquina: str = "", usuario_so: str = ""):
    """Registrar un programa de escritorio como activo"""
    try:
        # Crear ID único para el programa
        app_id = f"{nombre_programa}_{maquina}_{usuario_so}"
        
        ACTIVE_SESSIONS[app_id] = {
            "tipo": "desktop",
            "nombre_programa": nombre_programa,
            "version": version,
            "maquina": maquina,
            "usuario_so": usuario_so,
            "departamento": "Programas Desktop",
            "ultima_actividad": time.time()
        }
        
        return {"id": app_id, "message": f"Programa {nombre_programa} registrado"}
    except Exception as e:
        logger.error(f"Error registering desktop app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/desktop/heartbeat/{app_id}")
async def desktop_heartbeat(app_id: str):
    """Actualizar actividad de programa desktop (heartbeat)"""
    try:
        if app_id in ACTIVE_SESSIONS and ACTIVE_SESSIONS[app_id].get("tipo") == "desktop":
            ACTIVE_SESSIONS[app_id]["ultima_actividad"] = time.time()
            return {"message": "Heartbeat registrado"}
        else:
            raise HTTPException(status_code=404, detail="Programa no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in desktop heartbeat: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/desktop/unregister/{app_id}")
async def unregister_desktop_app(app_id: str):
    """Desregistrar un programa de escritorio"""
    try:
        if app_id in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[app_id]
            return {"message": "Programa desconectado"}
        else:
            raise HTTPException(status_code=404, detail="Programa no encontrado")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error unregistering desktop app: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/online")
async def get_online_users():
    """Listar usuarios y programas desktop online"""
    try:
        # Limpiar sesiones antiguas (más de 30 minutos sin actividad)
        current_time = time.time()
        timeout = 30 * 60  # 30 minutos
        
        usuarios_timeout = [uid for uid, data in ACTIVE_SESSIONS.items() if current_time - data["ultima_actividad"] > timeout]
        for uid in usuarios_timeout:
            del ACTIVE_SESSIONS[uid]
        
        # Separar usuarios de programas desktop
        usuarios = {}
        programas = []
        
        por_departamento = {
            "Tienda": [],
            "Departamento TI": [],
            "Finanzas": [],
            "Otros": []
        }
        
        for session_id, datos in ACTIVE_SESSIONS.items():
            if datos.get("tipo") == "desktop":
                # Es un programa de escritorio
                programas.append({
                    "id": session_id,
                    "nombre_programa": datos.get("nombre_programa", "N/A"),
                    "version": datos.get("version", ""),
                    "maquina": datos.get("maquina", ""),
                    "usuario_so": datos.get("usuario_so", "")
                })
            else:
                # Es un usuario web
                depto = datos.get("departamento", "Otros")
                por_departamento[depto].append({
                    "id": session_id,
                    "username": datos.get("username", "N/A"),
                    "nombre_completo": datos.get("nombre_completo", "N/A"),
                    "rol": datos.get("rol", "N/A"),
                    "email": datos.get("email", "")
                })
        
        # Eliminar departamentos vacíos
        usuarios_result = {k: v for k, v in por_departamento.items() if v}
        
        return {
            "total": len(ACTIVE_SESSIONS),
            "usuarios_web": usuarios_result,
            "programas_desktop": programas,
            "total_usuarios": sum(len(v) for v in usuarios_result.values()),
            "total_programas": len(programas)
        }
    except Exception as e:
        logger.error(f"Error getting online users: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/logout/{usuario_id}")
async def logout_user(usuario_id: int):
    """Desloguear a un usuario"""
    try:
        if usuario_id in ACTIVE_SESSIONS:
            del ACTIVE_SESSIONS[usuario_id]
            return {"message": "Usuario deslogeado correctamente"}
        else:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en sesiones activas")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error logging out user: {e}")
        raise HTTPException(status_code=500, detail=str(e))




@app.get("/api/v1/login-activity")
async def get_login_activity(limit: int = 50, db=Depends(get_db)):
    """Obtener historial de logins recientes"""
    try:
        cur = db.cursor()
        cur.execute("""
            SELECT usuario_id, username, nombre_completo, rol, sucursal, fecha_hora_login 
            FROM login_audits 
            ORDER BY fecha_hora_login DESC 
            LIMIT %s
        """, (limit,))
        
        audits = cur.fetchall()
        
        result = [
            {
                "usuario_id": a[0],
                "username": a[1],
                "nombre_completo": a[2],
                "rol": a[3],
                "sucursal": a[4],
                "fecha_hora_login": a[5].isoformat() if a[5] else None
            }
            for a in audits
        ]
        
        return {
            "total": len(result),
            "logins": result
        }
    except Exception as e:
        logger.error(f"Error getting login activity: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8001)
