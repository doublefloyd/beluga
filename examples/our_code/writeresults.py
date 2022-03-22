from beluga.utils import load
import numpy as np
import os
import math

data = load('data.beluga')
sol_set = data['solutions']
final_continuation = sol_set[-1]

#fields = ['t', 'h', 'theta', 'v', 'gam', 'alfa']
fields = ['time(s)', 'altitude(m)', 'longitude(deg)', 'speed(m/s)', 'flight_path_angle(deg)', 'angle_of_attack(deg)']
header = ' '.join(fields)

## Make the results directory to store csv files, if it does not already exist
if not(os.path.isdir('./csvresults/')):
    os.makedirs('./csvresults/')
    print("Made directory: './csvresults/' ")

index=0
for trajectory in final_continuation:
    index += 1

    raw_time              = trajectory.t
    # raw_altitude          = trajectory.y[:,[0]]
    # raw_longitude         = trajectory.y[:,[1]]*180/np.pi
    # raw_speed             = trajectory.y[:,[2]]
    # raw_flight_path_angle = trajectory.y[:,[3]]*180/np.pi
    # raw_angle_of_attack   = trajectory.u[:,[0]]*180/np.pi

    time = np.arange(math.ceil(raw_time[0]), math.floor(raw_time[-1]), 1)
    itraj = trajectory(time)

    altitude          = itraj[0][:,[0]]
    longitude         = itraj[0][:,[1]]*180/np.pi
    speed             = itraj[0][:,[2]]
    flight_path_angle = itraj[0][:,[3]]*180/np.pi
    angle_of_attack   = itraj[2][:]*180/np.pi
    
    time = time[..., np.newaxis]
    angle_of_attack = angle_of_attack[..., np.newaxis]

    fname = "csvresults/" + "{:06d}".format(index) + ".csv"
    rows = np.concatenate((time, altitude, longitude, speed, flight_path_angle, angle_of_attack), axis=1)
    np.savetxt(fname, rows, fmt='%f', delimiter=" ")

    with open(fname, 'r+') as f:
        contents = f.read()
        f.seek(0,0)
        f.write(header + '\n' + contents)

    print(f"Trajectory {index} saved.")
