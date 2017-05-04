#!/usr/bin/python2.7

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

    baseName = args.baseFileName

    trumpJson, historyJson, userJson = generateOldIntermediateFileNames(baseName)

    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweets = json.load(file)

    with codecs.open(historyJson, "r", "utf-8") as file:
        nontrumpHistories = json.load(file)

    with codecs.open(userJson, "r", "utf-8") as file:
        users = json.load(file)


    # clean up only necessary for first few files
    allTrumpTweets = cleanHashtags(allTrumpTweets)

    allHashtags = createHashtagDict(allTrumpTweets)

    allTrumpTweets = [ primaryAssignment(tweet, allHashtags) for tweet in allTrumpTweets ]
    printClassDistribution(allTrumpTweets, "trump tweets")

    users = [ userClassAssignment(user, allTrumpTweets) for user in users ]
    printClassDistribution(users, "users")

    allTrumpTweets = [ auxiliaryAssignment(tweet, users) for tweet in allTrumpTweets ]
    printClassDistribution(allTrumpTweets, "trump tweets")

    users = [ userClassAssignment(user, allTrumpTweets) for user in users ]
    printClassDistribution(users, "users")

    categorizedHistories = []

    for user in users:
        history = []
        for item in nontrumpHistories:
            if item["userId"] == user["userId"]:
                history = item["tweetTexts"]
                break
        categorizedHistories.append({
            "class": user["class"],
            "tweets": history
        }) # only user class and nontrump history

    with codecs.open(generateOutputFileName(baseName), "w+", "utf-8") as file:
        json.dump(categorizedHistories, file, indent=4, separators=(',', ': '))

# output: 
#   categorizedHistories = [(user 1 class, [tweet 1 text, tweet 2 text, ...]), (user 2 class, [tweet 1 text, ...]), ...]


def cleanHashtags(tweets):
    for tweet in tweets:
        hashtags = tweet["hashtags"]
        cleaned = []
        for hashtag in hashtags:
            if hashtag.find(ELLIPSES) == -1:
                for i, c in enumerate(hashtag):
                    cleantag = hashtag
                    if not c.isalnum():
                        cleantag = cleantag[:i] + cleantag[(i + 1):]
                cleaned.append(cleantag)

        tweet["hashtags"] = cleaned
    return tweets

# CHC: maybe consider later doing something with cut-off hashtags?
def createHashtagDict(tweets):
    # hashtagDict = {hashtag: (frequency, {other1: joint_frequency, ...}, hashtag class), ...} 
    hashtagDict = dict()
    # print "tweets is", tweets
    for tweet in tweets:
        hashtags = tweet["hashtags"]
        for i, hashtag in enumerate(hashtags):
            hashtag = hashtag.lower()
            if hashtag not in hashtagDict:
                hashtagDict[hashtag] = {
                    "count": 1,
                    "associatedTags": dict(),
                    "alignment": list(),
                    "class": NEUT
                }
            else:
                hashtagDict[hashtag]["count"] += 1
            others = hashtags[:i] + hashtags[(i + 1):] # take the list of other hashtags
            otherDict = hashtagDict[hashtag]["associatedTags"]
            for other in others: 
                if other not in otherDict: # add other hashtags to associated hashtags or increment
                    otherDict[other] = 1
                else:
                    otherDict[other] += 1
            hashtagDict[hashtag]["associatedTags"] = otherDict

    # read in currently available assignments from file and assign if possible
    filename = HASHTAG_FILE_NAME
    if os.path.isfile(filename):
        with codecs.open(filename, "r", "utf-8") as file:
            classifiedHashtags = json.load(file)
        for classifiedHashtag in classifiedHashtags:
            hashtagDict[classifiedHashtag]["class"] = classifiedHashtags[classifiedHashtag]
        # increment alignment for classes of associated hashtags
        hashtagDict = shareHashtagAlignments(hashtagDict)

    # create list of common unclassified hashtags
    significantHashtags = list()
    for hashtag in hashtagDict:
        tagTuple = hashtagDict[hashtag]
        if tagTuple["class"] == NEUT and \
        tagTuple["count"] >= MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY and \
        not any(i in tagTuple["associatedTags"] for i in significantHashtags):
                significantHashtags.append(hashtag)

    hashtagNum = len(significantHashtags)
    if hashtagNum:
        print "List of major unclassified hashtags"
        print "==================================="
        
    hashtagNum = str(len(significantHashtags)) 
    for i, h in enumerate(significantHashtags):
        if (h.find(ELLIPSES) == -1):
            prompt = "#" + str(i) + " of " + hashtagNum + " - #" + h + ": "
            op = raw_input(prompt.encode("utf-8"))
            if op == "+":
                hashtagDict[h]["class"] = PRO
                hashtagDict = shareHashtagAlignments(hashtagDict)
            elif op == "-":
                hashtagDict[h]["class"] = ANT
                hashtagDict = shareHashtagAlignments(hashtagDict)

    with codecs.open(filename, "w+", "utf-8") as file:
        json.dump(hashtagDict, file, indent=4, separators=(',', ': '))

    return { h: hashtagDict[h]["class"] for h in hashtagDict } # return dict that gives hashtags and assigned class


