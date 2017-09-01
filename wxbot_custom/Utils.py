import logging
import sys
import os

from collections import defaultdict
from urllib.parse import urlparse



def catchKeyboardInterrupt(fn):
    def wrapper(*args):
        try:
            return fn(*args)
        except KeyboardInterrupt:
            print('\n[*] 强制退出程序')
            logging.debug('[*] 强制退出程序')
    return wrapper


def _decode_list(data):
    rv = []
    for item in data:
        if isinstance(item, str):
            item = item.encode('utf-8')
        elif isinstance(item, list):
            item = _decode_list(item)
        elif isinstance(item, dict):
            item = _decode_dict(item)
        rv.append(item)
    return rv


def _decode_dict(data):
    rv = {}
    for key, value in data.items():
        if isinstance(key, str):
            key = key.encode('utf-8')
        if isinstance(value, str):
            value = value.encode('utf-8')
        elif isinstance(value, list):
            value = _decode_list(value)
        elif isinstance(value, dict):
            value = _decode_dict(value)
        rv[key] = value
    return rv

def run(str, func, *args):
    echo(str)
    if func(*args):
        print('成功')
        logging.debug('%s... 成功' % (str))
    else:
        print('失败\n[*] 退出程序')
        logging.debug('%s... 失败' % (str))
        logging.debug('[*] 退出程序')
        exit()

def echo(str):
    logging.info(str)
    sys.stdout.write(str)
    sys.stdout.flush()
