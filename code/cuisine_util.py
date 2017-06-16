import json
import os
import pickle
from collections import Counter
import subprocess
import sys

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
# Creating dummy data folder
PSL_PATH = os.path.join("..", "psl", "data")

REVIEWS_FILE = os.path.join(DATA_PATH, "yelp_academic_dataset_review.json")
USERS_FILE = os.path.join(DATA_PATH, "yelp_academic_dataset_user.json")
FAVORITE_CUISINE_REVIEWS = os.path.join(YELP_PATH, "fav_cuisine_reviews.json")

# pickle files
USER_IDS_WITH_CUISINE = os.path.join(YELP_PATH, "user_ids_with_cuisine_friends")

USER_USEFUL = os.path.join(YELP_PATH, "user_useful_votes")
USER_FUNNY = os.path.join(YELP_PATH, "user_funny_votes")
USER_COOL = os.path.join(YELP_PATH, "user_cool_votes")
USER_FANS = os.path.join(YELP_PATH, "user_fans_votes")

EVAL_USER_FRIENDS = os.path.join(YELP_PATH, "eval_user_friends")
EVAL_USER_LABELED_CUISINE = os.path.join(YELP_PATH, "eval_user_labeled_cuisine")
EVAL_USER_UNLABELED_CUISINE = os.path.join(YELP_PATH, "eval_user_unlabeled_cuisine")

PSL_USER_USEFUL_FILE = os.path.join(PSL_PATH, "useful.txt")
PSL_USER_COOL_FILE = os.path.join(PSL_PATH, "cool.txt")
PSL_USER_FUNNY_FILE = os.path.join(PSL_PATH, "funny.txt")
PSL_USER_FANS_FILE = os.path.join(PSL_PATH, "fans.txt")
PSL_FRIENDS_FILE = os.path.join(PSL_PATH, "friends.txt")
PSL_CUISINE_FILE = os.path.join(PSL_PATH, "cuisine.txt")
PSL_FAVORITE_CUISINE_TARGET_FILE = os.path.join(PSL_PATH, "favoriteCuisineTarget.txt")
PSL_SOCIAL_INFLUENCE_TARGET_FILE = os.path.join(PSL_PATH, "socialInfluenceTarget.txt")
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
    print 'max number of friends: ', len(max(common_friends_list, key=len))


def unique_users_cuisine_info():
    """
    Returns: Unique user_ids with favourite cuisines and at least 1 friend
    """
    
    if os.path.exists(USER_IDS_WITH_CUISINE):
        user_ids = pickle.load(open(USER_IDS_WITH_CUISINE))
    else:
        user_ids = []
        with open(FAVORITE_CUISINE_REVIEWS) as rf:
            for line in rf:
                data = json.loads(line)
                user_id = data['user_id']
                if user_id not in user_ids:
                    user_ids.append(user_id)
        pickle.dump(user_ids, open(USER_IDS_WITH_CUISINE, 'w'))    

    return (user_ids)

def load_user_friends_list(user_ids, within_cuisine_network=False):
    """
    Input: list of unique users with favorite cuisine
    Returns: dictionary[userID] = [friend list], if within_cuisine_network is set, only friends in network
    """
    user_friends = {}

    with open(USERS_FILE, "r") as inFile:
        for line in inFile:
            data = json.loads(line)
            friends = data["friends"]
            if within_cuisine_network:
                friends = list(set(friends) & set(user_ids))
            if data["user_id"] in user_ids and "None" not in friends and len(friends) > 0:
                user_friends[data["user_id"]] = friends
    
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

def get_cuisine_count_sorted(user_cuisine):
    """
    Input: User cuisine dictionary from load_user_cuisine_list()
    Output: User cuisine dictionary with count user_cuisine_count[user_id] = [(cuisine, count)]
    """
    user_cuisine_count = {}
    for user, cuisine in user_cuisine.iteritems():
        cuisine_count = Counter(cuisine).items()
        cuisine_count.sort(key=lambda x: x[1], reverse=True)
        user_cuisine_count[user] = cuisine_count

    return user_cuisine_count

