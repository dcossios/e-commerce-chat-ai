import asyncio
from datetime import datetime
from unittest.mock import Mock

import pytest

from src.application.chat_service import ChatService
from src.application.dtos import ChatMessageRequestDTO, ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import ChatMessage, Product
from src.domain.exceptions import ChatServiceError, ProductNotFoundError


@pytest.fixture
def sample_product() -> Product:
	return Product(
		id=1,
		name="Air Zoom",
		brand="Nike",
		category="Running",
		size="42",
		color="Negro",
		price=120.0,
		stock=5,
		description="Zapatilla",
	)


@pytest.fixture
def product_dto() -> ProductDTO:
	return ProductDTO(
		name="Air Zoom",
		brand="Nike",
		category="Running",
		size="42",
		color="Negro",
		price=120.0,
		stock=5,
		description="Zapatilla",
	)


def test_product_service_get_product_by_id_raises_when_not_found() -> None:
	repository = Mock()
	repository.get_by_id.return_value = None
	service = ProductService(repository)

	with pytest.raises(ProductNotFoundError):
		service.get_product_by_id(999)


def test_product_service_create_product_uses_repository_save(
	sample_product: Product,
	product_dto: ProductDTO,
) -> None:
	repository = Mock()
	repository.save.return_value = sample_product
	service = ProductService(repository)

	created = service.create_product(product_dto)

	assert created == sample_product
	repository.save.assert_called_once()


def test_product_service_get_available_products_filters_stock(
	sample_product: Product,
) -> None:
	unavailable = Product(
		id=2,
		name="Classic",
		brand="Puma",
		category="Casual",
		size="41",
		color="Azul",
		price=80.0,
		stock=0,
		description="Sin stock",
	)
	repository = Mock()
	repository.get_all.return_value = [sample_product, unavailable]
	service = ProductService(repository)

	available = service.get_available_products()

	assert available == [sample_product]


def test_product_service_delete_product_raises_when_repo_delete_fails(
	sample_product: Product,
) -> None:
	repository = Mock()
	repository.get_by_id.return_value = sample_product
	repository.delete.return_value = False
	service = ProductService(repository)

	with pytest.raises(ProductNotFoundError):
		service.delete_product(sample_product.id)


class _AsyncAIService:
	async def generate_response(self, user_message, products, context):
		return f"respuesta para: {user_message}"


def test_chat_service_process_message_success(sample_product: Product) -> None:
	product_repository = Mock()
	product_repository.get_all.return_value = [sample_product]

	chat_repository = Mock()
	chat_repository.get_recent_messages.return_value = []

	service = ChatService(
		product_repository=product_repository,
		chat_repository=chat_repository,
		ai_service=_AsyncAIService(),
	)
	request = ChatMessageRequestDTO(session_id="s1", message="hola")

	response = asyncio.run(service.process_message(request))

	assert response.session_id == "s1"
	assert response.user_message == "hola"
	assert "respuesta para: hola" in response.assistant_message
	assert chat_repository.save_message.call_count == 2


def test_chat_service_process_message_wraps_errors(sample_product: Product) -> None:
	class FailingAI:
		def generate_response(self, user_message, products, context):
			raise RuntimeError("fallo IA")

	product_repository = Mock()
	product_repository.get_all.return_value = [sample_product]

	chat_repository = Mock()
	chat_repository.get_recent_messages.return_value = []

	service = ChatService(
		product_repository=product_repository,
		chat_repository=chat_repository,
		ai_service=FailingAI(),
	)
	request = ChatMessageRequestDTO(session_id="s1", message="hola")

	with pytest.raises(ChatServiceError, match="Error procesando mensaje"):
		asyncio.run(service.process_message(request))


def test_chat_service_get_session_history_maps_to_dto() -> None:
	now = datetime.utcnow()
	history = [
		ChatMessage(id=1, session_id="s1", role="user", message="hola", timestamp=now),
		ChatMessage(id=2, session_id="s1", role="assistant", message="ok", timestamp=now),
	]

	product_repository = Mock()
	chat_repository = Mock()
	chat_repository.get_session_history.return_value = history

	service = ChatService(
		product_repository=product_repository,
		chat_repository=chat_repository,
		ai_service=None,
	)

	result = service.get_session_history("s1", limit=10)

	assert len(result) == 2
	assert result[0].role == "user"
	assert result[1].message == "ok"


def test_chat_service_clear_session_history_returns_deleted_count() -> None:
	product_repository = Mock()
	chat_repository = Mock()
	chat_repository.delete_session_history.return_value = 3

	service = ChatService(
		product_repository=product_repository,
		chat_repository=chat_repository,
		ai_service=None,
	)

	deleted = service.clear_session_history("s1")

	assert deleted == 3
	chat_repository.delete_session_history.assert_called_once_with("s1")
