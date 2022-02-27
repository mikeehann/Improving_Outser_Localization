
from filterpy.kalman import ExtendedKalmanFilter
from filterpy.common import Q_discrete_white_noise
import sympy as sp
import numpy as np

'''
Instantiate an Extended Kalman Filter with 
3 state properties (x=3)
    -GNSS x3   (lat, lon, alt)
    
6 measurement properties (z=1)
    -IMU  x6   (linear acceleration x3)
                (angular velocity x3)

2 input properties (u=2)
    -Velocity
'''
class EKF(ExtendedKalmanFilter):
    def __init__(self, dt, ):
        ExtendedKalmanFilter.__init__(self, 0.01, )
        self.dt = dt
        self.x

        a, x, y, v, w, theta, time = symbols(
            'a, x, y, v, w, theta, t')

kf = EKF(dim_x=3, dim_z=6, dim_u=0)

# Initial state (location and velocity)
kf.x = np.array([   [2.],
                    [0.],
                    [0.]
])

kf.F = np.array([   [1., 1.],
                    [0., 1.],
                    [0.]
])

# Measurement array (unchanging)
kf.H = np.array([[1., 0.]]) 

# Covariance matrix
kf.P *= 1000. 

# Uncertainty of state
kf.R = 5

# Uncertainty of process
kf.Q = Q_discrete_white_noise(2, dt, .1)

# Run the filter
while True:
    kf.predict()
    kf.update(get_measurement())

    x = kf.x
    values.append(x)
    plotting_function(x)


def getVel(x1, y1, z1, x2, y2, z2, dt):
    # In m/s
    vel_x = (x2-x1)/dt
    vel_y = (y2-y1)/dt
    vel_z = (z2-z1)/dt

    return (vel_x, vel_y, vel_z)

# Example getVel call
'''
vels = getVel(  df.GPS_Long[i+1], df.GPS_Lat[i+1], df.GPS_Alt[i+1],
                df.GPS_Long[i], df.GPS_Lat[i], df.GPS_Alt[i],
                dt)
'''