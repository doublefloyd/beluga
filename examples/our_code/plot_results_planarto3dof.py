####################################################################################################
# Plot beluga dataset stored as beluga filetype
####################################################################################################

import os
import numpy as np
import matplotlib.pyplot as plt

import beluga

####################################################################################################
# USER INPUTS
####################################################################################################
## Specify filepath to data file that will be used for plotting
# Note: expected filetype is .beluga file
# Example: BELUGA_DATA_FILE = "./generated_datasets/beluga_v2_planarto3dof/data_beluga_format/data_stage_3_final_output.beluga"
BELUGA_DATA_FILE = "./generated_datasets/beluga_v2_planarto3dof/data_beluga_format/data_stage_3_final_output.beluga"

## Specify directory to store plots
# Note: make sure to include "/" at the end of the filepath
# Example: PLOT_DIR = "./generated_datasets/beluga_v2_planarto3dof/plots/"
PLOT_DIR = "./generated_datasets/beluga_v2_planarto3dof/plots/"
####################################################################################################

## Load the dataset formatted as beluga type
data = beluga.utils.load(BELUGA_DATA_FILE)
sol_set = data['solutions']
final_continuation = sol_set

## Make the plots directory to store plots, if it does not already exist
if not(os.path.isdir(PLOT_DIR)):
    os.makedirs(PLOT_DIR)
    print(f"Created directory to store plots of dataset: '{PLOT_DIR}' ")

# Plot altitude vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Altitude [m]')
plt.title("Altitude vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 0])
plt.show()
plot_name = f'{PLOT_DIR}altitude-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot velocity vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Velocity [m/s]')
plt.title("Velocity vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 3])
plt.show()
plot_name = f'{PLOT_DIR}velocity-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot altitude vs velocity
plt.figure()
plt.xlabel('Velocity [m/s]')
plt.ylabel('Altitude [m]')
plt.title("Altitude vs. Velocity")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.y[:, 3], trajectory.y[:, 0])
plt.show()
plot_name = f'{PLOT_DIR}altitude-vs-velocity.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot longitude vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Longitude [deg]')
plt.title("Longitude vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 1]*180/np.pi)
plt.show()
plot_name = f'{PLOT_DIR}longitude-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot latitude vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Latitude [deg]')
plt.title("Latitude vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 2]*180/np.pi)
plot_name = f'{PLOT_DIR}latitude-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot latitude vs longitude
plt.figure()
plt.xlabel('Longitude [deg]')
plt.ylabel('Latitude [deg]')
plt.title("Latitude vs. Longitude")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.y[:, 1]*180/np.pi, trajectory.y[:, 2]*180/np.pi)
plot_name = f'{PLOT_DIR}latitude-vs-longitude.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot flight path angle vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Flight Path Angle [deg]')
plt.title("Flight Path Angle vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 4]*180/np.pi)
plot_name = f'{PLOT_DIR}flight-path-angle-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot velocity azimuth angle vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Velocity Azimuth Angle [deg]')
plt.title("Velocity Azimuth Angle vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.y[:, 5]*180/np.pi)
plot_name = f'{PLOT_DIR}velocity-azimuth-angle-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot angle of attack vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Angle of Attack [deg]')
plt.title("Angle of Attack vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    # plt.plot(trajectory.t, trajectory.u[:, 0]*180/np.pi)
    plt.plot(trajectory.t, np.exp(trajectory.u[:, 0])*180/np.pi)
plot_name = f'{PLOT_DIR}angle-of-attack-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

# Plot bank angle vs time
plt.figure()
plt.xlabel('Time [s]')
plt.ylabel('Bank Angle [deg]')
plt.title("Bank Angle vs. Time")
plt.grid(True)
for trajectory in final_continuation:
    plt.plot(trajectory.t, trajectory.u[:, 1]*180/np.pi)
plot_name = f'{PLOT_DIR}bank-angle-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

print("\nDone.\n")