"""Aplicación FastAPI y definición de endpoints del sistema e-commerce chat."""

from datetime import datetime
from typing import List

from fastapi import Depends, FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from src.application.chat_service import ChatService
from src.application.dtos import (
	ChatHistoryDTO,
	ChatMessageRequestDTO,
	ChatMessageResponseDTO,
	ProductDTO,
)
from src.application.product_service import ProductService
from src.domain.exceptions import ChatServiceError, ProductNotFoundError
from src.infrastructure.db.database import get_db, init_db
from src.infrastructure.llm_providers.gemini_service import GeminiService
from src.infrastructure.repositories.chat_repository import SQLChatRepository
from src.infrastructure.repositories.product_repository import SQLProductRepository

app = FastAPI(
	title="E-commerce Chat AI API",
	description="API REST para e-commerce de zapatos con asistente conversacional usando Gemini.",
	version="1.0.0",
)

app.add_middleware(
	CORSMiddleware,
	allow_origins=["*"],
	allow_credentials=True,
	allow_methods=["*"],
	allow_headers=["*"],
)


@app.on_event("startup")
def on_startup() -> None:
	"""
	Ejecuta la inicialización de la base de datos al arranque del servicio.

	Returns:
		None
	"""
	init_db()


@app.get("/")
def root() -> dict:
	"""
	Retorna metadatos básicos del servicio y rutas principales.

	Returns:
		dict: Información descriptiva de la API.
	"""
	return {
		"name": "E-commerce Chat AI API",
		"version": "1.0.0",
		"description": "Servicio de productos y chat con IA para recomendación de zapatos.",
		"endpoints": [
			"/products",
			"/products/{product_id}",
			"/chat",
			"/chat/history/{session_id}",
			"/health",
		],
	}


@app.get("/products", response_model=List[ProductDTO])
def get_products(db: Session = Depends(get_db)) -> List[ProductDTO]:
	"""
	Lista todos los productos del catálogo.

	Args:
		db (Session): Sesión de base de datos inyectada por FastAPI.

	Returns:
		List[ProductDTO]: Lista completa de productos.
	"""
	repository = SQLProductRepository(db)
	service = ProductService(repository)
	products = service.get_all_products()
	return [ProductDTO.model_validate(product) for product in products]


@app.get("/products/{product_id}", response_model=ProductDTO)
def get_product_by_id(product_id: int, db: Session = Depends(get_db)) -> ProductDTO:
	"""
	Obtiene un producto por identificador.

	Args:
		product_id (int): ID del producto.
		db (Session): Sesión de base de datos inyectada.

	Returns:
		ProductDTO: Producto encontrado.

	Raises:
		HTTPException: 404 cuando el producto no existe.
	"""
	repository = SQLProductRepository(db)
	service = ProductService(repository)
	try:
		product = service.get_product_by_id(product_id)
		return ProductDTO.model_validate(product)
	except ProductNotFoundError as exc:
		raise HTTPException(status_code=404, detail=str(exc)) from exc


@app.post("/chat", response_model=ChatMessageResponseDTO)
async def send_chat_message(
	request: ChatMessageRequestDTO,
	db: Session = Depends(get_db),
) -> ChatMessageResponseDTO:
	"""
	Procesa un mensaje de chat y retorna una respuesta generada por IA.

	Args:
		request (ChatMessageRequestDTO): Carga útil con sesión y mensaje.
		db (Session): Sesión de base de datos inyectada.

	Returns:
		ChatMessageResponseDTO: Resultado de la interacción conversacional.

	Raises:
		HTTPException: 500 si ocurre error de aplicación o infraestructura.
	"""
	product_repository = SQLProductRepository(db)
	chat_repository = SQLChatRepository(db)
	try:
		ai_service = GeminiService()
		chat_service = ChatService(product_repository, chat_repository, ai_service)
		return await chat_service.process_message(request)
	except ChatServiceError as exc:
		raise HTTPException(status_code=500, detail=str(exc)) from exc
	except Exception as exc:
		raise HTTPException(status_code=500, detail=f"Error interno: {exc}") from exc


@app.get("/chat/history/{session_id}", response_model=List[ChatHistoryDTO])
def get_chat_history(
	session_id: str,
	limit: int = Query(default=10, ge=1),
	db: Session = Depends(get_db),
) -> List[ChatHistoryDTO]:
	"""
	Obtiene historial de una sesión con límite configurable.

	Args:
		session_id (str): Identificador de sesión.
		limit (int): Cantidad máxima de mensajes a retornar.
		db (Session): Sesión de base de datos inyectada.

	Returns:
		List[ChatHistoryDTO]: Historial de la sesión solicitado.
	"""
	product_repository = SQLProductRepository(db)
	chat_repository = SQLChatRepository(db)
	# El servicio requiere product_repository para su constructor aunque no se use en este método.
	chat_service = ChatService(product_repository, chat_repository, ai_service=None)
	return chat_service.get_session_history(session_id=session_id, limit=limit)


@app.delete("/chat/history/{session_id}")
def delete_chat_history(session_id: str, db: Session = Depends(get_db)) -> dict:
	"""
	Elimina todo el historial asociado a una sesión.

	Args:
		session_id (str): Identificador de sesión.
		db (Session): Sesión de base de datos inyectada.

	Returns:
		dict: Sesión y cantidad total de mensajes eliminados.
	"""
	product_repository = SQLProductRepository(db)
	chat_repository = SQLChatRepository(db)
	# El servicio requiere product_repository para su constructor aunque no se use en este método.
	chat_service = ChatService(product_repository, chat_repository, ai_service=None)
	deleted_count = chat_service.clear_session_history(session_id=session_id)
	return {
		"session_id": session_id,
		"deleted_count": deleted_count,
	}


@app.get("/health")
def health() -> dict:
	"""
	Retorna el estado de salud del servicio.

	Returns:
		dict: Estado del servicio y marca temporal.
	"""
	return {
		"status": "ok",
		"timestamp": datetime.utcnow().isoformat(),
	}
