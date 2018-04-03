# -*- coding: utf-8 -*-
"""
Created on Wed Nov 15 11:57:20 2017

"""

from flask import Flask
from flask import request
import json
import urllib.request
import logging

import cortex

#For Demo
import db

app = Flask(__name__)  

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
  
def sendSparkGET(url):  
    """ 
    This method is used for: 
        -retrieving message text, when the webhook is triggered with a message 
        -Getting the username of the person who posted the message if a command is recognized 
    """  

    bearer_token= "Bearer "+"Nzk1Y2M3NzgtZWVjMy00M2VlLTk0OWEtZDIzOTJkNmJlNzRmZDAwYmY0N2ItZmZk"
    header={"Accept" : "application/json",
             "Content-Type":"application/json",
             "Authorization":bearer_token}
    request_body = urllib.request.Request(url, headers=header)
    response_body = urllib.request.urlopen(request_body)
    response_data = response_body.read() 
    return response_data  
     
def sendSparkPOST(url, data):  
    """ 
    This method is used for: 
        -posting a message to the Spark room to confirm that a command was received and processed 
    """  
    data_body = urllib.parse.urlencode(data).encode("utf-8")
    print(data_body)
    request_body = urllib.request.Request(url, json.dumps(data).encode('utf-8') ,  
                            headers={"Accept" : "application/json",  
                                     "Content-Type":"application/json"})  
    request_body.add_header("Authorization", "Bearer "+bearer)  
    contents = urllib.request.urlopen(request_body).read()  
    return contents  
     
 
 
#@post('/')  

@app.route('/', methods=['POST'])
def index():  
    """ 
    When messages come in from the webhook, they are processed here.  The message text needs to be retrieved from Spark, 
    using the sendSparkGet() function.  The message text is parsed.  If an expected command is found in the message, 
    further actions are taken. 
    """  
    #logger.debug("Request received for: %s", request.get_json()['data']['name'])
    webhook = request.get_json()
    result = sendSparkGET('https://api.ciscospark.com/v1/messages/{0}'.format(webhook['data']['id']))  
    print('**********************************************************')
    print(type(result))
    result = json.loads(result.decode())  
    msg = None  
    if webhook['data']['personEmail'] != bot_email:  
        in_message = result.get('text', '').lower()  
        in_message = in_message.replace(bot_name, '')  
        
        msg=cortex.process(in_message)
        if msg != None:  
            logger.debug(msg)  
            sendSparkPOST("https://api.ciscospark.com/v1/messages", {"roomId": webhook['data']['roomId'], "text": msg})  
    return "true"  
  
  
####CHANGE THESE VALUES#####  
bot_email = "xbot1souvbose@sparkbot.io"  
bot_name = "XBot"  
bearer ='Nzk1Y2M3NzgtZWVjMy00M2VlLTk0OWEtZDIzOTJkNmJlNzRmZDAwYmY0N2ItZmZk' 
bat_signal  = "https://upload.wikimedia.org/wikipedia/en/c/c6/Bat-signal_1989_film.jpg"  
if __name__ == '__main__':
    app.run(debug=True)