# add to alignment and find the highest class
# if tie, choose neut if tie involves both pro and anti, else choose non-neut if tied with neut
# not the most efficient because it reassigns the class every time alignment is touched, but OK
def shareHashtagAlignments(hashtagDict):
    for hashtag in hashtagDict:
        tagTuple = hashtagDict[hashtag]
        if tagTuple["class"] != NEUT:
            hashtags = tagTuple["associatedTags"]
            hashtagDict[h]["alignment"] = list()
            for h in hashtags:
                if tagTuple["class"] == ANT:
                    hashtagDict[h]["alignment"][LEFT] += 1
                elif tagTuple["class"] == PRO:
                    hashtagDict[h]["alignment"][RIGHT] += 1
    for hashtag in hashtagDict:
        votes = hashtagDict[hashtag]["alignment"]
        if votes[RIGHT] > votes[LEFT]:
            hashtagDict[hashtag]["class"] = PRO
        elif votes[LEFT] > votes[RIGHT]:
            hashtagDict[hashtag]["class"] = ANT
        else:
            hashtagDict[hashtag]["class"] = NEUT
    return hashtagDict


# if categorized, change user's alignment distribution: (+1, -1, +0) for anti, (+0, -1, +1) for pro
def primaryAssignment(tweet, hashtagDict):
    # hashtagDict = {hashtag: hashtag class, ...} 
    tweet["class"] = vote(tweet["hashtags"], hashtagDict)
    return tweet


def auxiliaryAssignment(tweet, users):
    users = { user["screenName"]: user["class"] for user in users }

    if tweet["class"] == NEUT:
        tweet["class"] = vote(tweet["mentionedScreenNames"], users)
    return tweet


def vote(voters, voterDict):
    votes = [0, 0, 0]
    for voter in voters:
        voter = voter.lower()
        if voter in voterDict:
            if voterDict[voter] == PRO:
                votes[RIGHT] += 1
            elif voterDict[voter] == ANT:
                votes[LEFT] += 1
            else:
                votes[NEUT] += 1

    if votes[RIGHT] > votes[LEFT]:
        return PRO
    elif votes[RIGHT] < votes[LEFT]:
        return ANT
    else:
        return NEUT

# DP: Allow unassigned to be an end category or prioritize pro/anti? For now, let it be a category
def userClassAssignment(user, tweetList):
    # allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...]
    votes = user["alignment"]
    for tweet in tweetList: # TODO: faster if I make this a dict with { user id: [tweet1, tweet2, ...] , ... }
        if tweet["userId"] == user["userId"]:
            if tweet["class"] == PRO:
                votes[RIGHT] += 1
                votes[NEUT] -= 1
            elif tweet["class"] == ANT:
                votes[LEFT] += 1
                votes[NEUT] -= 1
    

    if votes[RIGHT] > votes[LEFT]:
        tweet["class"] = PRO
    elif votes[RIGHT] < votes[LEFT]:
        tweet["class"] = ANT
    else:
        tweet["class"] = NEUT

    user["alignment"] = votes
    return user


def printClassDistribution(items, description):
    distribution = [0, 0, 0]

    for item in items:
        if item["class"] == ANT:
            distribution[LEFT] += 1
        elif item["class"] == PRO:
            distribution[RIGHT] += 1
        else:
            distribution[NEUT] += 1

    print "Class distribution of", description, ":"
    print distribution[LEFT], distribution[NEUT], distribution[RIGHT]

if __name__ == '__main__':
    main()