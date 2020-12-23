import twint
import fire
import csv
import os
import logging
from tqdm import tqdm
from datetime import datetime
from time import sleep

# Suppress warnings
logger = logging.getLogger()
logger.disabled = True

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

    pbar = tqdm(range(limit), desc="Oldest Tweet")
    for i in range((limit // 20) - 1):
      tweet_data = []

      # Can't run a search if the user is shadowbanned, can somewhat bypass 
      # this with twint.run.Profile(c) and setting c.Profile_full = True

      # twint may fail; give it up to 5 tries to return tweets
      for _ in range(0, 4):
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
        c.Username = username
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

      oldest_tweet = datetime.utcfromtimestamp(
          tweet_data[-1].datetime / 1000.0
      ).strftime("%Y-%m-%d %H:%M:%S")
      pbar.set_description("Oldest Tweet: " + oldest_tweet)

  pbar.close()
  os.remove(".temp")