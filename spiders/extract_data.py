import json
import sys
from geopy.geocoders import Nominatim

def extract(filename, keywords):
    raw_data = json.load(open(filename))
    print('{} reviews loaded from {}\n'.format(len(raw_data), filename))
    raw_data.sort(key=lambda review : review['park'])
    data = []
    for review in raw_data:
	if review['text'] is not None and any(keyword in review['text'] for keyword in keywords):
	    data.append(review)
    print('{} reviews extracted.\n'.format(len(data)))
    return data

def split_by_country(data):
    domestic, international, unknown = [], [], []
    geolocator = Nominatim()
    for i, review in enumerate(data):
	try:
	    loc = geolocator.geocode(review['location'], timeout=100)
	except Exception as e:
	    print('Error message:\n' + str(e))
	    print('Processed upto review number {}\n'.format(i))
    	    return [domestic, international, unknown]

        if loc is None:
	    unknown.append(review)
	elif loc.address.split(',')[-1].strip().lower() == "united states of america":
	    domestic.append(review)
	else:
	    international.append(review)
    return [domestic, international, unknown]
            
		

with open('keywords.txt') as f:
    lines = f.read()
keywords = lines.split()
data = extract('park_reviews.json', keywords)
with open('data/extracted_reviews.json', 'w') as output:
    json.dump(data, output, indent = 4)

[dom_data, int_data, unk_data] = split_by_country(data)
print('domestic reviews: {}\n international reviews: {}\n unknown location reivews: {}'.format(len(dom_data), len(int_data), len(unk_data)))

with open('data/domestic_reviews.json', 'a+') as output:
    json.dump(dom_data, output, indent = 4)

with open('data/international_reviews.json', 'a+') as output:
    json.dump(int_data, output, indent = 4)

with open('data/unknow_loc_reviews.json', 'a+') as output:
    json.dump(unk_data, output, indent = 4)



   
