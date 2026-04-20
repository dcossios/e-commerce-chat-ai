"""Servicios de aplicación para orquestar el chat conversacional."""

import inspect
from datetime import datetime
from typing import Any, List, Optional

from src.application.dtos import ChatHistoryDTO, ChatMessageRequestDTO, ChatMessageResponseDTO
from src.domain.entities import ChatContext, ChatMessage
from src.domain.exceptions import ChatServiceError
from src.domain.repositories import IChatRepository, IProductRepository


class ChatService:
	"""
	Servicio de aplicación para gestionar el chat con IA.

	Este servicio coordina productos, historial conversacional y proveedor
	de inteligencia artificial para producir respuestas contextuales.

	Attributes:
		_product_repository (IProductRepository): Repositorio de productos.
		_chat_repository (IChatRepository): Repositorio de historial de chat.
		_ai_service (Any): Servicio de IA con método ``generate_response``.
	"""

	def __init__(
		self,
		product_repository: IProductRepository,
		chat_repository: IChatRepository,
		ai_service: Any,
	):
		"""
		Inicializa el servicio con sus dependencias.

		Args:
			product_repository (IProductRepository): Repositorio de productos.
			chat_repository (IChatRepository): Repositorio de mensajes.
			ai_service (Any): Adaptador de IA para generar respuestas.
		"""
		self._product_repository = product_repository
		self._chat_repository = chat_repository
		self._ai_service = ai_service

	async def process_message(self, request: ChatMessageRequestDTO) -> ChatMessageResponseDTO:
		"""
		Procesa un mensaje de usuario y genera respuesta con IA.

		Flujo:
		1. Obtiene productos disponibles.
		2. Recupera mensajes recientes de la sesión.
		3. Construye contexto de conversación.
		4. Solicita respuesta al proveedor de IA.
		5. Persiste mensaje de usuario y respuesta del asistente.

		Args:
			request (ChatMessageRequestDTO): Solicitud de mensaje entrante.

		Returns:
			ChatMessageResponseDTO: Respuesta consolidada para API.

		Raises:
			ChatServiceError: Si ocurre cualquier error durante el proceso.
		"""
		try:
			products = self._product_repository.get_all()
			recent_history = self._chat_repository.get_recent_messages(
				session_id=request.session_id,
				count=6,
			)
			context = ChatContext(messages=recent_history, max_messages=6)

			generated = self._ai_service.generate_response(
				user_message=request.message,
				products=products,
				context=context,
			)
			assistant_message_text = (
				await generated if inspect.isawaitable(generated) else generated
			)

			user_message = ChatMessage(
				id=None,
				session_id=request.session_id,
				role="user",
				message=request.message,
				timestamp=datetime.utcnow(),
			)
			assistant_message = ChatMessage(
				id=None,
				session_id=request.session_id,
				role="assistant",
				message=str(assistant_message_text),
				timestamp=datetime.utcnow(),
			)

			self._chat_repository.save_message(user_message)
			self._chat_repository.save_message(assistant_message)

			return ChatMessageResponseDTO(
				session_id=request.session_id,
				user_message=request.message,
				assistant_message=str(assistant_message_text),
				timestamp=assistant_message.timestamp,
			)
		except Exception as exc:
			raise ChatServiceError(f"Error procesando mensaje de chat: {exc}") from exc

	def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatHistoryDTO]:
		"""
		Obtiene historial de sesión y lo transforma a DTO de salida.

		Args:
			session_id (str): Identificador de sesión.
			limit (Optional[int]): Límite máximo de mensajes a retornar.

		Returns:
			List[ChatHistoryDTO]: Historial formateado para capa de presentación.
		"""
		history = self._chat_repository.get_session_history(session_id=session_id, limit=limit)
		return [
			ChatHistoryDTO(
				id=message.id or 0,
				role=message.role,
				message=message.message,
				timestamp=message.timestamp,
			)
			for message in history
		]

	def clear_session_history(self, session_id: str) -> int:
		"""
		Elimina todo el historial de una sesión.

		Args:
			session_id (str): Identificador de sesión.

		Returns:
			int: Cantidad de mensajes eliminados.
		"""
		return self._chat_repository.delete_session_history(session_id)
