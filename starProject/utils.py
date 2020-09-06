import inspect
import json
from copy import copy

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


def str_errors(serializer_errors, fields=True):
    """ serializer_errors:
         1) dict where key = fileld name, value = list strings of errors, OR
         2) list dicts from 1) if serializer with many=True
         3) etc...
    """

    def collect_errors(collect_list, errors, parent_field=''):
        if isinstance(errors, dict):
            for field, str_errors in errors.items():
                prefix = '%s > %s' % (parent_field, field) if parent_field else field
                if isinstance(str_errors, list):
                    for str_error in str_errors:
                        prefix = '%s > %s' % (parent_field, field) if parent_field else field
                        if isinstance(str_error, str):
                            collect_list.append('%s: %s' % (prefix, str_error))
                        else:
                            collect_errors(collect_list, str_error, prefix)
                elif isinstance(str_errors, str):
                    collect_list.append('%s: %s' % (prefix, str_errors))
                else:
                    collect_errors(collect_list, str_errors, prefix)
        elif isinstance(errors, list):
            for error in errors:
                collect_errors(collect_list, error)
        else:
            collect_list.append(errors)

    res_errors = []
    collect_errors(res_errors, serializer_errors)

    if fields:
        res = '<br>'.join(res_errors).replace('non_field_errors:','')
    else:
        res = '<br>'.join([err.split(':', maxsplit=1)[-1].lstrip() for err in res_errors])
    return res


def json_loads(filters):
    """ delete none values from filters
    """
    _filters = json.loads(filters or '{}')
    res_filters = copy(_filters)

    for param, value in _filters.items():
        # Выкидываем пустые значения из фильтров, при этом ноль оставляем
        if not value and value != 0:
            res_filters.pop(param)
    return res_filters