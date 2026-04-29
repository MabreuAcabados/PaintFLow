with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# 1. Agregar c.codigo_empleado al SELECT de coloristas
old_select = """            SELECT 
                c.id, 
                c.nombre, 
                c.sucursal, 
                c.activo,
                c.rol,
                u.email,
                u.telefono
            FROM coloristas c
            LEFT JOIN usuarios u ON u.id = c.id"""

new_select = """            SELECT 
                c.id, 
                c.nombre, 
                c.sucursal, 
                c.activo,
                c.rol,
                u.email,
                u.telefono,
                c.codigo_empleado
            FROM coloristas c
            LEFT JOIN usuarios u ON u.id = c.id"""

contenido = contenido.replace(old_select, new_select)

# 2. Agregar NULL as codigo_empleado al SELECT de encargados
old_encargados = """            SELECT 
                e.id, 
                e.nombre, 
                e.sucursal, 
                e.activo,
                e.rol,
                NULL as email,
                NULL as telefono
            FROM encargados e"""

new_encargados = """            SELECT 
                e.id, 
                e.nombre, 
                e.sucursal, 
                e.activo,
                e.rol,
                NULL as email,
                NULL as telefono,
                NULL as codigo_empleado
            FROM encargados e"""

contenido = contenido.replace(old_encargados, new_encargados)

# 3. Agregar codigo_empleado al diccionario result
old_result = """            result.append({
                "id": e[0],
                "nombre_completo": e[1] or "",
                "email": e[5] or "",
                "posicion": e[4] or "colorista",
                "sucursal_id": sucursal_id,
                "sucursal_nombre": sucursal_mapped,
                "telefono": e[6] or "",
                "activo": e[3] if e[3] is not None else True
            })"""

new_result = """            result.append({
                "id": e[0],
                "nombre_completo": e[1] or "",
                "email": e[5] or "",
                "posicion": e[4] or "colorista",
                "sucursal_id": sucursal_id,
                "sucursal_nombre": sucursal_mapped,
                "telefono": e[6] or "",
                "codigo_empleado": e[8] or "",
                "activo": e[3] if e[3] is not None else True
            })"""

contenido = contenido.replace(old_result, new_result)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(contenido)

print("main.py actualizado con codigo_empleado")
