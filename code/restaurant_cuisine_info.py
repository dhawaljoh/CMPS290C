import json
import os

'''
Output:
No of restaurant with cuisine info: 20612
No of restaurant: 48485

users with cuisine info: 21600
users with fav cuisine info: 13017
Total users: 1029432
'''

CUISINE_CATEGORIES = ['chinese', 'french', 'korean', 'turkish', 'asian', 'indian', 'vietnamese', 'thai', 'mediterranean', \
			'japanese', 'german', 'european', 'irish', 'southern', 'malaysian', 'carribean', 'mexican', \
			'greek', 'lebanese', 'spanish', 'british', 'italian', 'cuban', 'american', 'brazilian', 'jamaican' \
			'palestinian', 'hawaiian', 'salvadorian', 'bosnian', 'pakistani']

def restaurants_with_cuisine_info():
	business_file_name = "yelp_academic_dataset_business.json"
	business_file = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", business_file_name)

	#Business Ids with cuisine mentioned in the category
	business_ids_with_cuisine = []
	business_cuisine = {}
	#Business Ids with restaurant mentioned in the category
	business_ids_with_restaurant = []

	with open(business_file) as bf:
		for line in bf:
			business = json.loads(line)
			if u'categories' in business.keys():
				if business[u'categories'] is not None:
					categories_lower = [x.lower() for x in business[u'categories']]
					#print categories_lower
					if u'restaurants' in categories_lower:
						business_ids_with_restaurant.append(business[u'business_id'])
					cuisine = list(set(categories_lower) & set(CUISINE_CATEGORIES))
					if len(cuisine) > 0:
						business_ids_with_cuisine.append(business[u'categories'])
						business_cuisine[business[u'business_id']] = cuisine
					if len(cuisine) > 1:
						1+1
						#print cuisine


	print 'No of restaurant with cuisine info: ', len(business_ids_with_cuisine)
	print 'No of restaurant: ', len(business_ids_with_restaurant)
	#print business_cuisine


def user_with_cuisie_info():
	review_file_name = "yelp_academic_dataset_review.json"
	review_file = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", review_file_name)

	user_with_cuisine = {}
	users_with_fav_cuisine = {}

	with open(review_file) as rf:
		for line in rf:
			review = json.loads(line)
			if u'cuisin' in review[u'text'].lower():
				if int(review[u'stars']) > 2:
					review_list = review['text'].lower().split()
					fav_cuisine = list(set(CUISINE_CATEGORIES) & set(review_list))
					if len(fav_cuisine) > 0:
						users_with_fav_cuisine[review[u'user_id']] = fav_cuisine
				if review[u'user_id'] in user_with_cuisine.keys():
					user_with_cuisine[review[u'user_id']] += 1
				else:
					user_with_cuisine[review[u'user_id']] = 1

	print 'users with cuisine info: ', len(user_with_cuisine.keys())
	print 'users with fav cuisine info: ', len(users_with_fav_cuisine.keys())

user_with_cuisie_info()
