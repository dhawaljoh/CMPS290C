import cuisine_util
from sklearn.svm import SVC
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from collections import Counter


user_cuisine_count_sorted ={}

def SVM(training_features, labels):
    clf = SVC()
    classifier = clf.fit(training_features, labels)
    return classifier


# load features: business_ids and average stars
def load_input_features_business_ids(user_ids):
    """
    Input: user_ids
    Output: feature vector: [[features for user_id1]]
    """
    # average stars for very business user has visited
    user_business_average_stars = cuisine_util.get_business_average_stars()

    # set of business_ids
    unique_business_list = list(set([x[0] for user, bus_list in user_business_average_stars.iteritems() for x in bus_list]))

    feature_vectors = []
    for user in user_ids:
        vector = [0] * len(unique_business_list)
        businesses = user_business_average_stars[user]
        for business in businesses:
            vector[unique_business_list.index(business[0])] = business[1]
        feature_vectors.append(vector)
        
    return feature_vectors

def get_labels(user_ids):
    """
    Input: user_ids
    Output: list of favorit cuisines in int format
    """
    user_cuisine = cuisine_util.load_user_cuisine_list(user_ids)
    # favorite cuisine and count for users
    user_cuisine_count_sorted = cuisine_util.get_cuisine_count_sorted(user_cuisine) 
    labels = []
    for user in user_ids:
        cuisine_list = user_cuisine_count_sorted[user]
        if len(cuisine_list) > 0:
            fav_cuisine = cuisine_list[0][0]
            labels.append(cuisine_util.CUISINE_CATEGORIES.index(fav_cuisine))
        else:
            labels.append(-1)

    return labels

def load_input_features_cuisines(user_ids):
    """
    Input: user_ids
    Output: feature vector: [[cuisines 1/0]]
    """
    feature_vector = []
    for user in user_ids:
        features = [0] * len(cuisine_util.CUISINE_CATEGORIES)
        fav_cuisines = user_cuisine_count_sorted[user]
        for cuisine in fav_cuisines:
            cuisine_index = cuisine_util.CUISINE_CATEGORIES.index(cuisine[0])
            cuisine_count = cuisine[1]
            features[cuisine_index] = cuisine_count
        feature_vector.append(features)
    print feature_vector
    return feature_vector

def classify(split_ratio):
    user_ids = cuisine_util.unique_users_cuisine_info()
    #user_cuisine = cuisine_util.load_user_cuisine_list(user_ids)

    # create features
    #input_features = load_input_features_business_ids(user_ids)
    input_features = load_input_features_cuisines(user_ids)

    # get the highest label in int format
    labels = get_labels(user_ids)
 
    split_point = int(len(user_ids) * split_ratio)

    train_x, test_x = input_features[:split_point], input_features[split_point:]
    train_y, test_y = labels[:split_point], labels[split_point:]

    classifier_model = SVM(train_x, train_y)
    
    pred_y = classifier_model.predict(test_x)

    conf_matrix = confusion_matrix(test_y, pred_y)

    accuracy = accuracy_score(test_y, pred_y)

    print "conf_matrix", conf_matrix
    print "accuracy", accuracy
    print "no of labels: ", len(labels)
    print "no of -1: ", Counter(labels)

    return conf_matrix, accuracy


def main():
    classify(0.8)


if __name__ == '__main__':
    main()
