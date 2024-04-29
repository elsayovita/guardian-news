import logging
import os
import tempfile
import datetime
from datetime import timedelta, date
import pandas as pd

from .utils import parse_rss_feed

import azure.functions as func

def main(mytimer: func.TimerRequest, 
         outputBlob: func.Out[bytes], 
         outputBlob2: func.Out[bytes], 
         context: func.Context) -> None:
    # Define the RSS feed URL
    rss_urls = [
        'https://www.theguardian.com/international/rss',
        'https://www.theguardian.com/sport/rss',
        'https://www.theguardian.com/culture/rss',
        'https://www.theguardian.com/lifeandstyle/rss'
        ]
    # get df using get_feed_news containing the dataframes concatenated by row from rss_urls
    df = pd.concat([parse_rss_feed(the_url) for the_url in rss_urls], axis=0)
    df = df.reset_index(drop=True)
    
    # Preparing the file name
    yesterday_date = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    file_name = f"{yesterday_date}_news.csv"
    # Define file path
    local_path = tempfile.gettempdir()
    file_path = os.path.join(local_path, file_name)
    # Write to csv
    df.to_csv(file_path, index=False)
    # stores in the Blob container
    with open(file_path, "r") as f:
        outputBlob.set(f.read())
        f.close()
    print(file_path)

    # Define file path 2
    file_path2 = os.path.join(local_path, "today_feed.csv")
    # Write to csv
    df.to_csv(file_path2, index=False)
    # stores in the Blob container
    with open(file_path2, "r") as f:
        outputBlob2.set(f.read())
        f.close()
    print(file_path2)

    utc_timestamp = datetime.datetime.utcnow().replace(
        tzinfo=datetime.timezone.utc).isoformat()
    
    if mytimer.past_due:
        logging.info('The timer is past due!')

    logging.info('Python timer trigger function ran at %s', utc_timestamp)


