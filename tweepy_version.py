"""
 This script accesses accounts using the OAuth on TweePy, allowing for a web application
 
"""
from credentials import *
import tweepy
import fire
import pandas as pd
import time

def get_tweets_from_user(username):

    # Authorize with the access credentials to the account, set up tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # make an initial request to extract tweets
    tweets = api.user_timeline(screen_name=username, count=200, include_rts= False, tweet_mode= 'extended')

    all_tweets = []
    all_tweets.extend(tweets)

    try:
      oldest_id = tweets[-1].id -1
    except:
      print("This account doesn't seem to have any tweets.")

    # keep getting tweets until all of them are obtained
    while len(tweets) > 0:
        print(f"getting tweets before {oldest_id}")
        
        #all subsiquent requests use the max_id param to prevent duplicates
        tweets = api.user_timeline(screen_name= username, count= 200, max_id= oldest_id, tweet_mode= 'extended')
        all_tweets.extend(tweets)
        
        oldest_id = all_tweets[-1].id -1
        
        print(f"...{len(all_tweets)} tweets downloaded so far")

        # add something to wait on the rate limit / sleep if 3200 tweets have been reached

    #transform the tweepy tweets into a 2D array that will populate the csv 
    outtweets = [[tweet.created_at, tweet.full_text.encode("utf-8").decode("utf-8")] for tweet in all_tweets]

    df = pd.DataFrame(outtweets, columns=["Time Created At","Text"])
    df.to_csv('%s_tweets.csv' % username ,index=False)


def search_phrase(search_key, limit, iters):
  print("to do later")



  
if __name__ == "__main__":
  username = input("Please enter the username of the account you want to imitate, WITHOUT the @: ")

  # Need to add an exception for when the account searched doesn't exist.
  fire.Fire(get_tweets_from_user(username))