import os
import smtplib
from functools import wraps
from pathlib import Path
from email.mime.text import MIMEText

from flask import Flask, render_template, request, redirect, url_for, jsonify, session

import joblib
import pandas as pd
from dotenv import load_dotenv

from database import (
    init_db,
    supabase,
    insertar_tramite,
    insertar_notificacion,
    obtener_tramite,
    listar_tramites,
    actualizar_estado_tramite,
    listar_notificaciones,
    obtener_stats,
    reporte_por_area,
)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "nova_salud_secret")

init_db()

MODEL_PATH = Path("model/modelo_prioridad.pkl")


def enviar_correo(destino, asunto, mensaje):
    remitente = os.getenv("MAIL_EMAIL")
    password = os.getenv("MAIL_PASSWORD")

    print("Intentando enviar correo a:", destino)
    print("MAIL_EMAIL:", remitente)
    print("MAIL_PASSWORD existe:", bool(password))

    if not remitente or not password:
        print("Correo no enviado: faltan MAIL_EMAIL o MAIL_PASSWORD en .env")
        return

    msg = MIMEText(mensaje, "html", "utf-8")
    msg["Subject"] = asunto
    msg["From"] = remitente
    msg["To"] = destino

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(remitente, password)
            server.send_message(msg)

        print(f"Correo enviado a {destino}")

    except Exception as e:
        print("Error enviando correo:", e)


def cargar_modelo():
    if not MODEL_PATH.exists():
        raise FileNotFoundError("Primero ejecuta: python train_model.py")
    return joblib.load(MODEL_PATH)


