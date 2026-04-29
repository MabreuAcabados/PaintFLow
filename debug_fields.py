# Revisar específicamente qué está pasando en main.py para el error
with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# Encontrar la línea del error
if '"codigo_empleado": e[7] or ""' in contenido:
    print("OK: codigo_empleado usa e[7]")
else:
    print("ERROR: no encontrado codigo_empleado: e[7]")

# Contar cuántos campos hay en ambos SELECTs
import re
matches_c = re.findall(r"c\.(\w+)|u\.(\w+)", contenido[contenido.find("SELECT"):contenido.find("FROM coloristas")])
matches_e = re.findall(r"e\.(\w+)|NULL", contenido[contenido.find("SELECT", contenido.find("FROM coloristas")):contenido.find("FROM encargados")])

print(f"Campos coloristas: {len([x for x in matches_c if x])}")
print(f"Campos encargados: {len([x for x in matches_e])}")
