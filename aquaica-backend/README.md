# AquaIca Backend API

API para gestión de incidencias de agua potable y alcantarillado en la región Ica.

## Tecnologías
- Python 3.11+
- FastAPI
- SQLAlchemy 2.0 (Async)
- PostgreSQL 16
- Pydantic v2
- Docker

## Estructura del Proyecto
```
aquaica-backend/
├── app/
│   ├── api/
│   │   └── v1/
│   ├── core/
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
├── tests/
├── .env
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## Prerrequisitos
- Python 3.11+
- PostgreSQL 16
- Docker (Opcional)

## Configuración y Ejecución

1. **Crear entorno virtual e instalar dependencias:**
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Variables de entorno:**
   Configurar archivo `.env` basado en `.env.example`.

3. **Base de Datos (Docker):**
   ```bash
   docker-compose up -d
   ```

4. **Migraciones:**
   ```bash
   alembic upgrade head
   ```

5. **Ejecutar servidor:**
   ```bash
   uvicorn app.main:app --reload
   ```

## Documentación API
Una vez ejecutado, la documentación está disponible en:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Resumen de Endpoints Principales
| Recurso | Ruta | Descripción |
|---|---|---|
| Auth | `/api/v1/auth/...` | Login, registro, token |
| Users | `/api/v1/users/...` | Gestión de usuarios |
| Incidents | `/api/v1/incidents/...` | Reporte y gestión de incidencias |
| Assignments | `/api/v1/assignments/...` | Asignaciones a técnicos |
| Evidence | `/api/v1/evidence/...` | Archivos adjuntos |
| Dashboard | `/api/v1/dashboard/...` | Estadísticas para admin |

## Pruebas
Ejecutar pruebas con pytest:
```bash
pytest
```

## Arquitectura
La aplicación sigue una arquitectura en capas:
- **Routes (app/api/):** Controladores de endpoints FastAPI.
- **Services (app/services/):** Lógica de negocio.
- **Models (app/models/):** Modelos ORM SQLAlchemy.
- **Schemas (app/schemas/):** Modelos Pydantic para validación.

## Licencia
MIT
