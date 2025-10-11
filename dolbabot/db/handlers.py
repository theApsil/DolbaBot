from db.models import RegionIndex
from db.database import db_manager
from utils.logger import logger


class RegionIndexHandler:
   def get_city_index(self, city) -> RegionIndex:
    """Получение индекса города из БД по городу"""
    session = db_manager.get_session()
    try:
        city_index = session.query(RegionIndex).filter(RegionIndex.city == city).order_by(RegionIndex.id.desc()).first()
        return city_index
    except Exception as e:
        logger.error(f"Ошибка при получении индекса города: {e}")
        return None
    finally:
        session.close()
