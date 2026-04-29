import json
import urllib.request

with urllib.request.urlopen('http://localhost:8001/api/v1/empleados?limit=500') as response:
    data = json.loads(response.read())

empleados_db = data.get('empleados', [])

print(f'Total empleados en DB: {len(empleados_db)}\n')
print('ID | Nombre | Sucursal')
print('-' * 60)

for emp in empleados_db[:30]:
    print(f'{emp.get(\"id\", \"N/A\")} | {emp.get(\"nombre_completo\", \"N/A\")[:30]} | {emp.get(\"sucursal_nombre\", \"N/A\")}')

print(f'\n\nTodos los IDs en DB: {[e.get(\"id\") for e in empleados_db]}')
