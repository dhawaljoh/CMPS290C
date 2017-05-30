import dill
import os
import re
import sys

TRUTH_FILE = os.path.join("..", "psl", "data", "truth.txt")
PREDICTIONS_FILE = os.path.join("..", "psl", "groovy", "output", "default", "favoriteCuisine.txt")

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
			predicted_false_cuisines = [x[0] for x in predicted_cuisines[user] if x[1] == str(0)]

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

	return precision, accuracy

def main():
	get_truth()
	get_predictions(n=1)
	precision, accuracy = get_results(n=3)	
	print "Precision: {} \nAccuracy {}".format(precision, accuracy)

if __name__ == '__main__':
	main()