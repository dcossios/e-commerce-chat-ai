"""Servicios de aplicación para casos de uso de productos."""

from typing import Dict, List

from src.application.dtos import ProductDTO
from src.domain.entities import Product
from src.domain.exceptions import InvalidProductDataError, ProductNotFoundError
from src.domain.repositories import IProductRepository


class ProductService:
    """
    Servicio de aplicación para gestionar operaciones de productos.

    Attributes:
        _repository (IProductRepository): Repositorio de productos inyectado.
    """

    def __init__(self, product_repository: IProductRepository):
        """
        Inicializa el servicio con su dependencia de persistencia.

        Args:
            product_repository (IProductRepository): Implementación de repositorio.
        """
        self._repository = product_repository

    def get_all_products(self) -> List[Product]:
        """
        Lista todos los productos registrados.

        Returns:
            List[Product]: Productos disponibles en repositorio.
        """
        return self._repository.get_all()

    def get_product_by_id(self, product_id: int) -> Product:
        """
        Obtiene un producto por ID o lanza excepción si no existe.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Product: Producto encontrado.

        Raises:
            ProductNotFoundError: Si no hay producto con el ID indicado.
        """
        product = self._repository.get_by_id(product_id)
        if product is None:
            raise ProductNotFoundError(product_id)
        return product

    def search_products(self, filters: Dict[str, str]) -> List[Product]:
        """
        Filtra productos por marca y/o categoría.

        Args:
            filters (Dict[str, str]): Filtros opcionales (brand, category).

        Returns:
            List[Product]: Productos que cumplen filtros.
        """
        products = self._repository.get_all()

        brand = filters.get("brand")
        category = filters.get("category")

        if brand:
            products = [product for product in products if product.brand.lower() == brand.lower()]
        if category:
            products = [
                product for product in products if product.category.lower() == category.lower()
            ]

        return products

    def create_product(self, product_dto: ProductDTO) -> Product:
        """
        Crea un nuevo producto a partir de un DTO.

        Args:
            product_dto (ProductDTO): Datos del producto a crear.

        Returns:
            Product: Producto creado y persistido.

        Raises:
            InvalidProductDataError: Si la entidad no pasa validaciones.
        """
        try:
            product = Product(
                id=None,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as exc:
            raise InvalidProductDataError(str(exc)) from exc

        return self._repository.save(product)

    def update_product(self, product_id: int, product_dto: ProductDTO) -> Product:
        """
        Actualiza un producto existente validando que exista.

        Args:
            product_id (int): ID del producto a actualizar.
            product_dto (ProductDTO): Nueva información del producto.

        Returns:
            Product: Producto actualizado.

        Raises:
            ProductNotFoundError: Si no existe el producto.
            InvalidProductDataError: Si la información no es válida.
        """
        _existing = self.get_product_by_id(product_id)

        try:
            updated_product = Product(
                id=product_id,
                name=product_dto.name,
                brand=product_dto.brand,
                category=product_dto.category,
                size=product_dto.size,
                color=product_dto.color,
                price=product_dto.price,
                stock=product_dto.stock,
                description=product_dto.description,
            )
        except ValueError as exc:
            raise InvalidProductDataError(str(exc)) from exc

        return self._repository.save(updated_product)

    def delete_product(self, product_id: int) -> bool:
        """
        Elimina un producto validando su existencia previa.

        Args:
            product_id (int): ID del producto a eliminar.

        Returns:
            bool: ``True`` cuando la eliminación se ejecuta correctamente.

        Raises:
            ProductNotFoundError: Si el producto no existe.
        """
        self.get_product_by_id(product_id)
        deleted = self._repository.delete(product_id)
        if not deleted:
            raise ProductNotFoundError(product_id)
        return True

    def get_available_products(self) -> List[Product]:
        """
        Retorna únicamente productos con stock disponible.

        Returns:
            List[Product]: Productos cuyo stock es mayor que cero.
        """
        return [product for product in self._repository.get_all() if product.is_available()]