import json
import os
import sys

def load_data():
	with open(os.path.join("..", "data", "Yelp")) as data_file:
		data = json.load(data_file)

def main():

if __name__ == '__main__':
	main()