"""Carga de datos iniciales para el catálogo de productos."""

from sqlalchemy.orm import Session

from src.infrastructure.db.database import SessionLocal
from src.infrastructure.db.models import ProductModel


def load_initial_data() -> None:
	"""
	Inserta productos semilla en la tabla de productos si está vacía.

	Returns:
		None

	Raises:
		Exception: Re-lanza cualquier error tras ejecutar rollback.
	"""
	db: Session = SessionLocal()
	try:
		existing_products = db.query(ProductModel).count()
		if existing_products > 0:
			return

		seed_products = [
			ProductModel(
				name="Air Zoom Pegasus 40",
				brand="Nike",
				category="Running",
				size="42",
				color="Negro",
				price=120.0,
				stock=8,
				description="Zapatilla de running con gran amortiguacion.",
			),
			ProductModel(
				name="Ultraboost 22",
				brand="Adidas",
				category="Running",
				size="41",
				color="Blanco",
				price=150.0,
				stock=5,
				description="Modelo premium para entrenamiento diario.",
			),
			ProductModel(
				name="Suede Classic",
				brand="Puma",
				category="Casual",
				size="40",
				color="Azul",
				price=80.0,
				stock=10,
				description="Estilo urbano clasico y comodo.",
			),
			ProductModel(
				name="Chuck Taylor All Star",
				brand="Converse",
				category="Casual",
				size="39",
				color="Rojo",
				price=70.0,
				stock=12,
				description="Silueta iconica para uso diario.",
			),
			ProductModel(
				name="Gel-Kayano 30",
				brand="ASICS",
				category="Running",
				size="43",
				color="Gris",
				price=180.0,
				stock=4,
				description="Estabilidad y soporte para largas distancias.",
			),
			ProductModel(
				name="Classic Leather",
				brand="Reebok",
				category="Casual",
				size="41",
				color="Blanco",
				price=90.0,
				stock=9,
				description="Diseno minimalista y versatil.",
			),
			ProductModel(
				name="Oxford Elegance",
				brand="Clarks",
				category="Formal",
				size="42",
				color="Cafe",
				price=140.0,
				stock=6,
				description="Zapato formal de cuero para ocasiones especiales.",
			),
			ProductModel(
				name="Derby Premium",
				brand="Hush Puppies",
				category="Formal",
				size="43",
				color="Negro",
				price=160.0,
				stock=3,
				description="Acabado elegante para oficina y eventos.",
			),
			ProductModel(
				name="Fresh Foam 1080",
				brand="New Balance",
				category="Running",
				size="42",
				color="Verde",
				price=170.0,
				stock=7,
				description="Confort avanzado para runners frecuentes.",
			),
			ProductModel(
				name="Court Vision Low",
				brand="Nike",
				category="Casual",
				size="40",
				color="Blanco",
				price=95.0,
				stock=11,
				description="Inspiracion retro para look urbano.",
			),
		]

		db.add_all(seed_products)
		db.commit()
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()
