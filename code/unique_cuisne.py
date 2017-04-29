import json

review_input_file = '../cmps-296/yelp_academic_dataset_review.json'

business_ids = []
review_data = []

with open(review_input_file) as data_file:
	for new_line in data_file:
		if ('cuisine' in s for s in json.loads(new_line).values()):
			if json.loads(new_line)['business_id'] not in business_ids:
				business_ids.append(json.loads(new_line)[u'business_id'])

print len(business_ids)
				

