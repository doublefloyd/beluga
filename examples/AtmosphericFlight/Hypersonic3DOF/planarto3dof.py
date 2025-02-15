"""
References
----------
.. [1] Vinh, Nguyen X., Adolf Busemann, and Robert D. Culp. "Hypersonic and planetary entry flight mechanics."
    NASA STI/Recon Technical Report A 81 (1980).
"""

from math import *

import beluga
import logging

import matplotlib.pyplot as plt

'''
Begin the planar portion of the solution process.
'''
ocp = beluga.Problem('planarHypersonic')

# Define independent variables
ocp.independent('t', 's')


# Define equations of motion
ocp.state('h', 'v*sin(gam)', 'm')   \
   .state('theta', 'v*cos(gam)/r', 'rad')  \
   .state('v', '-D/mass - mu*sin(gam)/r**2', 'm/s') \
   .state('gam', 'L/(mass*v) + (v/r - mu/(v*r**2))*cos(gam)', 'rad')


# Define quantities used in the problem
ocp.quantity('rho', 'rho0*exp(-h/H)')
ocp.quantity('Cl', '(1.5658*alfa + -0.0000)')
ocp.quantity('Cd', '(1.6537*alfa**2 + 0.0612)')
ocp.quantity('D', '0.5*rho*v**2*Cd*Aref')
ocp.quantity('L', '0.5*rho*v**2*Cl*Aref')
ocp.quantity('r', 're+h')

# Define controls
ocp.control('alfa', 'rad')

# Define constants
ocp.constant('mu', 3.986e5*1e9, 'm**3/s**2')  # Gravitational parameter, m**3/s**2
ocp.constant('rho0', 0.0001*1.2, 'kg/m**3')  # Sea-level atmospheric density, kg/m**3
ocp.constant('H', 7500, 'm')  # Scale height for atmosphere of Earth, m
ocp.constant('mass', 750/2.2046226, 'kg')  # Mass of vehicle, kg
ocp.constant('re', 6378000, 'm')  # Radius of planet, m
ocp.constant('Aref', pi*(24*.0254/2)**2, 'm**2')  # Reference area of vehicle, m**2
ocp.constant('h_0', 80000, 'm')
ocp.constant('v_0', 4000, 'm/s')
ocp.constant('gam_0', (-90)*pi/180, 'rad')
ocp.constant('h_f', 0, 'm')
ocp.constant('theta_f', 0, 'rad')

# Define costs
ocp.terminal_cost('-v**2', 'm**2/s**2')

# Define constraints
ocp.initial_constraint('h-h_0', 'm')
ocp.initial_constraint('theta', 'rad')
ocp.initial_constraint('v-v_0', 'm/s')
ocp.initial_constraint('gam-gam_0', 'rad')
ocp.initial_constraint('t', 's')
ocp.terminal_constraint('h-h_f', 'm')
ocp.terminal_constraint('theta-theta_f', 'rad')

ocp.scale(m='h', s='h/v', kg='mass', rad=1)

bvp_solver = beluga.bvp_algorithm('spbvp')

guess_maker = beluga.guess_generator(
    'auto',
    start=[40000, 0, 2000, (-90)*pi/180],
    direction='forward',
    costate_guess=-0.1,
    control_guess=[0],
    use_control_guess=True)

continuation_steps = beluga.init_continuation()

# Start by flying straight towards the ground
continuation_steps.add_step('bisection') \
                .num_cases(5) \
                .const('h_f', 0)

# Slowly turn up the density
continuation_steps.add_step('bisection') \
                .num_cases(3) \
                .const('rho0', 1.2)

# Move downrange out a tad
continuation_steps.add_step('bisection') \
                .num_cases(3) \
                .const('theta_f', 0.01*pi/180)

# Bring flight-path angle up slightly to activate the control
continuation_steps.add_step('bisection') \
                .num_cases(11) \
                .const('gam_0', -80*pi/180) \
                .const('theta_f', 0.5*pi/180)

continuation_steps.add_step('bisection') \
                .num_cases(31) \
                .const('gam_0', -0*pi/180) \
                .const('theta_f', 3*pi/180)

