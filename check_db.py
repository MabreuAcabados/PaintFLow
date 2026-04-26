import psycopg2
try:
    conn = psycopg2.connect(
        host="dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com",
        port=5432,
        database="labels_app_db",
        user="admin",
        password="KCFjzM4KYzSQx63ArufESIXq03EFXHz3"
    )
    cursor = conn.cursor()
    
    print("--- Listado de Tablas ---")
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
    tables = cursor.fetchall()
    for table in tables:
        print(table[0])
    
    print("\n--- Verificando Tabla 'empleados' ---")
    cursor.execute("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'empleados')")
    exists = cursor.fetchone()[0]
    
    if exists:
        print("La tabla 'empleados' existe.")
        cursor.execute("SELECT * FROM empleados LIMIT 5")
        rows = cursor.fetchall()
        colnames = [desc[0] for desc in cursor.description]
        print(f"Columnas: {colnames}")
        for row in rows:
            print(row)
    else:
        print("La tabla 'empleados' no existe.")
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
