
from time import perf_counter
from os import chdir, getcwd

import numpy as np
import pandas as pd

from plot import *

class del_then_inter:
    def __init__(self, infile: str, has_imu: bool, conv_time: bool, plot_choice):
        self.df, _ = setup(infile, has_imu, conv_time)
        self.plot_choice = plot_choice
        
    # Delete unimportant columns
    #self.df.drop(self.df.loc[:,'IMU_AngVelX':'IMU_LinearAccZ'].columns, inplace=True, axis=1)

    def delete_vals(self) -> None:
        print('\n\tdeleting bad values...\n')
        self.df = self.df.reset_index()

        for i in range(len(self.df.GPS_Long)):
            if self.df.SDn[i] > 0.005:
                self.df.loc[i,'GPS_Long':'GPS_Alt'] = pd.NA

    def interpolate(self) -> None:
        print('\tinterpolating...\n')

        # Force columns into numeric data types
        self.df['GPS_Long'] = pd.to_numeric(self.df['GPS_Long'], errors='coerce')
        self.df['GPS_Lat'] = pd.to_numeric(self.df['GPS_Lat'], errors='coerce')
        self.df['GPS_Alt'] = pd.to_numeric(self.df['GPS_Alt'], errors='coerce')

        # Interpolate all GNSS values in the df as floats
        self.df.loc[:, 'GPS_Long':'GPS_Alt'] = self.df.loc[:, 'GPS_Long':'GPS_Alt'].interpolate(method='linear')
        self.df['GPS_Status'] = self.df['GPS_Status'].interpolate(method='ffill')

        # Remove previously deleted values
        self.df = self.df[self.df['GPS_Long'].notna()]

    def write_to_file(self, name: str):
        # Change 'time' back to rospy.time[] 
        self.df.Time = self.df.Time.apply(lambda x: f'rospy.Time[{x:19d}]')
        self.df.drop('index', axis=1, inplace=True)

        # Save the file
        self.df.to_csv(f'.\\results\\{name}.csv', index=False)
        print(f'\nSaved new file to .\\results\\{name}.csv')

        # Plot the desired plot
        if self.plot_choice:
            print(f'\nPlotting...\n')
            choose_plot(self.df, self.plot_choice)

class fix_from_vel:
    def __init__(self, infile, has_imu, conv_time):
        self.gnss_df, _ = setup(infile, has_imu, conv_time)
        self.gnss_df.loc[:, 'GPS_Long':'GPS_Lat'] = [geodetic_to_geocentric(*a) for a in tuple(zip(self.gnss_df['GPS_Long'], self.gnss_df['GPS_Lat'], self.gnss_df['GPS_Alt']))]
        self.gnss_df = add_vectors(self.gnss_df)
    
    def rem_vel_outlier(df) -> None:
        '''
        Status:
        nulling values based on Std works, but not based on absolute velocity change
        Values are still strecthed when compared to GPS_Long, GPS_Lat
            This notably wasnt the case before I force converted the merged df to numeric
        '''
        df['Rolling_X'] = df.VelX.rolling(5).mean()
        df['Rolling_Y'] = df.VelY.rolling(5).mean()
        df['Rolling_Z'] = df.VelZ.rolling(5).mean()

        #df.loc[df[df.SDn > 10].index, 'VelX':'VelZ'] = pd.NA
        df.VelX.map(lambda x: pd.NA if abs(x-df.Rolling_X)/() > 1 else x.VelX)
        
class fix_from_imu:
    def __init__(self, infile, has_imu): 
        self.gnss_df, self.imu_df = setup(infile, has_imu)
        
        self.gnss_df.loc[:, 'GPS_Long':'GPS_Lat'] = [geodetic_to_geocentric(*a) for a in tuple(zip(self.gnss_df['GPS_Long'], self.gnss_df['GPS_Lat'], self.gnss_df['GPS_Alt']))]
        
        self.gnss_df = add_vectors(self.gnss_df)
        
        self.gnss_df = trim_df_vel(self.gnss_df, 10, 1)
        
        self.df = merge_dfs(self.gnss_df, self.imu_df)
    

### PLOT FUNCTIONS

def choose_plot(df, plot_choice):
    if plot_choice == 1:
        plot_track(df)
    elif plot_choice == 2:
        pass


### MAIN FUNCTIONS

