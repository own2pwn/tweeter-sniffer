#!/usr/bin/python2.7

import codecs
import json
import argparse
from snifferCommons import generateOldIntermediateFileNames
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
    while currentNum < endingPartialNumber:
        trumpJson = generateOldIntermediateFileNames(baseName + ordinal.format(currentNum))[0]
        if os.path.exists(trumpJson):

            with codecs.open(trumpJson, "r", "utf-8") as file:
                fileList = json.load(file)

            # do need to look at all users at once? only when using to vote for tweets, so search through each file then
            #       deduping was done jankily, make sure deduping is included in flow of scripts -> rawSplit.py
            # do need to look at all user histories at once? search through each file by user id when necesary
            #   reformat histories to be dict of userId => [texts]
            #            users to be     dict of userId => [screen_name, alignment, class]
            #            trumpTweets     dict of userId => { tweetId => text, tweetId => text }
            # do need to look at all trump tweets at once? loop through files when voting via hashtags, when voting for users, when auxiliary voting via 
            masterFileDict = dict()
            for tweet in fileList:
                if tweet["id"] not in masterFileDict:
                    tweet.pop("id")
                    masterFileDict[tweet["id"]] = tweet # ensure no duplicate tweets
        else:
            print "Error:", trumpJson, "does not exist in current directory"
            exit()


            # generator???? sequential read-in of hashtagFile
            # for each file:
                # generate file name
                # open and read in hashtag dict
                # close file
                # for each tag:
                    # if tag is new:
                        # add tag item to masterDict
                    # else:
                        # add tag stats to matching tag item in masterDict

    hashtagFileName = generateHashtagDictFileName(baseName)
                
    with codecs.open(hashtagFileName, "w+", "utf-8") as masterFile:
        json.dump(masterHashtagDict, masterFile, indent=4, separators=(',', ': '))


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