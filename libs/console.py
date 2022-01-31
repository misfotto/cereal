from termcolor import colored
import logging


log = logging.getLogger('console')


def info(message):
    print(colored(" INFO    ", color='blue',  attrs=['reverse', 'bold']) + \
              colored(" " +message, color='white', attrs=['dark']))


def debug(message):
    print(colored(" DEBUG   ", color='grey',  attrs=['reverse', 'bold']) + \
          colored(" " +message, color='white', attrs=['dark']))


def success(message):
    #log.info(message)
    print(colored(" SUCCESS ", color='green', attrs=['reverse', 'bold']) + \
          colored(" " + message, color='white'))


def error(message):
    #log.error(message)
    print(colored(" ERRROR  ", color='red', attrs=['reverse', 'bold']) + \
          colored(" " + message, color='white'))


def warning(message):
    #log.warning(message)
    print(colored(" WARNING ", color='yellow', attrs=['reverse', 'bold']) + \
          colored(" " + message, color='white'))


def exception(message):
    #log.critical(message)
    print(colored(" EXCEPT  ", color='red', on_color='on_white', attrs=['bold']) + \
          colored(" " + message, color='white'))
