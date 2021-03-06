'''
Filename: server.py
Author: kalyons11 <mailto:kalyons@mit.edu>
Created: 2017-06-01 21:27:53
Last modified by: kalyons11
Last modified time: 2017-06-11 23:35:17
Description:
    - Our complete CityMatrixServer controller. Accepts incoming cities, runs ML + AI work, and
        provides output to Grasshopper.
TODO:
    - None at this time.
'''

# Import local scripts for all key functionality, both ML and AI
import sys, logging
sys.path.extend(['../global/', '../CityPrediction/', '../CityMAItrix/'])
from utils import *
import city_udp, simulator, predictor as ML
from strategies import random_single_moves as Strategy
from objective import objective
log = logging.getLogger('__main__')
result = None #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not

# Check input parameters for AUTO_RESTART value
if len(sys.argv) == 2: AUTO_RESTART = False

# Create instance of our server
server = city_udp.City_UDP(SERVER_NAME, receive_port = RECEIVE_PORT, send_port = SEND_PORT)

# Close all ports if server closed
@atexit.register
def register():
    server.close()
    log.warning("Closing all ports for {}.".format(SERVER_NAME))

# Create instance of our simulator, if needed
if DO_SIMULATE: sim = simulator.CitySimulator(SIM_NAME, log)

log.info("{} listening on ip: {}, port: {}. Waiting to receive new city...".format(SERVER_NAME, RECEIVE_IP, RECEIVE_PORT))

# Constantly loop and wait for new city packets to reach our UDP server
while True:
    # Get city from server and note timestamp
    input_city = server.receive_city()
    timestamp = str(int(time.time()))

    # Only consider new city if it is different from most recent
    if input_city != None:
        key, data = diff_cities(input_city)
        if FORCE_PREDICTION or key is not CityChange.NO:
            # First, write new city to local file
            log.info("New city received @ timestamp {}.".format(timestamp))
            inputSimCity = simulator.SimCity(input_city, timestamp)
            write_city(inputSimCity)

            # Run our black box predictor on this city with given changes
            ml_city = ML.predict(input_city, key, data)

            # Run our AI on this city
            ai_city, move, ai_metrics_list = Strategy.search(input_city)

            # Now, we need to send 2 city objects back to GH
            # First, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Save result locally and send
            result = { 'predict' : ml_dict , 'ai' : ai_dict }
            write_city(result, timestamp = timestamp)
            server.send_data(result)
            log.info("Predicted city data successfully sent to GH.\n")

            # Now, run the GAMA simulation "async" on this city and save the resulting JSON for later use
            if DO_SIMULATE: sim.simulate(simCity)

            log.info("Waiting to receive new city...")

        elif result is not None: #RZ This is necessary to check if ml_city and ai_city has been calculated onece or not
            #RZ firstly, we need to update only the meta data of the 2 cities, including slider position and AI Step
            ml_city.updateMeta(input_city) #RZ necessary, do not delete
            ai_city.updateMeta(input_city) #RZ necessary, do not delete

            # Then, get metrics dicts for cities
            ml_metrics = metrics_dictionary(objective.get_metrics(ml_city))
            ai_metrics = metrics_dictionary(ai_metrics_list)

            # Now, update dictionaries
            ml_dict = ml_city.to_dict()
            ml_dict['objects']['metrics'] = ml_metrics
            ai_dict = ai_city.to_dict()
            ai_dict['objects']['metrics'] = ai_metrics

            # Send result
            result = { 'predict' : ml_dict , 'ai' : ai_dict }
            server.send_data(result)
            log.info("Same city received. Still sent some metadata to GH. Waiting to receive new city...")