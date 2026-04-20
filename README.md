# E-commerce Chat AI

API REST de e-commerce de zapatos con chat inteligente, construida con Clean Architecture (Domain, Application, Infrastructure), FastAPI, SQLAlchemy, SQLite y Google Gemini.

## Descripción del proyecto

Este proyecto implementa una tienda de zapatos con dos capacidades principales:

- Gestión de productos (listar, consultar por ID, filtrar y validar disponibilidad).
- Asistente conversacional con memoria de sesión para recomendar productos.

La solución está organizada por capas para mantener separación de responsabilidades y facilitar mantenimiento, pruebas y evolución.

## Características principales

- API REST con FastAPI y documentación automática en Swagger.
- Arquitectura limpia en 3 capas:
  - Domain: reglas de negocio y contratos.
  - Application: casos de uso y DTOs.
  - Infrastructure: API, repositorios SQL, DB y proveedor LLM.
- Persistencia con SQLite y SQLAlchemy ORM.
- Carga de datos iniciales de productos.
- Chat con contexto conversacional (últimos mensajes).
- Integración con Google Gemini para respuestas de IA.
- Testing con pytest + pytest-cov.
- Ejecución local y con Docker / Docker Compose.

## Arquitectura (diagrama)

```text
Cliente HTTP (Postman / Frontend)
        |
        v
+-------------------------------+
| Infrastructure Layer          |
| - FastAPI (endpoints)         |
| - SQL Repositories            |
| - Gemini Service              |
+-------------------------------+
        |
        v
+-------------------------------+
| Application Layer             |
| - ProductService              |
| - ChatService                 |
| - DTOs                        |
+-------------------------------+
        |
        v
+-------------------------------+
| Domain Layer                  |
| - Entities                    |
| - Repository Interfaces       |
| - Domain Exceptions           |
+-------------------------------+
```

## Instalación

### Requisitos previos

- Python 3.10+
- pip
- Docker y Docker Compose (opcional, para ejecución en contenedores)

### Pasos

1. Clonar el repositorio:

```bash
git clone https://github.com/dcossios/e-commerce-chat-ai.git
cd e-commerce-chat-ai
```

2. Crear y activar entorno virtual:

```bash
python -m venv venv
source venv/bin/activate
```

3. Instalar dependencias:

```bash
pip install -r requirements.txt
```

4. Crear variables de entorno:

```bash
cp .env.example .env
```

5. Configurar GEMINI_API_KEY en .env.

6. Ejecutar la API localmente:

```bash
uvicorn src.infrastructure.api.main:app --reload
```

## Configuración

Variables de entorno esperadas:

- GEMINI_API_KEY: API key de Google Gemini.
- DATABASE_URL: URL de base de datos (por defecto SQLite local).
- ENVIRONMENT: entorno de ejecución (ejemplo: development).

Ejemplo de .env:

```env
GEMINI_API_KEY=tu_api_key_aqui
DATABASE_URL=sqlite:///./data/ecommerce_chat.db
ENVIRONMENT=development
```

## Uso (ejemplos de endpoints)

Base URL local:

- http://localhost:8000

Documentación:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Health check

```bash
curl http://localhost:8000/health
```

### Listar productos

```bash
curl http://localhost:8000/products
```

### Obtener producto por ID

```bash
curl http://localhost:8000/products/1
```

### Enviar mensaje al chat

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"session_id":"user_001","message":"Busco zapatos para correr talla 42"}'
```

### Obtener historial de chat

```bash
curl "http://localhost:8000/chat/history/user_001?limit=10"
```

### Eliminar historial de chat

```bash
curl -X DELETE http://localhost:8000/chat/history/user_001
```

## Testing

Ejecutar tests:

```bash
pytest -q
```

Ejecutar tests con cobertura:

```bash
pytest --cov=src --cov-report=term-missing
```

Estado actual:

- Tests: 50 passed
- Coverage total: 98%

## Docker

### Construir y levantar con Docker Compose

```bash
docker compose up --build
```

La API queda disponible en:

- http://localhost:8000
- Swagger: http://localhost:8000/docs

### Detener servicios

```bash
docker compose down
```

## Tecnologías utilizadas

- Python 3.12
- FastAPI
- Pydantic
- SQLAlchemy
- SQLite
- Google Generative AI (Gemini)
- pytest
- pytest-cov
- Docker
- Docker Compose

## Estructura del proyecto

```text
e-commerce-chat-ai/
├── src/
│   ├── domain/
│   │   ├── entities.py
│   │   ├── repositories.py
│   │   └── exceptions.py
│   ├── application/
│   │   ├── dtos.py
│   │   ├── product_service.py
│   │   └── chat_service.py
│   └── infrastructure/
│       ├── api/main.py
│       ├── db/
│       │   ├── database.py
│       │   ├── models.py
│       │   └── init_data.py
│       ├── repositories/
│       │   ├── product_repository.py
│       │   └── chat_repository.py
│       └── llm_providers/gemini_service.py
├── tests/
├── data/
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── pyproject.toml
└── README.md
```

## Autor

Proyecto académico - Universidad EAFIT
