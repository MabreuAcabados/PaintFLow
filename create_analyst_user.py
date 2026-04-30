#!/usr/bin/env python3
"""
Script para crear o actualizar un usuario analista para pruebas
"""

import hashlib
from database import DatabasePool

def create_or_update_analyst():
    """Crear o actualizar usuario analista para pruebas"""
    conn = None
    try:
        conn = DatabasePool.get_connection()
        cur = conn.cursor()
        
        # Datos del usuario analista
        username = "analista"
        password = "analista123"
        nombre_completo = "Usuario Analista"
        email = "analista@paintflow.com"
        password_hash = hashlib.sha256(password.encode()).hexdigest()
        
        # Verificar si existe el usuario
        cur.execute("SELECT id FROM usuarios WHERE username = %s", (username,))
        user_exists = cur.fetchone()
        
        if user_exists:
            # Actualizar usuario existente
            cur.execute("""
                UPDATE usuarios 
                SET password_hash = %s, nombre_completo = %s, email = %s, rol = 'analista', activo = true
                WHERE username = %s
            """, (password_hash, nombre_completo, email, username))
            print(f"✅ Usuario '{username}' actualizado exitosamente")
        else:
            # Crear nuevo usuario
            cur.execute("""
                INSERT INTO usuarios (username, password_hash, nombre_completo, email, rol, sucursal_id, activo)
                VALUES (%s, %s, %s, %s, 'analista', 1, true)
            """, (username, password_hash, nombre_completo, email))
            print(f"✅ Usuario '{username}' creado exitosamente")
        
        conn.commit()
        print(f"📝 Credenciales: {username} / {password}")
        print(f"🎯 Rol: analista")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if conn:
            DatabasePool.return_connection(conn)

if __name__ == "__main__":
    create_or_update_analyst()