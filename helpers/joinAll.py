#!/usr/bin/python2.7

import codecs

filenames = [
    # "trump_mixed_bad_cleaned.txt",
    # "trump_mixed_cleaned.txt",
    # "trump_mixed_good_cleaned.txt",
    # "trump_recent_cleaned.txt"
    "trump_all_cleaned.txt"
]

tweetStrings = []
uniqueUsers = []

for filename in filenames:
    with codecs.open(filename, "r", "utf-8") as file:
        for line in file:
            string = line.split(",", 1)
            if int(string[0]) not in uniqueUsers:
                uniqueUsers.append(int(string[0]))
                tweetStrings.append(string)

print len(tweetStrings)
            
with codecs.open("trump_all_dedup.txt", "w+", "utf-8") as masterFile:
    for line in tweetStrings:
        masterFile.write(line[0] + ", " + line[1])