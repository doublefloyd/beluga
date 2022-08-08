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
# Example: BELUGA_DATA_FILE = "./generated_datasets/beluga_v2_planarto3dof/data_beluga_format/data_stage_3_final_output.beluga"
BELUGA_DATA_FILE = "./generated_datasets/beluga_v2_planarto3dof/data_beluga_format/data_stage_3_final_output.beluga"

## Specify directory to store csv files
# Note: make sure to include "/" at the end of the filepath
# Example: CSV_DIR = "./generated_datasets/beluga_v2_planarto3dof/data_csv_format/"
CSV_DIR = "./generated_datasets/beluga_v2_planarto3dof/data_csv_format/"
####################################################################################################

## Load the dataset formatted as beluga type
data = beluga.utils.load(BELUGA_DATA_FILE)
sol_set = data['solutions']
final_continuation = sol_set

#fields = ['t', 'h', 'theta', 'phi', 'v', 'gam', 'psi', 'alfa', 'bank']
fields = ['time(s)', 'altitude(m)', 'longitude(deg)', 'latitude(deg)', 'speed(m/s)', 'flight_path_angle(deg)', 'velocity_azimuth_angle(deg)', 'angle_of_attack(deg)', 'bank_angle(deg)']
header = ' '.join(fields)

## Make the results directory to store csv files, if it does not already exist
if not(os.path.isdir(CSV_DIR)):
    os.makedirs(CSV_DIR)
    print(f"Created directory to store data formatted as .csv files: '{CSV_DIR}' ")

index = 0
for trajectory in final_continuation:
    index += 1
    
    raw_time                   = trajectory.t
    raw_altitude               = trajectory.y[:,[0]]
    raw_longitude              = trajectory.y[:,[1]]*180/np.pi
    raw_latitude               = trajectory.y[:,[2]]*180/np.pi
    raw_speed                  = trajectory.y[:,[3]]
    raw_flight_path_angle      = trajectory.y[:,[4]]*180/np.pi
    raw_velocity_azimuth_angle = trajectory.y[:,[5]]*180/np.pi
    raw_angle_of_attack        = trajectory.u[:,[0]]*180/np.pi
    raw_bank_angle             = trajectory.u[:,[1]]*180/np.pi
    
    time = np.arange(math.ceil(raw_time[0]), math.floor(raw_time[-1]), 1)
    itraj = trajectory(time)
	
    altitude               = itraj[0][:,[0]]
    longitude              = itraj[0][:,[1]]*180/np.pi
    latitude               = itraj[0][:,[2]]*180/np.pi
    speed                  = itraj[0][:,[3]]
    flight_path_angle      = itraj[0][:,[4]]*180/np.pi
    velocity_azimuth_angle = itraj[0][:,[5]]*180/np.pi
    angle_of_attack        = itraj[2][:,[0]]*180/np.pi
    bank_angle             = itraj[2][:,[1]]*180/np.pi
	
    time = time[..., np.newaxis]
    
    ## Create filename for this trajectory (include full filepath)
    fname = f"{CSV_DIR}{index:06d}.csv"
    ## Concatenate all rows to be saved to csv file
    rows = np.concatenate((time, altitude, longitude, latitude, speed, flight_path_angle, velocity_azimuth_angle, angle_of_attack, bank_angle), axis=1)
    ## Save this trajectory to a csv file
    np.savetxt(fname, rows, fmt='%f', delimiter=" ", header=header)
    ## Print status
    print(f"Trajectory {index} saved to {fname}")

print("\nDone.\n")


