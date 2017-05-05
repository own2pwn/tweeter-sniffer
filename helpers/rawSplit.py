#!/usr/bin/python2.7


import codecs
import argparse
from snifferCommons import NUM_TWEETS_PER_FILE


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()

    baseName = args.baseFileName

    with codecs.open(baseName + ".txt", "r", "utf-8") as file:
        content = file.readlines()

    numDigits = 1
    numFiles = 1 + (len(content) / NUM_TWEETS_PER_FILE)
    while(numFiles >= 10):
        numFiles = numFiles % 10
        numDigits += 1

    ordinal = "%0" + str(numDigits) + "d"

    num = 0
    for i, line in enumerate(content):
        if (i % NUM_TWEETS_PER_FILE) == 0:
            num += 1
            file.close()
            file = codecs.open(baseName + (ordinal % (num,)) + ".txt", "w+", "utf-8")
        file.write(line)

    file.close()

if __name__ == '__main__':
    main()