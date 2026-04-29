with open("main.py", "r", encoding="utf-8") as f:
    lines = f.readlines()

# Encontrar la línea que tiene "u.telefono" en el SELECT de coloristas y agregar codigo_empleado
for i, line in enumerate(lines):
    if "u.telefono" in line and "FROM coloristas c" in "".join(lines[max(0, i-5):i]):
        lines[i] = line.rstrip() + ",\n" + " " * 16 + "c.codigo_empleado\n"
        break

with open("main.py", "w", encoding="utf-8") as f:
    f.writelines(lines)

print("Agregado codigo_empleado al SELECT")
