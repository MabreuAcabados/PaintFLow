with open("main.py", "r", encoding="utf-8") as f:
    contenido = f.read()

# Agregar codigo_empleado al modelo EmpleadoUpdate
old_model = """class EmpleadoUpdate(BaseModel):
    nombre_completo: str = None
    email: str = None
    rol: str = None
    sucursal_id: int = None
    telefono: str = None
    activo: bool = True"""

new_model = """class EmpleadoUpdate(BaseModel):
    nombre_completo: str = None
    email: str = None
    rol: str = None
    sucursal_id: int = None
    telefono: str = None
    codigo_empleado: str = None
    activo: bool = True"""

contenido = contenido.replace(old_model, new_model)

with open("main.py", "w", encoding="utf-8") as f:
    f.write(contenido)

print("Modelo EmpleadoUpdate actualizado con codigo_empleado")
