#!/usr/bin/env python
# coding: utf-8

import WechatApi

class AbstractMessageHandler(object):

    wechatApi = None

    def __init__(self,currentWecharApi):
        self.wechatApi = currentWecharApi

    def userMessageHandler(self,MessageModel):
        return;

    def groupMessageHandler(self,MessageModel):
        return;
