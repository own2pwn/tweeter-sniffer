 #!/usr/bin/python2.7
 
import codecs
import re
import json
import os
import argparse
from snifferCommons import *
 
def main():
 
#   input:  allTopicTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...], 
#           histories = [(user 1 id, [tweet 1 text, tweet 2 text, ...]), ...],
#           users = [(user 1 id, user 1 screen_name, user alignment, user class)]
 
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    parser.add_argument('lastPartialNumber', help="enter the last partial file with any leading zeros")
    args = parser.parse_args()

    baseName = args.baseFileName

    hashtagJson = generateHashtagDictFileName(baseName)

    with codecs.open(hashtagJson, "r", "utf-8") as file:
        classifiedHashtags = json.load(file)

    # for now ignore case of whole file, best is to just update format from start so this script is unnecessary
    endingPartialNumber = int(args.lastPartialNumber)
    ordinal = "{" + ":0{}d".format(len(args.lastPartialNumber)) + "}"

    allTopicTweets = list()
    histories = dict()
    users = dict()

    currentNum = 1
    while currentNum <= endingPartialNumber:
        print "Next ordinal:", ordinal.format(currentNum)
        topicJson, historyJson, userJson = generateOldIntermediateFileNames(baseName + ordinal.format(currentNum))

        if os.path.exists(topicJson) and os.path.exists(topicJson) and os.path.exists(topicJson):
            with codecs.open(topicJson, "r", "utf-8") as file:
                allTopicTweets.extend(json.load(file))
         
            with codecs.open(historyJson, "r", "utf-8") as file:
                histories.update(json.load(file))
         
            with codecs.open(userJson, "r", "utf-8") as file:
                users.update(json.load(file))

        else:
            print "Error: full set of files for {} do not exist in current directory".format(baseName + ordinal.format(currentNum))
            exit()

        currentNum += 1
 
        # read in dict of { hashtag: class, hashtag: class, ... }
        # print the statistics for the dict:
        #   - # of tags
        #   - distribution over ANT, UNK, PRO
        #   - # of tags present in both dict and tweets
        #   - # of tags present in only dict, # of tags present in only tweets

        # do need to look at all users at once? only when using to vote for tweets, so search through each file then
        #       deduping was done jankily, make sure deduping is included in flow of scripts -> rawSplit.py
        # do need to look at all user histories at once? search through each file by user id when necesary
        #   reformat histories to be dict of userId => [texts]
        #            users to be     dict of userId => [screen_name, alignment, class]
        #            trumpTweets     dict of userId => { tweetId => text, tweetId => text }
        # do need to look at all trump tweets at once? loop through files when voting via hashtags, when voting for users, when auxiliary voting via 


    hashtagDict = { hashtag: classifiedHashtags[hashtag]["class"] for hashtag in classifiedHashtags }

    allTopicTweets = [ primaryAssignment(tweet, hashtagDict) for tweet in allTopicTweets ]
    printClassDistribution(allTopicTweets, "trump tweets")
 
    usersList = list()
    for user in users:
        users[user].update({"userId": user})
        usersList.append(users[user])

    tweetDict = { int(tweet["userId"]): tweet for tweet in allTopicTweets }

    usersList = [ userClassAssignment(user, tweetDict) for user in usersList ]
    printClassDistribution(usersList, "users")

    screenNameDict = { users[user]["screenName"]: users[user]["class"] for user in users }
 
    # allTopicTweets = [ auxiliaryAssignment(tweetDict[tweet], screenNameDict) for tweet in tweetDict ]
    # printClassDistribution(allTopicTweets, "trump tweets")
 
    # usersList = [ userClassAssignment(user, tweetDict) for user in usersList ]
    # printClassDistribution(usersList, "users")
 
    categorizedHistories = []

    for user in usersList:
        categorizedHistories.append({
            "class": user["class"],
            "tweets": histories[user["userId"]]["tweetTexts"]
        }) # only user class and nontrump history
     
    with codecs.open(generateOutputFileName(baseName), "w+", "utf-8") as file:
         json.dump(categorizedHistories, file, indent=4, separators=(',', ': '))
 
# output: 
#   categorizedHistories = [(user 1 class, [tweet 1 text, tweet 2 text, ...]), (user 2 class, [tweet 1 text, ...]), ...]


# if categorized, change user's alignment distribution: (+1, -1, +0) for anti, (+0, -1, +1) for pro
def primaryAssignment(tweet, hashtagDict):
    # hashtagDict = {hashtag: hashtag class, ...} 
    tweet = vote(tweet, "hashtags", hashtagDict)
    return tweet


def auxiliaryAssignment(tweet, screennames):
    tweet = vote(tweet, "mentionedScreenNames", screennames)
    return tweet


def vote(item, voterKey, voterDict):
    if "alignment" not in item: # should have added to all dicts and didn't
        item["alignment"] = [0, 0, 0]

    for voter in item[voterKey]:
        voter = voter.lower()
        if voter in voterDict:
            if voterDict[voter] == PRO:
                item["alignment"][RIGHT] += 1
            elif voterDict[voter] == ANT:
                item["alignment"][LEFT] += 1
            else:
                item["alignment"][NEUT] += 1

    votes = item["alignment"]
    if votes[RIGHT] > votes[LEFT]:
        item["class"] = PRO
    elif votes[RIGHT] < votes[LEFT]:
        item["class"] = ANT
    else:
        item["class"] = UNK

    return item


# DP: Allow unassigned to be an end category or prioritize pro/anti? For now, let it be a category
def userClassAssignment(user, tweetDict):
    # allTopicTweets = [(tweet 1 id, tweet 1 text, tweeter user id, mentioned screen_names, hashtags, tweet class), ...]
    if "alignment" in user:
        votes = user["alignment"]
    else: # should have added to all dicts and didn't
        votes = [0, 0, 0]

    userId = int(user["userId"])

    if userId in tweetDict:  # there IS possibility that user cannot be found due to differences in querying times between steps!
        if tweetDict[userId]["class"] == PRO:
            votes[RIGHT] += 1
            votes[NEUT] -= 1
        elif tweetDict[userId]["class"] == ANT:
            votes[LEFT] += 1
            votes[NEUT] -= 1

        if votes[RIGHT] > votes[LEFT]:
            user["class"] = PRO
        elif votes[RIGHT] < votes[LEFT]:
            user["class"] = ANT
        else:
            user["class"] = UNK

    user["alignment"] = votes
    return user

 
def printClassDistribution(items, description):
    distribution = [0, 0, 0]
 
    for item in items:
        if item is not None:
            if item["class"] == ANT:
                distribution[LEFT] += 1
            elif item["class"] == PRO:
                distribution[RIGHT] += 1
            else:
                distribution[NEUT] += 1
 
    print "Class distribution of {}:".format(description)
    print distribution

if __name__ == '__main__':
    main()

