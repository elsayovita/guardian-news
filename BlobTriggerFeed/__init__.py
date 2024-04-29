import logging
import os
import tempfile
import datetime
from datetime import timedelta, date

import azure.functions as func
from .utils import read_blob_as_df, get_all_news_content

def main(myblob: func.InputStream, 
         outputBlob: func.Out[bytes], 
         outputBlob2: func.Out[bytes]) -> None:
    logging.info(f"Python blob trigger function processed blob \n"
                 f"Name: {myblob.name}\n"
                 f"Blob Size: {myblob.length} bytes")
    try:
        df = read_blob_as_df(myblob)
    except Exception as e:
        logging.error(f"Error reading existing data blobs: {e}")
        return
    print(df.shape)
    df_news = get_all_news_content(df)
    print(df_news.shape)

   # Preparing the file name
    yesterday_date = (date.today() - timedelta(days=1)).strftime("%Y%m%d")
    file_name = f"{yesterday_date}_news_content.csv"
    # Define file path
    local_path = tempfile.gettempdir()
    file_path = os.path.join(local_path, file_name)
    # Write to csv
    df_news.to_csv(file_path, index=False)
    # stores in the Blob container
    with open(file_path, "r") as f:
        outputBlob.set(f.read())
        f.close()
    print(file_path)

    # Define file path 2
    file_path2 = os.path.join(local_path, "today_news_content.csv")
    # Write to csv
    df_news.to_csv(file_path2, index=False)
    # stores in the Blob container
    with open(file_path2, "r") as f:
        outputBlob2.set(f.read())
        f.close()
    print(file_path2)