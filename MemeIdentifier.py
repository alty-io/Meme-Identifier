import praw
from praw.helpers import comment_stream
import nltk
from nltk.corpus import stopwords
from operator import itemgetter
import re

# set up praw
user_agent = "User-Agent: MemeIdentifier 0.1 (by /u/teefour)"
r = praw.Reddit(user_agent=user_agent)

# sets the length of the list of comments to return to the main program
comListLength = 300

# dict of unique WordClass words in comment list. Values are word counts.
wordDict = dict()

# set of words flagged for potential comparison
flaggedWords = list()

# sets sleep time in sec to wait between mass comment pulls and analysis
waitTime = 3600

# make list of stopwords to ignore
swords = set(stopwords.words('english'))
swords.add("i'm")
swords.add("it's")
swords.add("don't")
swords.add("like")
swords.add("would")
swords.add("really")


# class for containing all info on a certain word
# word is the word as a string, count is the number of times it is used
class WordClass:
    def __init__(self, myword):
        self.word = myword
        self.count = 1

    def inc_count(self):
        self.count += 1

    def get_count(self):
        return self.count

    def get_word(self):
        return self.word

    def print_word(self):
        print(self.word, ": ", self.count)


# function to return a list of comment bodies
def get_comments():
    com_list = list()

    for comment in comment_stream(r, 'all', limit=100):
        # strip out non-alphabet chars and replace with spaces
        thiscomment = comment.body.lower()
        thiscomment = re.sub("[^a-zA-Z]", " ", thiscomment)

        com_list.append(thiscomment)
        if len(com_list) >= comListLength:
            break

    return com_list


# gets comments from reddit and returns a dict of all words used with values of how many times used
def get_comment_stats():
    # fill a list with all comments
    comlist = get_comments()

    # add unique, non-stopwords to wordDict
    for comment in comlist:
        for theword in comment.split():
            # ignore stopwords
            if theword in swords:
                continue

            # if it's already in dict, increase count. If not, add it.
            if theword in wordDict:
                wordDict[theword].inc_count()
            else:
                wordDict[theword] = WordClass(theword)
    return wordDict


# compares two word counts to determine if increase is abnormal
def word_count_compare(currcount, initcount):
    if initcount > 1000:
        if (currcount/initcount) >= 1.05:
            return True
    elif initcount > 500:
        if (currcount/initcount) > 1.023:
            return True
    elif initcount > 250:
        if (currcount / initcount) > 1.025:
            return True
    elif initcount > 100:
        if (currcount / initcount) > 1.06:
            return True
    elif initcount > 50:
        if (currcount / initcount) > 1.13:
            return True
    elif (currcount - initcount) > 0:
        return True


# build initial dict to compare to
initialDict = get_comment_stats()
for words in initialDict:
    initialDict[words].print_word()

# main loop
while True:
    currentDict = get_comment_stats()
    for words in currentDict:
        currentDict[words].print_word()

    # compares old and new values to check for increased usage
    # the greater the word count, the less an increase needed to flag as abnormal increase
    for word in currentDict:
        if currentDict[word].get_word() not in initialDict:
            flaggedWords.append(currentDict[word].get_word())
        elif currentDict[word].get_word() in initialDict and \
                word_count_compare(currentDict[word].get_count(), initialDict[word].get_count()):
            flaggedWords.append(currentDict[word].get_word())

    print('\n\n testing:')
    print('flaggedWords len: ', len(flaggedWords))
    break

"""
# iterate over dict to make an ordered
orderedDict = sorted(wordDict.items(), key=itemgetter(1), reverse=True)

print(orderedDict)

for x in orderedDict:
    print(str(x), ": ", str(orderedDict[x]))
"""