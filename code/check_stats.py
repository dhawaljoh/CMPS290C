import dill
import os
import re
import sys
import numpy as np
TRUTH_FILE = os.path.join("..", "psl", "data", "truth.txt")
PREDICTIONS_FILE = os.path.join("..", "psl", "groovy", "output", "default", "favoriteCuisine.txt")
#PREDICTIONS_FILE = os.path.join("..", "psl", "groovy", "output", "default", "socialInfluence.txt")

CUISINE_CATEGORIES = ['chinese', 'french', 'korean', 'turkish', 'asian', 'indian', 'vietnamese', 'thai', 'mediterranean', \
            'japanese', 'german', 'european', 'irish', 'southern', 'malaysian', 'carribean', 'mexican', \
            'greek', 'lebanese', 'spanish', 'british', 'italian', 'cuban', 'american', 'brazilian', 'jamaican', \
            'palestinian', 'hawaiian', 'salvadorian', 'bosnian', 'pakistani']

predicted_cuisines = {}
truth_cuisines = {}

def get_truth():
	"""
	Populates truth_cuisines dictionary with dict(userId) = [list of favorite cuisines]
	"""
	with open(TRUTH_FILE, 'r') as in_file:
		for line in in_file:
			line = line.strip('\n').split("\t")
			if line[0] in truth_cuisines:
				truth_cuisines[line[0]] += [line[1]]
			else:
				truth_cuisines[line[0]] = [line[1]]

def get_predictions(n=-1):
	"""
	Populates predicted_cuisines dictionary with dict(userId) = [list of n favoriteCuisines]
	"""
	with open(PREDICTIONS_FILE, 'r') as in_file:
		in_file = in_file.read().split("\n") # removes the "--- Atoms:" line from the predictions file
		for line in in_file[1:-2]:
			match = re.search(r'\(\'(.*)\'\,\s\'(\w*)\'\).*\[(.*)\]', line)
			user = match.group(1)
			cuisine = match.group(2)
			truth = match.group(3)
			if user in predicted_cuisines:
				predicted_cuisines[user] += [(cuisine, truth)]
			else:
				predicted_cuisines[user] = [(cuisine, truth)]

	for user, cuTr in predicted_cuisines.iteritems():
		cuTr.sort(key=lambda x: x[1], reverse=True)
		'''if n != -1 and n <= 30:
			cuTr = cuTr[:n]
			predicted_cuisines[user] = [x[0] for x in cuTr]'''

def get_results(n=-1):
    """
    Input: n - number of top cuisines per user to consider
    """
    true_positives = 0
    true_negatives = 0
    false_positives = 0
    false_negatives = 0
    for user in truth_cuisines.keys():
        truth_true_cuisines = truth_cuisines[user]
        truth_false_cuisines = list(set(CUISINE_CATEGORIES) - set(truth_true_cuisines))
        if user in predicted_cuisines:
            predicted_true_cuisines = [x[0] for x in predicted_cuisines[user][:n]]
            predicted_false_cuisines = [x[0] for x in predicted_cuisines[user] if float(x[1]) < 0.05]
            if len(set(truth_true_cuisines) & set(predicted_true_cuisines)) > 0:
                true_positives += 1
            if len(set(truth_false_cuisines) & set(predicted_false_cuisines)) > 0:
                true_negatives += 1
            if len(set(truth_true_cuisines) & set(predicted_false_cuisines)) > 0:
                false_negatives += 1
            if len(set(truth_false_cuisines) & set(predicted_true_cuisines)) > 0:
                false_positives += 1

    # precision
    precision = true_positives/float(true_positives + false_positives)
    accuracy = (true_positives + true_negatives)/float(true_positives + true_negatives + false_positives + false_negatives)

    print "total users in truth", len(truth_cuisines.keys())
    print "true_positives", true_positives
    print "true_negatives", true_negatives
    print "false_negatives", false_negatives
    print "false_positives", false_positives

    return precision, accuracy

def create_confusion_matrix(n):
    no_classes = len(CUISINE_CATEGORIES)
    confusion_matrix = [[0  for i in range(no_classes)] for i in range(no_classes)]
   
    for user in truth_cuisines.keys():
        user_truth_cuisines = truth_cuisines[user]
        if user in predicted_cuisines:
            predicted_true_cuisines = [x[0] for x in predicted_cuisines[user][:n]]
            for cuisine in user_truth_cuisines:
                if cuisine in predicted_true_cuisines:
                    cuisine_index = CUISINE_CATEGORIES.index(cuisine)
                    confusion_matrix[cuisine_index][cuisine_index] += 1
                    user_truth_cuisines.remove(cuisine)
                    predicted_true_cuisines.remove(cuisine)
            while len(user_truth_cuisines) > 0 and len(predicted_true_cuisines) > 0:
                truth_index = CUISINE_CATEGORIES.index(user_truth_cuisines[0])
                predicted_index = CUISINE_CATEGORIES.index(predicted_true_cuisines[0])
                confusion_matrix[truth_index][predicted_index] += 1
                user_truth_cuisines.pop(0)
                predicted_true_cuisines.pop(0)


    confusion_np = np.matrix(confusion_matrix)
    
    accuracy = np.trace(confusion_np)/float(np.matrix.sum(confusion_np))
    precision = np.diag(confusion_np).astype(float)/(np.matrix.transpose(confusion_np.sum(axis=1)))
    recall = np.diag(confusion_np).astype(float)/(confusion_np.sum(axis=0))
    F1 = (2 * np.multiply(precision, recall))/precision + recall
    print "accuracy", accuracy
    print CUISINE_CATEGORIES

    print "precision"
    print precision

    print "recall"
    print recall

    print "F1"
    print F1
    
    print np.diag(confusion_np)

def main():
    get_truth()
    get_predictions(n=3)
    create_confusion_matrix(n=3)
    #precision, accuracy = get_results(n=3)
    #print "Precision: {} \nAccuracy {}".format(precision, accuracy)

if __name__ == '__main__':
	main()
