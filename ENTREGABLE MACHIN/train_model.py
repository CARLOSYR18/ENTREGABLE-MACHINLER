import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, classification_report
import joblib
from pathlib import Path

# Dataset simulado para el caso práctico de la municipalidad
data = [
    ["Licencia de funcionamiento", "Desarrollo Económico", 1, 2, 0, "media"],
    ["Licencia de funcionamiento", "Desarrollo Económico", 7, 1, 1, "alta"],
    ["Licencia de funcionamiento", "Desarrollo Económico", 15, 3, 1, "critica"],
    ["Defensa civil", "Gestión de Riesgos", 2, 5, 1, "critica"],
    ["Defensa civil", "Gestión de Riesgos", 1, 4, 1, "alta"],
    ["Constancia de posesión", "Catastro", 3, 1, 0, "media"],
    ["Constancia de posesión", "Catastro", 10, 2, 1, "alta"],
    ["Reclamo ciudadano", "Atención Ciudadana", 1, 5, 1, "critica"],
    ["Reclamo ciudadano", "Atención Ciudadana", 4, 3, 1, "alta"],
    ["Pago de arbitrios", "Rentas", 1, 1, 0, "baja"],
    ["Pago de arbitrios", "Rentas", 6, 1, 0, "media"],
    ["Solicitud de obra", "Obras Públicas", 2, 3, 1, "alta"],
    ["Solicitud de obra", "Obras Públicas", 12, 4, 1, "critica"],
    ["Certificado domiciliario", "Secretaría General", 1, 1, 0, "baja"],
    ["Certificado domiciliario", "Secretaría General", 5, 1, 0, "media"],
    ["Denuncia ambiental", "Medio Ambiente", 1, 5, 1, "critica"],
    ["Denuncia ambiental", "Medio Ambiente", 6, 4, 1, "critica"],
    ["Mesa de partes", "Administración", 1, 1, 0, "baja"],
    ["Mesa de partes", "Administración", 8, 2, 0, "media"],
    ["Autorización de evento", "Fiscalización", 2, 3, 0, "media"],
    ["Autorización de evento", "Fiscalización", 9, 4, 1, "alta"],
]

df = pd.DataFrame(data, columns=[
    "tipo_tramite", "area", "dias_espera", "urgencia", "documentos_observados", "prioridad"
])

X = df[["tipo_tramite", "area", "dias_espera", "urgencia", "documentos_observados"]]
y = df["prioridad"]

preprocessor = ColumnTransformer(
    transformers=[
        ("cat", OneHotEncoder(handle_unknown="ignore"), ["tipo_tramite", "area"]),
        ("num", "passthrough", ["dias_espera", "urgencia", "documentos_observados"]),
    ]
)

model = Pipeline(steps=[
    ("preprocessor", preprocessor),
    ("classifier", RandomForestClassifier(n_estimators=120, random_state=42))
])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.25, random_state=42, stratify=y
)

model.fit(X_train, y_train)
pred = model.predict(X_test)

print("Accuracy:", round(accuracy_score(y_test, pred), 2))
print(classification_report(y_test, pred, zero_division=0))

Path("model").mkdir(exist_ok=True)
joblib.dump(model, "model/modelo_prioridad.pkl")
print("Modelo guardado en: model/modelo_prioridad.pkl")
