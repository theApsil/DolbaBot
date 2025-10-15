import logging


# Настройка базового логгера
logging.basicConfig(
    level=logging.INFO,  # INFO, DEBUG, WARNING, ERROR
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler()          # лог в консоль
    ]
)

logger = logging.getLogger("dolbabot_app")