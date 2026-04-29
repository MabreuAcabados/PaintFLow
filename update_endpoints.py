with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# 1. Actualizar POST para usar data.codigo_empleado si se proporciona
old_post = """        cur.execute(
            "INSERT INTO coloristas (nombre, sucursal, rol, activo, creado_en, codigo_empleado) VALUES (%s, %s, %s, true, NOW(), %s) RETURNING id",
            (data.nombre_completo, sucursal_code, data.rol or "colorista", data.nombre_completo.replace(" ", "_").lower())
        )"""

new_post = """        codigo_empleado = data.codigo_empleado or data.nombre_completo.replace(" ", "_").lower()
        cur.execute(
            "INSERT INTO coloristas (nombre, sucursal, rol, activo, creado_en, codigo_empleado) VALUES (%s, %s, %s, true, NOW(), %s) RETURNING id",
            (data.nombre_completo, sucursal_code, data.rol or "colorista", codigo_empleado)
        )"""

contenido = contenido.replace(old_post, new_post)

# 2. Agregar codigo_empleado al PUT
old_put_start = """        # Agregar rol a coloristas
        if data.rol:
            coloristas_updates.append("rol = %s")
            coloristas_params.append(data.rol)
        
        # Ejecutar actualización en coloristas"""

new_put_start = """        # Agregar rol a coloristas
        if data.rol:
            coloristas_updates.append("rol = %s")
            coloristas_params.append(data.rol)
        
        # Agregar codigo_empleado a coloristas
        if data.codigo_empleado:
            coloristas_updates.append("codigo_empleado = %s")
            coloristas_params.append(data.codigo_empleado)
        
        # Ejecutar actualización en coloristas"""

contenido = contenido.replace(old_put_start, new_put_start)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(contenido)

print("Endpoints POST y PUT actualizados con codigo_empleado")
