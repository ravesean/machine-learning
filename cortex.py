# -*- coding: utf-8 -*-
"""
Created on Sat Nov 18 22:41:53 2017

"""

import logging
import db

import nltk
import pandas as pd
import json
from nltk.stem.snowball import SnowballStemmer
import re
from sklearn.feature_extraction.text import CountVectorizer
import sys
import scipy as sp

import sklearn.feature_extraction
import numpy as np
import pickle

from nltk.stem import WordNetLemmatizer
from sklearn.feature_extraction.text import TfidfVectorizer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

nltk.download('punkt')
nltk.download('stopwords')
nltk.download('wordnet')
result_set_from_db = {}
def process(message):
    # input query from user
    filtered_list = preprocess();
    # filtered_list contains details corresponding to all the jiras
    op1 = "hello"
    op = vectorize(filtered_list, message)
    return op
    
def preprocess():
    logger.debug('preprocessing Jira to remove redundant fields')
    global result_set_from_db
    if not result_set_from_db:
        logger.info('Memory empty. Fetching from DB')
        result_set_from_db=db.load_all()
    logger.info('Total results in cortex: %d',len(result_set_from_db))
    filtered_list = []
    for jira_id, jira_body in result_set_from_db.items():
        # jira_id corresponds here to https://jira-eng-sjc12.cisco.com/jira/browse/AVRIL-750
        logger.info("@@@@@@@@@@@@@ %s", jira_id)
        logger.info("@@@@@@@@@@@@@ %s", jira_body)
        filtered_fields = extract_relevant(jira_body, jira_id) # returns a JSON dictionary
        filtered_list.append(filtered_fields)
        # filtered_list contains list of JSON dictionary = [JSON1, JSON2, JSON3]
        
    return filtered_list


def tokenize_only(text):
    stops = nltk.corpus.stopwords.words('english')
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word.lower() for sent in nltk.sent_tokenize(text) if not sent in stops for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    return filtered_tokens
  
    #jira_frame=load_as_frames(filtered_list)
    

'''
Returns a dict
'''
def extract_relevant(jira_body, jira_id):
    jira_as_json = json.dumps(jira_body)
    jira_body = json.loads(jira_as_json)
    
    logger.info('@@@@@@@@@@@@@@@@@@@@@@@@ %s', jira_body)
    jira_json = {}
    jira_json['key'] = jira_body['key']
    jira_json['status'] = jira_body['fields']['resolution']['name']
    jira_json['created_on'] = jira_body['fields']['created']
    #jira_json['assignee'] = jira_body['fields']['assignee']['name']
    #jira_json['creator'] = jira_body['fields']['creator']['name']
    
    #jira_json['description'] = tokenize_and_stem(jira_body['fields']['description'])
    jira_json['description'] = jira_body['fields']['description']
    logger.debug("jira description: %s", jira_json['description'])
    jira_json['summary'] = jira_body['fields']['summary']
    jira_json['url'] = "https://jira-eng-sjc12.cisco.com/jira/browse/"+jira_id
    #logger.debug("jira summary: %s", jira_json['summary'])
    
    return jira_json

'''
Returns dataframe
'''
def load_as_frames(filtered_fields):
    column_names = [
            "key",
            "status",
            "created_on",
            "assignee",
            "creator",
            "description",
            "summary",
            ]
    jira_frame=pd.DataFrame(filtered_fields, columns=column_names)
    #logger.debug("Count of keys: %s", type(stops))
    return jira_frame

