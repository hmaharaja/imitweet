"""
 This script accesses private accounts using the OAuth on TweePy along with any other public user
 
"""
from credentials import *
import tweepy
import fire
from pandas import DataFrame

def get_tweets(username):

    # Authorize with the access credentials to the account, set up tweepy
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)
    api = tweepy.API(auth)

    # extract the tweets and save to a csv
    tweets = api.user_timeline(screen_name=username, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )

if __name__ == "__main__":
  username = input("Please enter the username of the account you want to imitate, WITHOUT the @: ")

  # Need to add an exception for when the account searched doesn't exist. Maybe also one for when it doesn't have any tweets.
  fire.Fire(get_tweets(username))