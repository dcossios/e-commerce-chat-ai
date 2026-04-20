from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Product, ChatMessage


class IProductRepository(ABC):
    """
    Contrato abstracto para operaciones de persistencia de productos.

    Las implementaciones concretas viven en infraestructura y deben respetar
    las firmas y semántica definidas en esta interfaz.
    """
    
    @abstractmethod
    def get_all(self) -> List[Product]:
        """
        Obtiene todos los productos disponibles.

        Returns:
            List[Product]: Lista completa de productos.
        """
        pass
    
    @abstractmethod
    def get_by_id(self, product_id: int) -> Optional[Product]:
        """
        Busca un producto por su identificador.

        Args:
            product_id (int): ID del producto.

        Returns:
            Optional[Product]: Producto encontrado o ``None`` si no existe.
        """
        pass
    
    @abstractmethod
    def get_by_brand(self, brand: str) -> List[Product]:
        """
        Recupera productos de una marca específica.

        Args:
            brand (str): Marca a consultar.

        Returns:
            List[Product]: Productos de la marca indicada.
        """
        pass
    
    @abstractmethod
    def get_by_category(self, category: str) -> List[Product]:
        """
        Recupera productos de una categoría específica.

        Args:
            category (str): Categoría a consultar.

        Returns:
            List[Product]: Productos de la categoría indicada.
        """
        pass
    
    @abstractmethod
    def save(self, product: Product) -> Product:
        """
        Crea o actualiza un producto.

        Args:
            product (Product): Entidad de producto a persistir.

        Returns:
            Product: Entidad persistida, potencialmente con ID asignado.
        """
        pass
    
    @abstractmethod
    def delete(self, product_id: int) -> bool:
        """
        Elimina un producto por ID.

        Args:
            product_id (int): Identificador del producto.

        Returns:
            bool: ``True`` si se eliminó, ``False`` si no existía.
        """
        pass


class IChatRepository(ABC):
    """
    Contrato abstracto para persistencia del historial conversacional.
    """
    
    @abstractmethod
    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje de chat en almacenamiento.

        Args:
            message (ChatMessage): Mensaje a persistir.

        Returns:
            ChatMessage: Mensaje guardado con datos finales de persistencia.
        """
        pass
    
    @abstractmethod
    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene historial de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de sesión.
            limit (Optional[int]): Máximo de mensajes a retornar.

        Returns:
            List[ChatMessage]: Historial de la sesión.
        """
        pass
    
    @abstractmethod
    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todo el historial de una sesión.

        Args:
            session_id (str): Identificador de sesión.

        Returns:
            int: Cantidad de mensajes eliminados.
        """
        pass
    
    @abstractmethod
    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los últimos mensajes de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de sesión.
            count (int): Cantidad máxima de mensajes recientes.

        Returns:
            List[ChatMessage]: Lista de mensajes recientes.
        """
        pass