beluga.add_logger(file_level=logging.DEBUG, display_level=logging.INFO)

cont_planar = beluga.solve(ocp=ocp,
                           method='indirect',
                           optim_options={'control_method': 'differential'},
                           bvp_algorithm=bvp_solver,
                           steps=continuation_steps,
                           guess_generator=guess_maker,
                           initial_helper=True)

sol = cont_planar[-1][-1]

'''
Begin the 3 dof portion of the solution process.
'''
ocp_2 = beluga.Problem('hypersonic3DOF')

# Define independent variables
ocp_2.independent('t', 's')

rho = 'rho0*exp(-h/H)'
Cl = '(1.5658*alpha + -0.0000)'
Cd = '(1.6537*alpha**2 + 0.0612)'
D = '(0.5*{}*v**2*{}*Aref)'.format(rho, Cd)
L = '(0.5*{}*v**2*{}*Aref)'.format(rho, Cl)
r = '(re+h)'

# Define equations of motion
## These state estimates are the outputs of beluga
ocp_2 \
    .state('h', 'v*sin(gam)', 'm') \
    .state('theta', 'v*cos(gam)*cos(psi)/({}*cos(phi))'.format(r), 'rad') \
    .state('phi', 'v*cos(gam)*sin(psi)/{}'.format(r), 'rad') \
    .state('v', '-{}/mass - mu*sin(gam)/{}**2'.format(D, r),  'm/s') \
    .state('gam', '{}*cos(bank)/(mass*v) - mu/(v*{}**2)*cos(gam) + v/{}*cos(gam)'.format(L, r, r),  'rad') \
    .state('psi', '{}*sin(bank)/(mass*cos(gam)*v) - v/{}*cos(gam)*cos(psi)*tan(phi)'.format(L, r),  'rad')

# Define controls
ocp_2.control('alpha', 'rad') \
   .control('bank', 'rad')

# Define costs
ocp_2.terminal_cost('-v**2', 'm**2/s**2')

# Define constraints
ocp_2.initial_constraint('h-h_0', 'm')
ocp_2.initial_constraint('theta-theta_0', 'rad')
ocp_2.initial_constraint('phi-phi_0', 'rad')
ocp_2.initial_constraint('v-v_0', 'm/s')
ocp_2.initial_constraint('gam-gam_0', 'rad')
ocp_2.initial_constraint('psi-psi_0', 'rad')
ocp_2.initial_constraint('t', 's')
ocp_2.terminal_constraint('h-h_f', 'm')
ocp_2.terminal_constraint('theta-theta_f', 'rad')
ocp_2.terminal_constraint('phi-phi_f', 'rad')

# Define constants
ocp_2.constant('mu', 3.986e5*1e9, 'm**3/s**2')  # Gravitational parameter, m**3/s**2
ocp_2.constant('rho0', 1.2, 'kg/m**3')  # Sea-level atmospheric density, kg/m**3
ocp_2.constant('H', 7500, 'm')  # Scale height for atmosphere of Earth, m
ocp_2.constant('mass', 750/2.2046226, 'kg')  # Mass of vehicle, kg
ocp_2.constant('re', 6378000, 'm')  # Radius of planet, m
ocp_2.constant('Aref', pi*(24*.0254/2)**2, 'm**2')  # Reference area of vehicle, m**2
ocp_2.constant('rn', 1/12*0.3048, 'm')  # Nose radius, m
ocp_2.constant('h_0', sol.y[0, 0], 'm')
ocp_2.constant('theta_0', sol.y[0, 1], 'rad')
ocp_2.constant('phi_0', 0, 'rad')
ocp_2.constant('v_0', sol.y[0, 2], 'm/s')
ocp_2.constant('gam_0', sol.y[0, 3], 'rad')
ocp_2.constant('psi_0', 0, 'rad')
ocp_2.constant('h_f', sol.y[-1, 0], 'm')
ocp_2.constant('theta_f', sol.y[-1, 1], 'rad')
ocp_2.constant('phi_f', 0, 'rad')

ocp_2.scale(m='h', s='h/v', kg='mass', rad=1)

