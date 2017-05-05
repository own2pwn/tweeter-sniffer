#!/usr/bin/python2.7

from snifferConstants import FRESH_TRUMP_TWEET_SEARCH_FILENAME
from twitterSecrets import twitterSecrets
from TwitterSearch import *
import codecs
import time
import json
# if need to get new,   save screen_names at the same time
#                       save data as JSON strings

try:
    tso = TwitterSearchOrder()
    tso.set_keywords(['trump'])
    tso.set_language('en')
    tso.set_result_type('mixed')

    ts = TwitterSearch(
        consumer_key = twitterSecrets[0]['consumer_key'],
        consumer_secret = twitterSecrets[0]['consumer_secret'],
        access_token = twitterSecrets[0]['access_token'],
        access_token_secret = twitterSecrets[0]['access_token_secret'],
        verify=True
     )

    def queryCallback(current_ts_instance): # accepts ONE argument: an instance of TwitterSearch
        queries, tweets_seen = current_ts_instance.get_statistics()
        if queries > 0 and (queries % 5) == 0: # trigger delay every 5th query
            time.sleep(60) # sleep for 60 seconds

    with codecs.open(FRESH_TRUMP_TWEET_SEARCH_FILENAME,"a+", 'utf-8') as file:
        for tweet in ts.search_tweets_iterable(tso, callback=queryCallback):
            text = (tweet['text']).replace('\n', ' ')
            print( '@%s tweeted: %s' % (tweet['user']['screen_name'], text) )
            file.write('%s, %s\n' % (tweet['user']['id'], text))

except TwitterSearchException as e:
    print(e)