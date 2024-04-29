import logging
from zenrows import ZenRowsClient
import time
import random
import requests
from bs4 import BeautifulSoup
import datetime
import pandas as pd
import xml.etree.ElementTree as ET
import azure.functions as func
from io import BytesIO
from azure.storage.blob import BlobServiceClient
import os

def read_blob_as_df(blob: func.InputStream):
    try:
        df = pd.read_csv(BytesIO(blob.read()))
        return df
    except Exception as e:
        logging.error(f"Error reading blob: {e}")

def get_news_content(url):
  result = requests.get(url)
  soup = BeautifulSoup(result.content, 'html5lib')
  # Get text from results using beatiful soup, all under "p" html
  text = ''
  for p in soup.find_all('p'):
    text += p.text
    if p.text[-1] != '.':
      text += '. '
  return text

def get_news_content_v2(url):
  ZenKeyValue = os.getenv("ZenKey")
  client = ZenRowsClient(ZenKeyValue)
  result = client.get(url)
  soup = BeautifulSoup(result.text, 'html5lib')
  # Get text from results using beatiful soup, all under "p" html
  text = ''
  for p in soup.find_all('p'):
    text += p.text
    if p.text[-1] != '.':
      text += '. '
  return text

def get_all_news_content(df):
  for i, url in enumerate(df['Link']):
    try:
        df.loc[i, 'Content'] = get_news_content_v2(url)
        print("Done for Iteration: ", i)
        t = random.randint(1, 4)
        print("Wait (s) : ", t)
        time.sleep(t)
    except IndexError:
      continue
  return df

def save_dataframe_to_blob(df: pd.DataFrame, connection_string: str, container_name: str, blob_name: str):
   """
   Saves a dataframe to azure blob storage.
   :param df: The dataframe to be saved.
   :param connection_string: The blob storage connection string.
   :param container_name: The container name.
   :param blob_name: The file name. 
   """
   # Convert the DataFrame to a CSV string
   csv_data = df.to_csv(index=False)

   # Create a BlobServiceClient object
   blob_service_client = BlobServiceClient.from_connection_string(connection_string)

   # Create a ContainerClient object
   container_client = blob_service_client.get_container_client(container_name)

   # Create a blob client and upload the CSV data
   blob_client = container_client.get_blob_client(blob_name)
   blob_client.upload_blob(csv_data, overwrite=True)