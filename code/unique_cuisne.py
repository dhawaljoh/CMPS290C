import json

review_input_file = '/soe/vajoshi/cmps-290/CMPS290C/data/Yelp/yelp_dataset_challenge_round9/yelp_academic_dataset_review.json'

business_ids = []
review_data = []

with open(review_input_file) as data_file:
	for new_line in data_file:
		if ('cuisine' in s for s in json.loads(new_line).values()):
			business_id = json.loads(new_line)[u'business_id']
			if business_id not in business_ids:
				business_ids.append(business_id)

print len(business_ids)
				

