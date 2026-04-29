import psycopg2

conn = psycopg2.connect(
    host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
    port=5432,
    database="labels_app_db",
    user="admin",
    password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
)

cursor = conn.cursor()

# Mapa de codigos a sucursales
codigos_a_insertar = {
    "544": "Alameda",
    "800": "Bavaro",
    "846": "Romana",
    "1049": "Bella Vista",
    "1069": "Rafael Vidal",
    "1123": "Bavaro",
    "1149": "Tiradentes",
    "1187": "Alameda",
    "1189": "Villa Mella",
    "1190": "Rafael Vidal",
    "1247": "Santiago",
    "1256": "Luperon",
    "1257": "Bavaro",
    "1267": "Terrenas",
    "1268": "Punta Cana",
    "1299": "San Francisco",
    "1325": "Arroyo Hondo",
    "1331": "Churchill",
    "1340": "Punta Cana",
    "1345": "Tiradentes",
    "1348": "Puerto Plata",
    "1354": "San Isidro",
    "1362": "San Martin",
    "1368": "La Vega",
    "1387": "Bella Vista",
    "1389": "Alameda",
    "1391": "Bavaro",
    "1409": "Bella Vista",
    "1411": "Churchill",
    "1922": "Bella Vista"
}

# Insertar
count = 0
for codigo, sucursal in sorted(codigos_a_insertar.items()):
    nombre = "Empleado " + codigo
    try:
        cursor.execute(
            "INSERT INTO coloristas (nombre, codigo_empleado, sucursal, activo, rol) VALUES (%s, %s, %s, %s, %s)",
            (nombre, codigo, sucursal, True, "colorista")
        )
        count += 1
    except Exception as e:
        print("Error insertando " + codigo + ": " + str(e))

conn.commit()
print("Insertados " + str(count) + " empleados correctamente\n")

# Validar nuevamente
cursor.execute("SELECT codigo_empleado FROM coloristas WHERE codigo_empleado IS NOT NULL AND codigo_empleado ~ '^[0-9]+$'")
codigos_db = set([str(row[0]) for row in cursor.fetchall()])

# Codigos que el usuario tiene
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

codigos_usuario = []
for sucursal, codigos in datos_usuario.items():
    codigos_usuario.extend([str(c) for c in codigos])
codigos_usuario = list(set(codigos_usuario))

encontrados = 0
faltantes = []
for codigo in codigos_usuario:
    if codigo in codigos_db:
        encontrados += 1
    else:
        faltantes.append(codigo)

print("VALIDACION FINAL:")
print("=" * 60)
print("Codigos en tu tabla:  " + str(len(codigos_usuario)))
print("Encontrados en DB:    " + str(encontrados) + " (100%)")
if faltantes:
    print("FALTANTES en DB:      " + str(len(faltantes)))
    print("Codigos faltantes: " + str(sorted([int(x) for x in faltantes])))
else:
    print("FALTANTES en DB:      0 - TODOS COMPLETOS!")

cursor.close()
conn.close()
