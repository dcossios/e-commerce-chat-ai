from datetime import datetime

import pytest

from src.domain.entities import ChatContext, ChatMessage, Product


@pytest.fixture
def valid_product() -> Product:
    return Product(
        id=1,
        name="Air Zoom",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=120.0,
        stock=5,
        description="Zapatilla de running",
    )


def test_product_validates_price_greater_than_zero() -> None:
    with pytest.raises(ValueError, match="precio"):
        Product(
            id=None,
            name="Producto",
            brand="Marca",
            category="Cat",
            size="42",
            color="Negro",
            price=0,
            stock=1,
            description="desc",
        )


def test_product_validates_non_negative_stock() -> None:
    with pytest.raises(ValueError, match="stock"):
        Product(
            id=None,
            name="Producto",
            brand="Marca",
            category="Cat",
            size="42",
            color="Negro",
            price=10,
            stock=-1,
            description="desc",
        )


def test_product_validates_name_not_empty() -> None:
    with pytest.raises(ValueError, match="nombre"):
        Product(
            id=None,
            name="   ",
            brand="Marca",
            category="Cat",
            size="42",
            color="Negro",
            price=10,
            stock=1,
            description="desc",
        )


def test_product_is_available_based_on_stock(valid_product: Product) -> None:
    assert valid_product.is_available() is True
    valid_product.stock = 0
    assert valid_product.is_available() is False


def test_product_reduce_stock_success(valid_product: Product) -> None:
    valid_product.reduce_stock(2)
    assert valid_product.stock == 3


@pytest.mark.parametrize("quantity", [0, -1])
def test_product_reduce_stock_requires_positive_quantity(
    valid_product: Product,
    quantity: int,
) -> None:
    with pytest.raises(ValueError, match="positiva"):
        valid_product.reduce_stock(quantity)


def test_product_reduce_stock_requires_enough_stock(valid_product: Product) -> None:
    with pytest.raises(ValueError, match="suficiente"):
        valid_product.reduce_stock(999)


def test_chat_message_validates_role() -> None:
    with pytest.raises(ValueError, match="rol"):
        ChatMessage(
            id=None,
            session_id="s1",
            role="system",
            message="hola",
            timestamp=datetime.utcnow(),
        )


def test_chat_message_validates_message_not_empty() -> None:
    with pytest.raises(ValueError, match="mensaje"):
        ChatMessage(
            id=None,
            session_id="s1",
            role="user",
            message="   ",
            timestamp=datetime.utcnow(),
        )


def test_chat_message_validates_session_not_empty() -> None:
    with pytest.raises(ValueError, match="session_id"):
        ChatMessage(
            id=None,
            session_id="",
            role="user",
            message="hola",
            timestamp=datetime.utcnow(),
        )


def test_chat_context_formats_prompt_and_respects_max_messages() -> None:
    messages = [
        ChatMessage(None, "s1", "user", "hola", datetime.utcnow()),
        ChatMessage(None, "s1", "assistant", "hola, en que te ayudo", datetime.utcnow()),
        ChatMessage(None, "s1", "user", "busco running", datetime.utcnow()),
    ]
    context = ChatContext(messages=messages, max_messages=2)

    formatted = context.format_for_prompt()

    assert "Usuario: busco running" in formatted
    assert "Asistente: hola, en que te ayudo" in formatted
    assert "Usuario: hola" not in formatted
