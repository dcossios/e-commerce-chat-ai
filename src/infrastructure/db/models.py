"""Modelos ORM de SQLAlchemy para productos e historial de chat."""

from datetime import datetime

from sqlalchemy import Column, DateTime, Float, Integer, String, Text

from src.infrastructure.db.database import Base


class ProductModel(Base):
	"""
	Modelo ORM para la tabla ``products``.

	Representa un producto persistido en base de datos relacional.
	"""

	__tablename__ = "products"

	# Identificador unico del producto.
	id = Column(Integer, primary_key=True, autoincrement=True)
	# Nombre comercial del producto.
	name = Column(String(200), nullable=False)
	# Marca del producto (Nike, Adidas, etc.).
	brand = Column(String(100), nullable=False, index=True)
	# Categoria del producto (Running, Casual, etc.).
	category = Column(String(100), nullable=False, index=True)
	# Talla del producto.
	size = Column(String(20), nullable=False)
	# Color del producto.
	color = Column(String(50), nullable=False)
	# Precio del producto.
	price = Column(Float, nullable=False)
	# Stock disponible del producto.
	stock = Column(Integer, nullable=False)
	# Descripcion larga del producto.
	description = Column(Text, nullable=False)


class ChatMemoryModel(Base):
	"""
	Modelo ORM para la tabla ``chat_memory``.

	Almacena mensajes de conversación asociados a una sesión.
	"""

	__tablename__ = "chat_memory"

	# Identificador unico del mensaje.
	id = Column(Integer, primary_key=True, autoincrement=True)
	# Identificador de la sesion de conversacion.
	session_id = Column(String(100), nullable=False, index=True)
	# Rol del emisor del mensaje (user/assistant).
	role = Column(String(20), nullable=False)
	# Contenido del mensaje.
	message = Column(Text, nullable=False)
	# Momento de creacion del mensaje en UTC.
	timestamp = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
