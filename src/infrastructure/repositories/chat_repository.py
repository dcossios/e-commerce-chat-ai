"""Repositorio SQLAlchemy para historial de conversaciones de chat."""

from typing import List, Optional

from sqlalchemy.orm import Session

from src.domain.entities import ChatMessage
from src.domain.repositories import IChatRepository
from src.infrastructure.db.models import ChatMemoryModel


class SQLChatRepository(IChatRepository):
    """
    Implementación concreta de persistencia de historial de chat.

    Attributes:
        db (Session): Sesión activa de base de datos.
    """

    def __init__(self, db: Session):
        """
        Inicializa el repositorio con una sesión SQLAlchemy.

        Args:
            db (Session): Sesión de base de datos inyectada.
        """
        self.db = db

    def save_message(self, message: ChatMessage) -> ChatMessage:
        """
        Guarda un mensaje en base de datos.

        Args:
            message (ChatMessage): Mensaje del dominio a persistir.

        Returns:
            ChatMessage: Mensaje guardado con atributos finales.
        """
        model = self._entity_to_model(message)
        self.db.add(model)
        self.db.commit()
        self.db.refresh(model)
        return self._model_to_entity(model)

    def get_session_history(self, session_id: str, limit: Optional[int] = None) -> List[ChatMessage]:
        """
        Obtiene historial de una sesión en orden cronológico.

        Args:
            session_id (str): Identificador de sesión.
            limit (Optional[int]): Límite opcional de mensajes.

        Returns:
            List[ChatMessage]: Historial de conversación.
        """
        query = self.db.query(ChatMemoryModel).filter(ChatMemoryModel.session_id == session_id)

        if limit is not None:
            models = query.order_by(ChatMemoryModel.timestamp.desc()).limit(limit).all()
            models.reverse()
            return [self._model_to_entity(model) for model in models]

        models = query.order_by(ChatMemoryModel.timestamp.asc()).all()
        return [self._model_to_entity(model) for model in models]

    def delete_session_history(self, session_id: str) -> int:
        """
        Elimina todos los mensajes de una sesión.

        Args:
            session_id (str): Identificador de sesión.

        Returns:
            int: Número de registros eliminados.
        """
        deleted_count = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .delete(synchronize_session=False)
        )
        self.db.commit()
        return deleted_count

    def get_recent_messages(self, session_id: str, count: int) -> List[ChatMessage]:
        """
        Obtiene los mensajes más recientes de una sesión.

        Args:
            session_id (str): Identificador de sesión.
            count (int): Cantidad máxima de mensajes.

        Returns:
            List[ChatMessage]: Mensajes recientes en orden cronológico.
        """
        if count <= 0:
            return []

        models = (
            self.db.query(ChatMemoryModel)
            .filter(ChatMemoryModel.session_id == session_id)
            .order_by(ChatMemoryModel.timestamp.desc())
            .limit(count)
            .all()
        )
        models.reverse()
        return [self._model_to_entity(model) for model in models]

    def _model_to_entity(self, model: ChatMemoryModel) -> ChatMessage:
        """Convierte un modelo ORM en entidad de dominio ChatMessage."""
        return ChatMessage(
            id=model.id,
            session_id=model.session_id,
            role=model.role,
            message=model.message,
            timestamp=model.timestamp,
        )

    def _entity_to_model(self, entity: ChatMessage) -> ChatMemoryModel:
        """Convierte una entidad ChatMessage en modelo ORM ChatMemoryModel."""
        return ChatMemoryModel(
            id=entity.id,
            session_id=entity.session_id,
            role=entity.role,
            message=entity.message,
            timestamp=entity.timestamp,
        )
