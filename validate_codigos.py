import psycopg2

conn = psycopg2.connect(
    host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
    port=5432,
    database="labels_app_db",
    user="admin",
    password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
)

cursor = conn.cursor()

# Datos que el usuario compartio
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

# Extraer codigos unicos
codigos_usuario = []
for sucursal, codigos in datos_usuario.items():
    codigos_usuario.extend([str(c) for c in codigos])
codigos_usuario = list(set(codigos_usuario))

# Obtener codigos en DB
cursor.execute("SELECT codigo_empleado FROM coloristas WHERE codigo_empleado IS NOT NULL")
codigos_db = set([str(row[0]) for row in cursor.fetchall()])

# Validar
encontrados = []
faltantes = []

for codigo in sorted(codigos_usuario):
    if codigo in codigos_db:
        encontrados.append(codigo)
    else:
        faltantes.append(codigo)

print("VALIDACION DE CODIGOS DE EMPLEADOS")
print("=" * 60)
print("Codigos en tu tabla:  " + str(len(codigos_usuario)))
print("Encontrados en DB:    " + str(len(encontrados)))
print("FALTANTES en DB:      " + str(len(faltantes)))
print("\n")

if faltantes:
    print("CODIGOS QUE FALTAN:")
    print(str(sorted([int(x) for x in faltantes])))
    print("\n")

print("CODIGOS ENCONTRADOS EN DB:")
print(str(sorted([int(x) for x in encontrados])))

cursor.close()
conn.close()
