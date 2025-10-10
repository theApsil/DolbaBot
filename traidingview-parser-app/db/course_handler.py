from sqlalchemy.orm import Session
from .models import Course
from .database import db_manager
from datetime import datetime, timezone
from services.logger import logger


class CourseHandler:
    def save_course(self, course_value: float) -> bool:
        """Сохранение курса в БД с текущим временем"""
        try:
            session = db_manager.get_session()
            current_time = datetime.now(timezone.utc).replace(tzinfo=None)

            new_course = Course(
                date=current_time,
                course=course_value
            )
            session.add(new_course)
            session.commit()
            logger.info(f"Курс {course_value} сохранен в БД на время {current_time}")
            return True

        except Exception as e:
            logger.error(f"Ошибка при сохранении курса в БД: {e}")
            session.rollback()
            return False
        finally:
            session.close()

    def get_last_course(self) -> Course:
        """Получение последнего курса из БД по ID"""
        try:
            session = db_manager.get_session()
            last_course = session.query(Course).order_by(Course.id.desc()).first()
            return last_course
        except Exception as e:
            logger.error(f"Ошибка при получении последнего курса: {e}")
            return None
        finally:
            session.close()

    def get_courses_by_date_range(self, start_date: datetime, end_date: datetime):
        """Получение курсов за период времени"""
        try:
            session = db_manager.get_session()
            courses = session.query(Course).filter(
                Course.date >= start_date,
                Course.date <= end_date
            ).order_by(Course.date).all()
            return courses
        except Exception as e:
            logger.error(f"Ошибка при получении курсов за период: {e}")
            return []
        finally:
            session.close()


# Глобальный экземпляр хендлера
course_handler = CourseHandler()