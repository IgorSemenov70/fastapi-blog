import logging.config

from app.logging.logging_config import dict_config

logging.config.dictConfig(dict_config)
logger = logging.getLogger('main')
