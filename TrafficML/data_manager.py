'''
    File name: data_manager.py
    Author: Kevin Lyons
    Date created: 4/14/2017
    Date last modified: 4/26/2017
    Python Version: 3.5
    Purpose: Create util functions to load data into pickle files. Also need to be able to extract min/max of data points for normalization analysis. Uses histogram for analysis.
'''

import glob, json, time, numpy as np, sys, os, pickle, matplotlib.pyplot as plt

# Custom imports
sys.path.insert(0, '../TrafficTreeSim/')

import cityiograph

from traffic_regression import get_features, get_results

# REGION: Global instance variable declarations
POP_ARR = [5, 8, 16, 16, 23, 59]
TRAIN_GOOD_DIR = '../../../data/train_good/*.json'
TEST_GOOD_DIR = '../../../data/test_good/*.json'
PREDICTIONS_DIR = './neural_predictions/*.json'

# REGION: Util methods

# Get population given an index in an array. Population array is constant
def get_population(t, density_array):
	if t not in range(0, 6):
		return 0
	return density_array[t] * POP_ARR[t]

def extract_features(directory):

	cities = []
	filenames = []
	input_features = []
	output_features = []

	files = glob.glob(directory)

	for name in files:
		with open(name, 'r') as f:
			city = cityiograph.City(f.read())
			cities.append(city)
			input_features.append(get_features(city))
			output_features.append(get_results(city))

	input_features = np.array(input_features).astype('int32')
	output_features = np.array(output_features).astype('int32')

	return cities, input_features, output_features

	# This funciton has been giving me some trouble when it comes to training the neural model - sticking with my custom extract_data functin below...

def extract_data(directory, return_endpoints=False):

	files = glob.glob(directory) # Load list of filenames from the directory

	cities = [] # City objects list
	filenames = [] # List of raw filenames
	inp = [] # Input feature matrix
	out = [] # Output feature matrix

	# Create dictionary mapping of bounds for both traffic and wait
	# bounds = { 'low_traffic' : 0 , 'high_traffic' : 0 , 'low_wait' : 0 , 'high_wait' : 0 }

	# Create np array objects for traffic and wait values
	traffic = []
	wait = []

	for name in files:
		with open(name, 'r') as f:
			current_input = []
			current_output = []
			s = f.read()
			city = cityiograph.City(s)
			cities.append(city) # Append city structure
			raw = os.path.splitext(os.path.basename(name))[0]
			filenames.append(raw) # Append raw filename for later reference
			d = json.loads(s)
			max_traffic = max([cell['data']['traffic'] for cell in d['grid'] if 'data' in cell])
			max_wait = max([cell['data']['wait'] for cell in d['grid'] if 'data' in cell])
			# Check bounds if needed
			if return_endpoints:
				traffic.append(max_traffic)
				wait.append(max_wait)
			# Ignore zero cities - suprisingly high percentage
			if max_traffic == 0 or max_wait == 0:
				continue
			# Else, construct feature vector for city
			for i in range(city.width):
				for j in range(city.height):
					cell = city.cells.get((i, j))
					current_input.append(cell.population)
					current_input.append(0) if (cell.type_id == 6) else current_input.append(1)
					current_output.append(cell.data["traffic"])
					current_output.append(cell.data["wait"])
			inp.append(np.array(current_input))
			out.append(np.array(current_output))

	# Return correct data based on return_endpoints parameter
	if return_endpoints:
		return np.array(traffic), np.array(wait)

	# Construct feature matrices and return
	inp = np.array(inp).astype(int)
	out = np.array(out).astype(int)

	return cities, filenames, inp, out

# Data manager...

# print('Extracting data...')

# train_data = extract_data(TRAIN_GOOD_DIR)
# test_data = extract_data(TEST_GOOD_DIR)

# pickle.dump(train_data, open('latest_data_train.p', 'wb'))
# pickle.dump(test_data, open('latest_data_test.p', 'wb'))

# Determining bounds on data

# train_bounds = extract_data(TRAIN_GOOD_DIR, return_endpoints = True)
# test_bounds = extract_data(TEST_GOOD_DIR, return_endpoints = True)

# print("Training bounds on raw data = {}.".format(train_bounds))
# print("Testing bounds on raw data = {}.".format(test_bounds))

# pred_bounds = extract_data(PREDICTIONS_DIR, return_endpoints = True)

# print("Prediction bounds (2000 cities) = {}.".format(pred_bounds))

# Get bounds

# traffic, wait = extract_data(PREDICTIONS_DIR, return_endpoints = True)

# Write to local pickle files

TRAIN_BOUNDS_NAME = './bounds/train.p'
TEST_BOUNDS_NAME = './bounds/test.p'
PRED_BOUNDS_NAME = './bounds/pred.p'

# pickle.dump((traffic, wait), open(PRED_BOUNDS_NAME, 'wb'))

# Load from pickle file

traffic, wait = pickle.load(open(PRED_BOUNDS_NAME, 'rb'))

# Compute metrics from this data

# traffic_mean = np.mean(traffic); print("Traffic mean =", traffic_mean);
# traffic_std = np.std(traffic); print("Traffic std =", traffic_std);
# traffic_max = np.max(traffic); print("Traffic max =", traffic_max);
# traffic_min = np.min(traffic); print("Traffic min =", traffic_min);
# wait_mean = np.mean(wait); print("Wait mean =", wait_mean);
# wait_std = np.std(wait); print("Wait std =", wait_std);
# wait_max = np.max(wait); print("Wait max =", wait_max);
# wait_min = np.min(wait); print("Wait min =", wait_min);

# print(traffic_mean, traffic_std, traffic_max, traffic_min, wait_mean, wait_std, wait_max, wait_min)

# Now, take action with these metrics...

# Plot histogram

plt.hist(wait, bins='auto')
plt.title('Predicted Wait (CNN)')
plt.show()

# print('Successfully extracted test data. Wrote to local pickle files.')

print("Process complete.")