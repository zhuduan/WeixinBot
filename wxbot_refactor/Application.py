#!/usr/bin/env python
# coding: utf-8
import WechatApi
import UnicodeStreamFilter


if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)


if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    if not sys.platform.startswith('win'):
        import coloredlogs
        coloredlogs.install(level='DEBUG')

    webwx = WechatApi()
    webwx.start()
