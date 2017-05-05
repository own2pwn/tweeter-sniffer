#!/usr/bin/python2.7

import codecs
import argparse

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()

    baseName = args.baseFileName

    with codecs.open(baseName + ".txt", "r", "utf-8") as file:
        content = file.readlines()

    numDigits = 0
    numFiles = 1 + (len(content) / NUM_TWEETS_PER_FILE)
    while(numFiles > 1):
        numFiles = numFiles / 10
        numDigits += 1

    ordinal = "{:0" + str(numDigits) + "d}"

    num = 0
    for i, line in enumerate(content):
        if (i % NUM_TWEETS_PER_FILE) == 0:
            num += 1
            file.close()
            file = codecs.open(baseName + ordinal.format(num) + ".txt", "w+", "utf-8")
        file.write(line)

    file.close()

if __name__ == '__main__':
    # add file to path to include module in parent directory if no packages defined when script called 
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from snifferCommons import NUM_TWEETS_PER_FILE
    else:
        from ..snifferCommons import NUM_TWEETS_PER_FILE
    main()