def setup(infile: str, has_imu: bool, conv_time: bool) -> pd.DataFrame:

    t1 = perf_counter()
    print('\n' + '#'*80 + '\n')

    def ingest_file(infile) -> pd.DataFrame:

        # Set and Get directory
        chdir(r'C:\Users\mikeh\OneDrive\Documents\GitHub\ouster_localization')
        dir = getcwd()
        print(f'\ndirectory: {dir}\n\n')

        print('\treading file...\n')

        # Import the comma delimited .txt file as a pandas dataframe
        df = pd.read_csv(f'{dir}\\{infile}', delimiter=',')

        return df


    def edit_dtypes(df) -> pd.DataFrame:

        print('\tediting data types...\n')
        # Extract only the numbers from the 'Time' column using a reg ex, convert to long integer
        df['Time'] = df['Time'].str.extract('(\d+)').astype(np.int64)

        #gnss_df.Time = gnss_df.Time.map(lambda x: datetime.fromtimestamp(x))

        if conv_time:
            # Convert Time into seconds from onset
            t0 = df['Time'][0]
            df['Time'] = (df['Time']-t0)/10**9

        # Forcing proper data types for each column
        df = df.apply(lambda x: pd.to_numeric(x, errors='coerce'))

        # Forward fill standard deviations, so they are not linearly interpolated later
        df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].interpolate(method='ffill')

        return df

    df = ingest_file(infile)
    df = edit_dtypes(df)

    print(f'\n\t| Setup done, time: {perf_counter()-t1}\n')

    # If the dataframe contains IMU data, split the dataframes into separate components
    if has_imu:
        gnss_gnss_df = df.iloc[:, :8].dropna()
        imu_df = df.iloc[:, [0,8,9,10,11,12,13]].dropna()

        return gnss_gnss_df, imu_df
    # Otherwise just return the GNSS gnss_df
    else:
        return df


def geodetic_to_geocentric(lat, lon, h, ellps=(6378137, 298.257223563)) -> list:
    '''
    Convert GNSS Decimal Degrees to Metres

    Sampled from YeO 
    (https://codereview.stackexchange.com/questions/195933/convert-geodetic-coordinates-to-geocentric-cartesian)

    Compute the Geocentric (Cartesian) Coordinates X, Y, Z
    given the Geodetic Coordinates lat, lon + Ellipsoid Height h
    
    Ellipsoid Parameters as tuples (semi major axis, inverse flattening)
    grs80 = (6378137, 298.257222100882711)
    wgs84 = default
    '''

    t1 = perf_counter()
    print('#'*80 + '\n')

    a, rf = ellps
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    N = a / np.sqrt(1 - (1 - (1 - 1 / rf) ** 2) * (np.sin(lat_rad)) ** 2)
    X = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = ((1 - 1 / rf) ** 2 * N + h) * np.sin(lat_rad)

    print(f'\n\t| Convert coordinates done, time: {perf_counter()-t1}\n')

    # Only return the latitude and longitude
    return [X, Y]


def add_vectors(df) -> pd.DataFrame:

    t1 = perf_counter()
    print('#'*80 + '\n')

    df['dt'] = df.Time.diff()
    df['VelX'] = df.GPS_Long.diff() / df.dt
    df['VelY'] = df.GPS_Lat.diff() / df.dt
    df['VelZ'] = df.GPS_Alt.diff() / df.dt

    # Smooth the velocity datasets by running a rolling mean over the series    
    #df.VelX = df.VelX.rolling(10).mean()

    df['AccX'] = df.VelX.diff() / df.dt
    df['AccY'] = df.VelY.diff() / df.dt
    df['AccZ'] = df.VelZ.diff() / df.dt

    df['Abs_Vel'] = np.sqrt(df.VelX**2 + df.VelY**2 + df.VelZ**2)
    df['Abs_Acc'] = np.sqrt(df.AccX**2 + df.AccY**2 + df.AccZ**2)

    print(f'\n\t| Vectors added, time: {perf_counter()-t1}\n')

    # Trim first value in gnss_df (holds null vels/accs)
    #df = df.drop(index=0)

    return df


def trim_df_vel(df, time: int, min_vel: int) -> pd.DataFrame:

        df = df.drop(df[(df.Time < time) & (df.Abs_Vel < min_vel)].index, axis=0)
        df = df.reset_index()

        return df


def merge_dfs(df1, df2) -> pd.DataFrame:

        t1 = perf_counter()
        print('#'*80 + '\n')

        df = df1.append(df2)
        df = df.sort_values(by=['Time'])

        # Force all values to numeric, again
        df = df.apply(lambda x: pd.to_numeric(x, errors='coerce'))

        df = df.interpolate(method='linear')

        # Remove previously deleted values
        df = df.dropna()

        print(f'\n\t| Merged dfs, time: {perf_counter()-t1}\n')

        return df



### FUNCTIONS IN TESTING

