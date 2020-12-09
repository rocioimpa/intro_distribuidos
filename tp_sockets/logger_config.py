import logging

LOGGING_LEVEL_DEBUG = logging.DEBUG
LOGGING_LEVEL_INFO = logging.INFO


def configLogger(identifier):
    logger = logging.getLogger(identifier)
    logger.setLevel(LOGGING_LEVEL_DEBUG)
    console = logging.StreamHandler()
    console.setLevel(LOGGING_LEVEL_DEBUG)
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    console.setFormatter(formatter)
    logger.addHandler(console)
    return logger
