
'''
Using an Unscented Kalman Filter to enhance
the localiation of GNSS and IMU data.

Created using the filterpy library + more

NOTE: Incomplete
'''
# Import EKF libraries
from filterpy.kalman import ExtendedKalmanFilter

# Import Matrix libraries
import sympy
from sympy.abc import alpha, x, y, v, w, R, theta
from sympy import beta, symbols, Matrix

# Import left-over required functions
from numpy import array, sqrt





