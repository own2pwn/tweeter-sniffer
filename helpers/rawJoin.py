#!/usr/bin/python2.7

import codecs

tweetStrings = []
uniqueUsers = []

with codecs.open("trump_all_cleaned.txt", "r", "utf-8") as file:
    for line in file:
        string = line.split(",", 1)
        if int(string[0]) not in uniqueUsers:
            uniqueUsers.append(int(string[0]))
            tweetStrings.append(string)

print len(tweetStrings)
            
with codecs.open("trump_all_dedup.txt", "w+", "utf-8") as masterFile:
    for line in tweetStrings:
        masterFile.write(line[0] + ", " + line[1])