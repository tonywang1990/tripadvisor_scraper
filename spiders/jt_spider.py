import scrapy


class QuotesSpider(scrapy.Spider):
    name = "joshuatree"

    def start_requests(self):
        self.url = 'https://www.tripadvisor.com/Attraction_Review-g60870-d4443876-Reviews-Joshua_Tree_National_Park-Twentynine_Palms_California.html'
	self.page_pos = self.url.find('-Reviews-')+7
	yield scrapy.Request(url=self.url, callback=self.parse)

    def parse_save_page(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
    
    def parse(self, response):
	for review in response.css('div.quote'):
	    yield response.follow(review.css('a::attr(href)').extract_first(), callback=self.parse_review)
	    
   	# process to next page
	next_page = response.css('span.nav.next.taLnk')
	if next_page is not None:
	    offset = next_page.css('span::attr(data-offset)').extract_first()
	    next_page = self.url[:self.page_pos] + "-or" + offset +self.url[self.page_pos+1:]
	    yield scrapy.Request(next_page, callback=self.parse)

    def parse_review(self, response):
	review = response.css('div.review-container')[0]
	yield {
            'location': ''.join(review.css('div.location span.expand_inline::text').extract()),
            'text': review.css('div.entry p.partial_entry::text').extract_first(),
	    'contribution': review.css('span.badgetext::text')[0].extract(),
	    'thumbsup': review.css('span.badgetext::text')[1].extract(),
	    'time': review.css('span.ratingDate::attr(title)').extract_first(),
	}

