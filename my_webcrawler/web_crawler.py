import scrapy
import csv
import os
from urllib.parse import urlparse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

class SEOSpider(scrapy.Spider): #Spider web crawler for SEO analysis
    name = 'seo_crawler'
    
    def __init__(self, start_url=None, max_pages=500, *args, **kwargs):
        super(SEOSpider, self).__init__(*args, **kwargs)
        self.start_urls = [start_url] if start_url else []
        self.max_pages = int(max_pages)
        self.pages_crawled = 0
        self.allowed_domains = [urlparse(start_url).netloc]
        self.results = []
        # keep a reference to each page data by URL so it can be
        # updated later with broken link information
        self.page_data_by_url = {}
        # store broken links detected for each page
        self.broken_links = {}
        
        # Output CSV file setup
        domain_name = urlparse(start_url).netloc.replace('www.', '').replace('.', '_')
        output_folder = "webcrawler_reports"
        os.makedirs(output_folder, exist_ok=True)
        self.csv_filename = os.path.join(output_folder, f"{domain_name}_scrapy_report.csv")
    
    def parse(self, response):
        # If this request came from another page, check if it's broken
        source_url = response.meta.get('source_url')
        if source_url and response.status >= 400:
            self.broken_links.setdefault(source_url, []).append(response.url)

        # Do not crawl more pages than the limit
        if self.pages_crawled >= self.max_pages:
            return
        
        self.pages_crawled += 1
        
        # Extract SEO data
        title = response.css('title::text').get(default='').strip()
        meta_description = response.css('meta[name="description"]::attr(content)').get(default='')
        meta_keywords = response.css('meta[name="keywords"]::attr(content)').get(default='')
        
        h1_tags = response.css('h1::text').getall()
        h1_count = len(h1_tags)
        h1_text = h1_tags[0].strip() if h1_tags else ''
        
        h2_count = len(response.css('h2').getall())

        # detect images missing alt text
        images_missing_alt = response.xpath("//img[not(@alt) or normalize-space(@alt)='']/@src").getall()
        
        # I might delete this if not needed
        # body_text = ' '.join(response.css('body *::text').getall())
        # word_count = len(body_text.split()) if body_text else 0
        
        # Crear registro de datos
        page_data = {
            'URL': response.url,
            'Status Code': response.status,
            'Title': title,
            'Title Length': len(title),
            'Meta Description': meta_description,
            'Meta Description Length': len(meta_description),
            'Meta Keywords': meta_keywords,
            'H1 Count': h1_count,
            'H1 Text': h1_text,
            'H2 Count': h2_count,
            #'Word Count': word_count, (commented out for now)
            'Response Time (ms)': int(response.meta.get('download_latency', 0) * 1000),
            'Content Type': response.headers.get('content-type', b'').decode('utf-8'),
            'Content Length': len(response.body),
            # will be filled later with URLs that return error codes
            'Broken Links': '',
            # list of image sources missing alt text
            'Images Missing Alt': '; '.join(images_missing_alt),
        }
        
        self.results.append(page_data)
        self.page_data_by_url[response.url] = page_data
        
        yield page_data
        
        # internal links if not already crawled
        if self.pages_crawled < self.max_pages:
            for link in response.css('a::attr(href)').getall():
                # Filtrar enlaces no válidos
                if link and not link.startswith(('javascript:', 'mailto:', 'tel:', '#')):
                    yield response.follow(link, self.parse, meta={'source_url': response.url})
    
    def closed(self, reason):
        # Save results to CSV file when spider is closed
        if self.results:
            # update each page data with any broken links found
            for url, links in self.broken_links.items():
                if url in self.page_data_by_url:
                    self.page_data_by_url[url]['Broken Links'] = '; '.join(links)

            fieldnames = [
                'URL', 'Status Code', 'Title', 'Title Length',
                'Meta Description', 'Meta Description Length', 'Meta Keywords',
                'H1 Count', 'H1 Text', 'H2 Count', #'Word Count', # Uncomment if needed
                'Response Time (ms)', 'Content Type', 'Content Length',
                'Broken Links', 'Images Missing Alt'
            ]
            
            with open(self.csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(self.results)
            
            print(f"\nResultados guardados en: {self.csv_filename}")
            print(f"Total de páginas crawleadas: {len(self.results)}")

def run_scrapy_crawler(url, max_pages=5000):
    """Ejecuta el crawler de Scrapy"""
    
    # Scrapy settings
    settings = get_project_settings()
    settings.setdict({
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'ROBOTSTXT_OBEY': True,  # Respetar robots.txt
        'DOWNLOAD_DELAY': 1,     # Delay entre peticiones
        'RANDOMIZE_DOWNLOAD_DELAY': 0.5,  # Randomizar delay
        'CONCURRENT_REQUESTS': 1,  # Peticiones concurrentes
        'DEPTH_LIMIT': 10,       # Límite de profundidad
        'CLOSESPIDER_PAGECOUNT': max_pages,  # Cerrar spider después de N páginas
    })
    
    # create a CrawlerProcess with the settings
    process = CrawlerProcess(settings)
    process.crawl(SEOSpider, start_url=url, max_pages=max_pages)
    process.start()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Uso: python scrapy_crawler.py <URL> [max_pages]")
        print("Ejemplo: python scrapy_crawler.py https://www.ejemplo.com 100")
        sys.exit(1)
    
    url = sys.argv[1]
    max_pages = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    
    # URL validation
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    
    print(f"Iniciando crawler Scrapy para: {url}")
    print(f"Máximo de páginas: {max_pages}")
    
    run_scrapy_crawler(url, max_pages)