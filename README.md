# AIRBNB-ECUADOR

Proyecto Django + PostgreSQL.

## Requisitos

- Python 3.12
- PostgreSQL (con el servicio corriendo)

## Instalación

1. Crear y activar un entorno virtual:

   ```bash
   python3 -m venv venv
   source venv/bin/activate      # Linux/Mac
   venv\Scripts\activate         # Windows
   ```

2. Instalar dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Crear la base de datos en PostgreSQL:

   ```bash
   createdb -U postgres DB_AIRBNB
   ```

   O importar el respaldo incluido en `sql/BD_AIRBNB.sql`:

   ```bash
   psql -U postgres -d DB_AIRBNB -f sql/BD_AIRBNB.sql
   ```

4. Configurar variables de entorno:

   ```bash
   cp .env.example .env
   ```

   Editar `.env` y poner el usuario/password de tu PostgreSQL local.

5. Aplicar migraciones (si no importaste el `.sql`):

   ```bash
   python manage.py migrate
   ```

6. Levantar el servidor:

   ```bash
   python manage.py runserver
   ```

7. Abrir en el navegador: http://127.0.0.1:8000/