def get_business_average_stars():
    """
    Output: returns average business rating for restaurants reviewed by user
    """

    # get businesses and star count

    user_business = {}
    with open(FAVORITE_CUISINE_REVIEWS, 'r') as fc:
        for line in fc:
            data = json.loads(line)
            user_id = data['user_id']
            stars = data['stars']
            business_id = data['business_id']
            if user_id not in user_business:
                user_business[user_id] = {business_id: [stars, 1]}
            else:
                if business_id in user_business[user_id]:
                    user_business[user_id][business_id][0] += stars
                    user_business[user_id][business_id][1] += 1
                else:
                    user_business[user_id][business_id] = [stars, 1]

    user_business_average = {}
    for user, business_dict in user_business.iteritems():
        # list of tuples
        business_average = []
        for business in business_dict:
            average = business_dict[business][0]/float(business_dict[business][1])
            business_average.append((business, average))
        user_business_average[user] = business_average

    return user_business_average

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
    with open(PSL_FAVORITE_CUISINE_TARGET_FILE, "w") as target_file, \
        open(PSL_SOCIAL_INFLUENCE_TARGET_FILE, "w") as influence_target_file:
        for user in target_users:
            for cuisine in CUISINE_CATEGORIES:
                if user in user_cuisine.keys():
                    if cuisine not in user_cuisine[user]: # to remove observed entries from target file
                        target_file.write(user + "\t" + cuisine + "\n")
                else:
                    target_file.write(user + "\t" + cuisine + "\n")
                influence_target_file.write(user + "\t" + cuisine + "\n")

    
def write_data_subset_files(user_ids):
    # get users from outside the network linked to the network
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
    # remove duplicates from users_with_cuisine
    users_with_cuisine = list(set(users_with_cuisine))
    user_cuisine = load_user_cuisine_list(users_with_cuisine)

    write_in_file(PSL_FRIENDS_FILE, user_friends)
    write_in_file(PSL_CUISINE_FILE, user_cuisine)

    print "Wrote friends and cuisine files"
    all_people = users_with_cuisine

    target_users = list(set(user_friends.keys()) | set(user_cuisine.keys()) | set(all_people))
    print 'Number of users', len(target_users)
	# write target file
    with open(PSL_FAVORITE_CUISINE_TARGET_FILE, "w") as target_file, \
        open(PSL_SOCIAL_INFLUENCE_TARGET_FILE, "w") as influence_target_file:
        for user in target_users:
            for cuisine in CUISINE_CATEGORIES:
                if user in user_cuisine.keys():
                    if cuisine not in user_cuisine[user]:
                        target_file.write(user + "\t" + cuisine + "\n")
                else:
                    target_file.write(user + "\t" + cuisine + "\n")
                influence_target_file.write(user + "\t" + cuisine + "\n")

