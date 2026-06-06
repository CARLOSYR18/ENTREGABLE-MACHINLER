from dotenv import load_dotenv
import os
from supabase import create_client

load_dotenv()

url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")

print("URL:", url)
print("KEY length:", len(key) if key else "NONE")

supabase = create_client(url, key)

# Intenta insertar un registro de prueba
res = supabase.table("tramites").insert({
    "ciudadano": "TEST",
    "dni": "00000000",
    "correo": "test@test.com",
    "tipo_tramite": "Prueba",
    "area": "Test",
    "descripcion": "Test de conexión",
    "dias_espera": 1,
    "urgencia": 1,
    "documentos_observados": 0,
    "prioridad": "baja",
    "estado": "Recibido"
}).execute()

print("Resultado:", res.data)