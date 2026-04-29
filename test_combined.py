import psycopg2

conn = psycopg2.connect(
    host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
    port=5432,
    database="labels_app_db",
    user="admin",
    password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
)

cursor = conn.cursor()

# Ejecutar exactamente la consulta de coloristas
cursor.execute("""
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
    LIMIT 3
""")
coloristas = cursor.fetchall()
print(f"Coloristas ({len(coloristas)} filas):")
for row in coloristas:
    print(f"  Campos: {len(row)}, Valores: {row}")

# Ejecutar exactamente la consulta de encargados
cursor.execute("""
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
    LIMIT 3
""")
encargados = cursor.fetchall()
print(f"\nEncargados ({len(encargados)} filas):")
for row in encargados:
    print(f"  Campos: {len(row)}, Valores: {row}")

# Combinar
todos = list(coloristas) + list(encargados)
print(f"\nTotal combinados: {len(todos)}")
print(f"Intentando acceder a e[7] para cada uno:")
for i, e in enumerate(todos[:5]):
    try:
        val = e[7]
        print(f"  Row {i}: e[7] = {val}")
    except IndexError as ex:
        print(f"  Row {i}: ERROR - {ex}")

cursor.close()
conn.close()
