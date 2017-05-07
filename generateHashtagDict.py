#!/usr/bin/env python2.7
 
import codecs
import json
import argparse
import os
from snifferCommons import *
import operator

# do need to look at all users at once? only when using to vote for tweets, so search through each file then
#       deduping was done jankily, make sure deduping is included in flow of scripts -> rawSplit.py
# do need to look at all user histories at once? search through each file by user id when necesary
#   reformat histories to be dict of userId => [texts]
#            users to be     dict of userId => [screen_name, alignment, class]
# do need to look at all trump tweets at once? loop through files when voting via hashtags, when voting for users, when auxiliary voting via mentioned users

# all trumpTweet dicts -> produce single hashtag dictionary
# all trumpTweet dicts + hashtag dictionary -> classify tweets (primary)
# all trumpTweet dicts + user dicts -> classify users
# all trumpTweet dicts + user dicts -> classify tweets (auxiliary)
# all trumpTweet dicts + user dicts -> classify users
# all user dicts + history dicts -> produce dataset

def giveCount(hashtag, hashtagDict):
    return 


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    parser.add_argument('lastPartialNumber', help="enter the last partial file with any leading zeros")
    args = parser.parse_args()

    baseName = args.baseFileName

    # for now ignore case of whole file, best is to just update format from start so this script is unnecessary
    endingPartialNumber = int(args.lastPartialNumber)
    ordinal = "{" + ":0{}d".format(len(args.lastPartialNumber)) + "}"

    hashtagDict = dict()

    currentNum = 1 
    while currentNum <= endingPartialNumber: # for now, only allow creation of hashtagDicts for split files
        topicJson = generateOldIntermediateFileNames(baseName + ordinal.format(currentNum))[0]
        # print "Searching for file {}...".format(topicJson)
        if os.path.exists(topicJson):
            print "Reading from {}...".format(topicJson)
            with codecs.open(topicJson, "r", "utf-8") as file:
                allTopicTweets = json.load(file)
 
            hashtagDict = enterHashtagEntries(hashtagDict, allTopicTweets)
        currentNum += 1

    totalCount = len(hashtagDict)
    print "\nNumber of hashtags in the dict is {}".format(totalCount)
 
    classify = True
    hashtagFreq = MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY

    # create list of hashtags sorted by frequency
    sortedByFreq = sorted(hashtagDict.keys(), key=lambda x: hashtagDict[x]["count"], reverse=True)

    while classify:
        significantHashtags = list()    # create list of common hashtags
        print ""
        for hashtag in sortedByFreq:
            if MAXIMUM_SIGNIFICANT_HASHTAGS > len(significantHashtags):
                tagTuple = hashtagDict[hashtag]
                # check if any alignment votes to see if need to assign
                if sum(tagTuple["alignment"]) == 0 and \
                tagTuple["count"] >= hashtagFreq and \
                tagTuple["noComment"] == False and \
                not any(i in tagTuple["associatedTags"] for i in significantHashtags):
                    print "Found significant tag {} (count: {})".format(hashtag, tagTuple["count"])
                    significantHashtags.append(hashtag)
                # else:
                    # print "-----Tag \"{}\" not significant: only {} instances".format(hashtag, hashtagDict[hashtag]["count"])

        if len(significantHashtags) == 0 and hashtagFreq > 0:
            prompt = "No hashtags of frequency >={} left to classify! Would you like to classify hashtags of frequency == {}? (y/n) ".format(hashtagFreq, hashtagFreq / 2)
            stopAsking = False
            while not stopAsking:
                op = raw_input(prompt.encode("utf-8"))
                if op != "":
                    op = op.lower()[0]
                if op == "n":
                    stopAsking = True
                    classify = False
                elif op == "y":
                    stopAsking = True
                    hashtagFreq /= 2     
        else:
            print "==================================="
            
            hashtagNum = str(len(significantHashtags)) 
            for i, h in enumerate(significantHashtags):
                if (h.find(ELLIPSES) == -1):
                    prompt = "#{} of {} - #{}: ".format(i + 1, hashtagNum, h)
                    op = raw_input(prompt.encode("utf-8"))
                    if op == "+":
                        hashtagDict[h]["alignment"][RIGHT] += USER_SPECIFIED_CLASS_WEIGHT
                        hashtagDict = shareHashtagAlignments(h, RIGHT, hashtagDict)
                    elif op == "-":
                        hashtagDict[h]["alignment"][LEFT] += USER_SPECIFIED_CLASS_WEIGHT
                        hashtagDict = shareHashtagAlignments(h, LEFT, hashtagDict)
                    elif op == "":
                        hashtagDict[h]["noComment"] = True

            hashtagDict, reassignments = assignHashtagClasses(hashtagDict)

            printReassignments(reassignments)

            classifiedCount = 0
            for i in hashtagDict:
                if hashtagDict[i]["class"] != UNK:
                    classifiedCount += 1

            print "\nNumber of unclassified hashtags:", totalCount - classifiedCount
            print "Number of classified hashtags: {:d} ({:.1%})".format(classifiedCount, classifiedCount/float(totalCount))
            prompt = "Would you like to classify another batch of up to {} more hashtags? (y/n) ".format(MAXIMUM_SIGNIFICANT_HASHTAGS)
            
            stopAsking = False
            while not stopAsking:
                op = raw_input(prompt.encode("utf-8"))
                if op != "":
                    op = op.lower()[0]
                if op == "n":
                    classify = False
                    stopAsking = True
                elif op == "y":
                    stopAsking = True

    print "Hashtag classification complete"

    classifiedHashtags = { h: hashtagDict[h]["class"] for h in hashtagDict } # return dict that gives hashtags and assigned class

    with codecs.open(generateHashtagDictFileName(baseName), "w+", "utf-8") as file:
        json.dump(hashtagDict, file, indent=4, separators=(',', ': '))

