# check to see what happens with private, restricted, and other accounts that aren't public. Watch out that
# they don't get treated like a public account with no tweets, as those are different things.

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


c = twint.Config()
c.Username = 'hf_dreamcatcher'
c.Custom = ['id', 'date', 'time', 'timezone', 'user_id', 'username', 'tweet', 'replies', 
            'retweets', 'likes', 'hashtags', 'link', 'retweet', 'user_rt', 'mentions']
c.Store_csv = True
c.Profile_full = True 
#c.Output = os.path.join(tw_path, c.Username + '.csv')

# Start search
twint.run.Profile(c)