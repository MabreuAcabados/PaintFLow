with open("employees.html", "r", encoding="utf-8") as f:
    contenido = f.read()

# 1. Agregar codigo_empleado en abrirModalEmpleado cuando se cargan datos existentes
old_edit = """                if (empleado) {
                    document.getElementById("editingEmpleadoId").value = id;
                    document.getElementById("inputNombreEmpleado").value = empleado.nombre_completo || empleado.nombre || "";
                    document.getElementById("inputEmailEmpleado").value = empleado.email || "";
                    document.getElementById("inputPosicionEmpleado").value = empleado.posicion || empleado.rol || "colorista";
                    document.getElementById("inputSucursalEmpleado").value = empleado.sucursal_id || "";
                    document.getElementById("inputTelefonoEmpleado").value = empleado.telefono || "";
                    document.getElementById("inputActivoEmpleado").checked = (empleado.activo === true || empleado.activo === 1);"""

new_edit = """                if (empleado) {
                    document.getElementById("editingEmpleadoId").value = id;
                    document.getElementById("inputNombreEmpleado").value = empleado.nombre_completo || empleado.nombre || "";
                    document.getElementById("inputCodigoEmpleado").value = empleado.codigo_empleado || "";
                    document.getElementById("inputEmailEmpleado").value = empleado.email || "";
                    document.getElementById("inputPosicionEmpleado").value = empleado.posicion || empleado.rol || "colorista";
                    document.getElementById("inputSucursalEmpleado").value = empleado.sucursal_id || "";
                    document.getElementById("inputTelefonoEmpleado").value = empleado.telefono || "";
                    document.getElementById("inputActivoEmpleado").checked = (empleado.activo === true || empleado.activo === 1);"""

contenido = contenido.replace(old_edit, new_edit)

# 2. Limpiar codigo_empleado para nuevo empleado
old_new = """            } else {
                document.getElementById("editingEmpleadoId").value = "";
                document.getElementById("inputNombreEmpleado").value = "";
                document.getElementById("inputEmailEmpleado").value = "";
                document.getElementById("inputPosicionEmpleado").value = "colorista";
                document.getElementById("inputTelefonoEmpleado").value = "";
                document.getElementById("inputActivoEmpleado").checked = true;"""

new_new = """            } else {
                document.getElementById("editingEmpleadoId").value = "";
                document.getElementById("inputNombreEmpleado").value = "";
                document.getElementById("inputCodigoEmpleado").value = "";
                document.getElementById("inputEmailEmpleado").value = "";
                document.getElementById("inputPosicionEmpleado").value = "colorista";
                document.getElementById("inputTelefonoEmpleado").value = "";
                document.getElementById("inputActivoEmpleado").checked = true;"""

contenido = contenido.replace(old_new, new_new)

# 3. Agregar codigo_empleado al payload en guardarEmpleado
old_payload = """            const payload = {
                nombre_completo: nombre,
                email: email,
                rol: posicion,
                sucursal_id: sucursal_id,
                telefono: telefono,
                activo: activo
            };"""

new_payload = """            const codigo_empleado = document.getElementById("inputCodigoEmpleado").value;
            const payload = {
                nombre_completo: nombre,
                email: email,
                rol: posicion,
                sucursal_id: sucursal_id,
                telefono: telefono,
                codigo_empleado: codigo_empleado,
                activo: activo
            };"""

contenido = contenido.replace(old_payload, new_payload)

with open("employees.html", "w", encoding="utf-8") as f:
    f.write(contenido)

print("Funciones JavaScript actualizadas para codigo_empleado")
