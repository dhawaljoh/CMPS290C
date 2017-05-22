import json
import os

VARSHA = 1

CUISINE_CATEGORIES = ['chinese', 'french', 'korean', 'turkish', 'asian', 'indian', 'vietnamese', 'thai', 'mediterranean', \
            'japanese', 'german', 'european', 'irish', 'southern', 'malaysian', 'carribean', 'mexican', \
            'greek', 'lebanese', 'spanish', 'british', 'italian', 'cuban', 'american', 'brazilian', 'jamaican', \
            'palestinian', 'hawaiian', 'salvadorian', 'bosnian', 'pakistani']

if VARSHA == 1:
    DATA_PATH = os.path.join("/", "soe", "dhawal", "projects", "CMPS290C", "data", "Yelp", "yelp_dataset_challenge_round9")
else:
    DATA_PATH = os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9")

YELP_PATH = os.path.join("..", "data", "Yelp")
PSL_PATH = os.path.join("..", "psl", "data")

REVIEWS_FILE = os.path.join(DATA_PATH, "yelp_academic_dataset_review.json")
USERS_FILE = os.path.join(DATA_PATH, "yelp_academic_dataset_user.json")
FAVORITE_CUISINE_REVIEWS = os.path.join(YELP_PATH, "fav_cuisine_reviews.json")

PSL_FRIENDS_FILE = os.path.join(PSL_PATH, "friends.txt")
PSL_CUISINE_FILE = os.path.join(PSL_PATH, "cuisine.txt")
PSL_TARGET_FILE = os.path.join(PSL_PATH, "target.txt")
PSL_TRUTH_FILE = os.path.join(PSL_PATH, "truth.txt")
def common_friends_with_cuisine(user_ids):
    """
    Input: list of unique users with favourite cuisine
    Output: prints stats of the network
    """
    friend_count_1 = 0
    friend_count_2 = 0
    friend_count_3 = 0
    friend_count_more = 0
    count = 0
    common_friends_list = []
    user_ids_set = set(user_ids)
    with open(USERS_FILE, 'r') as uf:
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
    """
    Returns: Unique user_ids with favourite cuisines
    """
    user_ids = []
    with open(FAVORITE_CUISINE_REVIEWS) as rf:
        for line in rf:
            data = json.loads(line)
            user_id = data['user_id']
            if user_id not in user_ids:
                user_ids.append(user_id)

    return (user_ids)

def load_user_friends_list(user_ids, within_cuisine_network=False):
    """
    Input: list of unique users with favorite cuisine
    Returns: dictionary[userID] = [friend list]
    """
    user_friends = {}

    with open(USERS_FILE, "r") as inFile:
        for line in inFile:
            data = json.loads(line)
            friends = data["friends"]
            if within_cuisine_network:
                friends = list(set(friends) & set(user_ids))
            if data["user_id"] in user_ids and "None" not in friends and len(friends) > 0:
                user_friends[data["user_id"]] = data["friends"]
    
    return user_friends

def get_user_favorite_cuisine(review_text):
    """
    Input: review text
    Output: [list of cuisines]
    """
    review_list = review_text.lower().split()
    fav_cuisine = list(set(CUISINE_CATEGORIES) & set(review_list))
    return fav_cuisine

def load_user_cuisine_list(user_ids):
    """
    Input: list of unique users with favorite cuisine
    Output: dictionary[userID] = [cuisine list]
    """
    user_cuisine = {}
    
    with open(FAVORITE_CUISINE_REVIEWS, "r") as inFile:
        for line in inFile:
            data = json.loads(line)
            cuisines = get_user_favorite_cuisine(data["text"])
            if data["user_id"] in user_ids: #added to control number of users
		    if data["user_id"] in user_cuisine.keys():
			user_cuisine[data["user_id"]] += cuisines
		    else:
			user_cuisine[data["user_id"]] = cuisines
	    
    return user_cuisine

def write_in_file(file_name, dictionary):
    """
    Input: filename and a dictionary
    Output: generates file with all key and values
    """
    with open(file_name, "w") as out_file:
        for key, values in dictionary.iteritems():
            for val in list(set(values)): # to prevent the case if an user has mentioned the same cuisine twice
                out_file.write(key + "\t" + val + "\n")

