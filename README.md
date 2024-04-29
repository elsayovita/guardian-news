# Daily News Retrieval using Azure Function
This project uses Azure Function to retrieve news from The Guardian's RSS feed at a daily cadence.

Azure Function was chosen due to the serverless nature of the solution, as it keeps the application running regardless of the local infrastructure and availability.



## Timer Trigger

The workflow of the Timer Trigger Azure Function is shown below:

![image](https://github.com/elsayovita/guardian-news/assets/112252367/10f5c400-89e9-4d67-8ec7-ce90ce73060a)

First, Timer Trigger was used to schedule the script to run daily at 12 am UTC.

Python module `xml.etree.ElementTree` was used to parse the RSS feed of the 4 main pages of the website:
```
rss_urls = [
  'https://www.theguardian.com/international/rss',
  'https://www.theguardian.com/sport/rss',
  'https://www.theguardian.com/culture/rss',
  'https://www.theguardian.com/lifeandstyle/rss'
]
```
News data, consisting of title, link, description, published date, and the full article was obtained in Pandas Dataframe format, 
which was then filtered to only show the previous day's news, and exported in CSV format through utilizing Azure output binding to Azure Blob Storage container.



## Azure Blob Storage Trigger

The workflow of the Azure Blob Trigger Azure Function is shown below:

![image](https://github.com/elsayovita/guardian-news/assets/112252367/b6d5977d-71d3-4a27-8218-6fcf44cde640)

Upon completion of the Timer Trigger Azure Function, a CSV file would be newly added to the Azure Blob Storage, which triggers the execution of this Function App.

This function works by importing the CSV file from the previous function's output as a Pandas Dataframe, 
going into each of the news URLs obtained from RSS, and parsing the source code using `BeautifulSoup`.

The Dataframe with the additional column "content" was then exported to Azure Blob Storage container in CSV format by utilizing Azure output binding.



