dict_config = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'base': {
            'format': '%(levelname)s | %(name)s | %(funcName)s | %(asctime)s | %(lineno)d | %(message)s',
        }
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'level': 'DEBUG',
            'formatter': 'base',
        },
        'file': {
            "class": "logging.handlers.TimedRotatingFileHandler",
            "when": "midnight",
            "backupCount": 7,
            "formatter": "base",
            "level": "DEBUG",
            "filename": "app/logging/logs/logs.log"
        }
    },
    'loggers': {
        'main': {
            'level': 'DEBUG',
            'handlers': ['console', 'file'],
        },
    },
    'root': {
        'level': 'DEBUG',
        'handlers': [],
    }
}