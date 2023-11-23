import os


LOGGING_CONFIG = {
    'version': 1,
    # loggersで''として指定してもOK
    # 'root': {
    #     'level': 'NOTSET',
    #     'handlers': ['debug_console_handler', 'info_rotating_file_handler', 'error_file_handler'],
    # },
    'loggers': {
        '': {  # root
            'level': 'NOTSET',
            'handlers': ['debug_console_handler'],
        },
    },
    'handlers': {
        'debug_console_handler': {
            'level': os.getenv("LOG_LEVEL", 'INFO'),
            'formatter': 'error',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
    },
    'formatters': {
        'info': {
            'format': '[%(levelname)s],%(process)d,%(filename)s::%(lineno)s,%(message)s'
        },
        'error': {
            'format': '[%(levelname)s],%(process)d,%(filename)s::%(lineno)s,%(message)s'
        },
    },

}