modelo = cargar_modelo()


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("user_email"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def predecir_prioridad(tipo_tramite, area, dias_espera, urgencia, documentos_observados):
    entrada = pd.DataFrame([{
        "tipo_tramite": tipo_tramite,
        "area": area,
        "dias_espera": int(dias_espera),
        "urgencia": int(urgencia),
        "documentos_observados": int(documentos_observados)
    }])

    return modelo.predict(entrada)[0]


@app.route("/register", methods=["GET", "POST"])
def register():
    error = ""

    if request.method == "POST":
        correo = request.form.get("correo", "").strip()
        password = request.form.get("password", "").strip()

        if not correo or not password:
            error = "Completa todos los campos"
        else:
            existente = (
                supabase.table("usuarios")
                .select("*")
                .eq("correo", correo)
                .execute()
            )

            if existente.data:
                error = "El usuario ya existe"
            else:
                supabase.table("usuarios").insert({
                    "correo": correo,
                    "password": password,
                    "rol": "admin"
                }).execute()

                return redirect(url_for("login"))

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = ""

    if request.method == "POST":
        email = request.form.get("email", "").strip()
        password = request.form.get("password", "").strip()

        if not email or not password:
            error = "Completa todos los campos"
        else:
            usuario = (
                supabase.table("usuarios")
                .select("*")
                .eq("correo", email)
                .eq("password", password)
                .execute()
            )

            if usuario.data:
                session.clear()
                session["user_email"] = usuario.data[0]["correo"]
                session["rol"] = usuario.data[0]["rol"]

                return redirect(request.args.get("next") or url_for("index"))

            error = "Correo o contraseña incorrectos"

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


@app.route("/")
@login_required
def index():
    tramites_recientes = listar_tramites(None)[:5]
    return render_template("index.html", tramites_recientes=tramites_recientes)


@app.route("/registrar", methods=["GET", "POST"])
@login_required
def registrar():
    if request.method == "POST":
        ciudadano = request.form["ciudadano"]
        dni = request.form["dni"]
        correo = request.form["correo"]
        tipo_tramite = request.form["tipo_tramite"]
        area = request.form["area"]
        descripcion = request.form["descripcion"]
        dias_espera = request.form["dias_espera"]
        urgencia = request.form["urgencia"]
        documentos_observados = request.form.get("documentos_observados", "0")

        prioridad = predecir_prioridad(
            tipo_tramite,
            area,
            dias_espera,
            urgencia,
            documentos_observados
        )

        tramite = insertar_tramite({
            "ciudadano": ciudadano,
            "dni": dni,
            "correo": correo,
            "tipo_tramite": tipo_tramite,
            "area": area,
            "descripcion": descripcion,
            "dias_espera": int(dias_espera),
            "urgencia": int(urgencia),
            "documentos_observados": int(documentos_observados),
            "prioridad": prioridad,
            "estado": "Recibido"
        })

        tramite_id = tramite["id"]

        insertar_notificacion(
            tramite_id,
            f"Su trámite fue registrado correctamente. Prioridad asignada: {prioridad.upper()}."
        )

        enviar_correo(
            correo,
            "Trámite registrado correctamente - NovaNotifi",
            f"""
            <div style="font-family: Arial, sans-serif; background:#f4f7fb; padding:24px;">
                <div style="max-width:620px; margin:auto; background:white; border-radius:18px; padding:28px; border:1px solid #e5e7eb;">
                    <h2 style="color:#1557c0;">Trámite registrado correctamente</h2>
                    <p>Hola <b>{ciudadano}</b>,</p>
                    <p>Su trámite fue recibido correctamente en el sistema.</p>
                    <div style="background:#f8fafc; padding:16px; border-radius:12px; margin:18px 0;">
                        <p><b>Número de solicitud:</b> {tramite_id}</p>
                        <p><b>Tipo de trámite:</b> {tipo_tramite}</p>
                        <p><b>Área responsable:</b> {area}</p>
                        <p><b>Estado actual:</b> Recibido</p>
                        <p><b>Prioridad asignada:</b> {prioridad.upper()}</p>
                    </div>
                    <p>Le notificaremos por correo cuando el estado de su trámite cambie.</p>
                    <p style="color:#64748b;">Gracias por usar NovaNotifi.</p>
                </div>
            </div>
            """
        )

        return redirect(url_for("resultado", tramite_id=tramite_id))

    return render_template("registrar.html")


@app.route("/resultado/<int:tramite_id>")
@login_required
def resultado(tramite_id):
    tramite = obtener_tramite(tramite_id)
    return render_template("resultado.html", tramite=tramite)


@app.route("/admin")
@login_required
def admin():
    filtro = request.args.get("prioridad", "")
    tramites = listar_tramites(filtro if filtro else None)
    stats = obtener_stats()

    return render_template(
        "admin.html",
        tramites=tramites,
        stats=stats,
        filtro=filtro
    )


@app.route("/actualizar_estado/<int:tramite_id>", methods=["POST"])
@login_required
def actualizar_estado(tramite_id):
    nuevo_estado = request.form["estado"]

    actualizar_estado_tramite(tramite_id, nuevo_estado)

    insertar_notificacion(
        tramite_id,
        f"El estado de su trámite cambió a: {nuevo_estado}."
    )

    tramite = obtener_tramite(tramite_id)

    if tramite:
        enviar_correo(
            tramite["correo"],
            "Actualización del estado de su trámite - NovaNotifi",
            f"""
            <div style="font-family: Arial, sans-serif; background:#f4f7fb; padding:24px;">
                <div style="max-width:620px; margin:auto; background:white; border-radius:18px; padding:28px; border:1px solid #e5e7eb;">
                    <h2 style="color:#1557c0;">Actualización de trámite</h2>
                    <p>Hola <b>{tramite["ciudadano"]}</b>,</p>
                    <p>El estado de su trámite ha sido actualizado.</p>
                    <div style="background:#f8fafc; padding:16px; border-radius:12px; margin:18px 0;">
                        <p><b>Número de solicitud:</b> {tramite["id"]}</p>
                        <p><b>Tipo de trámite:</b> {tramite["tipo_tramite"]}</p>
                        <p><b>Área responsable:</b> {tramite["area"]}</p>
                        <p><b>Nuevo estado:</b> {nuevo_estado}</p>
                        <p><b>Prioridad:</b> {tramite["prioridad"].upper()}</p>
                    </div>
                    <p>Gracias por usar NovaNotifi.</p>
                </div>
            </div>
            """
        )

    return redirect(url_for("admin"))


@app.route("/notificaciones/<int:tramite_id>")
@login_required
def notificaciones(tramite_id):
    tramite = obtener_tramite(tramite_id)
    notis = listar_notificaciones(tramite_id)

    return render_template(
        "notificaciones.html",
        tramite=tramite,
        notis=notis
    )


@app.route("/api/reportes")
@login_required
def api_reportes():
    return jsonify(reporte_por_area())


if __name__ == "__main__":
    app.run(debug=True)