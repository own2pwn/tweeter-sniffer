#!/usr/bin/env python2.7

import codecs
import json
import argparse
import snifferCommons
import sys


def main():

#   input:  allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...]
 
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()
 
    baseName = args.baseFileName
 
    trumpJson, historyJson, userJson = snifferCommons.generateOldIntermediateFileNames(baseName)
 
    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweets = json.load(file)
 
 
    # clean up only necessary for first few files
    totalCount = 0
    cleanedCount = 0
    removedCount = 0
    splitCount = 0
    for tweet in allTrumpTweets:
        totalCount += 1
        hashtags = tweet["hashtags"]
        # if len(tweet["hashtags"]) != 0:
            # print len(tweet["hashtags"]), "present before cleaning"

        individualTags = []
        for hashtag in hashtags:
            symbolIndex = hashtag.find("#")
            if symbolIndex != -1:
                splitCount += 1
                # cut and add as separate hashtags
                individualTags.append(hashtag[:symbolIndex])
                individualTags.append(hashtag[symbolIndex + 1:])
                # print hashtag, "->", hashtag[:symbolIndex], "&", hashtag[symbolIndex + 1:]
            else:
                individualTags.append(hashtag)

        cleaned = []
        for hashtag in individualTags:
            if hashtag.find(snifferCommons.ELLIPSES) == -1:
                cleanTag = hashtag
                for i, c in enumerate(hashtag):
                    # print "index", i, "of", hashtag
                    if not c.isalnum():
                        cleanedCount += 1
                        cleanTag = cleanTag[:i]
                        # print hashtag, "->", cleanTag
                        break
                cleaned.append(cleanTag)
            else:
                # print "removed", hashtag
                removedCount += 1
            # if does contain ellipses, just discard

        tweet["hashtags"] = cleaned
        # if len(tweet["hashtags"]) != 0:
        #     print len(tweet["hashtags"]), "present after cleaning"

    # trumpJson, historyJson, userJson = snifferCommons.generateNewIntermediateFileNames(baseName)

    with codecs.open(trumpJson, "w+", "utf-8") as file:
        json.dump(allTrumpTweets, file, indent=4, separators=(',', ': '))

    # if sum([cleanedCount, removedCount, splitCount]) == 0:
    #     for tweet in allTrumpTweets:
    #         print tweet["hashtags"]


    print "Total tweets reviewed:", totalCount
    print "Total tweets cleaned:", cleanedCount
    print "Total tweets removed:", removedCount
    print "Total tweets split:", splitCount


if __name__ == '__main__':
    main()
