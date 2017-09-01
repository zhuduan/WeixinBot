import re
import json
import time

import WechatApi
import Utils

autoReplyMode = False
userNicknameWhiteList = ["云儿","罗慧","翎漓雪","木易王罙","杨高翔","谢翠","卢磊","杨西","笑笑","陈俊超"]

# dispatch the request, base on: from type
def handle(msg, api):
    if msg==None :
        return

    fromUserID = msg['FromUserName']
    toUserID = msg['ToUserName']

    messageToShow = {'raw_msg' : msg, 'message': 'this a default message'}
    fromSource = messageSource(fromUserID, toUserID)
    if fromSource==1 or fromSource==0 :
        messageToShow = userMessageHandler(msg, api)
    elif fromSource==2 :
        messageToShow = groupMessageHandler(msg, api)
    else :
        messageToShow = {'raw_msg' : msg, 'message': '该类消息不需要处理'}

    api._showMsg(messageToShow)
    return

def userMessageHandler(msg, api):
    msgid = msg['MsgId']
    msgType = msg['MsgType']
    fromUserID = msg['FromUserName']
    fromUserName = api.getUserRemarkName(fromUserID)
    toUserID = msg['ToUserName']
    toUserName = api.getUserRemarkName(fromUserID)
    content = msg['Content'].replace('&lt;', '<').replace('&gt;', '>')

    if msgType == 1:
        raw_msg = {'raw_msg': msg}
        #如果是自己发给自己，则说明是命令
        if fromUserID==toUserID and content!='' :
            answer = doCommand(content)
            api.webwxsendmsg(answer)
            Utils.echo('命令模式： 命令是' + content + "回复是" + answer)
        elif autoReplyMode and isInWhiteList(fromUserName) :
            answer = TulingRobot.getInfoFromTulingRobot(content,"中文",fromUserID)
            if api.webwxsendmsg(answer, fromUserID):
                Utils.echo('自动回复: ' + answer)
            else:
                Utils.echo('自动回复失败')
        return raw_msg
    elif msgType == 3:
        image = api.webwxgetmsgimg(msgid)
        raw_msg = {'raw_msg': msg,
                   'message': '%s 发送了一张图片: %s' % (fromUserName, image)}
        api._safe_open(image)
        return raw_msg
    elif msgType == 34:
        voice = api.webwxgetvoice(msgid)
        raw_msg = {'raw_msg': msg,
                   'message': '%s 发了一段语音: %s' % (fromUserName, voice)}
        api._safe_open(voice)
        return raw_msg
    elif msgType == 42:
        info = msg['RecommendInfo']
        print('%s 发送了一张名片:' % fromUserName)
        print('=========================')
        print('= 昵称: %s' % info['NickName'])
        print('= 微信号: %s' % info['Alias'])
        print('= 地区: %s %s' % (info['Province'], info['City']))
        print('= 性别: %s' % ['未知', '男', '女'][info['Sex']])
        print('=========================')
        raw_msg = {'raw_msg': msg, 'message': '%s 发送了一张名片: %s' % (
            fromUserName.strip(), json.dumps(info))}
        return raw_msg
    elif msgType == 47:
        url = api._searchContent('cdnurl', content)
        raw_msg = {'raw_msg': msg,
                   'message': '%s 发了一个动画表情，点击下面链接查看: %s' % (fromUserName, url)}
        api._safe_open(url)
        return raw_msg
    elif msgType == 49:
        appMsgType = defaultdict(lambda: "")
        appMsgType.update({5: '链接', 3: '音乐', 7: '微博'})
        print('%s 分享了一个%s:' % (fromUserName, appMsgType[msg['AppMsgType']]))
        print('=========================')
        print('= 标题: %s' % msg['FileName'])
        print('= 描述: %s' % api._searchContent('des', content, 'xml'))
        print('= 链接: %s' % msg['Url'])
        print('= 来自: %s' % api._searchContent('appname', content, 'xml'))
        print('=========================')
        card = {
            'title': msg['FileName'],
            'description': api._searchContent('des', content, 'xml'),
            'url': msg['Url'],
            'appname': api._searchContent('appname', content, 'xml')
        }
        raw_msg = {'raw_msg': msg, 'message': '%s 分享了一个%s: %s' % (
            fromUserName, appMsgType[msg['AppMsgType']], json.dumps(card))}
        return raw_msg
    elif msgType == 51:
        raw_msg = {'raw_msg': msg, 'message': '[*] 成功获取联系人信息'}
        return raw_msg
    elif msgType == 62:
        video = api.webwxgetvideo(msgid)
        raw_msg = {'raw_msg': msg,
                   'message': '%s 发了一段小视频: %s' % (fromUserName, video)}
        api._safe_open(video)
        return raw_msg
    elif msgType == 10002:
        raw_msg = {'raw_msg': msg, 'message': '%s 撤回了一条消息' % fromUserName}
        return raw_msg
    else:
        logging.debug('[*] 该消息类型为: %d，可能是表情，图片, 链接或红包: %s' %
                      (msg['MsgType'], json.dumps(msg)))
        raw_msg = {
            'raw_msg': msg, 'message': '[*] 该消息类型为: %d，可能是表情，图片, 链接或红包' % msg['MsgType']}
        return raw_msg
    return { 'raw_msg': msg, 'message': 'userMessageHandler无法处理的类型'};

def groupMessageHandler(msg, api):
    #TODO:
    return {'raw_msg' : msg, 'message': '群组消息待处理'}

def doCommand(content):
    if "影分身之术" in content :
        autoReplyMode = True
        return "好哒！看我的！"
    elif "不玩了" in content :
        autoReplyMode = False
        return "我在这儿等着你回来~等着你回来~"
    elif "可撩" in content :
        regx = r'(@\S+)'
        pm = re.search(regx, content)
        if pm:
            userNicknameWhiteList.append(pm.group()[1:])
            return "\"" + pm.group()[1:] + "\" 已加入您的豪华撩妹/汉名单"
        else :
            return "没get到您说的名字，请用@Name告诉我是谁"
    elif "不撩" in content :
        regx = r'(@\S+)'
        pm = re.search(regx, content)
        if pm:
            userNicknameWhiteList.remove(pm.group()[1:])
            return "哼，已经移除了 \"" + pm.group()[1:] + "\" 这个小婊砸！"
        else :
            return "没get到您说的名字，请用@Name告诉我是谁"
    elif "上去撩他" in content :
        regx = r'(@\S+)'
        pm = re.search(regx, content)
        if pm:
            userNicknameWhiteList.append(pm.group()[1:])
            return "as you wish, my lord"
        else :
            return "我们没能击穿敌军的装甲"
    else :
        return "I can not understand your command, my lord"

# 1 means user, 2 means group
def isInWhiteList(name="", mode=1):
    if mode==1 :
        if (name in userNicknameWhiteList) :
            return True
        else :
            return False
    elif mode==2 :
        # TODO: group is to do
        return False
    else :
        # other condition is not supported now
        return False

# judge the message from user or group :
# return 1 for user, 2 for group, 0 for others, -1 for error
def messageSource(fromUserName="", toUserName=""):
    if len(fromUserName)<3 and len(toUserName)<3 :
        return -1

    fromKey = "defaultKey"
    toKey = "defaultKey"
    if len(fromUserName)>2 :
        fromKey = fromUserName[:2]
    if len(toUserName)>2 :
        toKey = toUserName[:2]

    if fromKey=="@@" or toKey=="@@" :
        return 2
    elif fromKey[:1]=="@" and toKey[:1]=="@" :
        return 1
    else :
        return 0
