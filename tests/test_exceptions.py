import pytest

from src.domain.exceptions import (
    ChatServiceError,
    InvalidProductDataError,
    ProductNotFoundError,
)


def test_product_not_found_error_default_message() -> None:
    error = ProductNotFoundError()
    assert str(error) == "Producto no encontrado"


def test_product_not_found_error_with_id_message() -> None:
    error = ProductNotFoundError(product_id=10)
    assert str(error) == "Producto con ID 10 no encontrado"


def test_product_not_found_error_can_be_raised_and_caught() -> None:
    with pytest.raises(ProductNotFoundError) as exc_info:
        raise ProductNotFoundError(product_id=5)

    assert str(exc_info.value) == "Producto con ID 5 no encontrado"


def test_invalid_product_data_error_default_message() -> None:
    error = InvalidProductDataError()
    assert str(error) == "Datos de producto inválidos"


def test_invalid_product_data_error_custom_message() -> None:
    error = InvalidProductDataError("Precio inválido")
    assert str(error) == "Precio inválido"


def test_invalid_product_data_error_can_be_raised_and_caught() -> None:
    with pytest.raises(InvalidProductDataError) as exc_info:
        raise InvalidProductDataError("Stock inválido")

    assert str(exc_info.value) == "Stock inválido"


def test_chat_service_error_default_message() -> None:
    error = ChatServiceError()
    assert str(error) == "Error en el servicio de chat"


def test_chat_service_error_custom_message_and_raise() -> None:
    with pytest.raises(ChatServiceError) as exc_info:
        raise ChatServiceError("Error de timeout con IA")

    assert str(exc_info.value) == "Error de timeout con IA"
