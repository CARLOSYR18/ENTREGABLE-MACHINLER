# Sistema Inteligente de Gestión de Trámites Municipales con Machine Learning + Supabase

Caso práctico: Municipalidad Provincial de Yau.

## Funciones
- Login de administrador.
- Registro de trámites ciudadanos.
- Clasificación automática de prioridad con Machine Learning.
- Base de datos en Supabase.
- Panel administrativo.
- Actualización de estados.
- Notificaciones internas.
- Reportes básicos.

## 1. Instalar dependencias

```bash
pip install -r requirements.txt
```

## 2. Crear tablas en Supabase

Entra a Supabase > SQL Editor y ejecuta el archivo:

```text
supabase_schema.sql
```

## 3. Crear archivo .env

Copia `.env.example` y renómbralo a `.env`.

Luego coloca tus datos:

```env
SECRET_KEY=mi-clave-secreta
ADMIN_EMAIL=admin@novasalud.com
ADMIN_PASSWORD=admin123

SUPABASE_URL=https://TU-PROYECTO.supabase.co
SUPABASE_KEY=TU_SERVICE_ROLE_KEY_O_ANON_KEY
```

## 4. Entrenar modelo

```bash
python train_model.py
```

## 5. Ejecutar sistema

```bash
python app.py
```

Abre:

```text
http://127.0.0.1:5000
```

## Login por defecto

```text
Correo: admin@novasalud.com
Clave: admin123
```
