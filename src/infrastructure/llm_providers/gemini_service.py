"""Adaptador de infraestructura para generar respuestas con Google Gemini."""

import asyncio
import os
from typing import List

import google.generativeai as genai
from dotenv import load_dotenv

from src.domain.entities import ChatContext, Product


class GeminiService:
    """
    Servicio de infraestructura para interacción con el modelo Gemini.

    Attributes:
        model: Instancia del modelo generativo configurado.
    """

    def __init__(self) -> None:
        """
        Configura el cliente de Gemini usando variables de entorno.

        Raises:
            ValueError: Si ``GEMINI_API_KEY`` no está configurada.
        """
        load_dotenv()

        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY no está configurada en variables de entorno")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel("gemini-2.5-flash")

    async def generate_response(
        self,
        user_message: str,
        products: List[Product],
        context: ChatContext,
    ) -> str:
        """
        Genera una respuesta contextual a partir del mensaje del usuario.

        Args:
            user_message (str): Mensaje actual del usuario.
            products (List[Product]): Catálogo de productos disponible.
            context (ChatContext): Contexto de conversación reciente.

        Returns:
            str: Respuesta del asistente.

        Raises:
            RuntimeError: Si ocurre error al invocar el proveedor de IA.
        """
        products_text = self.format_products_info(products)
        history_text = context.format_for_prompt().strip()
        if not history_text:
            history_text = "Sin historial previo."

        prompt = f"""Eres un asistente virtual experto en ventas de zapatos para un e-commerce.
Tu objetivo es ayudar a los clientes a encontrar los zapatos perfectos.

PRODUCTOS DISPONIBLES:
{products_text}

INSTRUCCIONES:
- Sé amigable y profesional
- Usa el contexto de la conversación anterior
- Recomienda productos específicos cuando sea apropiado
- Menciona precios, tallas y disponibilidad
- Si no tienes información, sé honesto

HISTORIAL DE CONVERSACIÓN:
{history_text}

Usuario: {user_message}

Asistente:"""

        try:
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            text = (response.text or "").strip()
            if not text:
                return "No pude generar una respuesta en este momento."
            return text
        except Exception as exc:
            raise RuntimeError(f"Error al generar respuesta con Gemini: {exc}") from exc

    def format_products_info(self, products: List[Product]) -> str:
        """
        Convierte productos del dominio a un bloque de texto para el prompt.

        Args:
            products (List[Product]): Productos disponibles.

        Returns:
            str: Texto formateado para incluir en el contexto del modelo.
        """
        if not products:
            return "No hay productos disponibles en este momento."

        lines = []
        for product in products:
            lines.append(
                f"- {product.name} | {product.brand} | ${product.price:.2f} | Stock: {product.stock}"
            )
        return "\n".join(lines)
