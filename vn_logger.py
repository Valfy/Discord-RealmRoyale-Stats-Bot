# -- coding: utf-8 --

import datetime
import traceback

class VN_logger():
    _FILENAME = datetime.datetime.now().strftime("%d_%m_%Y-%H_%M_%S")
    PRINT_MESSAGES = True
    LOGGING = True
    LOG_LEVEL_CEILING = 0
    _LEVELS = {
        'RUN': 0,
        'DEBUG': 10,
        'INFO': 20,
        'COMMAND': 30,
        'RESPONSE': 30,
        'ERROR': 40
    }

    @staticmethod
    def logging(level, message):
        level_to_compare = VN_logger._LEVELS[level] if level in VN_logger._LEVELS else 100
        if level_to_compare >= VN_logger.LOG_LEVEL_CEILING and VN_logger.LOGGING:
            try:
                with open(f'LOG-{VN_logger._FILENAME}.txt', 'a') as appender:
                    appender.write(f'[{datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")}] - {level} - {message} \n')
                    appender.close()
            except:
                with open(f'LOG-{VN_logger._FILENAME}.txt', 'w+') as create:
                    create.write(f'[{datetime.datetime.now().strftime("%d/%m/%Y-%H:%M:%S")}] - {level} - {message} \n')
                    create.close()
        if VN_logger.PRINT_MESSAGES:
            print(message)


    @staticmethod
    def collect_traceback():
        VN_logger.logging('ERROR', traceback.format_exc())



