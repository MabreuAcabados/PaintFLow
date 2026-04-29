import psycopg2

conn = psycopg2.connect(
    host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
    port=5432,
    database="labels_app_db",
    user="admin",
    password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
)

cursor = conn.cursor()

# Test coloristas
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
    LIMIT 1
""")
row_c = cursor.fetchone()
print(f"Coloristas: {len(row_c)} campos - {row_c}")

# Test encargados
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
    LIMIT 1
""")
row_e = cursor.fetchone()
print(f"Encargados: {len(row_e)} campos - {row_e}")

cursor.close()
conn.close()
