import json
import os

VARSHA = 0

CUISINE_CATEGORIES = ['chinese', 'french', 'korean', 'turkish', 'asian', 'indian', 'vietnamese', 'thai', 'mediterranean', \
            'japanese', 'german', 'european', 'irish', 'southern', 'malaysian', 'carribean', 'mexican', \
            'greek', 'lebanese', 'spanish', 'british', 'italian', 'cuban', 'american', 'brazilian', 'jamaican' \
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
PSL_USER_CUISINE_FILE = os.path.join(PSL_PATH, "target.txt")

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

def load_user_friends_list(user_ids):
    """
    Input: list of unique users with favorite cuisine
    Returns: dictionary[userID] = [friend list]
    """
    user_friends = {}

    with open(USERS_FILE, "r") as inFile:
        for line in inFile:
            data = json.loads(line)
            if data["user_id"] in user_ids and "None" not in data["friends"]:
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

def write_PSL_data_files(user_ids):
    """
    Input: list of unique users with favorite cuisine
    Output: data files for PSl
    """
    user_friends = load_user_friends_list(user_ids)
    user_cuisine = load_user_cuisine_list(user_ids)
    
    write_in_file(PSL_FRIENDS_FILE, user_friends) 
    write_in_file(PSL_CUISINE_FILE, user_cuisine)

    #write target file
    with open(PSL_USER_CUISINE_FILE, "w") as target_file:
        for user in user_ids:
            for cuisine in CUISINE_CATEGORIES: 
                target_file.write(user + "\t" + cuisine + "\n")

def main():
    user_ids = unique_users_cuisine_info()
    print len(user_ids)
    write_PSL_data_files(user_ids)
    #save_users_with_fav_cuisine(user_ids)
    # common_friends_with_cuisine(user_ids)

if __name__ == "__main__":
    main()
