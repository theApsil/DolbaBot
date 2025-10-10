from .settings import settings
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from .logger import logger
from .traidingview_parser import CourseParser
from db.database import db_manager
from db.course_handler import course_handler  # Импортируем хендлер


class BrowserManager:
    def __init__(self):
        self.driver = None
        self.is_ready = False
        self.old_driver = None
        self.last_course = None
        self.course_parser = CourseParser()

    def get_driver(self):
        chrome_opts = Options()
        chrome_opts.add_argument("--headless=new")
        chrome_opts.add_argument("--no-sandbox")
        chrome_opts.add_argument("--disable-dev-shm-usage")
        chrome_opts.add_argument("--disable-gpu")
        chrome_opts.add_argument("--window-size=1400,900")

        return webdriver.Remote(
            command_executor=settings.selenium_url,
            options=chrome_opts
        )

    def extract_course_from_page(self):
        """
        Извлечение курса с помощью CourseParser
        """
        try:
            course_value = self.course_parser.get_course(self.driver.page_source)
            return course_value
        except Exception as e:
            logger.error(f"Ошибка при извлечении курса: {e}")
            return None

    def run_browser(self, shutdown_event=None):
        try:
            # Инициализируем БД при запуске браузера
            db_manager.init_database(settings.database_schema)

            driver_a = self.get_driver()
            driver_a.get(settings.selenium_browser_link)
            wait = WebDriverWait(driver_a, settings.browser_timeout)
            wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.driver = driver_a
            self.is_ready = True

            # Сохраняем курс при первой загрузке
            course_value = self.extract_course_from_page()
            if course_value is not None:
                # Используем хендлер для сохранения
                course_handler.save_course(course_value)
                self.last_course = course_value

            logger.info("Браузер успешно запущен")

            while not shutdown_event or not shutdown_event.is_set():
                time.sleep(settings.poll_seconds)

                if shutdown_event and shutdown_event.is_set():
                    break

                self._refresh_browser()

        except Exception as e:
            logger.error(f"Критическая ошибка при запуске браузера: {e}")
            self.is_ready = False

    def _refresh_browser(self):
        try:
            driver_b = self.get_driver()
            driver_b.get(settings.selenium_browser_link)
            WebDriverWait(driver_b, settings.browser_timeout).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )

            # Извлекаем курс из нового драйвера перед заменой
            new_course_value = self.extract_course_from_page()

            # Закрываем предыдущий старый драйвер
            if self.old_driver:
                try:
                    self.old_driver.quit()
                except Exception as e:
                    logger.error(f"Ошибка при закрытии предыдущего старого драйвера: {e}")

            # Сохраняем текущий драйвер как старый и заменяем на новый
            self.old_driver = self.driver
            self.driver = driver_b

            # Сохраняем курс если он изменился или просто при каждой загрузке
            if new_course_value is not None:
                # Используем хендлер для сохранения
                course_handler.save_course(new_course_value)
                self.last_course = new_course_value

        except Exception as e:
            logger.error(f"Ошибка обновления браузера: {e}")

    def cleanup(self):
        """Закрывает все драйверы при завершении приложения"""
        logger.info("Завершение работы браузера...")
        self.is_ready = False

        if self.driver:
            try:
                self.driver.quit()
                self.driver = None
            except Exception as e:
                logger.error(f"Ошибка при закрытии текущего драйвера: {e}")

        if self.old_driver:
            try:
                self.old_driver.quit()
                self.old_driver = None
            except Exception as e:
                logger.error(f"Ошибка при закрытии старого драйвера: {e}")

        logger.info("Все драйверы закрыты")


# Глобальный экземпляр
browser_manager = BrowserManager()