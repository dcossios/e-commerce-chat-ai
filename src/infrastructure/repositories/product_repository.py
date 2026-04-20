"""Repositorio SQLAlchemy para operaciones de persistencia de productos."""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import Product
from src.domain.repositories import IProductRepository
from src.infrastructure.db.models import ProductModel


class SQLProductRepository(IProductRepository):
    """
    Implementación concreta de persistencia de productos con SQLAlchemy.

    Attributes:
        db (Session): Sesión activa de base de datos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con la sesión activa.

        Args:
            db (Session): Sesión SQLAlchemy inyectada.
        """
        self.db = db

    def get_all(self) -> List[Product]:
        """
        Recupera todos los productos persistidos.

        Returns:
            List[Product]: Lista de entidades de producto.
        """
        models = self.db.query(ProductModel).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            Optional[Product]: Entidad encontrada o ``None``.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            return None
        return self._model_to_entity(model)

    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera productos de una marca específica.

        Args:
            brand (str): Marca a filtrar.

        Returns:
            List[Product]: Productos de la marca indicada.
        """
        models = self.db.query(ProductModel).filter(ProductModel.brand == brand).all()
        return [self._model_to_entity(model) for model in models]

    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera productos de una categoría específica.

        Args:
            category (str): Categoría a filtrar.

        Returns:
            List[Product]: Productos de la categoría indicada.
        """
        models = self.db.query(ProductModel).filter(ProductModel.category == category).all()
        return [self._model_to_entity(model) for model in models]

    def save(self, product: Product) -> Product:
        """
        Crea o actualiza un producto en base de datos.

        Args:
            product (Product): Entidad a persistir.

        Returns:
            Product: Entidad persistida.
        """
        if product.id is None:
            model = self._entity_to_model(product)
            self.db.add(model)
            self.db.commit()
            self.db.refresh(model)
            return self._model_to_entity(model)

        model = self.db.query(ProductModel).filter(ProductModel.id == product.id).first()
        if model is None:
            model = self._entity_to_model(product)
            self.db.add(model)
        else:
            model.name = product.name
            model.brand = product.brand
            model.category = product.category
            model.size = product.size
            model.color = product.color
            model.price = product.price
            model.stock = product.stock
            model.description = product.description

        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            bool: ``True`` si se eliminó, ``False`` si no existía.
        """
        model = self.db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if model is None:
            return False

        self.db.delete(model)
        self.db.commit()
        return True

    def _model_to_entity(self, model: ProductModel) -> Product:
        """Convierte un modelo ORM en entidad de dominio Product."""
        return Product(
            id=model.id,
            name=model.name,
            brand=model.brand,
            category=model.category,
            size=model.size,
            color=model.color,
            price=model.price,
            stock=model.stock,
            description=model.description,
        )

    def _entity_to_model(self, entity: Product) -> ProductModel:
        """Convierte una entidad Product en modelo ORM ProductModel."""
        return ProductModel(
            id=entity.id,
            name=entity.name,
            brand=entity.brand,
            category=entity.category,
            size=entity.size,
            color=entity.color,
            price=entity.price,
            stock=entity.stock,
            description=entity.description,
        )
