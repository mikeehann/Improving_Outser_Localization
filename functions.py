
import numpy as np
import pandas as pd
from time import perf_counter
from scipy.spatial.transform import Rotation


# Ellipsoid Parameters as tuples (semi major axis, inverse flattening)
#grs80 = (6378137, 298.257222100882711)
wgs84 = (6378137, 298.257223563)

def geodetic_to_geocentric(lat, lon, h, ellps=wgs84):

    # Convert GNSS DD to Metres

    # Sampled from YeO 
    # (https://codereview.stackexchange.com/questions/195933/convert-geodetic-coordinates-to-geocentric-cartesian)


    # Compute the Geocentric (Cartesian) Coordinates X, Y, Z
    # given the Geodetic Coordinates lat, lon + Ellipsoid Height h
    '''
    lat = coord_array[0]
    lon = coord_array[1]
    h   = coord_array[2]
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


# Convert Euler Angles to Quaternions using scipy

def euler_to_quat(euler):
    rot = Rotation.from_euler('xyz', [euler[0], euler[1], euler[2]], degrees=True)
    return rot.as_quat()


# Convert Quaternions to Euler Angles using scipy

def quat_to_euler(quat):
    rot = Rotation.from_quat(quat)
    x, y, z = rot.as_euler('xyz', degrees=True)
    return (x, y, z)


# Write data frames to csvs

def write_to_csv(df):

    # Write data
    df.to_csv('new_data.csv')


# Delete GNSS values with too much error, then interpolate 
# Not necessarily recommended

def del_interpol(df):

    t1 = perf_counter()

    print('\tdeleting bad values...\n')

    # Copy the dataframe and maniuplate the copy (don't mess up the original data)
    new_df = df.copy(deep=True)

    # Delete unimportant columns
    new_df.drop(new_df.loc[:,'IMU_AngVelX':'IMU_LinearAccZ'].columns, inplace=True, axis=1)

    # Loop through the dataframe, if standard  
    # deviations are too high set that row to null
    '''
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

    #End performance counter
    t2 = perf_counter()
    print(f'\n\n\t| deletion and interpolation time: {t2-t1}\n')

    return new_df