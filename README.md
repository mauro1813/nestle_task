# About the project
This project began as a coding challenge during an interview process for a Search Analyst position. What started as a task quickly evolved into an engaging and enjoyable exploration of web crawling and data analysis.

## Project Structure
This repository is divided into two distinct approaches. I wasn't satisfied with a single solution, so I embarked on two parallel paths:

### Screaming_frog/
This folder contains data analysis scripts developed in Python with the Pandas library. The datasets used for this analysis were extracted using the industry-standard Screaming Frog SEO Spider tool. Here, you'll find insights derived from pre-crawled data, focusing on practical application and data interpretation for SEO purposes. At the moment is very limited, it has a `seo_analysis.py` script which analyses a Screaming Frog crawl CSV and outputs an Excel report summarizing key SEO issues. The script accepts an optional positional argument specifying which Screaming Frog CSV to analyze. If omitted, it defaults to "internal_all.csv", which is the default Screaming Frog file name and is expected to be in the same folder as the script. 
Usage example:
```
python3 screaming_frog/seo_analysis.py madewithnestle_ca.csv

python3 screaming_frog/seo_analysis.py
```

### My_webcrawler/: 
A custom-built web crawler developed using Python and the Scrapy framework. This folder represents my efforts to build a web crawling script from scratch. 
This folder has a `main.py` script. The script sets up an argument parser and expects a starting URL plus an optional page limit. When executed, `main()` validates the URL, determines the maximum page count (defaulting to 500 if none is provided), runs the crawler via `run_scrapy_crawler`, performs analysis, and copies the resulting reports to a timestamped folder.
Usage examples:
```
python main.py https://example.com
python main.py https://example.com 100
python main.py https://example.com --max-pages 100
```

I'm still working on it and also learning about github on the process :)