# the robot defined here

import urllib.request, urllib.parse, urllib.error
import urllib.request, urllib.error, urllib.parse
import http.cookiejar
import requests
import xml.dom.minidom
import json
import time
import ssl

from lxml import html
from socket import timeout as timeout_error


class RobotAnswer(object):

    apiKey = ""
    secretKey = ""
    requestApi = ""

    def getAnswer(self,question):
        answer = "伦家还是个孩子，不懂你在说什么"
        # TODO: get the answer from the remote server
        return answer

    def doPost(self,question):
        result = "";
        #TODO: request to the server
        return result