# CHC: maybe consider later doing something with cut-off hashtags?
# create dict that gives hashtags, their frequencies, their joint frequencies with other hashtags, and assigned class 
def enterHashtagEntries(hashtagDict, tweets):
     # hashtagDict = {hashtag: (frequency, {other1: joint_frequency, ...}, hashtag class), ...} 
    for tweet in tweets:
        # print "Processing tweet id {}...".format(tweet["tweetId"])
        hashtags = tweet["hashtags"]
        for i, hashtag in enumerate(hashtags):
            hashtag = hashtag.lower()
            if hashtag != "":
                if hashtag not in hashtagDict:
                    hashtagDict[hashtag] = {
                        "count": 1,
                        "associatedTags": dict(),
                        "alignment": [0, 0, 0],
                        "noComment": False, # allows user to skip voting on if unsure
                        "class": UNK
                    }
                else:
                    hashtagDict[hashtag]["count"] += 1
                others = hashtags[:i] + hashtags[(i + 1):] # take the list of other hashtags
                otherDict = hashtagDict[hashtag]["associatedTags"]
                for other in others: 
                    other = other.lower()
                    if other != "":
                        if other not in otherDict: # add other hashtags to associated hashtags or increment
                             otherDict[other] = 1
                        else:
                             otherDict[other] += 1
                hashtagDict[hashtag]["associatedTags"] = otherDict
    return hashtagDict


# add to alignment and find the highest class
# if tie, choose unk if tie involves both pro and anti, else choose non-unk if tied with unk
# alignment votes are only shared with immediately associated hashtags to avoid extrapolating
def shareHashtagAlignments(h, voteDirection, hashtagDict):
    for hashtag in hashtagDict[h]["associatedTags"]:
        hashtagDict[hashtag]["alignment"][voteDirection] += 1
    return hashtagDict

# could be informative to compare how many class reassignments occurred in each direction
def assignHashtagClasses(hashtagDict):
    reassignments = [
        [   
            0,
            0,
            0
        ], # LEFT
        [
            0,
            0,
            0
        ], # NEUT
        [
            0,
            0,
            0
        ]  # RIGHT
    ]
    origDir = NEUT

    for hashtag in hashtagDict:
        votes = hashtagDict[hashtag]["alignment"]
        origClass = hashtagDict[hashtag]["class"] + 1 # really need to consolidate PRO/UNK/ANT and LEFT/NEUT/RIGHT
        if votes[RIGHT] > votes[LEFT]:
            hashtagDict[hashtag]["class"] = PRO
            reassignments[origClass][RIGHT] += 1
        elif votes[LEFT] > votes[RIGHT]:
            hashtagDict[hashtag]["class"] = ANT
            reassignments[origClass][LEFT] += 1
        else:
            hashtagDict[hashtag]["class"] = UNK
            reassignments[origClass][NEUT] += 1

    return hashtagDict, reassignments

def printReassignments(reassignments):
    print ""
    print "Stayed Anti:", reassignments[LEFT][LEFT]
    print "Anti -> Neutral:", reassignments[LEFT][NEUT]
    print "Anti -> Pro:", reassignments[LEFT][RIGHT]

    print "Neutral -> Anti:", reassignments[NEUT][LEFT]
    print "Stayed Neutral:", reassignments[NEUT][NEUT]
    print "Neutral -> Pro:", reassignments[NEUT][RIGHT]

    print "Pro -> Anti:", reassignments[RIGHT][LEFT]
    print "Pro -> Neutral:", reassignments[RIGHT][NEUT]
    print "Stayed Pro:", reassignments[RIGHT][RIGHT]


if __name__ == '__main__':
    main()
