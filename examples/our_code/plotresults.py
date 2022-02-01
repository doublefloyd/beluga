from beluga.utils import load
import matplotlib.pyplot as plt
import numpy as np
import os

data = load('data.beluga')
sol_set = data['solutions']
final_continuation = sol_set[-1]

## Make the results directory to store csv files, if it does not already exist
if not(os.path.isdir('./plots/')):
    os.makedirs('./plots/')
    print("Made directory: './plots/' ")

plt.figure()
for trajectory in final_continuation:
    # Plot altitude vs time
    plt.plot(trajectory.t, trajectory.y[:, 0])

plt.xlabel('Time [s]')
plt.ylabel('Altitude [m]')
plt.grid(True)
plt.show()
plt.savefig('./plots/altitude-vs-time.png')
plt.close()

plt.figure()
for trajectory in final_continuation:
    # Plot velocity vs time
    plt.plot(trajectory.t, trajectory.y[:, 2])

plt.xlabel('Time [s]')
plt.ylabel('Velocity [m/s]')
plt.grid(True)
plt.show()
plt.savefig('./plots/velocity-vs-time.png')
plt.close()

plt.figure()
for trajectory in final_continuation:
    # Plot velocity vs altitude
    plt.plot(trajectory.y[:, 2], trajectory.y[:, 0])

plt.xlabel('Velocity [m/s]')
plt.ylabel('Altitude [m]')
plt.grid(True)
plt.show()
plt.savefig('./plots/velocity-vs-altitude.png')
plt.close()

plt.figure()
for trajectory in final_continuation:
    # Plot longitude vs time
    plt.plot(trajectory.t, trajectory.y[:, 1]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Longitude [deg]')
plt.grid(True)
plt.show()
plt.savefig('./plots/longitude-vs-time.png')
plt.close()

plt.figure()
for trajectory in final_continuation:
    # Plot flight path angle vs time
    plt.plot(trajectory.t, trajectory.y[:, 3]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Flight Path Angle [deg]')
plt.grid(True)
plt.show()
plt.savefig('./plots/flight-path-angle.png')
plt.close()

plt.figure()
for trajectory in final_continuation:
    # Plot angle of attack vs time
    plt.plot(trajectory.t, trajectory.u[:, 0]*180/np.pi)

plt.xlabel('Time [s]')
plt.ylabel('Angle of Attack [deg]')
plt.grid(True)
plt.show()
plt.savefig('./plots/angle-of-attack.png')
plt.close()
