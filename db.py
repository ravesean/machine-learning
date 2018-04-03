# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 22:26:08 2017

@author: souvbose
"""

import logging
import json

#TO Remove
import requests
from pymongo import MongoClient

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def get_jira(message):
    logger.debug('Fetching Jira corresponding to jira-id')
    message = '''
    Found some similar issues:
    https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-750
    https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-752
    https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-754
    '''

    return message

def load_all():
    '''
    Loads all the jira from db into memory as json
    '''
    logger.debug('loading all results into memory for preprocessing')
    result_map = {}
    #To Remove
    #headers = {
     #       'authorization': "Basic cmF2cmF0aG86SnVseV8yMDE3",
     #       'cache-control': "no-cache"
    #}
    client = MongoClient('localhost', 27017)
    db = client.jira_database
    #issues = {}
    #for issue in db.JIRAS.find():
    #    issue = issue.encode('utf8').decode('utf8')
    #    print(issue)
    #    #.encode("utf-8")
    #    jira_key, jira_body = issue
    #    result_map[jira_key] = jira_body
   
    for i in range(2, 829):
        #issue = issue.encode('utf8').decode('utf8')
        ptr = "AVRIL-"+str(i)
        print("AVRIL-"+str(i)+".key"+" : " +"AVRIL-"+str(i))
        issue = db.ai.find_one({"AVRIL-"+str(i)+".key" : "AVRIL-"+str(i)})
        if issue is None:
            continue
        logger.info("##################### %s", issue)
        #.encode("utf-8")
        #jira_key, jira_body = issue
        #print(issue)
        #print(">>>>>>>>>>>>>>>>>>>>>>>>>>> %s", jira_key)
        result_map[ptr] = issue[ptr]
    
    #rest_url='https://jira-eng-chn-sjc3.cisco.com//jira/rest/api/2/issue/AVRIL-'
    #ui_url='https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-'
    #for id in range(2,829):
    #    url = rest_url+str(id)
    #    ui_key=ui_url+str(id)
    #    response_message = requests.request("GET", url, headers=headers, verify=False)
    #    #print("Type of message: %s",type(response_message.json()))
    #    result_json = response_message.json()
    #    result_map[ui_key]=result_json
    
    logger.info('Total results: %d',len(result_map))
    return result_map
    
#load_all()    
    