@app.route("/register", methods=["GET", "POST"])
def register():

    error = ""

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

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