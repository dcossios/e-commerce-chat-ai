"""DTOs de entrada y salida para los casos de uso de la aplicación."""

from pydantic import BaseModel, validator
from typing import Optional
from datetime import datetime


class ProductDTO(BaseModel):
    """
    DTO para representar productos en capa de aplicación y API.

    Attributes:
        id (Optional[int]): Identificador del producto.
        name (str): Nombre del producto.
        brand (str): Marca comercial.
        category (str): Categoría del producto.
        size (str): Talla.
        color (str): Color.
        price (float): Precio unitario.
        stock (int): Cantidad en inventario.
        description (str): Descripción del producto.
    """
    id: Optional[int] = None
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    
    @validator('price')
    def price_must_be_positive(cls, v):
        """
        Valida que el precio sea mayor que cero.

        Args:
            v (float): Precio recibido.

        Returns:
            float: Precio validado.

        Raises:
            ValueError: Si el precio es menor o igual a cero.
        """
        if v <= 0:
            raise ValueError('El precio debe ser mayor a 0')
        return v
    
    @validator('stock')
    def stock_must_be_non_negative(cls, v):
        """
        Valida que el stock sea mayor o igual a cero.

        Args:
            v (int): Stock recibido.

        Returns:
            int: Stock validado.

        Raises:
            ValueError: Si el stock es negativo.
        """
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v
    
    class Config:
        from_attributes = True  # Permite crear desde objetos ORM


class ChatMessageRequestDTO(BaseModel):
    """
    DTO para recibir mensajes entrantes de usuario.

    Attributes:
        session_id (str): Identificador de sesión conversacional.
        message (str): Texto del mensaje enviado por el usuario.
    """
    session_id: str
    message: str
    
    @validator('message')
    def message_not_empty(cls, v):
        """
        Valida que el mensaje no esté vacío.

        Args:
            v (str): Mensaje recibido.

        Returns:
            str: Mensaje validado.

        Raises:
            ValueError: Si el mensaje llega vacío.
        """
        if not v.strip():
            raise ValueError('El mensaje no puede estar vacío')
        return v
    
    @validator('session_id')
    def session_id_not_empty(cls, v):
        """
        Valida que el identificador de sesión no esté vacío.

        Args:
            v (str): Session ID recibido.

        Returns:
            str: Session ID validado.

        Raises:
            ValueError: Si ``session_id`` está vacío.
        """
        if not v.strip():
            raise ValueError('El session_id no puede estar vacío')
        return v


class ChatMessageResponseDTO(BaseModel):
    """
    DTO de salida para respuestas del flujo conversacional.

    Attributes:
        session_id (str): Identificador de sesión.
        user_message (str): Mensaje original del usuario.
        assistant_message (str): Respuesta generada por el asistente.
        timestamp (datetime): Fecha y hora de la respuesta.
    """
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime


class ChatHistoryDTO(BaseModel):
    """
    DTO para exponer mensajes del historial de chat.

    Attributes:
        id (int): Identificador del mensaje.
        role (str): Rol del emisor (user/assistant).
        message (str): Texto del mensaje.
        timestamp (datetime): Fecha y hora del mensaje.
    """
    id: int
    role: str
    message: str
    timestamp: datetime
    
    class Config:
        from_attributes = True