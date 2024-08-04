from logging import (
    getLogger,
    FileHandler,
    Logger,
    StreamHandler,
    Formatter
)
from logging.handlers import (
    QueueHandler,
    QueueListener
)
from queue import Queue

"""Базовая настройка корневого logger'а.

Находится в отдельном модуле для того чтобы не засорять код app.py"""


FILE_FORMAT: Formatter = Formatter(
    fmt="[{asctime}] [{levelname}/{name}]: {message}",
    datefmt=r"%d.%m.%Y %H:%M:%S",
    style="{"
)

CMD_FORMAT: Formatter = Formatter(
    fmt="[{levelname}/{name}]: {message}",
    style="{"
)

def configure_log(log_path: str) -> None:
    # Загрузка конфигурации с помощью fileConfig() в данном случае не является опцией, т.к. работать файловая конфигурация с QueueHandler стала нормально только в 3.12.

    log_queue: Queue = Queue() # «Очередь», в которую посылаются запросы при вызове методов logger'ов (e.g. logger.info(), logger.warn() и т.д.)
    queue_handler: QueueHandler = QueueHandler(log_queue) # «Ручка», которая при получении запроса кидает его в LOG_QUEUE 

    # Добавление «ручки» к корневому (root) logger'у
    root: Logger = getLogger()
    root.setLevel("DEBUG")
    root.addHandler(queue_handler)  

    file_handler: FileHandler = FileHandler(
        filename=log_path,
        mode="w",
        encoding="utf-8"
    )
    file_handler.setFormatter(FILE_FORMAT)
    console_handler: StreamHandler = StreamHandler()
    console_handler.setFormatter(CMD_FORMAT)

    # Тут мы запускаем отдельный поток, который принимает информацию с LOG_QUEUE
    listener: QueueListener = QueueListener(log_queue, file_handler, console_handler, respect_handler_level=False)
    listener.start()