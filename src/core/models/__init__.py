# Все модели SQLAlchemy импортируются сюда,
# чтобы alembic их увидел
# 
# Так же в других файлах (кроме файлов с моделями)
# модели лучше импортировать отсюда,
# чтобы избежать циркулярного импорта

from core.models.base import Base, SQLAlchemyModel

# Импорт моделей
from models import *