import psycopg2
from psycopg2.extras import RealDictCursor

# Test de optimización
conn_string = 'postgresql://admin:KCFjzM4KYzSQx63ArufESIXq03EFXHz3@dpg-d1b18u8dl3ps73e68v1g-a.oregon-postgres.render.com:5432/labels_app_db'
try:
    conn = psycopg2.connect(conn_string)
    cur = conn.cursor()
    
    # Cargar todas las sucursales de una sola vez
    cur.execute(" \\SELECT id nombre FROM sucursales\\\)
 sucursales = cur.fetchall()
 sucursal_dict = {s[1]: s[0] for s in sucursales}
 print(f'✓ Cargadas {len(sucursal_dict)} sucursales en 1 query')
 
 # Test de queries totales
 cur.execute('SELECT COUNT(*) FROM coloristas WHERE activo = true')
 count_coloristas = cur.fetchone()[0]
 print(f'✓ Coloristas: {count_coloristas}')
 
 cur.execute('SELECT COUNT(*) FROM encargados WHERE activo = true')
 count_encargados = cur.fetchone()[0]
 print(f'✓ Encargados: {count_encargados}')
 
 print(f'✓ TOTAL: {count_coloristas + count_encargados} empleados')
 print(f'✓ Ahorro: Antes {2 + count_coloristas + count_encargados} queries, Ahora 3 queries')
 
 conn.close()
except Exception as e:
 print(f'Error: {e}')
