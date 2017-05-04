#!/usr/bin/python2.7

import codecs
import re
import json
import os
import argparse
from snifferCommons import *
from random import randint


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


    users = [ userClassAssignment(user) for user in users ]
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



# DP: Allow unassigned to be an end category or prioritize pro/anti? For now, let it be a category
def userClassAssignment(user):
    # allTrumpTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...]
    while user["class"] == UNK:
        user["class"] = randint(-1, 1)
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