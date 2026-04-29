import json
import urllib.request

datos_usuario = {
    "Tiradentes": [1149, 1345, 1386, 1008, 1019, 1408],
    "San Martin": [1347, 1362, 1355],
    "Bavaro": [800, 1257, 1073, 947, 1123, 1335, 1401, 1391],
    "Santiago": [1247, 1379, 1344],
    "Romana": [846, 910, 1376],
    "Churchill": [1331, 1361, 1077, 1411, 1337],
    "Zona Oriental": [1257, 1283, 1261, 1351],
    "Bella Vista": [1049, 1387, 1922, 1333, 1409],
    "Punta Cana": [1268, 1127, 1332, 1136, 1340],
    "Luperon": [1256, 1059, 1419, 1272],
    "Terrenas": [1267, 1278],
    "Arroyo Hondo": [1325, 1145],
    "Rafael Vidal": [1069, 1146, 1190, 1405, 1392, 1324],
    "San Francisco": [1299, 1372],
    "Alameda": [544, 1187, 1389],
    "San Isidro": [1354, 1305],
    "Puerto Plata": [1348, 470, 1352],
    "Villa Mella": [1189, 1147],
    "La Vega": [1368, 1363],
    "Bani": [1306, 1361]
}

with urllib.request.urlopen('http://localhost:8001/api/v1/empleados?limit=500') as response:
    data = json.loads(response.read())

empleados_db = data.get('empleados', [])
ids_en_db = {e.get('id'): e for e in empleados_db}

codigos_usuario = []
for sucursal, codigos in datos_usuario.items():
    codigos_usuario.extend(codigos)
codigos_usuario = list(set(codigos_usuario))

encontrados = []
faltantes = []

for codigo in sorted(codigos_usuario):
    if codigo in ids_en_db:
        encontrados.append(codigo)
    else:
        faltantes.append(codigo)

print(f"Empleados en tu tabla: {len(codigos_usuario)}")
print(f"Encontrados en DB: {len(encontrados)}")
print(f"Faltantes en DB: {len(faltantes)}")
print(f"\nFALTANTES: {sorted(faltantes)}")
