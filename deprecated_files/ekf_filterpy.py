# Import EKF libraries
from filterpy.kalman import ExtendedKalmanFilter

# Import Matrix libraries
import sympy
from sympy.abc import alpha, x, y, v, w, R, theta
from sympy import symbols, Matrix

# Import left-over required functions
from numpy import array, sqrt

'''
Instantiate an Extended Kalman Filter class with 
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
        # Initizlize the class
        ExtendedKalmanFilter.__init__(self, 0.01, )

        # Define self characteristics
        self.dt = dt

        # Instantiate symbology
        a, x, y, v, w, theta, time = symbols(
            'a, x, y, v, w, theta, t')
        d = d*time
        beta = (d/w)*sympy.tan(a)
        r = w/sympy.tan(a)

        # Define the F matrix
        self.fxu = Matrix(
            [

            ])

        # Compute the jacobian forms of the F matrix
        self.F_j = self.fxu.jacobian(Matrix([Matrix[qwe, qwe, qwe]]))
        self.V_j = self.fxu.jacobian(Matrix([v, a]))

        # Save for later use
        self.subs = {   x:0,
                        y:0,
                        v:0,
                        a:0,
                        time:dt,
                        w:'wheelbase',
                        theta:0}
        self.x_x, self.x_y = x, y
        self.v, self.a, self.theta = v, a, theta

    def predict(self, u):
        self.x = self.update(self.x, u, self.dt)
        self.subs[self.theta] = self.x[2,0]


    def update(self, x, u, dt):

kf = EKF(dim_x=3, dim_z=6, dim_u=0)

# Initial state (location and velocity)
kf.x = array([   [2.],
                    [0.],
                    [0.]
])

kf.F = array([   [1., 1.],
                    [0., 1.],
                    [0.]
])

# Measurement array (unchanging)
kf.H = array([[1., 0.]]) 

# Covariance matrix
kf.P *= 1000. 

# Uncertainty of state
kf.R = 5


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