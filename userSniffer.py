#!/usr/bin/python2.7

from TwitterSearch import *
import codecs
import time
import re
import json
import argparse
from twitterSecrets import twitterSecrets
from snifferCommons import *

TRUMP_PATTERN = re.compile(r"(\W|^){}(\W|$)".format(TOPIC), re.IGNORECASE)
MENTIONED_PATTERN = re.compile(r"@(\w+)")
HASHTAG_PATTERN = re.compile(r"#([\w']+)")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    parser.add_argument('fileNumber', help="if no partial file number associated, enter 0")
    args = parser.parse_args()

    global TWITTER_SECRET
    baseName = args.baseFileName

    if int(args.fileNumber) != 0:
        baseName += args.fileNumber
        TWITTER_SECRET = twitterSecrets[(int(args.fileNumber) - 1) % len(twitterSecrets)]
    else:
        TWITTER_SECRET = twitterSecrets[0]

    with codecs.open("{}.txt".format(baseName), "r", "utf-8") as file:
        content = file.readlines()

    foundTweets = []
    uniqueUsers = []

    for line in content:
        x = line.split(",", 1)
        foundTweets.append(x)
        if x[0] not in uniqueUsers:
            uniqueUsers.append(x[0])

    foundLen = str(len(foundTweets))
    print "{} unique users initially present in dataset of {} tweets\n".format(len(uniqueUsers), foundLen)

    allTrumpTweets = []
    nontopicHistories = []
    profiles = []

    for n, uu in enumerate(uniqueUsers):
        tweets = []
        trump = []
        nontopic = []

        # need int id to pull by user ids
        uu = int(uu)

        # screenName, tweets = pullDummy(uu)
        screenName, tweets = pullInfo(uu)
        tweetLen = len(tweets)
        
        if tweetLen < MINIMUM_TWEET_COUNT:
            if tweetLen > 0:
                print "User #{} (id:{}) removed because only {} tweets are available\n".format(n + 1, uu, tweetLen)
            else:
                print "User #{} (id:{}) removed because no authored tweets were retrieved\n".format(n + 1, uu)
            continue

        for tweet in tweets:
            if isTrumpTweet(tweet):
                tweetDict = dict()
                tweetDict['tweetId'] = tweet['id']
                tweetDict['text'] = tweet['text']
                tweetDict['userId'] = uu
                tweetDict['mentionedScreenNames'] = getMentioned(tweet)
                tweetDict['hashtags'] = getHashtags(tweet)
                tweetDict['class'] = UNK
                trump.append(tweetDict)
            else:
                nontopic.append(tweet['text'])

        nontopicLen = len(nontopic)
        nontopicPerc = nontopicLen / float(tweetLen)
        if nontopicPerc < MINIMUM_NONTOPIC_PERC:
            print "User #{} (id:{}) removed because only {}% of tweet history does not mention {}\n".format(n + 1, uu, "{0:.2f}".format(nontopicPerc * 100), TOPIC)
            continue

        allTrumpTweets.extend(trump)

        historyDict = dict()
        historyDict['userId'] = uu
        historyDict['tweetTexts'] = nontopic
        nontopicHistories.append(historyDict)

        trumpLen = len(trump)
        userDict = dict()
        userDict['userId'] = uu
        userDict['screenName'] = screenName
        userDict['alignment'] = [0, trumpLen, 0]
        userDict['class'] = UNK
        profiles.append(userDict)

        print "User #{} of {}:".format(n + 1, foundLen)
        print "ID:", uu
        print "Screen name:", screenName
        print trumpLen, "trump tweets"
        print "{} tweets unrelated to {}\n".format(nontopicLen, TOPIC)

        time.sleep(15) # include delay between every user

    trumpJson, historyJson, userJson = generateOldIntermediateFileNames(baseName)

    with codecs.open(trumpJson, "w+", "utf-8") as file:
        json.dump(allTrumpTweets, file, indent=4, separators=(',', ': '))

    with codecs.open(historyJson, "w+", "utf-8") as file:
        json.dump(nontopicHistories, file, indent=4, separators=(',', ': '))

    with codecs.open(userJson, "w+", "utf-8") as file:
        json.dump(profiles, file, indent=4, separators=(',', ': '))


# output:   allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...], 
#           nontopicHistories = [(user 1 id, [tweet 1 text, tweet 2 text, ...]), ...],
#           profiles = [(user 1 id, user 1 screen_name, user alignment, user class)]

# pull tweet history and screen_name from last 7 days: (screen_name, list of dependent tweet tuple (tweet id, text))
def pullDummy(userId):
    return "goofy", [{"id":2, "text":"hello"}, {"id":3, "text":"nice to meet you"}, {"id":4, "text":"how you doing"}, {"id":5, "text":"trump's mad! @mickey"}, {"id":6, "text":"#trump"}, {"id":7, "text":"I want strumpets"}]

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
            tweetDict = dict()
            tweetDict['id'] = tweet['id']
            tweetDict['text'] = tweet['text']
            tweets.append(tweetDict)

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
    return (re.search(TRUMP_PATTERN, tweet["text"]) is not None)

# search tweet text for screen_names by matching with " @([a-zA-Z0-9_]+)" (/1 = screen_name)
def getMentioned(tweet):
    return re.findall(MENTIONED_PATTERN, tweet["text"])

# search tweet text for hashtags
# disregards those that are cut off
def getHashtags(tweet):
    return re.findall(HASHTAG_PATTERN, tweet["text"])




if __name__ == '__main__':
    main()