import feedparser
import requests
import datetime
import pandas as pd
import xml.etree.ElementTree as ET

import logging

import azure.functions as func

from azure.storage.blob import BlobServiceClient

def parse_rss_feed(the_url):
  response = requests.get(url=the_url)
  feed_content = response.content
  # Initialize lists to store data.
  titles = []
  descriptions = []
  links = []
  categories = []
  pub_dates = []

  # Parse the XML content.
  root = ET.fromstring(feed_content)

  # Find all articles by finding the "item" tag.
  articles_collection = root.findall("./channel/item")

  # Loop through the articles.
  for article in articles_collection:
    # Extract data from each article.
    title = article.find("title").text.strip()
    description = article.find("description").text.strip()
    link = article.find("link").text.strip()
    category = article.find("category").text.strip()
    pub_date = article.find("pubDate").text.strip()

    # Append data to respective lists.
    titles.append(title)
    descriptions.append(description)
    links.append(link)
    categories.append(category)
    pub_dates.append(pub_date)

  # Create a DataFrame from the collected data.
  df = pd.DataFrame({
      "Title": titles,
      "Description": descriptions,
      "Link": links,
      'Published Date': pub_dates
  })
  df['Published Date'] = pd.to_datetime(df['Published Date'])
  # Get yesterday's news only
  df_subset = df.loc[df['Published Date'].dt.date == datetime.date.today() - datetime.timedelta(days=1)]
  return df_subset

def get_feed_news(rss_url):
  feed = feedparser.parse(rss_url)
  # Iterate over feed
  titles = []
  summaries = []
  links = []
  published_dates = []
  for entry in feed.entries:
    titles.append(entry.title)
    summaries.append(entry.summary)
    links.append(entry.link)
    published_dates.append(entry.published)
  # create dataframe from feed entries
  df = pd.DataFrame({
      'Title': titles,
      'Summary': summaries,
      'Link': links,
      'Published Date': published_dates
  })
  df['Published Date'] = pd.to_datetime(df['Published Date'])
  # Get yesterday's news only
  df_subset = df.loc[df['Published Date'].dt.date == datetime.date.today() - datetime.timedelta(days=1)]
  return df_subset



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