from database import DatabasePool

conn = DatabasePool.get_connection()
cur = conn.cursor()

print("=== EMPLEADOS ACTIVOS ===")
cur.execute("SELECT id, nombre, codigo_empleado, activo FROM coloristas WHERE activo = true ORDER BY nombre")
activos = cur.fetchall()
print(f"Total empleados ACTIVOS: {len(activos)}")
for row in activos[:5]:  # Mostrar solo los primeros 5
    print(f'  - {row[1]} (ID: {row[0]}, Código: {row[2]})')
if len(activos) > 5:
    print(f'  ... y {len(activos) - 5} más')

print("\n=== EMPLEADOS INACTIVOS ===")
cur.execute("SELECT id, nombre, codigo_empleado, activo FROM coloristas WHERE activo = false ORDER BY nombre")
inactivos = cur.fetchall()
print(f"Total empleados INACTIVOS: {len(inactivos)}")
for row in inactivos:
    print(f'  - {row[1]} (ID: {row[0]}, Código: {row[2]})')

print(f"\n=== RESUMEN ===")
print(f"Activos: {len(activos)}")
print(f"Inactivos: {len(inactivos)}")
print(f"Total en BD: {len(activos) + len(inactivos)}")

cur.close()
DatabasePool.return_connection(conn)