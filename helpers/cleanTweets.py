#!/usr/bin/python2.7

import codecs
import re
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('fileName', help="name of TXT file to containing tweets to clean, not including ext")
args = parser.parse_args()

with codecs.open(args.fileName + ".txt", "r", "utf-8") as file:
    content = file.readlines()

lines = []

index = 0
corrections = 0

# pattern = re.compile(r'([^0-9])([0-9]+,)')

# for line in content:
#     good = re.sub(pattern, r'\1\n\2', line)
#     print re.sub(pattern, r'\1\n\2', line)

for i, line in enumerate(content):
    num = line.split(", ")[0]
    if num.isdigit() and len(num) > 6:
        lines.append(line.strip())
        index += 1
    elif i > 0:
        corrections += 1
        lines[index - 1] += " " + line.strip()

with codecs.open(args.fileName + "_cleaned.txt", "w+", "utf-8") as file:
    for line in lines:
        file.write(line + "\n")

print "Fixed", corrections, "errors"