CMPE 188 Tweeter-Sniffer

Part A. Dataset generation scripts (Megumi Page)

1. tweetSniffer.py

Queries Twitter for tweets related to the topic, i.e. "trump".

2. split.py

Splits the topic-based query results into smaller files for concurrent querying in next step.

3. userSniffer.py

Queries Twitter for information related to each user who was found tweeting about the topic. Information is user screen name and entire tweet history for the last 7 days (TwitterSearch library constraint).

4. generateHashtagDict.py

Creates a dictionary of hashtags with associated hashtags and various frequencies and prompts the user to start teaching the dictionary the positivity/negativity of the tags relative to the topic.

5. classify.py

Classifies tweets and tweeters using the hashtag dictionary (primary).
Also supposed to by mentioned screen names (auxiliary) after initial user class assignment, but that didn't quite happen.

*6. helper scripts

Reorganize and clean data for easier processing as necessary between other scripts



Part B. Machine learning algorithms

Random forest: Aaron Moffitt
Naive Bayes: Erick Mena