#!/usr/bin/python2.7

import codecs
import re
import json
import os
import argparse

ELLIPSES = u'\u2026' # UTF-8 for '...' character

UNK = 0 
PRO = 1 
ANT = -1

LEFT = 0
NEUT = 1
RIGHT = 2

MINIMUM_TWEET_COUNT = 4   # DP: find count in tweets: if total < 100, print and next user
MINIMUM_NONTRUMP_PERC = 0.4 # DP: if nontrump / total < 40%, print and next user
MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY = 1 # DP: let's say hashtag count > 100 is significant

# FILE_NAME = "trump_all_dedup"
FILE_NAME = "trump_sample"

param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))

HASHTAG_FILE_NAME = "classifiedHashtags"


def main():

#   input:  allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...], 
#           nontrumpHistories = [(user 1 id, [tweet 1 text, tweet 2 text, ...]), ...],
#           users = [(user 1 id, user 1 screen_name, user alignment, user class)]

    parser = argparse.ArgumentParser()
    parser.add_argument('fileNumber', help="file number if split file, 0 if not")
    args = parser.parse_args()

    global FILE_NAME

    if int(args.fileNumber) != 0:
        FILE_NAME += args.fileNumber


    with codecs.open(FILE_NAME + "_trumpTweets" + param + ".txt", "r", "utf-8") as file:
        allTrumpTweets = json.load(file)

    with codecs.open(FILE_NAME + "_histories" + param + ".txt", "r", "utf-8") as file:
        nontrumpHistories = json.load(file)

    with codecs.open(FILE_NAME + "_profiles" + param + ".txt", "r", "utf-8") as file:
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
        history = next(y for x, y in nontrumpHistories if x == user[0])[0]
        categorizedHistories.append((user[3], history)) # only user class and nontrump history

    with codecs.open(FILE_NAME + "_dataset" + param + ".txt", "w+", "utf-8") as file:
        json.dump(categorizedHistories, file, indent=4, separators=(',', ': '))

# output: 
#   categorizedHistories = [(user 1 class, [tweet 1 text, tweet 2 text, ...]), (user 2 class, [tweet 1 text, ...]), ...]


def cleanHashtags(tweets):
    for tweet in tweets:
        hashtags = tweet[4]
        cleaned = []
        for hashtag in hashtags:
            if hashtag.find(ELLIPSES) == -1:
                for i, c in enumerate(hashtag):
                    cleantag = hashtag
                    if not c.isalnum():
                        cleantag = cleantag[:i] + cleantag[(i + 1):]
                cleaned.append(cleantag)

        tweet[4] = cleaned
    return tweets

# CHC: maybe consider later doing something with cut-off hashtags?
def createHashtagDict(tweets):
    # hashtagDict = {hashtag: (frequency, {other1: joint_frequency, ...}, hashtag class), ...} 
    hashtagDict = dict()
    # print "tweets is", tweets
    for tweet in tweets:
        hashtags = tweet[4]
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
    filename = HASHTAG_FILE_NAME + ".json"
    if os.path.isfile(filename):
        with codecs.open(filename, "r", "utf-8") as file:
            classifiedHashtags = json.load(file)
        for classifiedHashtag in classifiedHashtags:
            hashtagDict[classifiedHashtag][2] = classifiedHashtags[classifiedHashtag]
        # assign same class as hashtags that appear alongside each other
        hashtagDict = shareHashtagClasses(hashtagDict)

    # create list of common unclassified hashtags
    significantHashtags = list()
    for hashtag in hashtagDict:
        tagTuple = hashtagDict[hashtag]
        if tagTuple[2] == NEUT and tagTuple[0] >= MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY:
        # and not any(i in tagTuple[1] for i in significantHashtags):
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
                hashtagDict[h][2] = PRO
                hashtagDict = shareHashtagClasses(hashtagDict)
            elif op == "-":
                hashtagDict[h][2] = ANT
                hashtagDict = shareHashtagClasses(hashtagDict)

    with codecs.open(filename, "w+", "utf-8") as file:
        json.dump(hashtagDict, file, indent=4, separators=(',', ': '))

    return { h: hashtagDict[h][2] for h in hashtagDict } # return dict that gives hashtags and assigned class


def shareHashtagClasses(hashtagDict):
    new_assignment = False
    while new_assignment:
        new_assignment = False
        for hashtag in hashtagDict:
            hashtagDict = shareHashtagClass(hashtag, hashtagDict)
    return hashtagDict

def shareHashtagClass(hashtag, hashtagDict):
    tagTuple = hashtagDict[hashtag]
    if tagTuple[2] != NEUT:
        hashtags = hashtagDict[hashtag][1]
        for h in hashtags:
            if hashtagDict[h][2] == NEUT:
                hashtagDict[h][2] = tagTuple[2]
                new_assignment = True
    return hashtagDict

# if categorized, change user's alignment distribution: (+1, -1, +0) for anti, (+0, -1, +1) for pro
def primaryAssignment(tweet, hashtagDict):
    # hashtagDict = {hashtag: hashtag class, ...} 
    tweet[5] = vote(tweet[4], hashtagDict)
    return tweet


def auxiliaryAssignment(tweet, users):
    users = { user[1]: user[3] for user in users }

    if tweet[5] == NEUT:
        tweet[5] = vote(tweet[3], users)
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
    votes = user[2]
    for tweet in tweetList: # TODO: faster if I make this a dict with { user id: [tweet1, tweet2, ...] , ... }
        if tweet[2] == user[0]:
            if tweet[5] == PRO:
                votes[RIGHT] += 1
                votes[NEUT] -= 1
            elif tweet[5] == ANT:
                votes[LEFT] += 1
                votes[NEUT] -= 1
    

    if votes[RIGHT] > votes[LEFT]:
        tweet[5] = PRO
    elif votes[RIGHT] < votes[LEFT]:
        tweet[5] = ANT
    else:
        tweet[5] = NEUT

    user[2] = votes
    return user


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