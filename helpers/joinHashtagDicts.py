#!/usr/bin/python2.7

import codecs
import json
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('baseFileName', help="enter base name without the extension")
    parser.add_argument('numberOfPartials', help="enter the number of partial hash dicts to join")
    args = parser.parse_args()

    baseName = args.baseFileName
    numFiles = int(args.numberOfPartials)

    masterHashtagDict = dict()

    for num in numFiles:
        hashtagFileName = generateHashtagDictFileName(baseName + str(num))

        with codecs.open(hashtagFileName, "r", "utf-8") as file:
            hashtagDict = json.load(file)

        # generator???? sequential read-in of hashtagFile
        # for each file:
            # generate file name
            # open and read in hashtag dict
            # close file
            # for each tag:
                # if tag is new:
                    # add tag item to masterDict
                # else:
                    # add tag stats to matching tag item in masterDict

    hashtagFileName = generateHashtagDictFileName(baseName)
                
    with codecs.open(hashtagFileName, "w+", "utf-8") as masterFile:
        json.dump(masterHashtagDict, masterFile, indent=4, separators=(',', ': '))


if __name__ == '__main__':
    # add file to path to include module in parent directory if no packages defined when script called 
    if __package__ is None:
        import sys
        from os import path
        sys.path.append( path.dirname( path.dirname( path.abspath(__file__) ) ) )
        from snifferCommons import generateHashtagDictFileName
    else:
        from ..snifferCommons import generateHashtagDictFileName
    main()