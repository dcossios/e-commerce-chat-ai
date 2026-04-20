"""
Excepciones específicas del dominio.
Representan errores de negocio, no errores técnicos.
"""

from typing import Optional

class ProductNotFoundError(Exception):
    """
    Error lanzado cuando un producto no existe en el repositorio.
    """

    def __init__(self, product_id: Optional[int] = None):
        """
        Construye la excepción con mensaje contextual.

        Args:
            product_id (Optional[int]): Identificador del producto buscado.
        """
        if product_id is not None:
            message = f"Producto con ID {product_id} no encontrado"
        else:
            message = "Producto no encontrado"
        super().__init__(message)


class InvalidProductDataError(Exception):
    """
    Error lanzado cuando los datos de un producto no cumplen reglas del dominio.
    """

    def __init__(self, message: str = "Datos de producto inválidos"):
        """
        Construye la excepción con mensaje personalizado.

        Args:
            message (str): Descripción específica del error de validación.
        """
        super().__init__(message)


class ChatServiceError(Exception):
    """
    Error de aplicación durante el procesamiento del flujo de chat.
    """

    def __init__(self, message: str = "Error en el servicio de chat"):
        """
        Construye la excepción de chat con mensaje personalizado.

        Args:
            message (str): Mensaje detallado de la causa del error.
        """
        super().__init__(message)