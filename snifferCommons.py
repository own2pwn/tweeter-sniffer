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

#### for rawSplit ####
NUM_TWEETS_PER_FILE = 1000

#### for dataPrepPart1 and dataPrepPart2 ###

# DP: find count in tweets: if total < 100, print and next user
MINIMUM_TWEET_COUNT = 100

# DP: if nontrump / total < 40%, print and next user
MINIMUM_NONTRUMP_PERC = 0.4

# DP: let's say hashtag count > 100 is significant
MINUMUM_SIGNIFICIANT_HASHTAG_FREQUENCY = 100 

# number of hashtags you're prompted for at a time
MAXIMUM_SIGNIFICANT_HASHTAGS = 15

# weight of user class-specification (user may NOT be right--overturn if user contradicts herself)
# USER_SPECIFIED_CLASS_WEIGHT * 100 (%) 
# should be greater than 1 unless you're really that suspicious of the user's judgment
USER_SPECIFIED_CLASS_WEIGHT = 2


def generateInputFileName():
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_dataset" + param + ".json"

def generateOldIntermediateFileNames(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_trumpTweets" + param + ".json", baseName + "_histories" + param + ".json", baseName + "_profiles" + param + ".json"

def generateNewIntermediateFileNames(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_trumps" + param + ".json", baseName + "_nontrumps" + param + ".json", baseName + "_users" + param + ".json"

def generateHashtagDictFileName(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_classifiedHashtags.json"

def generateOutputFileName(baseName):
    param = "_" + str(MINIMUM_TWEET_COUNT) + "_" + str(int(MINIMUM_NONTRUMP_PERC * 100))
    return baseName + "_dataset" + param + ".json"
