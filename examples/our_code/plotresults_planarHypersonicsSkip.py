####################################################################################################
# Plot beluga dataset stored as beluga filetype
####################################################################################################

from beluga.utils import load
import matplotlib.pyplot as plt
import numpy as np
import os

####################################################################################################
# USER INPUTS
####################################################################################################
## Specify filepath to data file that will be used for plotting
# Note: expected filetype is .beluga file
# Example: BELUGA_DATA_FILE = "/home/ebartusi/beluga/examples/our_code/generated_datasets/beluga_v1_planarHypersonicsSkip/data_beluga_format/data.beluga"
BELUGA_DATA_FILE = "/home/ebartusi/beluga/examples/our_code/generated_datasets/beluga_v1_planarHypersonicsSkip/data_beluga_format/data.beluga"

## Specify directory to store plots
# Note: make sure to include "/" at the end of the filepath
# Example: PLOT_DIR = "/home/ebartusi/beluga/examples/our_code/generated_datasets/beluga_v1_planarHypersonicsSkip/plots/"
PLOT_DIR = "/home/ebartusi/beluga/examples/our_code/generated_datasets/beluga_v1_planarHypersonicsSkip/plots/"
####################################################################################################

## Load the dataset formatted as beluga type
data = load(BELUGA_DATA_FILE)
sol_set = data['solutions']
final_continuation = sol_set[-1]

## Make the plots directory to store plots, if it does not already exist
if not(os.path.isdir(PLOT_DIR)):
    os.makedirs(PLOT_DIR)
    print(f"Created directory to store plots of dataset: '{PLOT_DIR}' ")

plt.figure()
for trajectory in final_continuation:
    # Plot altitude vs time
    plt.plot(trajectory.t, trajectory.y[:, 0])

plt.xlabel('Time [s]')
plt.ylabel('Altitude [m]')
plt.title("Altitude vs. Time")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}altitude-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

plt.figure()
for trajectory in final_continuation:
    # Plot velocity vs time
    plt.plot(trajectory.t, trajectory.y[:, 2])

plt.xlabel('Time [s]')
plt.ylabel('Velocity [m/s]')
plt.title("Velocity vs. Time")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}velocity-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

plt.figure()
for trajectory in final_continuation:
    # Plot velocity vs altitude
    plt.plot(trajectory.y[:, 2], trajectory.y[:, 0])

plt.xlabel('Velocity [m/s]')
plt.ylabel('Altitude [m]')
plt.title("Altitude vs. Velocity")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}velocity-vs-altitude.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

plt.figure()
for trajectory in final_continuation:
    # Plot longitude vs time
    plt.plot(trajectory.t, trajectory.y[:, 1]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Longitude [deg]')
plt.title("Longitude vs. Time")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}longitude-vs-time.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

plt.figure()
for trajectory in final_continuation:
    # Plot flight path angle vs time
    plt.plot(trajectory.t, trajectory.y[:, 3]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Flight Path Angle [deg]')
plt.title("Flight Path Angle vs. Time")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}flight-path-angle.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

plt.figure()
for trajectory in final_continuation:
    # Plot angle of attack vs time
    plt.plot(trajectory.t, trajectory.u[:, 0]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Angle of Attack [deg]')
plt.title("Angle of Attack vs. Time")
plt.grid(True)
plt.show()
plot_name = f'{PLOT_DIR}angle-of-attack.png'
plt.savefig(plot_name)
plt.close()
print(f"Saved plot '{plot_name}'")

print("\nDone.\n")
