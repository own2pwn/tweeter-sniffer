#!/usr/bin/env python2.7
 
import codecs
import json
import argparse
from snifferCommons import *


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()
 
    baseName = args.baseFileName

    trumpJson, historyJson, userJson = generateOldIntermediateFileNames(baseName)
 
    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweets = json.load(file)
 
    hashtagDict = dict()
    hashtagDict = enterHashtagEntries(hashtagDict, allTrumpTweets)

    totalCount = len(hashtagDict)
 
    classify = True
    hashtagFreq = MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY
    while classify:
        # create list of common hashtags
        significantHashtags = list()
        sigCount = 0
        produceSig = True

        while produceSig:
            for hashtag in hashtagDict:
                while MAXIMUM_SIGNIFICANT_HASHTAGS > sigCount:
                    tagTuple = hashtagDict[hashtag]
                    # check if any alignment votes to see if need to assign
                    if sum(tagTuple["alignment"]) != 0 and \
                    tagTuple["count"] >= hashtagFreq and \
                    not any(i in tagTuple["associatedTags"] for i in significantHashtags):
                        significantHashtags.append(hashtag)
                        sigCount += 1

            if sigCount == 0:
                prompt = "No more hashtags of frequency >=", hashtagFreq + \
                "! Would you like to classify hashtags of frequency", hashtagFreq / 2 + \
                "? (y/n) "
                stopAsking = False
                while stopAsking == False:
                    op = raw_input(prompt.encode("utf-8"))
                    answer = op.lower()[0]
                    if answer == "n":
                        classify = False
                        stopAsking = True
                    elif answer == "y":
                        hashtagFreq /= 2

            else:
                print "List of major unclassified hashtags"
                print "==================================="
                
                hashtagNum = str(len(significantHashtags)) 
                for i, h in enumerate(significantHashtags):
                    if (h.find(ELLIPSES) == -1):
                        prompt = "#" + str(i) + " of " + hashtagNum + " - #" + h + ": "
                        op = raw_input(prompt.encode("utf-8"))
                        if op == "+":
                            hashtagDict[h]["alignment"][RIGHT] += USER_SPECIFIED_CLASS_WEIGHT
                            hashtagDict = shareHashtagAlignments(h, RIGHT, hashtagDict)
                        elif op == "-":
                            hashtagDict[h]["alignment"][LEFT] += USER_SPECIFIED_CLASS_WEIGHT
                            hashtagDict = shareHashtagAlignments(h, LEFT, hashtagDict)

                hashtagDict, reassignments = assignHashtagClasses(hashtagDict)

                printReassignments()

                classifiedCount = 0
                for i in hashtagDict:
                    if hashtagDict[i]["class"] != UNK:
                        classifiedCount += 1

                print "\nNumber of unclassified hashtags:", totalCount - classifiedCount
                print "Number of classified hashtags:", classifiedCount, "(" + "%01d" % ((float)classifiedCount / totalCount) + ")"
                prompt = "Would you like to classify another batch of up to", MAXIMUM_SIGNIFICANT_HASHTAGS, "more hashtags? (y/n) "
                
                stopAsking = False
                while stopAsking == False:
                    op = raw_input(prompt.encode("utf-8"))
                    answer = op.lower()[0]
                    if answer == "n":
                        classify = False
                        stopAsking = True
                    if answer == "y":
                        stopAsking = True

    print "Classification complete"

    hashtagDict = { h: hashtagDict[h]["class"] for h in hashtagDict } # return dict that gives hashtags and assigned class

    with codecs.open(generateHashtagDictFileName(baseName), "w+", "utf-8") as file:
        json.dump(hashtagDict, file, indent=4, separators=(',', ': '))

# CHC: maybe consider later doing something with cut-off hashtags?
# create dict that gives hashtags, their frequencies, their joint frequencies with other hashtags, and assigned class 
def enterHashtagEntries(hashtagDict, tweets):
     # hashtagDict = {hashtag: (frequency, {other1: joint_frequency, ...}, hashtag class), ...} 
    for tweet in tweets:
        hashtags = tweet["hashtags"]
        for i, hashtag in enumerate(hashtags):
            hashtag = hashtag.lower()
            if hashtag not in hashtagDict:
                hashtagDict[hashtag] = {
                    "count": 1,
                    "associatedTags": dict(),
                    "alignment": list(),
                    "class": UNK
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
    return hashDict


# add to alignment and find the highest class
# if tie, choose unk if tie involves both pro and anti, else choose non-unk if tied with unk
# alignment votes are only shared with immediately associated hashtags to avoid extrapolating
def shareHashtagAlignments(h, voteDirection, hashtagDict):
    for hashtag in hashtagDict[h]["associatedTags"]:
        hashtagDict[hashtag]["alignment"][voteDirection] += 1
    return hashtagDict

# could be informative to compare how many class reassignments occurred in each direction
def assignHashtagClasses(hashtagDict):
    reassignments = list()
    reassignments[LEFT] = list()
    reassignments[NEUT] = list()
    reassignments[RIGHT] = list()
    origDir = NEUT

    for hashtag in hashtagDict:
        votes = hashtagDict[hashtag]["alignment"]
        origClass = hashtagDict[hashtag]["class"]
        if votes[RIGHT] > votes[LEFT]:
            hashtagDict[hashtag]["class"] = PRO
        elif votes[LEFT] > votes[RIGHT]:
            hashtagDict[hashtag]["class"] = ANT
        else:
            hashtagDict[hashtag]["class"] = UNK

        reassignments[origClass][hashtagDict[hashtag]["class"]] += 1

    return hashtagDict, reassignments

def printReassignments(reassignments):
    print "Stayed Anti:", reassignments[ANT][ANT]
    print "Anti -> Neutral:", reassignments[ANT][UNK]
    print "Anti -> Pro:", reassignments[ANT][PRO]

    print "Neutral -> Anti:", reassignments[UNK][ANT]
    print "Stayed Neutral:", reassignments[UNK][UNK]
    print "Neutral -> Pro:", reassignments[UNK][PRO]

    print "Pro -> Anti:", reassignments[PRO][ANT]
    print "Pro -> Neutral:", reassignments[PRO][NEUT]
    print "Stayed Pro:", reassignments[PRO][PRO]


if __name__ == '__main__':
    main()
