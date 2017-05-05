#!/usr/bin/python2.7

import codecs
import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    args = parser.parse_args()

    baseName = args.baseFileName

    tweetStrings = []

    for filename in filenames:
        with codecs.open(filename, "r", "utf-8") as file:
            for line in file:
                string = line.split(",", 1)
                if int(string[0]) not in uniqueUsers:
                    uniqueUsers.append(int(string[0]))
                    tweetStrings.append(string)

    print len(tweetStrings)
                
    with codecs.open(baseName + ".txt", "w+", "utf-8") as masterFile:
        for line in tweetStrings:
            masterFile.write(line[0] + ", " + line[1])

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