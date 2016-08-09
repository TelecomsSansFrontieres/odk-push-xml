#!/usr/bin/python
#
# MIT License
# 
# Copyright (c) 2016 Télécoms Sans Frontières
# 
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
# 
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
# 
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import sys
import urllib3
import ConfigParser
import logging
import requests
import time
from requests.auth import HTTPDigestAuth

#Disable urllib3 warnings when using HTTPS
urllib3.disable_warnings()

#The purposes of the script is to parse the entry text from xform formqt to xml format, 
#and send it to the ODK aggregate format
def getConfigVar():
    config = ConfigParser.RawConfigParser()
    config.read('./config.cfg')
    global server
    global login
    global password
    global logFile
    #login
    login = config.get('cfg', 'login')
    #password
    password = config.get('cfg', 'password')
    #serverNqme
    server = config.get('cfg', 'server')
    #logFile
    logFile = config.get('cfg', 'logFile')


def submitForm(_filename):
    logging.info(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Submit form to ODK Aggregate')
    #we prepare the submission
    xmlFile = { "xml_submission_file" : open(_filename, "rb") }

    s = requests.Session()
    auth = HTTPDigestAuth(login, password)
    formAdded = 0
    #Depending of the answer of the server we make the sms message
    code = 0
    try:
        code = s.get(url=server + "/local_login.html", auth=auth, verify=False, allow_redirects=True).status_code
    except Exception:
        logging.warning(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Error url')
    
    if (code == 401):
        #bad authentification
        logging.warning(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Error bad authentification')
    elif (code == 404):
        #not found
        logging.warning(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Error serveur not found')
    elif (code == 200):
        code2 = ""
        try:
            url = server + "/submission"
            code2 = s.post(url, files = xmlFile).status_code
        except Exception:
            logging.warning(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Error url')
        if (code2 == 200 or code2 == 201):
            formAdded = 1
            logging.info(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Form added to ODK Aggregate')
        else:
            logging.warning(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Wrong form, send again')
	
    return formAdded


#we call the function
getConfigVar()
#load debug file
logging.basicConfig(filename=logFile,level=logging.DEBUG)

#get file to submit
filename = sys.argv[1]
#submit form
submitForm(filename)

logging.info(time.strftime('%d/%m/%y %H:%M',time.localtime()) + ' Process finished successfully\n')
