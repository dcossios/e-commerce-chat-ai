import asyncio
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from src.domain.entities import ChatContext, ChatMessage, Product
from src.domain.exceptions import ChatServiceError
from src.infrastructure.api import main as api_main
from src.infrastructure.db import database, init_data
from src.infrastructure.db.database import Base
from src.infrastructure.db.models import ChatMemoryModel, ProductModel
from src.infrastructure.llm_providers import gemini_service
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


def _sample_product_entity(product_id=None, name="Air Zoom"):
    return Product(
        id=product_id,
        name=name,
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla",
    )


def test_sql_product_repository_crud_and_filters(db_session):
    repo = SQLProductRepository(db_session)

    created = repo.save(_sample_product_entity())
    assert created.id is not None

    assert len(repo.get_all()) == 1
    assert repo.get_by_id(created.id).name == "Air Zoom"
    assert len(repo.get_by_brand("Nike")) == 1
    assert len(repo.get_by_category("Running")) == 1

    updated = Product(
        id=created.id,
        name="Air Zoom Pro",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=130.0,
        stock=7,
        description="Actualizado",
    )
    saved_update = repo.save(updated)
    assert saved_update.name == "Air Zoom Pro"
    assert saved_update.price == 130.0

    inserted_with_id = repo.save(_sample_product_entity(product_id=999, name="Manual ID"))
    assert inserted_with_id.id == 999

    assert repo.delete(created.id) is True
    assert repo.delete(created.id) is False


def test_sql_chat_repository_history_recent_and_delete(db_session):
    repo = SQLChatRepository(db_session)

    base_time = datetime(2024, 1, 1, 12, 0, 0)
    messages = [
        ChatMessage(None, "s1", "user", "hola", base_time),
        ChatMessage(None, "s1", "assistant", "que tal", base_time + timedelta(seconds=1)),
        ChatMessage(None, "s1", "user", "busco nike", base_time + timedelta(seconds=2)),
    ]

    for msg in messages:
        repo.save_message(msg)

    history_all = repo.get_session_history("s1")
    assert [m.message for m in history_all] == ["hola", "que tal", "busco nike"]

    history_limited = repo.get_session_history("s1", limit=2)
    assert [m.message for m in history_limited] == ["que tal", "busco nike"]

    recent = repo.get_recent_messages("s1", count=2)
    assert [m.message for m in recent] == ["que tal", "busco nike"]
    assert repo.get_recent_messages("s1", count=0) == []

    deleted = repo.delete_session_history("s1")
    assert deleted == 3
    assert repo.get_session_history("s1") == []


def test_database_get_db_closes_session(monkeypatch):
    class FakeSession:
        def __init__(self):
            self.closed = False

        def close(self):
            self.closed = True

    fake = FakeSession()
    monkeypatch.setattr(database, "SessionLocal", lambda: fake)

    gen = database.get_db()
    got = next(gen)
    assert got is fake
    with pytest.raises(StopIteration):
        next(gen)
    assert fake.closed is True


def test_database_init_db_handles_optional_imports(monkeypatch):
    created_calls = []

    def fake_create_all(bind):
        created_calls.append(bind)

    monkeypatch.setattr(database.Base.metadata, "create_all", fake_create_all)

    def import_raises(_name):
        raise ImportError

    monkeypatch.setattr(database.importlib, "import_module", import_raises)

    database.init_db()

    assert len(created_calls) == 1


def test_database_init_db_calls_load_initial_data(monkeypatch):
    loaded = {"called": False}

    class FakeInitModule:
        @staticmethod
        def load_initial_data():
            loaded["called"] = True

    def fake_import(name):
        if name == "src.infrastructure.db.models":
            return object()
        if name == "src.infrastructure.db.init_data":
            return FakeInitModule
        raise ImportError

    monkeypatch.setattr(database.importlib, "import_module", fake_import)
    monkeypatch.setattr(database.Base.metadata, "create_all", lambda bind: None)

    database.init_db()

    assert loaded["called"] is True


def test_init_data_loads_once_and_is_idempotent(monkeypatch):
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    test_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)

    monkeypatch.setattr(init_data, "SessionLocal", test_session_local)

    init_data.load_initial_data()
    init_data.load_initial_data()

    session = test_session_local()
    try:
        assert session.query(ProductModel).count() == 10
    finally:
        session.close()


def test_init_data_rolls_back_on_error(monkeypatch):
    class FailingSession:
        def __init__(self):
            self.rolled_back = False
            self.closed = False

        def query(self, _model):
            return self

        def count(self):
            raise RuntimeError("boom")

        def rollback(self):
            self.rolled_back = True

        def close(self):
            self.closed = True

    failing = FailingSession()
    monkeypatch.setattr(init_data, "SessionLocal", lambda: failing)

    with pytest.raises(RuntimeError, match="boom"):
        init_data.load_initial_data()

    assert failing.rolled_back is True
    assert failing.closed is True


def test_gemini_service_init_requires_api_key(monkeypatch):
    monkeypatch.setenv("GEMINI_API_KEY", "")
    with pytest.raises(ValueError, match="GEMINI_API_KEY"):
        gemini_service.GeminiService()


