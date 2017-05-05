#!/usr/bin/python2.7

#
# THIS SCRIPT SHOULD NOT BE NECESSARY! 
# Created for one-time use to convert the original list of lists format to list of dicts
# so that Megumi didn't have to count list items every time she added or removed things
#


import codecs
import re
import json
import os
import argparse
from snifferCommons import *

def main():

#   input:  allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...], 
#           nontrumpHistories = [(user 1 id, [tweet 1 text, tweet 2 text, ...]), ...],
#           users = [(user 1 id, user 1 screen_name, user alignment, user class)]

    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()

    trumpJson, historyJson, userJson = generateOldIntermediateFileNames(args.baseFileName)

    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweetLists = json.load(file)

    with codecs.open(historyJson, "r", "utf-8") as file:
        nontrumpHistoryLists = json.load(file)

    with codecs.open(userJson, "r", "utf-8") as file:
        userLists = json.load(file)


    # change each item to dictionary instead of list
    allTrumpTweetDicts = [ tweetListToDict(tweet) for tweet in allTrumpTweetLists ]
    nontrumpHistoryDicts = [ historyListToDict(history) for history in nontrumpHistoryLists ]
    userDicts = [ userListToDict(user) for user in userLists ]

    # trumpJson, historyJson, userJson = generateNewIntermediateFileNames(baseName)

    with codecs.open(trumpJson, "w+", "utf-8") as file:
        json.dump(allTrumpTweetDicts, file, indent=4, separators=(',', ': '))

    with codecs.open(historyJson, "w+", "utf-8") as file:
        json.dump(nontrumpHistoryDicts, file, indent=4, separators=(',', ': '))

    with codecs.open(userJson, "w+", "utf-8") as file:
        json.dump(userDicts, file, indent=4, separators=(',', ': '))

def tweetListToDict(tweetList):
    tweetDict = dict()

    tweetDict['tweetId'] = tweetList[0]
    tweetDict['text'] = tweetList[1]
    tweetDict['userId'] = tweetList[2]
    tweetDict['mentionedScreenNames'] = tweetList[3]
    tweetDict['hashtags'] = tweetList[4]
    tweetDict['class'] = tweetList[5]

    return tweetDict

def historyListToDict(historyList):
    historyDict = dict()

    historyDict['userId'] = historyList[0]
    historyDict['tweetTexts'] = historyList[1]

    return historyDict

def userListToDict(userList):
    userDict = dict()

    userDict['userId'] = userList[0]
    userDict['screenName'] = userList[1]
    userDict['alignment'] = userList[2]
    userDict['class'] = userList[3]

    return userDict

if __name__ == '__main__':
    main()