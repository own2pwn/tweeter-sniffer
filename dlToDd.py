#!/usr/bin/python2.7

import codecs
import json
import argparse
from snifferCommons import generateOldIntermediateFileNames, generateNewIntermediateFileNames
import os


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    parser.add_argument('lastPartialNumber', help="enter the last partial file with any leading zeros")
    args = parser.parse_args()

    baseName = args.baseFileName

    # for now ignore case of whole file, best is to just update format from start so this script is unnecessary
    endingPartialNumber = int(args.lastPartialNumber)
    ordinal = "{" + ":0{}d".format(len(args.lastPartialNumber)) + "}"

    currentNum = 1
    while currentNum <= endingPartialNumber:
        print "Next ordinal:", ordinal.format(currentNum)
        topicJson, historyJson, userJson = generateOldIntermediateFileNames(baseName + ordinal.format(currentNum))

        for dataJson in [ historyJson, userJson ]:
            if os.path.exists(dataJson):
                print "Working on new dict for", dataJson
                with codecs.open(dataJson, "r", "utf-8") as file:
                    fileList = json.load(file)

                # do need to look at all users at once? only when using to vote for tweets, so search through each file then
                #       deduping was done jankily, make sure deduping is included in flow of scripts -> rawSplit.py
                # do need to look at all user histories at once? search through each file by user id when necesary
                #   reformat histories to be dict of userId => [texts]
                #            users to be     dict of userId => [screen_name, alignment, class]
                #            trumpTweets     dict of userId => { tweetId => text, tweetId => text }
                # do need to look at all trump tweets at once? loop through files when voting via hashtags, when voting for users, when auxiliary voting via 
                masterFileDict = dict()

                if isinstance(fileList, list) and isinstance(fileList[0], dict):
                    for item in fileList:
                        userId = item.pop("userId")
                        masterFileDict[userId] = item
                        # print "Added {} to dict for {}".format(userId, dataJson)
                    with codecs.open(dataJson, "w+", "utf-8") as file:
                        json.dump(masterFileDict, file, indent=4, separators=(',', ': '))
            else:
                print "Error: {} does not exist in current directory".format(dataJson)
                exit()

        currentNum += 1


if __name__ == '__main__':
    # add file to path to include module in parent directory if no packages defined when script called 
    # if __package__ is None:
    #     import sys
    #     from os import path
    #     sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
    #     from snifferCommons import generateHashtagDictFileName
    # else:
    #     from ..snifferCommons import generateHashtagDictFileName
    main()