"""Configuración de base de datos y utilidades de sesión para SQLAlchemy."""

from pathlib import Path
import importlib
from typing import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./data/ecommerce_chat.db"

# Ensure the SQLite directory exists before first connection.
Path("data").mkdir(parents=True, exist_ok=True)

engine = create_engine(
	DATABASE_URL,
	connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db() -> Generator[Session, None, None]:
	"""
	Provee una sesión de base de datos para inyección de dependencias.

	Yields:
		Generator[Session, None, None]: Sesión SQLAlchemy activa.

	Note:
		La sesión se cierra automáticamente al finalizar el ciclo de request.
	"""
	db = SessionLocal()
	try:
		yield db
	finally:
		db.close()


def init_db() -> None:
	"""
	Inicializa esquema de base de datos y carga datos semilla.

	Returns:
		None

	Note:
		Realiza imports diferidos para permitir ejecución progresiva del taller.
	"""
	# Import lazily so this module works even before models are created.
	try:
		importlib.import_module("src.infrastructure.db.models")
	except ImportError:
		pass

	Base.metadata.create_all(bind=engine)

	try:
		module = importlib.import_module("src.infrastructure.db.init_data")
		module.load_initial_data()
	except ImportError:
		# init_data.py can be added later in the workshop sequence.
		pass