bvp_solver_2 = beluga.bvp_algorithm('Shooting', num_arcs=8)
# bvp_solver_2 = beluga.bvp_algorithm('spbvp')

guess_maker_2 = beluga.guess_generator(
    'auto',
    start=[sol.y[0, 0], sol.y[0, 1], 0, sol.y[0, 2], sol.y[0, 3], 0],
    direction='forward',
    costate_guess=[sol.dual[0, 0], sol.dual[0, 1], -0.01, sol.dual[0, 2], sol.dual[0, 3], -0.01],
    control_guess=[sol.u[0, 0], 0.0],
    use_control_guess=True,
    time_integrate=sol.t[-1],
)

continuation_steps_2 = beluga.init_continuation()

continuation_steps_2.add_step('bisection').num_cases(3) \
    .const('h_f', sol.y[-1, 0]) \
    .const('theta_f', sol.y[-1, 1]) \
    .const('phi_f', 0)

continuation_steps_2.add_step('bisection').num_cases(41) \
    .const('phi_f', 2*pi/180)

cont_3dof = beluga.solve(
    ocp=ocp_2,
    method='indirect',
    optim_options={'control_method': 'algebraic', 'analytical_jacobian': False},
    bvp_algorithm=bvp_solver_2,
    steps=continuation_steps_2,
    guess_generator=guess_maker_2)

final_continuation = cont_3dof[-1]

## Trajectory values
# trajectory.y[:, 0] holds h: altitude in m
# trajectory.y[:, 1] holds theta: downrange in radians, pitch angle pertubation
# trajectory.y[:, 2] holds phi: bank angle, roll angle?
# trajectory.y[:, 3] holds v: velocity in m/s
# trajectory.y[:, 4] holds gamma: flight path angle, inclination, climb angle?
# trajectory.y[:, 5] holds psi: heading angle, turn rate?

# Altitude vs velocity corridor
plt.figure()
for trajectory in final_continuation:
    # Plot altitude vs velocity for the swept crossrange cases
    plt.plot(trajectory.y[:, 3], trajectory.y[:, 0])

plt.xlabel('v [m/s]')
plt.ylabel('h [m]')
plt.title('h-v Plot')
plt.grid(True)
plt.show()
plt.savefig('plot1-altitude-vs-velocity-.png')

plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( (trajectory.y[:, 1]), (trajectory.y[:, 0]))

plt.xlabel(r"${\Theta}$  [deg]")
plt.ylabel('h [m]')
plt.title('Downrange')
plt.grid(True)
plt.show()
plt.savefig('plot2-altitude-vs-downrange.png')

import numpy as np

## Emily plots
# Altitude vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 0]))

plt.xlabel("t [s]")
plt.ylabel('h [m]')
plt.title('Altitude vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot3-altitude-vs-time.png')

# Downrange vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 1]))

plt.xlabel("t [s]")
plt.ylabel(r"${\Theta}$  [deg]")
plt.title('Downrange vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot4-downrange-vs-time.png')

# Bank angle vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 2]))

plt.xlabel("t [s]")
plt.ylabel(r"${\phi}$  [deg]")
plt.title('Bank Angle vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot5-bank-angle-vs-time.png')

# Velocity vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 3]))

plt.xlabel("t [s]")
plt.ylabel('v [m/s]')
plt.title('Velocity vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot6-velocity-vs-time.png')

# Flight Path Angle vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 4]))

plt.xlabel("t [s]")
plt.ylabel(r"${\gamma}$  [deg]")
plt.title('Flight Path Angle vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot7-flight-path-angle-vs-time.png')

# Heading angle vs time
plt.figure()
for trajectory in final_continuation:
    # Plot downrange
    plt.plot( np.linspace(0, len(trajectory.y[:, 0]), len(trajectory.y[:, 0])), (trajectory.y[:, 5]))

plt.xlabel("t [s]")
plt.ylabel(r"${\Psi}$  [deg]")
plt.title('Heading Angle vs Time')
plt.grid(True)
plt.show()
plt.savefig('plot8-heading-angle-vs-time.png')

print("Done.")
