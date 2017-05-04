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
    parser.add_argument('fileNumber', help="file number if split file, 0 if not")
    args = parser.parse_args()

    baseName = FILE_NAME

    if int(args.fileNumber) != 0:
        baseName += args.fileNumber

    trumpJson, historyJson, userJson = generateIntermediateFileNames(baseName)

    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweetLists = json.load(file)

    with codecs.open(historyJson, "r", "utf-8") as file:
        nontrumpHistoryLists = json.load(file)

    with codecs.open(userJson, "r", "utf-8") as file:
        userLists = json.load(file)


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
        history = next(y for x, y in nontrumpHistories if x == user[0])[0]
        categorizedHistories.append((user[4], history)) # only user class and nontrump history

    outputJson = generateOutputFileName()

    with codecs.open(outputJson, "w+", "utf-8") as file:
        json.dump(categorizedHistories, file, indent=4, separators=(',', ': '))

# output: 
#   categorizedHistories = [(user 1 class, [tweet 1 text, tweet 2 text, ...]), (user 2 class, [tweet 1 text, ...]), ...]


# create dict that gives hashtags, their frequencies, their joint frequencies with other hashtags, and assigned class 
# CHC: maybe consider later doing something with cut-off ones?
def createHashtagDict(tweets):
    # hashtagDict = {hashtag: (frequency, {other1: joint_frequency, ...}, hashtag class), ...} 
    for tweet in tweets:
        hashtags = tweet[hashtagIndex]
        for i, hashtag in enumerate(hashtags):
            hashtag = hashtag.lower()
            if hashtag not in hashtagDict:
                hashtagDict[hashtag] = [ 1, dict(), NEUT ]
            else:
                hashtagDict[hashtag][0] += 1
            others = hashtags[:i] + hashtags[(i + 1):]
            otherDict = hashtagDict[hashtag][1]
            for other in others:
                if other not in otherDict:
                    otherDict[other] = 1
                else:
                    otherDict[other] += 1
            hashtagDict[hashtag][1] = otherDict

    # read in currently available assignments from file and assign if possible
    with codecs.open("classifiedHashtags.json", "r", "utf-8") as file:
        classifiedHashtags = json.load(file)
    for classifiedHashtag in classifiedHashtags:
        hashtagDict[classifiedHashtag[0]][2] = classifiedHashtag[1]

    # assign same class as hashtags that appear alongside each other and create list of those that 
    for hashtag in hashtagDict:
        tagTuple = hashtagDict[hashtag]
        if tagTuple[2] != NEUT:
            shareHashtagClass(tag, hashtagDict)
        elif tagTuple[0] >= MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY and not any(i in tagTuple[1] for i in significantHashtags):
            significantHashtags.append(hashtag)
    print "List of major hashtags"
    print "======================"
    hashtagNum = str(len(significantHashtags))
    for i, h in enumerate(significantHashtags):
        prompt = "#" + str(i) + " of " + hashtagNum + " - #" + h + ": "
        op = raw_input(prompt)
        if op == "+":
            hashtagDict[h][2] = PRO
            shareHashtagClass(tag, hashtagDict)
        elif op == "-":
            hashtagDict[h][2] = ANT
            shareHashtagClass(tag, hashtagDict)


def shareHashtagClass(tag, hashtagDict):
    hashtags = hashtagDict[tag][1]
    for h in hashtags:
        if hashtagDict[h][2] == NEUT:
            hashtagDict[h][2] = tagTuple[2]

# if categorized, change user's alignment distribution: (+1, -1, +0) for anti, (+0, -1, +1) for pro
# DP: find common phrases/hashtags and manually assign category to those (primary sort)
def primaryAssignment(tweet, hashtagList):
    return []

### Primary: Assigning tweet categories
#       look up any hashtags in hashtagList
#       loop through and assign same value as highest joint_frequency hashtag if nonzero value
#       keep looping until no more new assignments made
#
#       empty tuple votes
#       for screen_name:
#           search for screen_name in uuusers
#           DP: if user found and user assigned to a category, modify votes to (+1, +0, +0) or (+0, +0, +1)
#       results = R - L
#       if results > 0:
#           tweet category=pro
#       elif results < 0:
#           tweet category=anti
###

def userClassAssignment(users):
    return []

### Assigning user categories (refrain)
# for uu in users:
#   DP: Allow unassigned to be an end category or prioritize pro/anti? For now, let it be a category
#   empty tuple votes
#   results = R - L
#   if results > 0 and R > C:
#       user category=pro
#   elif results < 0 and L > C:
#       user category=anti
###

def auxiliaryAssignment(tweet):
    return []

### Auxiliary: Assigning tweet categories
# for each unassigned trump tweet:
#   if unassigned tweet mentions any screen_name(s):
#       empty tuple votes
#       for screen_name:
#           search for screen_name in uuusers
#           DP: if user found and user assigned to a category, modify votes to (+1, +0, +0) or (+0, +0, +1)
#       results = R - L
#       if results > 0:
#           tweet category=pro
#       elif results < 0:
#           tweet category=anti
###

def printClassDistribution(list, description):
    distribution = [0, 0, 0]

    last = len(list[0]) - 1

    for item in list:
        if item[last] == ANT:
            distribution[LEFT] += 1
        elif item[last] == PRO:
            distribution[RIGHT] += 1
        else:
            distribution[NEUT] += 1

    print "Class distribution of", description, ":"
    print distribution[LEFT], distribution[NEUT], distribution[RIGHT]

if __name__ == '__main__':
    main()