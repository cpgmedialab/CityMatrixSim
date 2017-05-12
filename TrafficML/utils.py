'''
    File name: utils.py
    Author(s): Kevin Lyons
    Date created: 5/12/2017
    Date last modified: 5/12/2017
    Python Version: 3.5
    Purpose: Simple utils script to be used alongside prediction_server. Various tasks, including model serialization.
'''

# Keras import for JSON functionality
from keras.models import model_from_json

# Serializes a Keras model to a JSON and h5 data file
def serialize_model(model, root_filename):

	# Convert to JSON
	model_in_json = model.to_json()

	# Write to file
	with open(root_filename + ".json", "w") as json_file:
		json_file.write(model_in_json)

    # Save weights
	model.save_weights(root_filename + ".h5")

	print("Successfully serialized model to local files {}.".format(root_filename))

# Deserialze data in .json and .h5 files into a Keras model that can be used for ML prediction
def deserialize_model(root_filename):

	# Read JSON string
	json_file = open(root_filename + '.json', 'r')
	model_in_json = json_file.read()
	json_file.close()

	# Load model with architecture and weights
	model = model_from_json(model_in_json)
	model.load_weights(root_filename + '.h5')

	# Compile the model with loss, optimizer and metrics
	model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])

	# Return the final model
	print("Successfully deserialized our model.")
	return model