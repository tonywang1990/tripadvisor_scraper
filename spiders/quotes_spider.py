import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            'http://quotes.toscrape.com/page/1/',
            'http://quotes.toscrape.com/page/2/',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse_save_page(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
    
    def parse(self, response):
	for quote in response.css('div.quote'):
	    yield {
	    	'text': quote.css('span.text::text').extract(),
	    	'author': quote.css('small.author::text').extract(),
	    	'tags': quote.css('meta.keywords::text').extract(),
	    }
	next_page = response.css('li.next a::attr(href)').extract_first()
  	if next_page is not None:
	    next_page = repsonse.urljoin(next_page)
	    yield scrapy.Request(next_page, callback=self.parse)

