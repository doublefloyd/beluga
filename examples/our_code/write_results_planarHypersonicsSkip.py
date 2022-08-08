####################################################################################################
# Convert beluga dataset stored as beluga filetype to csv files 
####################################################################################################

import os
import numpy as np
import math

import beluga

####################################################################################################
# USER INPUTS
####################################################################################################
## Specify filepath to data file
# Note: expected filetype is .beluga file
# Example: BELUGA_DATA_FILE = "./generated_datasets/beluga_v1_planarHypersonicsSkip/data_beluga_format/data.beluga"
BELUGA_DATA_FILE = "./generated_datasets/beluga_v1_planarHypersonicsSkip/data_beluga_format/data.beluga"

## Specify directory to store csv files
# Note: make sure to include "/" at the end of the filepath
# Example: CSV_DIR = "./generated_datasets/beluga_v1_planarHypersonicsSkip/data_csv_format/beluga_v1-2_planarHypersoncsSkip_uniformDataRecordingStepSize/"
CSV_DIR = "./generated_datasets/beluga_v1_planarHypersonicsSkip/data_csv_format/beluga_v1-2_planarHypersoncsSkip_uniformDataRecordingStepSize/"
####################################################################################################

## Load the dataset formatted as beluga type
data = beluga.utils.load(BELUGA_DATA_FILE)
sol_set = data['solutions']
final_continuation = sol_set[-1]

#fields = ['t', 'h', 'theta', 'v', 'gam', 'alfa']
fields = ['time(s)', 'altitude(m)', 'longitude(deg)', 'speed(m/s)', 'flight_path_angle(deg)', 'angle_of_attack(deg)']
header = ' '.join(fields)

## Make the results directory to store csv files, if it does not already exist
if not(os.path.isdir(CSV_DIR)):
    os.makedirs(CSV_DIR)
    print(f"Created directory to store data formatted as .csv files: '{CSV_DIR}' ")

index=0
for trajectory in final_continuation:
    index += 1

    raw_time              = trajectory.t

    time = np.arange(math.ceil(raw_time[0]), math.floor(raw_time[-1]), 1)
    itraj = trajectory(time)

    altitude          = itraj[0][:,[0]]
    longitude         = itraj[0][:,[1]]*180/np.pi
    speed             = itraj[0][:,[2]]
    flight_path_angle = itraj[0][:,[3]]*180/np.pi
    angle_of_attack   = itraj[2][:]*180/np.pi
    
    time = time[..., np.newaxis]
    angle_of_attack = angle_of_attack[..., np.newaxis]

    ## Create filename for this trajectory (include full filepath)
    fname = f"{CSV_DIR}{index:06d}.csv"
    ## Concatenate all rows to be saved to csv file
    rows = np.concatenate((time, altitude, longitude, speed, flight_path_angle, angle_of_attack), axis=1)
    ## Save this trajectory to a csv file
    np.savetxt(fname, rows, fmt='%f', delimiter=" ")
    ## Add header information to csv file
    with open(fname, 'r+') as f:
        contents = f.read()
        f.seek(0,0)
        f.write(header + '\n' + contents)
    ## Print status
    print(f"Trajectory {index} saved to {fname}")

print("\nDone.\n")