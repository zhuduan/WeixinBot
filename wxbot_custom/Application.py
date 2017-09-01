import sys
import os
import subprocess
import random
import multiprocessing
import platform
import logging
import xml.dom.minidom
import json
import time

import WechatApi
import MessageHandler

import Utils
from Utils import catchKeyboardInterrupt

api = WechatApi.weixin()
print(api.User)

class MainApp(object):

    def __init__(self):
        self.DEBUG = True
        self.interactive = False

    def toString(self):
        info = "TODO: show MainApp config"
        return info

    @catchKeyboardInterrupt
    def start(self):
        print('[*] 微信网页版 ... 开动')
        while True:
            Utils.run('[*] 正在获取 uuid ... ', api.getUUID)
            Utils.echo('[*] 正在获取二维码 ... 成功')
            logging.debug('[*] 微信网页版 ... 开动')
            api.genQRCode()
            Utils.echo('[*] 请使用微信扫描二维码以登录 ... ')
            if not api.waitForLogin():
                continue
                Utils.echo('[*] 请在手机上点击确认以登录 ... ')
            if not api.waitForLogin(0):
                continue
            break

        Utils.run('[*] 正在登录 ... ', api.login)
        Utils.run('[*] 微信初始化 ... ', api.webwxinit)
        Utils.run('[*] 开启状态通知 ... ', api.webwxstatusnotify)
        Utils.run('[*] 获取联系人 ... ', api.webwxgetcontact)
        Utils.echo('[*] 应有 %s 个联系人，读取到联系人 %d 个' % (api.MemberCount, len(api.MemberList)))
        print()
        Utils.echo('[*] 共有 %d 个群 | %d 个直接联系人 | %d 个特殊账号 ｜ %d 公众号或服务号' % (len(api.GroupList),
                                                                         len(api.ContactList), len(api.SpecialUsersList), len(api.PublicUsersList)))
        print()
        Utils.run('[*] 获取群 ... ', api.webwxbatchgetcontact)
        logging.debug('[*] 微信网页版 ... 初始化完成')
        if self.DEBUG:
            Utils.echo(self.toString())
        logging.debug(self)

        if self.interactive and input('[*] 是否开启自动回复模式(y/n): ') == 'y':
            self.autoReplyMode = True
            Utils.echo('[*] 自动回复模式 ... 开启')
        else:
            Utils.echo('[*] 自动回复模式 ... 关闭')

        if sys.platform.startswith('win'):
            import _thread
            _thread.start_new_thread(self.listenMsgMode())
        else:
            listenProcess = multiprocessing.Process(target=self.listenMsgMode)
            listenProcess.start()

        while True:
            text = input('')
            if text == 'quit':
                listenProcess.terminate()
                Utils.echo('[*] 退出微信')
                logging.debug('[*] 退出微信')
                exit()
            elif text[:2] == '->':
                [name, word] = text[2:].split(':')
                if name == 'all':
                    api.sendMsgToAll(word)
                else:
                    api.sendMsg(name, word)
            elif text[:3] == 'm->':
                [name, file] = text[3:].split(':')
                api.sendMsg(name, file, True)
            elif text[:3] == 'f->':
                Utils.echo('发送文件')
                logging.debug('发送文件')
            elif text[:3] == 'i->':
                Utils.echo('发送图片')
                [name, file_name] = text[3:].split(':')
                api.sendImg(name, file_name)
                logging.debug('发送图片')
            elif text[:3] == 'e->':
                Utils.echo('发送表情')
                [name, file_name] = text[3:].split(':')
                api.sendEmotion(name, file_name)
                logging.debug('发送表情')


    def handleMsg(self, r):
        for msg in r['AddMsgList']:
            Utils.echo('[*] 你有新的消息，请注意查收')
            logging.debug('[*] 你有新的消息，请注意查收')

            if self.DEBUG:
                fn = 'msg' + str(int(random.random() * 1000)) + '.json'
                with open(fn, 'w') as f:
                    f.write(json.dumps(msg))
                Utils.echo('[*] 该消息已储存到文件: ' + fn)
            MessageHandler.handle(msg, api)


    def listenMsgMode(self):
        Utils.echo('[*] 进入消息监听模式 ... 成功')
        Utils.run('[*] 进行同步线路测试 ... ', api.testsynccheck)
        playWeChat = 0
        redEnvelope = 0
        while True:
            api.lastCheckTs = time.time()
            [retcode, selector] = api.synccheck()
            if self.DEBUG:
                Utils.echo('retcode: %s, selector: %s' % (retcode, selector))
            logging.debug('retcode: %s, selector: %s' % (retcode, selector))
            if retcode == '1100':
                Utils.echo('[*] 你在手机上登出了微信，债见')
                break
            if retcode == '1101':
                Utils.echo('[*] 你在其他地方登录了 WEB 版微信，债见')
                break
            elif retcode == '0':
                if selector == '2':
                    r = api.webwxsync()
                    if r is not None:
                        self.handleMsg(r)
                elif selector == '6':
                    # TODO
                    redEnvelope += 1
                    Utils.echo('[*] 收到疑似红包消息 %d 次' % redEnvelope)
                elif selector == '7':
                    playWeChat += 1
                    Utils.echo('[*] 你在手机上玩微信被我发现了 %d 次' % playWeChat)
                    r = api.webwxsync()
                elif selector == '0':
                    time.sleep(1)
            if (time.time() - api.lastCheckTs) <= 20:
                time.sleep(time.time() - api.lastCheckTs)


if sys.stdout.encoding == 'cp936':
    sys.stdout = UnicodeStreamFilter(sys.stdout)

# app will start here
if __name__ == '__main__':
    logger = logging.getLogger(__name__)
    if not sys.platform.startswith('win'):
        import coloredlogs
        coloredlogs.install(level='DEBUG')
        app = MainApp()
        app.start()