def orient_imu(df) -> None:
    '''
    Takes in a dataframe with GNSS and IMU values
    Returns a df with the IMU values oriented to the intertial
    frame of reference

    math based off (https://www.allaboutcircuits.com/technical-articles/how-to-interpret-IMU-sensor-data-dead-reckoning-rotation-matrix-creation/)
    '''
    '''
    Current State:
    Creates an invalid martix that only theoretically rotates to the Z axis
    
    Need to:
    - Add the xy rotation matrix computation based on the sample documents
    - ^ will be difficult considering the above doc does not go into details
    - Need to use acceleration vectors to add in gravity vector
    '''
    
    def add_vectors(df) -> None:
        
        # Create a normalized IMU vector
        df['A_hat'] = tuple(zip(df.IMU_LinearAccX / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2),
                                df.IMU_LinearAccY / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2),
                                df.IMU_LinearAccZ / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2)))

        # Create a normalized GNSS vector as a target to match
        # Use derived accelerations from positions + gravity vector
        df['G_hat'] = tuple(zip(df.AccX / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2),
                                df.AccY / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2),
                                (df.AccZ-9.801) / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2)))

    def calc_matrix(a_hat, g_hat) -> list:
        a_hat = np.asarray(a_hat)
        g_hat = np.asarray(g_hat)

        dot_prod = np.dot(a_hat, g_hat)

        theta = np.arccos(dot_prod)

        print(theta)

        z_matrix = np.zeros()
        xy_matrix = np.zeros()
        new_vec = np.zeros()

        '''
        To Do
        '''

        # Aligns the Z axis
        for i, tup in enumerate(a_hat):
            z_matrix.append(  [[(tup[1]**2-(tup[0]**2*tup[2]))/(tup[0]**2+tup[1]**2),         ((-tup[0]*tup[1])-(tup[0]*tup[1]*tup[2]))/(tup[0]**2+tup[1]**2),    tup[0]],
                            [(-tup[0]*tup[1]-(tup[0]*tup[1]*tup[2]))/(tup[0]**2+tup[1]**2),   (tup[0]**2-(tup[1]**2*tup[2]))/(tup[0]**2+tup[1]**2),             tup[1]],
                            [ -tup[0],                                                        -tup[1],                                                         -tup[2]]])

            # Use the ith matrix and the g_hat vector at the same index as in a_hat
            new_vec.append(np.matmul(z_matrix[i], g_hat[i]))
        
        return new_vec

    add_vectors(df)
    new_vec = calc_matrix(df.A_hat, df.G_hat)

    print(new_vec[0:15])


def get_PRY(df) -> None: 
    '''
    Takes in a dataframe with a 6DOF IMU
    Appends Roll, Pitch, Yaw columns on the dataframe
    May become obsolete soon...
    '''
    
    t1 = perf_counter()
    print(f'\n\t Calculating PRY...\n')

    RAD_TO_DEG = 180 * np.pi

    df['Pitch'] = df.IMU_AngVelX * df.dt * 0.98 + (np.arctan2(df.IMU_LinearAccZ, df.IMU_LinearAccY) * RAD_TO_DEG) * 0.02
    df['Roll'] = df.IMU_AngVelY * df.dt * 0.98 + (np.arctan2(df.IMU_LinearAccZ, df.IMU_LinearAccX) * RAD_TO_DEG) * 0.02
    df['Yaw'] = df.IMU_AngVelZ * df.dt * 0.98 + (np.arctan2(df.IMU_LinearAccX, df.IMU_LinearAccY) * RAD_TO_DEG) * 0.02

    print(f'\n\t | Finished PRY calculations: time {perf_counter()-t1}')


def euler_to_quat(euler) -> list:

    from scipy.spatial.transform import Rotation

    '''
    Convert Euler Angles (Tait-Byran Angles) to Quaternions
    Uses scipy 
    '''

    rot = Rotation.from_euler('xyz', [euler[0], euler[1], euler[2]], degrees=True)
    return rot.as_quat()


def quat_to_euler(quat) -> tuple:

    from scipy.spatial.transform import Rotation

    '''
    Convert Quaternions to Euler Angles (Tait-Byran Agnles)
    Uses scipy 
    '''

    rot = Rotation.from_quat(quat)
    x, y, z = rot.as_euler('xyz', degrees=True)
    return (x, y, z)


def integrate_vel(df):

    init_lon = df.loc[0, 'GPS_Long']
    init_lat = df.loc[0, 'GPS_Lat']
    xs = df.VelX * df.dt
    ys = df.VelY * df.dt

    lon = np.zeros(len(xs))
    lat = np.zeros(len(ys))

    lon[0] = init_lon
    lat[0] = init_lat
    
    '''
    Create a list of lat lon values to pass to the plotting function
    '''

    for i in range(1, len(lon)):
        lon[i] = lon[i-1] + xs[i]
        lat[i] = lat[i-1] + ys[i]

    return lon, lat



