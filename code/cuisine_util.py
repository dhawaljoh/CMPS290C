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


def user_with_cuisine_info():
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

	print users_with_fav_cuisine
	print 'users with cuisine info: ', len(user_with_cuisine.keys())
	print 'users with fav cuisine info: ', len(users_with_fav_cuisine.keys())

def user_without_friends(user_ids):
	user_file_name = "yelp_academic_dataset_user.json"
	user_file = "/soe/dhawal/projects/CMPS290C/data/Yelp/yelp_dataset_challenge_round9/" + user_file_name
        #user_file = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", user_file_name)

	count = 0
	with open(user_file, 'r') as uf:
		for line in uf:
			data = json.loads(line)
			if data['user_id'] in user_ids:
				friends = data['friends']
				if 'None' in friends:
					count += 1

	print count		

'''
Output:
Total frinds in cuisine network 6153
friend_count_1 1645
friend_count_2 880
friend_count_3 527
friend_count_more 3101
max umber of friends:  715
'''

def common_friends_with_cuisine(user_ids):
	user_file_name = "yelp_academic_dataset_user.json"
        user_file = "/soe/dhawal/projects/CMPS290C/data/Yelp/yelp_dataset_challenge_round9/" + user_file_name
        #user_file = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", user_file_name)

        friend_count_1 = 0
	friend_count_2 = 0
	friend_count_3 = 0
	friend_count_more = 0
	count = 0
	common_friends_list = []
	user_ids_set = set(user_ids)
        with open(user_file, 'r') as uf:
                for line in uf:
                        data = json.loads(line)
                        if data['user_id'] in user_ids:
                                friends = data['friends']
				common_friends = list(set(friends) & user_ids_set)
				no_friends = len(common_friends)
                                if no_friends > 0:
					if no_friends == 1 : friend_count_1 += 1
					elif no_friends == 2 : friend_count_2 += 1
					elif no_friends == 3 : friend_count_3 += 1
					else: 
						friend_count_more += 1
                                        count += 1
					common_friends_list.append(common_friends)

        print "friends in network", count
	print 'friend_count_1', friend_count_1
	print 'friend_count_2', friend_count_2
	print 'friend_count_3', friend_count_3
	print 'friend_count_more', friend_count_more
	print 'max umber of friends: ', len(max(common_friends_list, key=len))


def unique_users_cuisine_info():
	review_file_name = "fav_cuisine_reviews.json"
	review_file = os.path.join("..", "data", "Yelp", review_file_name)

	user_ids = []
	with open(review_file) as rf:
		for line in rf:
			data = json.loads(line)
			user_id = data['user_id']
			if user_id not in user_ids:
				user_ids.append(user_id)

	return (user_ids)

def save_users_with_fav_cuisine(user_ids):
    review_file_name = "fav_cuisine_reviews.json"
    review_file = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", review_file_name)

    out_file = os.path.join("..", "data", "Yelp", "users_with_favorite_cuisine.json")
    
    with open(out_file, "w") as outFile:
        with open(review_file, "r") as inFile:
            for line in inFile:
                data = json.loads(line)
                if data["user_id"] in user_ids:
                    json.dump(outFile, data)
                    outFile.write("\n")

user_ids = unique_users_cuisine_info()
print len(users_ids)
save_users_with_fav_cuisine(user_ids)

# common_friends_with_cuisine(user_ids)
#user_without_friends()
#user_with_cuisine_info()
