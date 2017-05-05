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
    filename = HASHTAG_FILE_NAME
 
    with codecs.open(trumpJson, "r", "utf-8") as file:
        allTrumpTweets = json.load(file)
 
    with codecs.open(historyJson, "r", "utf-8") as file:
        nontrumpHistories = json.load(file)
 
    with codecs.open(userJson, "r", "utf-8") as file:
        users = json.load(file)
    
    with codecs.open(filename, "r", "utf-8") as file:
        classifiedHashtags = json.load(file)
        # read in dict of { hashtag: class, hashtag: class, ... }
        # print the statistics for the dict:
        #   - # of tags
        #   - distribution over ANT, UNK, PRO
        #   - # of tags present in both dict and tweets
        #   - # of tags present in only dict, # of tags present in only tweets


    allTrumpTweets = [ primaryAssignment(tweet, classifiedHashtags) for tweet in allTrumpTweets ]
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


# if categorized, change user's alignment distribution: (+1, -1, +0) for anti, (+0, -1, +1) for pro
def primaryAssignment(tweet, hashtagDict):
    # hashtagDict = {hashtag: hashtag class, ...} 
    tweet["class"] = vote(tweet["hashtags"], hashtagDict)
    return tweet


def auxiliaryAssignment(tweet, users):
    users = { user["screenName"]: user["class"] for user in users }

    if tweet["class"] == UNK:
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
        return UNK


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
        tweet["class"] = UNK

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

