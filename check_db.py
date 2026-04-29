import json
import urllib.request

with urllib.request.urlopen("http://localhost:8001/api/v1/empleados?limit=500") as response:
    data = json.loads(response.read())

empleados_db = data.get("empleados", [])

print(f"Total empleados en DB: {len(empleados_db)}\n")
print("ID | Nombre | Posicion | Sucursal")
print("-" * 70)

for emp in empleados_db:
    emp_id = emp.get("id", "N/A")
    nombre = emp.get("nombre_completo", "N/A")[:25]
    posicion = emp.get("posicion", "N/A")
    sucursal = emp.get("sucursal_nombre", "N/A")
    print(f"{emp_id} | {nombre:25s} | {posicion:15s} | {sucursal}")

ids = sorted([e.get("id") for e in empleados_db])
print(f"\n\nIDs encontrados: {ids}")