def test_gemini_service_formats_products_and_generates_response(monkeypatch):
    configured = {}

    class FakeResponse:
        def __init__(self, text):
            self.text = text

    class FakeModel:
        def __init__(self, _name):
            pass

        def generate_content(self, prompt):
            assert "PRODUCTOS DISPONIBLES" in prompt
            return FakeResponse("respuesta IA")

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service.genai, "configure", lambda api_key: configured.update({"key": api_key}))
    monkeypatch.setattr(gemini_service.genai, "GenerativeModel", FakeModel)

    service = gemini_service.GeminiService()
    assert configured["key"] == "test-key"

    products_text = service.format_products_info([_sample_product_entity()])
    assert "Air Zoom" in products_text
    assert "Stock: 5" in products_text

    context = ChatContext(messages=[])
    response = asyncio.run(service.generate_response("hola", [_sample_product_entity()], context))
    assert response == "respuesta IA"


def test_gemini_service_empty_and_error_paths(monkeypatch):
    class BlankModel:
        def __init__(self, _name):
            pass

        def generate_content(self, _prompt):
            return type("R", (), {"text": "  "})()

    class ExplodingModel:
        def __init__(self, _name):
            pass

        def generate_content(self, _prompt):
            raise RuntimeError("fallo proveedor")

    monkeypatch.setenv("GEMINI_API_KEY", "test-key")
    monkeypatch.setattr(gemini_service.genai, "configure", lambda api_key: None)

    monkeypatch.setattr(gemini_service.genai, "GenerativeModel", BlankModel)
    blank_service = gemini_service.GeminiService()
    blank_text = asyncio.run(blank_service.generate_response("hola", [], ChatContext(messages=[])))
    assert "No pude generar" in blank_text
    assert blank_service.format_products_info([]).startswith("No hay productos")

    monkeypatch.setattr(gemini_service.genai, "GenerativeModel", ExplodingModel)
    exploding_service = gemini_service.GeminiService()
    with pytest.raises(RuntimeError, match="Error al generar respuesta con Gemini"):
        asyncio.run(exploding_service.generate_response("hola", [], ChatContext(messages=[])))


@pytest.fixture
def api_client(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    class FakeGemini:
        async def generate_response(self, user_message, products, context):
            return f"respuesta: {user_message}"

    monkeypatch.setattr(api_main, "init_db", lambda: None)
    monkeypatch.setattr(api_main, "GeminiService", lambda: FakeGemini())
    api_main.app.dependency_overrides[api_main.get_db] = override_get_db

    db_session.add(
        ProductModel(
            name="Air Zoom",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla",
        )
    )
    db_session.commit()

    with TestClient(api_main.app) as client:
        yield client

    api_main.app.dependency_overrides.clear()


def test_api_root_health_and_products(api_client):
    root = api_client.get("/")
    assert root.status_code == 200
    assert root.json()["name"] == "E-commerce Chat AI API"

    health = api_client.get("/health")
    assert health.status_code == 200
    assert health.json()["status"] == "ok"

    products = api_client.get("/products")
    assert products.status_code == 200
    assert len(products.json()) == 1


def test_api_get_product_by_id_success_and_404(api_client):
    found = api_client.get("/products/1")
    assert found.status_code == 200
    assert found.json()["id"] == 1

    missing = api_client.get("/products/999")
    assert missing.status_code == 404
    assert "no encontrado" in missing.json()["detail"].lower()


def test_api_chat_flow_history_and_delete(api_client):
    chat = api_client.post("/chat", json={"session_id": "s-api", "message": "hola"})
    assert chat.status_code == 200
    payload = chat.json()
    assert payload["session_id"] == "s-api"
    assert "respuesta: hola" in payload["assistant_message"]

    history = api_client.get("/chat/history/s-api", params={"limit": 10})
    assert history.status_code == 200
    assert len(history.json()) == 2

    deleted = api_client.delete("/chat/history/s-api")
    assert deleted.status_code == 200
    assert deleted.json()["deleted_count"] == 2


def test_api_chat_error_paths(db_session, monkeypatch):
    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    db_session.add(
        ProductModel(
            name="Air Zoom",
            brand="Nike",
            category="Running",
            size="42",
            color="Negro",
            price=120.0,
            stock=5,
            description="Zapatilla",
        )
    )
    db_session.commit()

    monkeypatch.setattr(api_main, "init_db", lambda: None)
    api_main.app.dependency_overrides[api_main.get_db] = override_get_db

    class RaiseChatServiceError:
        def __init__(self):
            raise ChatServiceError("fallo controlado")

    monkeypatch.setattr(api_main, "GeminiService", RaiseChatServiceError)
    with TestClient(api_main.app) as client:
        resp = client.post("/chat", json={"session_id": "s1", "message": "hola"})
        assert resp.status_code == 500
        assert "fallo controlado" in resp.json()["detail"]

    class RaiseGenericError:
        def __init__(self):
            raise ValueError("fallo inesperado")

    monkeypatch.setattr(api_main, "GeminiService", RaiseGenericError)
    with TestClient(api_main.app) as client:
        resp = client.post("/chat", json={"session_id": "s1", "message": "hola"})
        assert resp.status_code == 500
        assert "error interno" in resp.json()["detail"].lower()

    api_main.app.dependency_overrides.clear()


def test_models_can_persist_and_query(db_session):
    db_session.add(
        ProductModel(
            name="Court Vision",
            brand="Nike",
            category="Casual",
            size="41",
            color="Blanco",
            price=95.0,
            stock=10,
            description="Retro",
        )
    )
    db_session.add(
        ChatMemoryModel(
            session_id="model-test",
            role="user",
            message="hola",
            timestamp=datetime(2024, 1, 1, 0, 0, 0),
        )
    )
    db_session.commit()

    assert db_session.query(ProductModel).count() == 1
    assert db_session.query(ChatMemoryModel).count() == 1