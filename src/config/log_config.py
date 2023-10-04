LOG_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'json': {
            '()': 'src.config.logger.JSONLogFormatter',
        },
    },
    'handlers': {
        # Используем AsyncLogDispatcher для асинхронного вывода потока.
        'console': {
            'formatter': 'json',
            'class': 'asynclog.AsyncLogDispatcher',
            'func': 'src.config.logger.print_console',
            'level': 'ERROR',
        },
        'loki': {
            'formatter': 'json',
            'class': 'asynclog.AsyncLogDispatcher',
            'func': 'src.config.logger.push_loki',
            'level': 'INFO',
        },
    },
    'loggers': {
        'default': {
            'handlers': ['console', 'loki'],
            'level': 'INFO',
            'propagate': False,
        },
        'console': {
            'handlers': ['console'],
            'level': 'ERROR',
            'propagate': False,
        },
        'loki': {
            'handlers': ['loki'],
            'level': 'INFO',
            'propagate': False,
        },
        'user_stat': {
            'handlers': ['loki'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
