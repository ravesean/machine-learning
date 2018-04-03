# -*- coding: utf-8 -*-
"""
Created on Tue Nov 14 16:02:07 2017

@author: ravratho
"""

from pymongo import MongoClient
import logging 
import requests

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

result_set_from_db = {}
client = MongoClient('localhost', 27017)
#db1 = client.jira_database
#cursor = db1.issues.find()
#for document in cursor:
#    print(document)

logger.debug('loading all results into memory for preprocessing')
result_map = {}
#To Remove
headers = {
            'authorization': "Basic cmF2cmF0aG86SnVseV8yMDE3",
            'cache-control': "no-cache"
}
rest_url='https://jira-eng-chn-sjc3.cisco.com//jira/rest/api/2/issue/AVRIL-'
ui_url='https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-'
db2 = client.jira_database
for id in range(2,829):
        url = rest_url+str(id)
        ui_key="AVRIL-"+str(id)
        response_message = requests.request("GET", url, headers=headers, verify=False)
        #print("Type of message: %s",type(response_message.json()))
        result_json = response_message.json()
        result_map[ui_key]=result_json
        db2.ai.insert({ ui_key: result_json},check_keys=False)
logger.info('Total results: %d',len(result_map))

#issue = []
#for i in range(2, 5):
        #issue = issue.encode('utf8').decode('utf8')
        #print("AVRIL-"+str(i)+".key"+" : " +"AVRIL-"+str(i))
#        issue = db2.ai.find_one({"AVRIL-"+str(i)+".key" : "AVRIL-"+str(i)})
#        logger.info("##################### %s", issue)
# =============================================================================
# #        #.encode("utf-8")
# #        jira_key, jira_body = issue
# #        result_map[jira_key] = jira_body
# =============================================================================

#print(result_map)
#global result_set_from_db
#if not result_set_from_db:
#       print('Memory empty. Fetching from DB')
#       result_set_from_db=db.load_all()
#db2 = client.test
#for jira_id, jira_body in result_set_from_db.items():
#    db2.JIRAS.insert({ jira_id: jira_body},check_keys=False)
    
#logger.info('Total number of jiras: %d',len(result_set_from_db))

