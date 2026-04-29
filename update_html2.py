with open("employees.html", "r", encoding="utf-8") as f:
    contenido = f.read()

# Agregar campo de Código de Empleado al formulario - después de Nombre
old_form = """            <div class="form-group">
                <label>Nombre Completo *</label>
                <input type="text" id="inputNombreEmpleado">
            </div>
            <div class="form-group">
                <label>Email</label>"""

new_form = """            <div class="form-group">
                <label>Nombre Completo *</label>
                <input type="text" id="inputNombreEmpleado">
            </div>
            <div class="form-group">
                <label>Código de Empleado</label>
                <input type="text" id="inputCodigoEmpleado">
            </div>
            <div class="form-group">
                <label>Email</label>"""

contenido = contenido.replace(old_form, new_form)

with open("employees.html", "w", encoding="utf-8") as f:
    f.write(contenido)

print("Campo Codigo de Empleado agregado al formulario")
