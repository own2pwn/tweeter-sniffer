#!/usr/bin/python2.7

import codecs

NUM_PER_FILE = 1000

# FILE_NAME = "trump_sample"
FILE_NAME = "trump_all_dedup"

with codecs.open(FILE_NAME + ".txt", "r", "utf-8") as file:
    content = file.readlines()

numDigits = 1
numFiles = 1 + (len(content) / NUM_PER_FILE)
while(numFiles >= 10):
    numFiles = numFiles % 10
    numDigits += 1

ordinal = "%0" + str(numDigits) + "d"

num = 0
for i, line in enumerate(content):
    if (i % NUM_PER_FILE) == 0:
        num += 1
        file.close()
        file = codecs.open(FILE_NAME + (ordinal % (num,)) + ".txt", "w+", "utf-8")
    file.write(line)

file.close()