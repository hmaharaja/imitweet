# check if twitter has banned words/phrases and what happens with them?

# what is oAuth? how to handle private accounts
import twint
import fire
import csv
import os
import logging
import re
from tqdm import tqdm
from datetime import datetime
from time import sleep
from download_tweets import is_reply

if __name__ == "__main__":
    c = twint.Config()
    c.Search = "pineapple"
    c.Store_object = True
    c.Hide_output = True
    c.Limit = 20

    tweetslist = []
    c.Store_object_tweets_list = tweetslist
    twint.run.Search(c)
    print(tweetslist)