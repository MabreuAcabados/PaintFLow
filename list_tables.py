import psycopg2
from config import settings

conn = psycopg2.connect(
    host=settings.DB_HOST,
    user=settings.DB_USER,
    password=settings.DB_PASSWORD,
    database=settings.DB_NAME,
    port=settings.DB_PORT
)
cur = conn.cursor()
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
""")
tables = cur.fetchall()
print("TABLAS DISPONIBLES:")
for t in tables:
    print(f"  - {t[0]}")
cur.close()
conn.close()