# Function to write evaluation data
def write_eval_data(user_ids, split_ratio, no_user=-1):
    """
    Input: User_ids with cuisine info and no of users to restrict size of data
    Outputs: Writes data for PSL evaluation
    """
    if no_user != -1:
        # take only subset of user_ids
        user_ids = user_ids[:no_user]
    
    if no_user == -1 and os.path.exists(EVAL_USER_FRIENDS):
        user_friends = pickle.load(open(EVAL_USER_FRIENDS))
    else:
        user_friends = load_user_friends_list(user_ids, within_cuisine_network=True)
        if no_user == -1:
            pickle.dump(user_friends, open(EVAL_USER_FRIENDS, "w"))

   
    # users with at least one friend 
    user_ids = user_friends.keys()
    
    split_point = int(len(user_ids) * split_ratio)
    
    # sort users according to number of friends
    # sorted_user_ids = [k for k in sorted(user_friends, key=lambda k: len(user_friends[k]), reverse=True)]
    # Changed sorting order to descending to capture influence of more friend
    sorted_user_ids = [k for k in sorted(user_friends, key=lambda k: len(user_friends[k]))]

    # take friends with maximum users as labeled
    user_ids_labeled = sorted_user_ids[:split_point]
    user_ids_unlabeled = sorted_user_ids[split_point:]
    
    # get favorite cuisine info for labeled uers

    if no_user == -1 and os.path.exists(EVAL_USER_LABELED_CUISINE):
        user_cuisine_labeled = pickle.load(open(EVAL_USER_LABELED_CUISINE))
        user_cuisine_unlabeled = pickle.load(open(EVAL_USER_UNLABELED_CUISINE)) 
    else:
        user_cuisine_labeled = load_user_cuisine_list(user_ids_labeled)
        user_cuisine_unlabeled = load_user_cuisine_list(user_ids_unlabeled)
        if no_user == -1:
            pickle.dump(user_cuisine_labeled, open(EVAL_USER_LABELED_CUISINE, "w"))
            pickle.dump(user_cuisine_unlabeled, open(EVAL_USER_UNLABELED_CUISINE, "w"))

    # ***********************************************************************
    # load attributes: useful, friendly, cool, funny
    if no_user == -1 and os.path.exists(USER_USEFUL):
        user_useful = pickle.load(open(USER_USEFUL))
    else:
        user_useful = get_votes(user_ids, "useful", minimum_votes=25)
        if no_user == -1:
            print "dumping in pickle file"
            pickle.dump(user_useful, open(USER_USEFUL, "w"))
    
    if no_user == -1 and os.path.exists(USER_FUNNY):
        user_funny = pickle.load(open(USER_FUNNY))
    else:
        user_funny = get_votes(user_ids, "funny", minimum_votes=15)
        if no_user == -1:
            print "dumping in pickle file"
            pickle.dump(user_funny, open(USER_FUNNY, "w"))

    if no_user == -1 and os.path.exists(USER_COOL):
        user_cool = pickle.load(open(USER_COOL))
    else:
        user_cool = get_votes(user_ids, "cool", minimum_votes=21)
        if no_user == -1:
            print "dumping in pickle file"
            pickle.dump(user_cool, open(USER_COOL, "w"))
    
    if no_user == -1 and os.path.exists(USER_FANS):
        user_fans = pickle.load(open(USER_FANS))
    else:
        user_fans = get_votes(user_ids, "fans", minimum_votes=1)
        if no_user == -1:
            print "dumping in pickle file"
            pickle.dump(user_fans, open(USER_FANS, "w"))

    # ***********************************************************************
    write_in_file(PSL_CUISINE_FILE, user_cuisine_labeled)
    write_in_file(PSL_TRUTH_FILE, user_cuisine_unlabeled)
    write_in_file(PSL_FRIENDS_FILE, user_friends)
    write_in_file(PSL_USER_USEFUL_FILE, user_useful)
    write_in_file(PSL_USER_COOL_FILE, user_cool)
    write_in_file(PSL_USER_FUNNY_FILE, user_funny)
    write_in_file(PSL_USER_FANS_FILE, user_fans)

    # write target file
    with open(PSL_FAVORITE_CUISINE_TARGET_FILE, 'w') as target_file, \
        open(PSL_SOCIAL_INFLUENCE_TARGET_FILE, "w") as influence_target_file:
        for user in user_ids:
            for cuisine in CUISINE_CATEGORIES:
                if user in user_cuisine_labeled.keys():
                    if cuisine not in user_cuisine_labeled[user]:
                        target_file.write(user + '\t' + cuisine + '\n')
                else:
                    target_file.write(user + '\t' + cuisine + '\n')
                influence_target_file.write(user + '\t' + cuisine + '\n')

def get_votes(user_ids, attribute, minimum_votes=sys.maxint):
    """
    Input: user_ids with cuisine information, attribute to be retrived from json file and minimum no of votes to be written
    Output: returns user_ids and attribute votes dictionary
    """
    user_useful = {}
    with open(USERS_FILE) as uf:
        for line in uf:
            data = json.loads(line)
            user_id = data['user_id']
            if user_id in user_ids:
                useful_votes = data[attribute]
                if useful_votes > minimum_votes:
                    user_useful[user_id] = [user_id]
    return user_useful 

def main():
    user_ids = unique_users_cuisine_info()
    print len(user_ids)
    write_eval_data(user_ids, 0.8, no_user=5000)
    # write_data_subset_files(user_ids)
    # write_PSL_data_files(user_ids, 100)
    # write_PSL_data_files(user_ids, 100)
    # write_PSL_data_files(user_ids, len(user_ids))
    # save_users_with_fav_cuisine(user_ids)
    # common_friends_with_cuisine(user_ids)

if __name__ == "__main__":
    main()
