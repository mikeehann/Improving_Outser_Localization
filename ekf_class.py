
import numpy as np

'''
Remember: 
    I will need to derive magnetometer values
    and velocities based on GNSS and IMU data 
'''

# Offset of each variable in the state vector
# Defined for readability
iX = 0
iY = 1
iZ = 2

# Used to determine size of matrix
NUM_VARS = 3

class EKF:
    # Define the initial state of the class (t=0)
    # Instantiate state properties as described
    def __init__(self,  init_x: float,
                        init_y: float,
                        init_z: float,
                        accel_var: float,
                        ) -> None:
            
        # Define the mean of state GRV
        self.x_bar = np.zeros(NUM_VARS)
        self.x_bar[iX] = init_x
        self.x_bar[iY] = init_y
        self.x_bar[iZ] = init_z

        self.accel_var = accel_var

        # Define the covariance of state GRV
        self.P_bar = np.eye(NUM_VARS)

    def predict(self, dt: float) -> None:
        # x = F dot x   <- CORRECT FOR EKF
        # P = F dot P dot F(transposed) + G dot G(transposed) dot a          <- CORRECT FOR EKF

        # Create an identity matrix of size NUM_VARS
        # to initialize the F matrix
        F = np.eye(NUM_VARS)

        # Insert dt into the matrix
        F[iX, iY, iZ] = dt

        ''' Iterate a new x_bar value based on the dot
        product of F and x_bar. This is our predicted
        next step. Equation used at top of 'predict'. '''
        new_x_bar = F.dot(self.x_bar)


        # Initialize G as a 2x1 matrix
        G = np.zeros((2,1))

        # Integrate dt and insert in x position
        G[iX] = 0.5 * dt**2
        
        #
        G[iY] = dt

        ''' Iterate a new P_bar value. P_bar is the 
        predicted covariance. Equation used at top of 'predict'.  '''
        new_P_bar = F.dot(self.P_bar).dot(F.T) + G.dot(G.T)
    


    def update(self, meas_x: float,
                     meas_y: float, 
                     meas_z: float,
                     meas_x_var: float,
                     meas_y_var: float,
                     meas_z_var: float,
                     ) -> None:
        # y = z - H x
        # S = H P Ht + R
        # K = P Ht S^-1
        # x = x + K y
        # P = (I - K H) * P

        H = np.zeros((1, NUM_VARS))
        H[0, iX] = 1

        z = np.array([meas_x])
        R = np.array([meas_x_var])

        y = z - H.dot(self._x)
        S = H.dot(self._P).dot(H.T) + R

        K = self._P.dot(H.T).dot(np.linalg.inv(S))

        new_x = self._x + K.dot(y)
        new_P = (np.eye(2) - K.dot(H)).dot(self._P)

        # Update P_bar and x_bar to their calculated values
        self._P = new_P
        self._x = new_x


    # Define simpler termed properties of the EKF that may be retrieved easily
    @property
    def cov(self) -> np.array:
        return self._P

    @property
    def mean(self) -> np.array:
        return self._x

    @property
    def pos(self) -> float:
        return self._x[iX]

    @property
    def vel(self) -> float:
        return self._x[iV]




