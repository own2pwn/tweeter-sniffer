# This file contains all the file names and data preprocessing parameters for the Sniffer

ELLIPSES = u'\u2026' # UTF-8 for '...' character

UNK = 0 
PRO = 1 
ANT = -1

LEFT = 0
NEUT = 1
RIGHT = 2

# output file for sniffer
FRESH_TRUMP_TWEET_SEARCH_FILENAME = "new_tweet_search.txt"

# for dataPrepPart1 and dataPrepPart2
MINIMUM_TWEET_COUNT = 100   # DP: find count in tweets: if total < 100, print and next user
MINIMUM_NONTRUMP_PERC = 0.4 # DP: if nontrump / total < 40%, print and next user
MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY = 10 # DP: let's say hashtag count > 100 is significant

# FILE_NAME = "trump_all_dedup"
FILE_NAME = "trump_sample"

HASHTAG_FILE_NAME = "classifiedHashtags.json"

def generateInputFileName():
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_dataset" + param + ".json"

def generateOldIntermediateFileNames(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_trumpTweets" + param + ".json", baseName + "_histories" + param + ".json", baseName + "_profiles" + param + ".json"

def generateNewIntermediateFileNames(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_trumps" + param + ".json", baseName + "_nontrumps" + param + ".json", baseName + "_users" + param + ".json"

def generateOutputFileName():
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_dataset" + param + ".json"
