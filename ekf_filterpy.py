
from filterpy.kalman import ExtendedKalmanFilter
from filterpy.common import Q_discrete_white_noise
import numpy as np


'''
Instantiate an Extended Kalman Filter with 
3 state properties (x=3)
    -GNSS x3   (lat, lon, alt)
    
6 measurement properties (z=1)
    -IMU  x6   (linear acceleration x3)
                (angular velocity x3)

0 noise properties (u=0)
'''
kf = ExtendedKalmanFilter(dim_x=3, dim_z=6, dim_u=0)

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
