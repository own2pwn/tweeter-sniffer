#!/usr/bin/python2.7


#
# THIS SCRIPT SHOULD NOT BE NECESSARY! 
# Created for quick test of TwitterSearch use and kept around because no real need to delete it
#


from TwitterSearch import *
import sys
import os
home = os.path.abspath('..')
sys.path.insert(0, home)
from twitterSecrets import twitterSecrets

TWITTER_SECRET = twitterSecrets[3]

userId = 860645659

sn = ""
tweets = []

try:
    ts = TwitterSearch(
        consumer_key = TWITTER_SECRET['consumer_key'],
        consumer_secret = TWITTER_SECRET['consumer_secret'],
        access_token = TWITTER_SECRET['access_token'],
        access_token_secret = TWITTER_SECRET['access_token_secret'],
        verify=True
     )

    for tweet in ts.search_tweets_iterable(TwitterUserOrder(userId)):
        print tweet['user']['screen_name']
        break

except TwitterSearchException as e:
    print(e)