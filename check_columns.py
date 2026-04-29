import psycopg2

conn = psycopg2.connect(
    host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
    port=5432,
    database="labels_app_db",
    user="admin",
    password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
)

cursor = conn.cursor()

# Obtener columnas de coloristas
cursor.execute("""
    SELECT column_name, data_type 
    FROM information_schema.columns 
    WHERE table_name = 'coloristas'
    ORDER BY ordinal_position
""")

print("Columnas en tabla COLORISTAS:")
for col in cursor.fetchall():
    print(f"  - {col[0]} ({col[1]})")

print("\n")

# Obtener algunas filas para ver los datos
cursor.execute("SELECT * FROM coloristas LIMIT 3")
print("Primeros registros de COLORISTAS:")
for row in cursor.fetchall():
    print(f"  {row}")

cursor.close()
conn.close()
