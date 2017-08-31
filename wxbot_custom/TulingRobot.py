import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import requests
import xml.dom.minidom
import json
import time
import ssl
import hashlib
import re
import logging
import http.client
from collections import defaultdict
from urllib.parse import urlparse

def getInfoFromTulingRobot(question,location="中国",userID="123"):
    baseUrl = "http://www.tuling123.com/openapi/api"
    apiKey = "f8f4bf501c344fcab3d31081ac9a8b1f"
    # current not use the Aes
    # apiSecret = "ccb3a92c14f8ba4e"

    data = { "key":apiKey, "info":question, "loc": location, "userid": userID}
    responeInfo = _doPost(baseUrl,data)
    answer = "伦家出错啦，哎嘿～"
    if responeInfo != "":
        answer = handleAnswer(responeInfo)
    return answer


def formatUserID(userID):
    formatedUserID = "default";
    if len(userID)<=0 :
        return formatedUserID
    if len(userID)>32 :
        userID = userID[:32]
    regx = r'\w+'
    pm = re.findall(regx, userID)
    if pm :
        formatedUserID = ""
        for tempRes in pm :
            formatedUserID = formatedUserID + tempRes
    return (formatedUserID.replace("_","0"))


def handleAnswer(responeInfo):
    #TODO: do more complicated parse
    print(responeInfo)
    return responeInfo["text"]


def _doPost(url: object, params: object):
    try:
        data = urllib.parse.urlencode(params).encode('utf-8')
        request = urllib.request.Request(url)
        request.add_header('ContentType', 'application/json; charset=UTF-8')

        response = urllib.request.urlopen(request, data)
        result = response.read()
        return json.loads(result.decode('utf-8'))
    except urllib.error.HTTPError as e:
        logging.error('HTTPError = ' + str(e.code))
    except urllib.error.URLError as e:
        logging.error('URLError = ' + str(e.reason))
    except http.client.HTTPException as e:
        logging.error('HTTPException')
    except Exception:
        import traceback
        logging.error('generic exception: ' + traceback.format_exc())
    return ""


print(getInfoFromTulingRobot("额，你为啥这么傲娇！"))
