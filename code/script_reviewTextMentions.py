# -*- coding: utf-8 -*-

import json
import os
import sys
import unicodedata

CUISINE_CATEGORIES = ['chinese', 'french', 'korean', 'turkish', 'asian', 'indian', 'vietnamese', 'thai', 'mediterrenean', \
						'japanese', 'german', 'european', 'irish', 'southern', 'malaysian', 'carribean', 'french', 'mexican', 'greek', 'lebanese', 'spanish', 'british']

def loadData(dataFile, attributes):
	"""
	Returns: dictionary: key = businessId, value = [neigborhood, city, state]
	"""

	ret = {}
	with open(os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", dataFile)) as data_file:
		for line in data_file:
			line_data = json.loads(line)
			ret[line_data[attributes[0]]] = [line_data[attributes[1]], line_data[attributes[2]], line_data[attributes[3]]]
	return ret

def crossProd(array):
	temp = []
	array = [ele for ele in array if ele != '']

	for i in range(len(array) - 1):
		for j in range(i+1, len(array)):
			temp.append((array[i], array[j]))
	return temp


def getUnicoded(word):
	return unicodedata.normalize('NFKD', word).encode('ascii', 'ignore')


def writeToFile(array):
	with open(os.path.join("..", "psl", "similarCuisine.txt"), 'w') as out_file:
		for ele in array:
			out_file.write(getUnicoded(ele[0]) + "\t" + getUnicoded(ele[1]) + "\n")


def writeToFile2(dictionary):
	with open(os.path.join("..", "psl", "restaurantLocation.txt"), 'w') as out_file:
		for business in dictionary.keys():
			if dictionary[business][0] != '':
				out_file.write(business + "\t" + getUnicoded(dictionary[business][0]) + "\n")
			if dictionary[business][1] != '':
				out_file.write(business + "\t" + getUnicoded(dictionary[business][1]) + "\n")
			if dictionary[business][2] != '':
				out_file.write(business + "\t" + getUnicoded(dictionary[business][2]) + "\n")

def loadReviewData(dataFile, attributes, businessIds=[]):
	temp = {}
	with open(os.path.join("..", "data", "Yelp", "yelp_dataset_challenge_round9", dataFile)) as data_file:
		for line in data_file.read().split("\n")[:1000]:
			line_data = json.loads(line)
			for cuisine in CUISINE_CATEGORIES:
				if cuisine in line_data:
					temp[line_data['business_id']] = cuisine

	return temp



def main():
	data = loadData('yelp_academic_dataset_business.json', ['business_id', 'neighborhood', 'city', 'state'])
	
	neighborhoods = [data[key][0] for key in data.keys() if data[key][0] != '']
	cities = [data[key][1] for key in data.keys() if data[key][1] != '']
	states = [data[key][2] for key in data.keys() if data[key][2] != '']

	uniqueNeighborhoods = list(set(neighborhoods))
	uniqueCities = list(set(cities))
	uniqueStates = list(set(states))

	#/////////////TEST///////////////
	# Restricting to 1000 businesses in interest of time
	smallKeySet = data.keys()[:100]
	crossProductBusinesses = crossProd(smallKeySet)
	crossProductNeighborhoods = crossProd(list(set([data[key][0] for key in smallKeySet])))
	crossProductCities = crossProd(list(set([data[key][1] for key in smallKeySet])))
	crossProductStates = crossProd(list(set([data[key][2] for key in smallKeySet])))
	
	writeToFile(crossProductBusinesses + crossProductNeighborhoods + crossProductCities + crossProductStates)
	writeToFile2(dict((k, data[k]) for k in smallKeySet))
	#////////////////////////////////

	#///////////////////load cuisine////////////
	review_data = loadReviewData('yelp_academic_dataset_review.json', ['business_id', 'review_text'], smallKeySet)
	print review_data
	#///////////////////////////////////////////



if __name__ == '__main__':
	main()