def tokenize_and_stem(text):
    # load nltk's English stopwords as variable called 'stopwords'
    stops = nltk.corpus.stopwords.words('english')
    custom_stops = ['to', 'has', 'been', 'if', 'this', 'was']
    stops = stops + custom_stops
    
    #logger.debug("stopwords: "+ str(stops[:20]))
    # load nltk's SnowballStemmer as variabled 'stemmer'
    #stemmer = SnowballStemmer("english")
    lemmatizer = WordNetLemmatizer()
    
    # first tokenize by sentence, then by word to ensure that punctuation is caught as it's own token
    tokens = [word for sent in nltk.sent_tokenize(text) if not sent in stops for word in nltk.word_tokenize(sent)]
    filtered_tokens = []
    # filter out any tokens not containing letters (e.g., numeric tokens, raw punctuation)
    for token in tokens:
        if re.search('[a-zA-Z]', token):
            filtered_tokens.append(token)
    stems = [lemmatizer.lemmatize(t, 'v') for t in filtered_tokens]
    return stems

def vectorize(filtered_list, message):
    
    #define vectorizer parameters
    tfidf_vectorizer = TfidfVectorizer(max_df=0.8, 
                                       max_features=200000, 
                                       min_df=0.2, 
                                       stop_words='english', 
                                       use_idf=True, 
                                       tokenizer=tokenize_and_stem
                                       )
    
    jira_description_list = []
    jira_urls = []
    for jira in filtered_list:
        jira_description_list.append(jira['description'])
        jira_urls.append(jira['url'])
    X_train = tfidf_vectorizer.fit_transform(jira_description_list)
    print('X_train')
    print(X_train)
    num_of_posts, num_of_words = X_train.shape
    print('$$$$$$$$$$$$')
    print(num_of_posts)
    print('$$$$$$$$$$$$')
    print(num_of_words)
    print('$$$$$$$$$$$$')
    print(tfidf_vectorizer.get_feature_names())
    user_input = [message]
    #new_post_vec = vectorizer.transform(user_input)
    new_post_vec = tfidf_vectorizer.transform(user_input)
    print('$$$$$$$$$$$$ ISSUE DISTANCE')
    print(new_post_vec.data.nbytes)
    if new_post_vec.data.nbytes == 0:
        print("No valid input provided")
        return "No similar issues found"
    best_doc = None
    best_i = -1
    best_dist = sys.maxsize
    best_i = None
    dist_list = []
    for i in range(0, num_of_posts):
        jira_description = jira_description_list[i]
        #print('JIRA DESCRIPTION : %s', jira_description)
        if jira_description == message:
            continue
        post_vec = X_train.getrow(i)
        d = norm_dist(post_vec, new_post_vec)
        dist_list.append(d)
        logger.info("=== Post %i with dist=%.2f: %s",i, d, jira_description)
        if d<best_dist:
            print('DISTANCE : %.2f', d)
            best_dist = d
            best_i = i
    logger.info("Best post is %i with dist=%.2f",best_i, best_dist)
    best = better = sys.maxsize
    first = second = sys.maxsize
    for i in range(0, num_of_posts):
        if dist_list[i] < best:
            better = best
            best = dist_list[i]
        if best<dist_list[i]<better:
            better = dist_list[i]
    print('RESOLUTION JIRA : ')
    i1 = dist_list.index(best)
    i2 = dist_list.index(better)
    print(better)
    print(best)
    print(dist_list.index(best))
    print(dist_list.index(better))
    return 'Found some similar issues: '+"\n"+jira_urls[i1]+"\n"+jira_urls[i2]
        
def norm_dist(v1, v2):
    v1_normalized = v1/sp.linalg.norm(v1.toarray())
    v2_normalized = v2/sp.linalg.norm(v2.toarray())
    delta = v1_normalized - v2_normalized
    return sp.linalg.norm(delta.toarray())


str = '''
Your account has been locked due to multiple repeated invalid login attempts. If this wasn't you, contact your administrator for further help.
For immediate voicemail access, goto selfcare portal to unlock your account.
'''
#process('Error while creating URL')



# 1. fetch list of jira in json
# 2. put them in columns and remove unnecessary columns
# 3. X_train=jira summary, Y_train=jira_id, X_test=user input, Y_test=related Jira
# 4. Check if jira can produced on spark room as URLs