def write_PSL_data_files(orig_user_ids, no_users):
    """
    Input: list of unique users with favorite cuisine, and a count of users to be loaded in file
    Output: data files for PSl
    """
    user_ids = orig_user_ids[:no_users]
    user_friends = load_user_friends_list(user_ids)
    user_cuisine = load_user_cuisine_list(user_ids)
    write_in_file(PSL_FRIENDS_FILE, user_friends) 
    write_in_file(PSL_CUISINE_FILE, user_cuisine)

    # Extract friends network from user_friends
    user_network = [x for x in user_friends.values()]
    all_people = []
    for friend_nw in user_network:
        all_people += friend_nw

    # Unioin of users in user_friends network and user_cuisine - Some people appear in friend lists but not in the dataset
    target_users = list(set(user_friends.keys()) | set(user_cuisine.keys()) | set(all_people))
    
    # write target file
    with open(PSL_TARGET_FILE, "w") as target_file:
        for user in target_users:
            for cuisine in CUISINE_CATEGORIES:
		if user in user_cuisine.keys():
            if cuisine not in user_cuisine[user]: # to remove observed entries from target file
                target_file.write(user + "\t" + cuisine + "\n")
		else:
			target_file.write(user + "\t" + cuisine + "\n")	

def write_data_subset_files(user_ids):
	# Get users from outside the network linked to the network
	no_users = 10
	i = 1
	min_friends_in_network = 30
	user_friends = {}
	users_with_cuisine = []
	with open(USERS_FILE, "r") as inFile:
		for line in inFile:
			if i > no_users:
				break
			data = json.loads(line)
			if data['user_id'] not in user_ids:
				friends_in_nw = list(set(user_ids) & set(data['friends']))
				if len(friends_in_nw) > 100:
					# friends_in_nw = friends_in_nw[:100]
					user_friends[data['user_id']] = friends_in_nw
					i += 1
					users_with_cuisine += friends_in_nw

	print "Done getting users"
	#remove duplicates from users_with_cuisine
	users_with_cuisine = list(set(users_with_cuisine))
	user_cuisine = load_user_cuisine_list(users_with_cuisine)

	write_in_file(PSL_FRIENDS_FILE, user_friends)
	write_in_file(PSL_CUISINE_FILE, user_cuisine)
	
	print "Wrote friends and cuisine files"
	all_people = users_with_cuisine

	target_users = list(set(user_friends.keys()) | set(user_cuisine.keys()) | set(all_people))
	print 'Number of users', len(target_users)
	# write target file
	with open(PSL_TARGET_FILE, "w") as target_file:
		for user in target_users:
			for cuisine in CUISINE_CATEGORIES:
				if user in user_cuisine.keys():
                    if cuisine not in user_cuisine[user]:
				        target_file.write(user + "\t" + cuisine + "\n")
				else:
					target_file.write(user + "\t" + cuisine + "\n")

# Function to write evaluation data
def write_eval_data(user_ids, split_ratio, no_user=-1):
    """
    Input: User_ids with cuisine info and no of users to restrict size of data
    Outputs: Writes data for PSL evaluation
    """
    if no_user == -1:
        no_user = len(user_ids)

    # Take only subset of user_ids
    no_user = no_user[:no_user]
    
    user_friends = load_user_friends_list(user_ids, within_cuisine_network=True)
    
    split_point = len(user_ids) * split_ratio
    
    # sort users according to number of friends
    sorted_user_ids = [k for k in sorted(user_friends, key=lambda k: len(user_friends[k]), reverse=True)]

    labeled_user_ids = sorted_user_ids[:split_point]
    unlabeled_user_ids = sorted_user_ids[split_point:]
    
    # get favorite cuisine info for labeled uers
    user_cuisine_labeled = load_user_cuisine_list(labeled_user_ids)
    user_cuisine_unlabeled = load_user_cuisine_list(unlabeled_user_ids)
    
    # all users with cuisine info
    user_cuisine_all = {**user_cuisine_labeled, **user_cuisine_unlabeled}
    
    write_in_file(PSL_CUISINE_FILE, user_cuisine_labeled)
    write_in_file(PSL_TRUTH_FILE, user_cuisine_unlabeld)
    write_in_file(PSL_FRIENDS_FILE, user_friends)

    # write target file

    with open(PSL_TARGET_FILE, 'w') as target_file:
        for user in user_ids:
            for cuisine in CUISINE_CATEGORIES:
                if cuisine not in user_cuisine_all[user]:
                    target_file.write(user + '\t' + cuisine + '\n') 


def main():
    user_ids = unique_users_cuisine_info()
    print len(user_ids)
    write_eval_data(user_ids, 0.8, 100)

    # write_data_subset_files(user_ids)
    # write_PSL_data_files(user_ids, 100)
    # write_PSL_data_files(user_ids, len(user_ids))
    # save_users_with_fav_cuisine(user_ids)
    # common_friends_with_cuisine(user_ids)

if __name__ == "__main__":
    main()
