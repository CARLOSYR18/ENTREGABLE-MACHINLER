import os
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError(
        "Faltan variables de entorno. Crea un archivo .env con SUPABASE_URL y SUPABASE_KEY."
    )

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def init_db():
    # Las tablas se crean desde Supabase usando el archivo supabase_schema.sql
    return True

def insertar_tramite(data):
    response = supabase.table("tramites").insert(data).execute()
    if not response.data:
        raise RuntimeError("No se pudo insertar el trámite en Supabase.")
    return response.data[0]

def insertar_notificacion(tramite_id, mensaje):
    data = {
        "tramite_id": tramite_id,
        "mensaje": mensaje
    }
    response = supabase.table("notificaciones").insert(data).execute()
    if not response.data:
        raise RuntimeError("No se pudo insertar la notificación en Supabase.")
    return response.data[0]

def obtener_tramite(tramite_id):
    response = (
        supabase.table("tramites")
        .select("*")
        .eq("id", tramite_id)
        .single()
        .execute()
    )
    return response.data

def listar_tramites(prioridad=None):
    query = supabase.table("tramites").select("*")

    if prioridad:
        query = query.eq("prioridad", prioridad)

    response = query.order("fecha_registro", desc=True).execute()
    tramites = response.data or []

    orden = {
        "critica": 1,
        "alta": 2,
        "media": 3,
        "baja": 4
    }

    return sorted(
        tramites,
        key=lambda item: (
            orden.get(item.get("prioridad"), 99),
            item.get("fecha_registro") or ""
        )
    )

def actualizar_estado_tramite(tramite_id, nuevo_estado):
    response = (
        supabase.table("tramites")
        .update({"estado": nuevo_estado})
        .eq("id", tramite_id)
        .execute()
    )
    return response.data

def listar_notificaciones(tramite_id):
    response = (
        supabase.table("notificaciones")
        .select("*")
        .eq("tramite_id", tramite_id)
        .order("fecha", desc=True)
        .execute()
    )
    return response.data or []

def obtener_stats():
    response = supabase.table("tramites").select("*").execute()
    tramites = response.data or []

    return {
        "total": len(tramites),
        "criticos": sum(1 for t in tramites if t.get("prioridad") == "critica"),
        "recibidos": sum(1 for t in tramites if t.get("estado") == "Recibido"),
        "proceso": sum(1 for t in tramites if t.get("estado") == "En proceso"),
        "finalizados": sum(1 for t in tramites if t.get("estado") == "Finalizado"),
    }

def reporte_por_area():
    response = supabase.table("tramites").select("area").execute()
    tramites = response.data or []

    conteo = {}
    for tramite in tramites:
        area = tramite.get("area") or "Sin área"
        conteo[area] = conteo.get(area, 0) + 1

    return [
        {"area": area, "cantidad": cantidad}
        for area, cantidad in sorted(conteo.items(), key=lambda x: x[1], reverse=True)
    ]
