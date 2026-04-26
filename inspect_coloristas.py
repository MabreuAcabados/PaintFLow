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
    
    # Obtener estructura de la tabla coloristas
    print("--- Estructura de la tabla 'coloristas' ---")
    cursor.execute("""
        SELECT column_name, data_type 
        FROM information_schema.columns 
        WHERE table_name = 'coloristas'
        ORDER BY ordinal_position;
    """)
    columns = cursor.fetchall()
    for col in columns:
        print(f"Columna: {col[0]}, Tipo: {col[1]}")
    
    print("\n--- Datos de ejemplo (5 registros) ---")
    cursor.execute("SELECT * FROM coloristas LIMIT 5;")
    rows = cursor.fetchall()
    colnames = [desc[0] for desc in cursor.description]
    print(f"Columnas detectadas: {colnames}")
    for row in rows:
        print(row)
        
    cursor.close()
    conn.close()
except Exception as e:
    print(f"Error: {e}")
