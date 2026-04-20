from unittest.mock import Mock

import pytest

from src.application.dtos import ProductDTO
from src.application.product_service import ProductService
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError


def _product(
    product_id,
    name,
    brand,
    category,
    stock=1,
):
    return Product(
        id=product_id,
        name=name,
        brand=brand,
        category=category,
        size="42",
        color="Negro",
        price=100.0,
        stock=stock,
        description="desc",
    )


def _dto(name="Nuevo", brand="Nike", category="Running", price=120.0, stock=5):
    return ProductDTO(
        name=name,
        brand=brand,
        category=category,
        size="42",
        color="Negro",
        price=price,
        stock=stock,
        description="Zapatilla",
    )


def test_get_all_products_returns_repository_list():
    repository = Mock()
    repository.get_all.return_value = [_product(1, "A", "Nike", "Running")]
    service = ProductService(repository)

    result = service.get_all_products()

    assert len(result) == 1
    repository.get_all.assert_called_once()


def test_search_products_filters_by_brand_and_category_case_insensitive():
    repository = Mock()
    repository.get_all.return_value = [
        _product(1, "A", "Nike", "Running"),
        _product(2, "B", "Nike", "Casual"),
        _product(3, "C", "Puma", "Running"),
    ]
    service = ProductService(repository)

    by_brand = service.search_products({"brand": "nike"})
    by_category = service.search_products({"category": "running"})
    by_both = service.search_products({"brand": "NIKE", "category": "RUNNING"})

    assert len(by_brand) == 2
    assert len(by_category) == 2
    assert len(by_both) == 1
    assert by_both[0].id == 1


def test_update_product_validates_exists_and_saves_updated_entity():
    existing = _product(10, "Viejo", "Nike", "Running")
    updated = _product(10, "Nuevo", "Nike", "Running")
    repository = Mock()
    repository.get_by_id.return_value = existing
    repository.save.return_value = updated
    service = ProductService(repository)

    result = service.update_product(10, _dto(name="Nuevo"))

    assert result.name == "Nuevo"
    repository.get_by_id.assert_called_once_with(10)
    repository.save.assert_called_once()


def test_delete_product_success_returns_true():
    repository = Mock()
    repository.get_by_id.return_value = _product(3, "X", "Nike", "Running")
    repository.delete.return_value = True
    service = ProductService(repository)

    assert service.delete_product(3) is True
    repository.delete.assert_called_once_with(3)


def test_create_product_wraps_entity_validation_errors_as_domain_error():
    repository = Mock()
    service = ProductService(repository)
    invalid_dto = ProductDTO.model_construct(
        name="Invalido",
        brand="Nike",
        category="Running",
        size="42",
        color="Negro",
        price=0,
        stock=5,
        description="Zapatilla",
    )

    with pytest.raises(InvalidProductDataError):
        service.create_product(invalid_dto)
