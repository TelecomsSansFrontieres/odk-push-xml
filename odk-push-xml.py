#!/usr/bin/python
# -*- coding utf-8 -*-
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
