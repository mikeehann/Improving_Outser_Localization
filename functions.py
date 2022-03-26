
from time import perf_counter

import numpy as np
import pandas as pd
from scipy.spatial.transform import Rotation


def geodetic_to_geocentric(lat, lon, h, ellps=(6378137, 298.257223563)):
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

    a, rf = ellps
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    N = a / np.sqrt(1 - (1 - (1 - 1 / rf) ** 2) * (np.sin(lat_rad)) ** 2)
    X = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = ((1 - 1 / rf) ** 2 * N + h) * np.sin(lat_rad)

    # Only return the latitude and longitude
    return [X, Y]


def orient_imu(df):
    '''
    Takes in a dataframe with GNSS and IMU values
    Returns a df with the IMU values oriented to the intertial
    frame of reference
    '''

    # Create a normalized IMU vector

    df['A_hat'] = tuple(zip(df.IMU_LinearAccX / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2),
                            df.IMU_LinearAccY / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2),
                            df.IMU_LinearAccZ / np.sqrt(df.IMU_LinearAccX**2 + df.IMU_LinearAccY**2 + df.IMU_LinearAccZ**2)))

    # Create a normalized GNSS vector as a target to match
    # Use derived accelerations from positions with gravity vector

    df['G_hat'] = tuple(zip(df.AccX / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2),
                            df.AccY / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2),
                            (df.AccZ-9.801) / np.sqrt(df.AccX**2 + df.AccY**2 + (df.AccZ-9.801)**2)))


def get_PRY(df): 
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


def euler_to_quat(euler):
    '''
    Convert Euler Angles (Tait-Byran Angles) to Quaternions
    Uses scipy 
    '''

    rot = Rotation.from_euler('xyz', [euler[0], euler[1], euler[2]], degrees=True)
    return rot.as_quat()


def quat_to_euler(quat):
    '''
    Convert Quaternions to Euler Angles (Tait-Byran Agnles)
    Uses scipy 
    '''

    rot = Rotation.from_quat(quat)
    x, y, z = rot.as_euler('xyz', degrees=True)
    return (x, y, z)


def write_to_csv(df, title):
    '''
    Writes a dataframe to a .csv in the local folder
    '''

    df.to_csv(f'{title}.csv')


def rem_vel_outlier(df):
    '''
    The goal of this function is the create a new GNSS path by smoothing velocity outliers
    and pathing the GNSS points as if there was no velocity outlier
    '''


def del_interpol(df):
    '''
    Takes in a df with GNSS data
    Deletes any GNSS value with too much error (default at over 0.005m)
    interpolates between the deleted values to 'refill' the track
    '''

    print('\n\tdeleting bad values...\n')

    # Copy the dataframe and maniuplate the copy (don't mess up the original data)
    new_df = df.copy(deep=True)

    # Delete unimportant columns
    new_df.drop(new_df.loc[:,'IMU_AngVelX':'IMU_LinearAccZ'].columns, inplace=True, axis=1)

    # Loop through the dataframe, if standard  
    # deviations are too high set that row to null
    ''' 
    the below function would be used to speed the for loop up if required (~28s on my comp vs ~0.7s) 
    wont implement if not desired

    def high_err(sd):
        pass
    '''
    for i in range(len(new_df.GPS_Long)):
        try:
            if new_df.SDn[i] > 0.005:
                new_df.loc[i,'GPS_Long':'GPS_Alt'] = pd.NA
        except KeyError as ke:
            pass

    print('\tinterpolating...\n')

    # Force columns into numeric data types
    new_df['GPS_Long'] = pd.to_numeric(new_df['GPS_Long'], errors='coerce')
    new_df['GPS_Lat'] = pd.to_numeric(new_df['GPS_Lat'], errors='coerce')
    new_df['GPS_Alt'] = pd.to_numeric(new_df['GPS_Alt'], errors='coerce')

    # Interpolate all GNSS values in the df as floats
    new_df.loc[:, 'GPS_Long':'GPS_Alt'] = new_df.loc[:, 'GPS_Long':'GPS_Alt'].interpolate(method='linear')
    new_df['GPS_Status'] = new_df['GPS_Status'].interpolate(method='ffill')

    # Remove previously deleted values
    new_df = new_df[new_df['GPS_Long'].notna()]

    return new_df
