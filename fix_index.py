with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# Cambiar e[8] por e[7] para codigo_empleado
contenido = contenido.replace(
    '"codigo_empleado": e[8] or "",',
    '"codigo_empleado": e[7] or "",'
)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(contenido)

print("Corregido indice de codigo_empleado: e[7]")
