import urllib.request
import json

with urllib.request.urlopen("http://localhost:8001/api/v1/empleados?limit=500") as response:
    data = json.loads(response.read())

empleados_db = data.get("empleados", [])
print("Total empleados en DB (API): " + str(len(empleados_db)))
print("\nEmpleados por sucursal:")

sucursales = {}
for emp in empleados_db:
    suc = emp.get("sucursal_nombre", "N/A")
    if suc not in sucursales:
        sucursales[suc] = 0
    sucursales[suc] += 1

for suc in sorted(sucursales.keys()):
    print("  " + suc + ": " + str(sucursales[suc]))
