import json
import sys
from geopy.geocoders import Nominatim

### extract_by_keywords:
### Filter reviews from data_file, return a list of reviews 
### that contain any keywords from the keyword_file, the extracted
### list is also saved into a json file
def extract_by_keywords(data_file, keyword_file):
    # read keywords
    with open(keyword_file) as f:
        lines = f.read()
    keywords = lines.split()

    # read raw data
    raw_data = json.load(open(data_file))
    print('{} reviews loaded from {}\n'.format(len(raw_data), filename))
    raw_data.sort(key=lambda review : review['park'])
    
    # output data list
    data = []
    for review in raw_data:
	if review['text'] is not None and any(keyword in review['text'] for keyword in keywords):
	    data.append(review)

    # get data size
    print('{} reviews extracted.\n'.format(len(data)))

    # dump data to json file
    data = extract('data/all_reviews.json', keywords)
    with open('data/price_related_reviews.json', 'w') as output:
        json.dump(data, output, indent = 4)

    return data

### split_by_country:
### use geopy to split data from start_idx into three seperated 
### lists by country: domestic, international and unknown
### failed geolocator request are reported by the review number
### resulting list are saved as seperate json files and returned
def split_by_country(data, start_idx = 0):
    domestic, international, unknown = [], [], []
    geolocator = Nominatim()
    
    # split data based on geo location
    idxs = [147, 643, 924, 954, 1038, 1084, 1266, 1271, 2007, 2385, 2390, 2813, 2927, 3328, 3438, 3609, 3716, 4047, 4112, 4159, 4309, 4338, 4519, 5000, 5266, 5310, 5447, 5723, 5911]
    for i in idxs:
    #for i, review in enumerate(data[start_idx:]):
        review = data[i]
	try:
	    loc = geolocator.geocode(review['location'], timeout=100)
	except Exception as e:
	    print('Error message:\n' + str(e))
	    #print('Processed upto review number {}\n'.format(i))
	    print('review number {} failed\n'.format(start_idx+i))
	    if 'Too Many Requests' in str(e):
		break
            else: 
	    	continue

        if loc is None:
	    unknown.append(review)
	elif loc.address.split(',')[-1].strip().lower() == "united states of america":
	    domestic.append(review)
	else:
	    international.append(review)
    
    # save to json files 
    with open('data/domestic_reviews.json', 'a+') as output:
        json.dump(domestic, output, indent = 4)
    
    with open('data/international_reviews.json', 'a+') as output:
        json.dump(international, output, indent = 4)
    
    with open('data/unknow_loc_reviews.json', 'a+') as output:
        json.dump(unknown, output, indent = 4)

    # report count
    print('domestic reviews: {}\ninternational reviews: {}\nunknown location reivews: {}'.format(len(domestic), len(international), len(unknown)))
   
    return [domestic, international, unknown]
            

# extract data from raw review data
#data = extract_by_keywords('data/all_reviews.json', 'keywords.txt')		

# use extracted data - price_related_reviews.json
data = json.load(open('data/price_related_reviews.json'))

split_by_country(data)

   
