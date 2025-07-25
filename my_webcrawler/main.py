import argparse
import os
import shutil
from datetime import datetime
from urllib.parse import urlparse

from web_crawler import run_scrapy_crawler
import analysis


def _domain_name(url: str) -> str:
    parsed = urlparse(url)
    return parsed.netloc.replace('www.', '').replace('.', '_')


def _folder_name(url: str) -> str:
    parsed = urlparse(url)
    domain = parsed.netloc.replace('www.', '')
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M')
    return f"{domain} SEO Analysis {timestamp}"


def main():
    parser = argparse.ArgumentParser(description="Run crawler and analysis")
    parser.add_argument("url", help="Starting URL for the crawl")
    parser.add_argument(
        "max_pages_positional",
        nargs="?",
        type=int,
        help="Maximum number of pages to crawl",
    )
    parser.add_argument(
        "--max-pages",
        dest="max_pages",
        type=int,
        default=None,
        help="Maximum number of pages to crawl",
    )
    args = parser.parse_args()

    url = args.url
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    max_pages = args.max_pages
    if max_pages is None:
        max_pages = args.max_pages_positional if args.max_pages_positional is not None else 500

    run_scrapy_crawler(url, max_pages)

    domain = _domain_name(url)
    output_folder = "webcrawler_reports"
    scrapy_csv = os.path.join(output_folder, f"{domain}_scrapy_report.csv")
    images_csv = os.path.join(output_folder, f"{domain}_images.csv")

    summary_csv, overview_txt = analysis.main(scrapy_csv=scrapy_csv, images_csv=images_csv)

    dest_folder = _folder_name(url)
    os.makedirs(dest_folder, exist_ok=True)

    for path in [scrapy_csv, images_csv, summary_csv, overview_txt]:
        if os.path.exists(path):
            shutil.copy(path, dest_folder)

    print(f"All reports copied to: {dest_folder}")


if __name__ == "__main__":
    main()