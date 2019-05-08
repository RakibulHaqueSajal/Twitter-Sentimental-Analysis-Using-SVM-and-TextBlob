# -*- coding: utf-8 -*-
"""
Created on Tue Apr 10 23:47:57 2018

@author: Sajal
"""



import sys
import time
import re
import nltk
from sklearn.externals import joblib

from tweepy import Stream
from tweepy import OAuthHandler
from tweepy.streaming import StreamListener



def preprocessTweets(tweet):
    
    #Convert www.* or https?://* to URL
    tweet = re.sub('((www\.[^\s]+)|(https?://[^\s]+))','URL',tweet)
    
    #Convert @username to __HANDLE
    tweet = re.sub('@[^\s]+','__HANDLE',tweet)  
    
    #Replace #word with word
    tweet = re.sub(r'#([^\s]+)', r'\1', tweet)
    
    #trim
    tweet = tweet.strip('\'"')
    
    # Repeating words like happyyyyyyyy
    rpt_regex = re.compile(r"(.)\1{1,}", re.IGNORECASE)
    tweet = rpt_regex.sub(r"\1\1", tweet)
    
    #Emoticons
    emoticons = \
    [
     ('__positive__',[ ':-)', ':)', '(:', '(-:', \
                       ':-D', ':D', 'X-D', 'XD', 'xD', \
                       '<3', ':\*', ';-)', ';)', ';-D', ';D', '(;', '(-;', ] ),\
     ('__negative__', [':-(', ':(', '(:', '(-:', ':,(',\
                       ':\'(', ':"(', ':((', ] ),\
    ]

    def replace_parenth(arr):
       return [text.replace(')', '[)}\]]').replace('(', '[({\[]') for text in arr]
    
    def regex_join(arr):
        return '(' + '|'.join( arr ) + ')'

    emoticons_regex = [ (repl, re.compile(regex_join(replace_parenth(regx))) ) \
            for (repl, regx) in emoticons ]
    
    for (repl, regx) in emoticons_regex :
        tweet = re.sub(regx, ' '+repl+' ', tweet)

     #Convert to lower case
    tweet = tweet.lower()
    
    return tweet

#Stemming of Tweets

def stem(tweet):
        stemmer = nltk.stem.PorterStemmer()
        tweet_stem = ''
        words = [word if(word[0:2]=='__') else word.lower() \
                    for word in tweet.split() \
                    if len(word) >= 3]
        words = [stemmer.stem(w) for w in words] 
        tweet_stem = ' '.join(words)
        return tweet_stem


def predict(tweet,classifier):
    
    tweet_processed = stem(preprocessTweets(tweet))
             
    if ( ('__positive__') in (tweet_processed)):
         sentiment  = 1
         return sentiment
        
    elif ( ('__negative__') in (tweet_processed)):
         sentiment  = 0
         return sentiment       
    else:
        
        X =  [tweet_processed]
        sentiment = classifier.predict(X)
        return sentiment[0]
 
#consumer key, consumer secret, access token, access secret.
ckey=''
csecret=''
atoken=''
asecret=''
ntweet=[]
ptweet=[]

classifier = joblib.load('svmClassifier.pkl')
print("Classifier loaded...")
class listener(StreamListener):
  

    def __init__(self, api=None):
     super(listener, self).__init__()
     self.num_tweets = 0
    def on_status(self, status):
      if self.num_tweets <=200:
        record =status.text
        tw = stem(preprocessTweets(record))
        self.num_tweets += 1
        if predict(tw,classifier)==0:
             ntweet.append(record)
        else:
             ptweet.append(record)
        return True
      else:
        return False
    
    def on_error(self, status_code):
        if status_code == 420:
            #returning False in on_data disconnects the stream
            return False

auth = OAuthHandler(ckey, csecret)
auth.set_access_token(atoken, asecret)

twitterStream = Stream(auth, listener())
twitterStream.filter(track=["Donald Trump"])

print("According to my trained Suppport vector classifier: ")
print("Positive tweets percentage: {} %".format(100*(len(ptweet)/200))) 
print("Negative tweets percentage: {} %".format(100*(len(ntweet)/200)))
ntweet.clear()
ptweet.clear()