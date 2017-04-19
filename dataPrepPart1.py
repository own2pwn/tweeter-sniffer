#!/usr/bin/python2.7

from TwitterSearch import *
import codecs
import time
import re
import json
import argparse

# import os
# import sys
# sys.path.insert(0, os.path.abspath('..'))
from twitterSecrets import twitterSecrets

UNK = 0 
PRO = 1 
ANT = -1

MINIMUM_TWEET_COUNT = 100   # DP: find count in tweets: if total < 100, print and next user
MINIMUM_NONTRUMP_PERC = 0.4 # DP: if nontrump / total < 40%, print and next user

TRUMP_PATTERN = re.compile(r"(\W|^)trump(\W|$)", re.IGNORECASE)
MENTIONED_PATTERN = re.compile(r"@(\w+)")
HASHTAG_PATTERN = re.compile(r"#(\w+)")

param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))

FILE_NAME = "trump_all_dedup"
# FILE_NAME = "trump_sample"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('fileNumber', help="file number if split file, 0 if not")
    args = parser.parse_args()

    global TWITTER_SECRET
    global FILE_NAME

    if int(args.fileNumber) != 0:
        FILE_NAME += args.fileNumber
        TWITTER_SECRET = twitterSecrets[(int(args.fileNumber) - 1) % 4]
    else:
        TWITTER_SECRET = twitterSecrets[0]

    with codecs.open(FILE_NAME + ".txt", "r", "utf-8") as file:
        content = file.readlines()

    foundTweets = []
    uniqueUsers = []

    for line in content:
        x = line.split(",", 1)
        foundTweets.append(x)
        if x[0] not in uniqueUsers:
            uniqueUsers.append(x[0])

    foundLen = len(foundTweets)
    print len(uniqueUsers), "unique users initially present in dataset of", foundLen, "tweets\n"

    allTrumpTweets = []
    nontrumpHistories = []
    profiles = []

    for n, uu in enumerate(uniqueUsers):
        tweets = []
        trump = []
        nontrump = []

        uu = int(uu)

        # screenName, tweets = pullDummy(uu)
        screenName, tweets = pullInfo(uu)
        tweetLen = len(tweets)
        
        if tweetLen < MINIMUM_TWEET_COUNT:
            if tweetLen > 0:
                print "User", uu, "removed because only", tweetLen, "tweets are available\n"
            else:
                print "User", uu, "removed because no authored tweets were retrieved\n"
            continue

        for tweet in tweets:
            if isTrumpTweet(tweet):
                trump.append([ tweet[0], tweet[1], uu, getMentioned(tweet), getHashtags(tweet), UNK ])
            else:
                nontrump.append(tweet[1])

        nontrumpLen = len(nontrump)
        nontrumpPerc = nontrumpLen / float(tweetLen)
        if nontrumpPerc < MINIMUM_NONTRUMP_PERC:
            print "User", uu, "removed because only", nontrumpPerc * 100, "% of tweet history does not mention Trump\n"
            continue

        allTrumpTweets.extend(trump)
        nontrumpHistories.append([ uu, nontrump ])
        trumpLen = len(trump)
        profiles.append([ uu, screenName, [0, trumpLen, 0], UNK ])

        print "User #", n + 1, "of", foundLen, ":"
        print "ID:", uu
        print "Screen name:", screenName
        print trumpLen, "trump tweets"
        print nontrumpLen, "nontrump tweets\n"

        time.sleep(30) # include delay between every user

    with codecs.open(FILE_NAME + "_trumpTweets" + param + ".json", "w+", "utf-8") as file:
        json.dump(allTrumpTweets, file, indent=4, separators=(',', ': '))

    with codecs.open(FILE_NAME + "_histories" + param + ".json", "w+", "utf-8") as file:
        json.dump(nontrumpHistories, file, indent=4, separators=(',', ': '))

    with codecs.open(FILE_NAME + "_profiles" + param + ".json", "w+", "utf-8") as file:
        json.dump(profiles, file, indent=4, separators=(',', ': '))


# output:   allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...], 
#           nontrumpHistories = [(user 1 id, [tweet 1 text, tweet 2 text, ...]), ...],
#           profiles = [(user 1 id, user 1 screen_name, user alignment, user class)]

# pull tweet history and screen_name from last 7 days: (screen_name, list of dependent tweet tuple (tweet id, text))
def pullDummy(userId):
    return ["goofy", [[2, "hello"], [3, "nice to meet you"], [4, "how you doing"], [5, "trump's mad! @mickey"], [6, "#trump"], [7, "I want strumpets"]]]

def pullInfo(userId):
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
            sn = tweet['user']['screen_name']
            tweets.append([tweet['id'], tweet['text']])

    except TwitterSearchException as e:
        print(e)

    finally:
        return sn, tweets

def queryCallback(current_ts_instance): # accepts ONE argument: an instance of TwitterSearch
    queries, tweets_seen = current_ts_instance.get_statistics()
    if queries > 0 and (queries % 5) == 0: # trigger delay every 5th query
        time.sleep(60) # sleep for 60 seconds

# decide if tweet is related to Trump by searching for keyword ".*trump.*" within tweet text
def isTrumpTweet(tweet):
    return (re.search(TRUMP_PATTERN, tweet[1]) is not None)

# search tweet text for screen_names by matching with " @([a-zA-Z0-9_]+)" (/1 = screen_name)
def getMentioned(tweet):
    return re.findall(MENTIONED_PATTERN, tweet[1])

# search tweet text for hashtags
# disregards those that are cut off
def getHashtags(tweet):
    return re.findall(HASHTAG_PATTERN, tweet[1])




if __name__ == '__main__':
    main()