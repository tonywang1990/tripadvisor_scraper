import scrapy


class QuotesSpider(scrapy.Spider):
    name = 'parkspider'
    

    def start_requests(self):
	start_url = 'https://www.tripadvisor.com/Search?geo=191&q=national+parks&ssrc=A'
	self.home_url = start_url
	yield scrapy.Request(url=start_url, callback=self.parse)

    # parse all national parks from search url
    def parse(self, response):
	for result in response.css('div.result'):
	    result_type = result.css('div.thumbnail div.type span::text').extract_first()
	    park_name = result.css('div.title span::text').extract_first()
	    if result_type == 'National Parks' or park_name[-13:].strip() == 'National Park':
		# get park url from javascript
		partial_url = result.css('div.title::attr(onclick)').extract_first().split(',')[-1].strip(" ')")
		url = response.urljoin(partial_url)
		request = scrapy.Request(url=url, callback=self.parse_park)
		request.meta['park_url'] = url
		yield request

	# process to next park page
	offset = response.css('a.ui_button.nav.next.primary::attr(data-offset)').extract_first()
	if offset is not '':
	    next_page = self.home_url+'&o='+offset
	    yield scrapy.Request(next_page, callback=self.parse)
	

    # parse one national parks   
    def parse_park(self, response):
	# get park url and position to insert pagination
	url = response.meta['park_url']
	page_pos = url.find('-Reviews-')+7
	# parse 10 reviews 
	for review in response.css('div.quote'):
	    yield response.follow(review.css('a::attr(href)').extract_first(), callback=self.parse_review)
   	# process to next review page
	offset = response.css('span.nav.next.taLnk::attr(data-offset)').extract_first()
	if offset is not None and offset is not '':
	    next_page = url[:page_pos] + "-or" + offset +url[page_pos+1:]
	    request = scrapy.Request(next_page, callback=self.parse_park)
	    request.meta['park_url'] = url
	    yield request

    # pase one reivew
    def parse_review(self, response):
	review = response.css('div.review-container')[0]
	badge_len = len(review.css('span.badgetext::text'))
	yield {
            'park': response.css('a.HEADING::text').extract_first().strip(),
            'location': ''.join(review.css('div.location span.expand_inline::text').extract()),
            'text': review.css('div.entry p.partial_entry::text').extract_first(),
	    'contribution': review.css('span.badgetext::text')[0].extract() if badge_len > 0 else '0',
	    'thumbsup': review.css('span.badgetext::text')[1].extract() if badge_len > 1 else '0',
	    'time': review.css('span.ratingDate::attr(title)').extract_first(),
	}

    def parse_and_save(self, response):
        page = response.url.split("/")[-2]
        filename = 'quotes-%s.html' % page
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log('Saved file %s' % filename)
 

