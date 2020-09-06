import inspect
import jwt
import logging
import pprint
from calendar import timegm
from datetime import datetime
from typing import List

from starProject.settings import TOKEN_LIFE, SECRET_KEY


def log_debug(*messages: List[str], pretty_print=False):
    """ logging messages lines into adminka_debug.log (view settings.py)
    :param *messages: list of str messages by '\n'
    :param kwargs:
    :return: None
    """
    message = None
    logger = logging.getLogger('debug')
    caller = inspect.stack()[1]
    filename = caller.filename
    lineno = caller.lineno
    function = caller.function

    try:
        if pretty_print:
            message = '\n'.join(map(pprint.pformat, messages)) or "!!! log_debug: Empty message !!!"
        else:
            message = '\n'.join(map(str, messages)) or "!!! log_debug: Empty message !!!"
    except Exception as e:
        message = "!!! log_debug: Can't convert message to str !!!"

    logger.info('%s | func: %s | line: %s\n\n%s' % (filename, function, lineno, message))


def log_info(*messages: List[str], index_stack: int = 1, show_filename: bool = False, **kwargs):
    """ logging short messages to 1 line into debug.log (view settings.py)

    :param messages: list of str messages
    :param index_stack: find func by index_stack in stack for show it in logs
    :param show_filename: show filename of found function in logs
    :param show_time: show time log in logs
    :param kwargs: kwargs
    :return: None
    """
    message = None
    logger = logging.getLogger('info')
    caller = inspect.stack()[index_stack]
    lineno = caller.lineno
    try:
        message = ''.join(map(str, messages)) or "!!! log_info: Empty message !!!"
    except Exception as e:
        message = "!!! log_info: Can't convert message to str !!!"

    if show_filename:
        message = '{} => {}'.format(caller.filename, message)

    logger.info('line: %s | %s' % (lineno, message))


def generate_token(user):
    date_now = datetime.now()
    # the start time of the day
    stod = datetime(date_now.year, date_now.month, date_now.day)
    date_exp = stod + TOKEN_LIFE

    token_data = {
        'iat': timegm(datetime.utcnow().timetuple()),
        'exp': timegm(date_exp.timetuple()),
        'user_id': user.id,
    }
    token = jwt.encode(token_data, SECRET_KEY, algorithm='HS256')
    return token