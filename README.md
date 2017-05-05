# tweeter-sniffer
CMPE 188 project

Dataset generation scripts

1. tweetSniffer.py

Queries Twitter for tweets related to the topic, i.e. "trump".

2. split.py

Splits the topic-based query results into smaller files for concurrent querying in next step.

3. userSniffer.py

Queries Twitter for information related to each user who was found tweeting about the topic. Information is user screen name and entire tweet history for the last 7 days (TwitterSearch library constraint).

4. cleanHashtags.py, and other cleaning scripts

Cleans up the intermediate lists of dictionaries for easier processing.

5. generateHashtagDict.py

Creates a dictionary of hashtags with associated hashtags and various frequencies and prompts the user to start teaching the dictionary the positivity/negativity of the tags relative to the topic.

6. joinHashtagDicts.py

Joins the hashtag dicts for the smaller files for culmulative local classification.

7. classify.py

Classifies tweets and tweeters using the hashtag dictionary (primary) and mentioned screen names (auxiliary)