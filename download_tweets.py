# Data extraction: scrape a user's tweets using twint
# Processing: get rid of rewtweets, URL'S, links, and any other sensitive info, save to a CSV 
# Training: train a LSTM

# Adapted using source code from download_tweets.py, found at: https://minimaxir.com/2020/01/twitter-gpt2-bot/import twint
import twint
import fire
import csv
import os
import logging
import re
from tqdm import tqdm
from datetime import datetime
from time import sleep

# Suppress warnings
logger = logging.getLogger()
logger.disabled = True

def is_reply(tweet):
    """
    Determines if the tweet is a reply to another tweet.
    Requires somewhat hacky heuristics since not included w/ twint
    """

    # If not a reply to another user, there will only be 1 entry in reply_to
    if len(tweet.reply_to) == 1:
        return False

    # Check to see if any of the other users "replied" are in the tweet text
    users = tweet.reply_to[1:]
    conversations = [user["screen_name"] in tweet.tweet for user in users]

    # If any if the usernames are not present in text, then it must be a reply
    if sum(conversations) < len(users):
        return True
    return False

def download_tweets(user=None, limit=None, include_replies=False, include_links=False, strip_usertags=False, strip_hashtags=False):
  # According to twint documentation, limit must be a multiple of 20
  if limit:
    while limit % 20 != 0:
      limit = input("Number of tweets to scrape must be a multiple of 20. Otherwise, to scrape all tweets, press Enter: ")
  
  # Get the profile information, including the number of tweets, and set that as the limit
  c = twint.Config()
  c.Username = user
  c.Store_object = True
  c.Hide_output = True

  if include_links:
      c.Links = "include"
  else:
      c.Links = "exclude"

  twint.run.Lookup(c)
  limit = twint.output.users_list[-1].tweets

  pattern = r"http\S+|pic\.\S+|\xa0|…"

  if strip_usertags:
      pattern += r"|@[a-zA-Z0-9_]+"

  if strip_hashtags:
      pattern += r"|#[a-zA-Z0-9_]+"

  # Create an empty file to store pagination id
  with open(".temp", "w", encoding="utf-8") as f:
      f.write(str(-1))

  print("Retrieving tweets for @{}...".format(user))

  with open("{}_tweets.csv".format(user), "w", encoding="utf8") as f:
    w = csv.writer(f)
    w.writerow(["tweets"])  # gpt-2-simple expects a CSV header by default

    pbar = tqdm(range(limit), desc="Creating CSV:")
    for i in range((limit // 20) - 1):
      tweet_data = []

      # Can't run a search if the user is shadowbanned, can somewhat bypass 
      # this with twint.run.Profile(c) and setting c.Profile_full = True

      # twint may fail; give it up to 5 tries to return tweets
      for j in range(0, 4):
        if len(tweet_data) == 0:
          c = twint.Config()
          c.Store_object = True
          c.Hide_output = True
          c.Username = user
          c.Limit = 40
          c.Resume = ".temp"

          c.Store_object_tweets_list = tweet_data

          twint.run.Search(c)

          # If it fails, sleep before retry.
          if len(tweet_data) == 0:
              sleep(1.0)
        else:
          continue

      # If still no tweets after multiple tries, we're done
      if len(tweet_data) == 0:
        c = twint.Config()
        c.Store_object = True
        c.Hide_output = True
        c.Username = user
        c.Limit = 40
        c.Resume = ".temp"

        c.Store_object_tweets_list = tweet_data

      if not include_replies:
          tweets = [re.sub(pattern, "", tweet.tweet).strip()
              for tweet in tweet_data
              if not is_reply(tweet)
          ]

          # On older tweets, if the cleaned tweet starts with an "@",
          # it is a de-facto reply.
          for tweet in tweets:
            if tweet != "" and not tweet.startswith("@"):
                w.writerow([tweet])
      else:
        tweets = [re.sub(pattern, "", tweet.tweet).strip() for tweet in tweet_data]

        for tweet in tweets:
          if tweet != "":
            w.writerow([tweet])

      if i > 0:
        pbar.update(20)
      else:
        pbar.update(40)

      #print(tweet_data[-1].datetime)
      #oldest_tweet = datetime.utcfromtimestamp(tweet_data[-1].datetime / 1000.0).strftime("%Y-%m-%d %H:%M:%S")
      #pbar.set_description("Oldest Tweet: " + oldest_tweet)

  pbar.close()
  os.remove(".temp")

# Running directly from the program, not the CLI, to make it easier to turn this into an application
if __name__ == "__main__":
  username = input("Please enter the username of the account you want to imitate, WITHOUT the @: ")

  # Need to add an exception for when the account searched doesn't exist. Maybe also one for when it doesn't have any tweets.
  fire.Fire(download_tweets(username))