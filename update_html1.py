with open("employees.html", "r", encoding="utf-8") as f:
    contenido = f.read()

# 1. Actualizar headers de la tabla - agregar "Codigo" al inicio
old_headers = """                ['Nombre', 'Email', 'Sucursal', 'Posición', 'Teléfono', 'Estado', 'Acciones']"""

new_headers = """                ['Codigo', 'Nombre', 'Email', 'Sucursal', 'Posición', 'Teléfono', 'Estado', 'Acciones']"""

contenido = contenido.replace(old_headers, new_headers)

# 2. Actualizar colspan de "Sin empleados" de 7 a 8
old_colspan = """                    td.colSpan = 7;"""
new_colspan = """                    td.colSpan = 8;"""

contenido = contenido.replace(old_colspan, new_colspan)

# 3. Actualizar las filas de empleados para incluir codigo_empleado
old_tr = """                        tr.innerHTML = `
                            <td>${nombreEmpleado}</td>
                            <td>${email}</td>
                            <td>${sucursal}</td>
                            <td>${posicion}</td>
                            <td>${telefono}</td>
                            <td>${estado}</td>
                            <td>
                                <button class="btn-action btn-edit" onclick="abrirModalEmpleado(${e.id})">Editar</button>
                                <button class="btn-action btn-delete" onclick="eliminarEmpleado(${e.id})" title="Eliminar">&times;</button>
                            </td>
                        `;"""

new_tr = """                        const codigoEmpleado = e.codigo_empleado || 'N/A';
                        tr.innerHTML = `
                            <td>${codigoEmpleado}</td>
                            <td>${nombreEmpleado}</td>
                            <td>${email}</td>
                            <td>${sucursal}</td>
                            <td>${posicion}</td>
                            <td>${telefono}</td>
                            <td>${estado}</td>
                            <td>
                                <button class="btn-action btn-edit" onclick="abrirModalEmpleado(${e.id})">Editar</button>
                                <button class="btn-action btn-delete" onclick="eliminarEmpleado(${e.id})" title="Eliminar">&times;</button>
                            </td>
                        `;"""

contenido = contenido.replace(old_tr, new_tr)

with open("employees.html", "w", encoding="utf-8") as f:
    f.write(contenido)

print("employees.html actualizado - tabla con codigo_empleado")
