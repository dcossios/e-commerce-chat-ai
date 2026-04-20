"""Entidades y value objects del dominio de e-commerce con chat."""

from dataclasses import dataclass
from typing import Optional
from datetime import datetime


@dataclass
class Product:
    """
    Entidad que representa un producto del catálogo.

    Esta clase encapsula validaciones y comportamiento asociado al
    inventario de un producto.

    Attributes:
        id (Optional[int]): Identificador único del producto.
        name (str): Nombre comercial del producto.
        brand (str): Marca del producto.
        category (str): Categoría del producto.
        size (str): Talla del producto.
        color (str): Color del producto.
        price (float): Precio unitario, debe ser mayor a 0.
        stock (int): Cantidad en inventario, debe ser mayor o igual a 0.
        description (str): Descripción textual del producto.
    """
    id: Optional[int]
    name: str
    brand: str
    category: str
    size: str
    color: str
    price: float
    stock: int
    description: str
    
    def __post_init__(self):
        """
        Ejecuta validaciones de consistencia al construir la entidad.

        Raises:
            ValueError: Si el precio no es positivo, el stock es negativo
                o el nombre está vacío.
        """
        if self.price <= 0:
            raise ValueError("El precio debe ser mayor a 0")
        if self.stock < 0:
            raise ValueError("El stock no puede ser negativo")
        if not self.name.strip():
            raise ValueError("El nombre del producto no puede estar vacío")
    
    def is_available(self) -> bool:
        """
        Indica si el producto tiene unidades disponibles.

        Returns:
            bool: True cuando el stock es mayor que cero.
        """
        return self.stock > 0
    
    def reduce_stock(self, quantity: int) -> None:
        """
        Reduce el stock en la cantidad solicitada.

        Args:
            quantity (int): Cantidad a descontar del inventario.

        Raises:
            ValueError: Si la cantidad no es positiva o excede el stock.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a reducir debe ser positiva")
        if quantity > self.stock:
            raise ValueError("No hay suficiente stock para reducir")
        self.stock -= quantity
    
    def increase_stock(self, quantity: int) -> None:
        """
        Aumenta el stock en la cantidad indicada.

        Args:
            quantity (int): Cantidad a sumar al inventario.

        Raises:
            ValueError: Si la cantidad no es positiva.
        """
        if quantity <= 0:
            raise ValueError("La cantidad a aumentar debe ser positiva")
        self.stock += quantity


@dataclass
class ChatMessage:
    """
    Entidad que representa un mensaje dentro de una sesión de chat.

    Attributes:
        id (Optional[int]): Identificador único del mensaje.
        session_id (str): Identificador de la sesión conversacional.
        role (str): Rol del emisor, permitido: ``user`` o ``assistant``.
        message (str): Contenido textual del mensaje.
        timestamp (datetime): Fecha y hora de creación del mensaje.
    """
    id: Optional[int]
    session_id: str
    role: str  # 'user' o 'assistant'
    message: str
    timestamp: datetime
    
    def __post_init__(self):
        """
        Valida que el mensaje cumpla las reglas del dominio.

        Raises:
            ValueError: Si el rol no es válido o campos de texto están vacíos.
        """
        if self.role not in ['user', 'assistant']:
            raise ValueError("El rol debe ser 'user' o 'assistant'")
        if not self.message.strip():
            raise ValueError("El mensaje no puede estar vacío")
        if not self.session_id.strip():
            raise ValueError("El session_id no puede estar vacío")
    
    def is_from_user(self) -> bool:
        """
        Verifica si el mensaje fue enviado por el usuario.

        Returns:
            bool: True si ``role`` es ``user``.
        """
        return self.role == 'user'
    
    def is_from_assistant(self) -> bool:
        """
        Verifica si el mensaje fue enviado por el asistente.

        Returns:
            bool: True si ``role`` es ``assistant``.
        """
        return self.role == 'assistant'
    

@dataclass
class ChatContext:
    """
    Value Object que encapsula el contexto conversacional reciente.

    Attributes:
        messages (list[ChatMessage]): Lista completa de mensajes disponibles.
        max_messages (int): Número máximo de mensajes a incluir en contexto.
    """
    messages: list[ChatMessage]
    max_messages: int = 6
    
    def get_recent_messages(self) -> list[ChatMessage]:
        """
        Obtiene los últimos mensajes según el límite configurado.

        Returns:
            list[ChatMessage]: Subconjunto de mensajes más recientes.
        """
        return self.messages[-self.max_messages:]
    
    def format_for_prompt(self) -> str:
        """
        Formatea el historial reciente en texto para prompts del LLM.

        Returns:
            str: Historial multilinea con etiquetas ``Usuario``/``Asistente``.
        """
        formatted_messages = []
        for msg in self.get_recent_messages():
            role_label = "Usuario" if msg.is_from_user() else "Asistente"
            formatted_messages.append(f"{role_label}: {msg.message}")
        return "\n".join(formatted_messages)