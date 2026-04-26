# Guia de Integracion - Programas de Escritorio con ACTIVIDAD

## Descripcion
Los programas de escritorio (LabelsApp, GestordeListadeEspera, etc.) pueden registrarse en el sistema de ACTIVIDAD para mostrar su estado online en la pestana ACTIVIDAD del dashboard.

## Endpoints Disponibles

### 1. Registrar Programa (Al iniciar)
POST /api/v1/desktop/register

Parametros:
- nombre_programa: string (Ej: "LabelsApp", "GestordeListadeEspera")
- version: string (Ej: "2.1.0")
- maquina: string (Ej: "PC-TIENDA-01")
- usuario_so: string (usuario del SO que ejecuta el programa, Ej: "admin")

Ejemplo Python:
import requests

response = requests.post(
    "https://paintflow.onrender.com/api/v1/desktop/register",
    params={
        "nombre_programa": "LabelsApp",
        "version": "2.1.0",
        "maquina": "PC-TIENDA-01",
        "usuario_so": "admin"
    }
)
app_id = response.json()["id"]  # Guardar este ID
print(f"Registrado: {app_id}")

Respuesta:
{
    "id": "LabelsApp_PC-TIENDA-01_admin",
    "message": "Programa LabelsApp registrado"
}

---

### 2. Heartbeat - Mantener Activo (Cada 5-10 minutos)
POST /api/v1/desktop/heartbeat/{app_id}

Ejemplo Python:
import time
import threading

def send_heartbeat(app_id):
    while True:
        time.sleep(300)  # Cada 5 minutos
        try:
            response = requests.post(
                f"https://paintflow.onrender.com/api/v1/desktop/heartbeat/{app_id}"
            )
            print(f"Heartbeat enviado: {response.status_code}")
        except Exception as e:
            print(f"Error en heartbeat: {e}")

# En thread separado
heartbeat_thread = threading.Thread(target=send_heartbeat, args=(app_id,), daemon=True)
heartbeat_thread.start()

---

### 3. Desregistrar Programa (Al cerrar)
POST /api/v1/desktop/unregister/{app_id}

Ejemplo Python:
def on_closing(app_id):
    try:
        response = requests.post(
            f"https://paintflow.onrender.com/api/v1/desktop/unregister/{app_id}"
        )
        print(f"Programa desconectado: {response.status_code}")
    except Exception as e:
        print(f"Error al desconectar: {e}")

---

## Integracion Completa - Ejemplo

import requests
import time
import threading
import atexit

class PaintFlowClient:
    def __init__(self, nombre_programa, version, maquina, usuario_so):
        self.api_url = "https://paintflow.onrender.com"
        self.nombre_programa = nombre_programa
        self.version = version
        self.maquina = maquina
        self.usuario_so = usuario_so
        self.app_id = None
        
    def registrarse(self):
        """Registrar programa al iniciar"""
        try:
            response = requests.post(
                f"{self.api_url}/api/v1/desktop/register",
                params={
                    "nombre_programa": self.nombre_programa,
                    "version": self.version,
                    "maquina": self.maquina,
                    "usuario_so": self.usuario_so
                }
            )
            self.app_id = response.json()["id"]
            print(f"Programa {self.nombre_programa} registrado como online")
            
            # Iniciar heartbeat en thread separado
            self._start_heartbeat()
            
            # Desregistrarse al cerrar
            atexit.register(self.desregistrarse)
            
        except Exception as e:
            print(f"Error registrando: {e}")
    
    def _start_heartbeat(self):
        """Enviar heartbeat cada 5 minutos"""
        def heartbeat_loop():
            while True:
                try:
                    time.sleep(300)  # 5 minutos
                    requests.post(f"{self.api_url}/api/v1/desktop/heartbeat/{self.app_id}")
                except:
                    pass
        
        thread = threading.Thread(target=heartbeat_loop, daemon=True)
        thread.start()
    
    def desregistrarse(self):
        """Desregistrar al cerrar"""
        if self.app_id:
            try:
                requests.post(f"{self.api_url}/api/v1/desktop/unregister/{self.app_id}")
                print(f"Programa {self.nombre_programa} desconectado")
            except:
                pass

# USO:
client = PaintFlowClient(
    nombre_programa="LabelsApp",
    version="2.1.0",
    maquina="PC-TIENDA-01",
    usuario_so="admin"
)
client.registrarse()

# Tu programa continua ejecutandose...
# El heartbeat se envia automaticamente cada 5 minutos

---

## Notas Importantes

1. Timeout: Si no se recibe heartbeat en 30 minutos, el programa se considera offline automaticamente
2. app_id: Se genera automaticamente como {nombre_programa}_{maquina}_{usuario_so}
3. Multiples instancias: Cada maquina/usuario_so reporta por separado
4. Error handling: Implementar reintentos en caso de falla de conexion

---

## Informacion que aparece en ACTIVIDAD

La pestana ACTIVIDAD mostrara:
- Nombre del programa (Ej: LabelsApp)
- Version (Ej: 2.1.0)
- Maquina (Ej: PC-TIENDA-01)
- Usuario del SO (Ej: admin)
- Boton Desconectar (para desconectar remotamente desde el dashboard)

---

## Departamentos

Los programas de escritorio se categorizan bajo: Programas Desktop

Diferente de:
- Tienda: Facturador, Colorista, Analista
- Departamento TI: Administrador
- Finanzas: Gerente, Contabilidad
