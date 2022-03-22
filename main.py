
from numpy import float64
from functions import geodetic_to_geocentric
from plot import plot_vel, plot_track
import matplotlib.pyplot as plt

from os import chdir, getcwd
from time import perf_counter

import pandas as pd


'''
TO DO
1. make everything a tuple
'''


# INGEST FILE

def setup(infile):

    # Set and Get directory
    chdir(r'C:\Users\mikeh\OneDrive\Documents\GitHub\ouster_localization')
    dir = getcwd()
    print(f'\ndirectory: {dir}\n\n')

    print('\treading file...\n')
    # Import the comma delimited .txt file as a pandas dataframe
    df = pd.read_csv(f'{dir}\\{infile}', delimiter=',')

    print('\tediting data types...\n')
    # Extract only the numbers from the 'Time' column using a reg ex, convert to long integer
    df['Time'] = df['Time'].str.extract('(\d+)').astype('float')

    # Convert Time into seconds from onset
    t0 = df['Time'][0]
    df['Time'] = (df['Time']-t0)/10**9

    # Set any future interpolated GNSS values to status 99
    # Set any future interpolated standard deviations as to value of previous GNSS
    df['GPS_Status'] = df['GPS_Status'].replace(' None', '99')
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].replace(' None', pd.NA)
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].astype('string').interpolate(method='ffill').astype('float')

    # Set all values GNSS and IMU 'None' values to null, convert all object data types to presumed data types
    df = df.replace(' None', pd.NA).convert_dtypes(infer_objects=True)
    df.loc[:, 'GPS_Long':'GPS_Alt'] = df.loc[:, 'GPS_Long':'GPS_Alt'].astype('float')

    return df


def main():

    t1 = perf_counter()
    print('\n' + '#'*80 + '\n')

    # Set the input file (full or small)
    #infile = r'data\C2_IMU.txt'
    #infile = r'data\less_data.txt'
    infile = r'data\GNSS.txt'

    # File headings:
    # Time, GNSS_Long, GNSS_Lat, GNSS_Alt, ... x6

    df = setup(infile)
    print(df.info())

    t2 = perf_counter()
    print(f'\n\n\t| Setup time: {t2-t1}\n')

##########################################################################

    # Eventually convert this to a dataframe map

    # Convert geodetic coordinates into geocentric (lat/lon to m)
    t1 = perf_counter()
    print('#'*80 + '\n')

    # Loop through every entry in the dataframe, converting each GNSS coord to geocentric metres
    for i in range(len(df.GPS_Long)):
        df.loc[i, 'GPS_Long':'GPS_Lat'] = geodetic_to_geocentric(df.loc[i, 'GPS_Long':'GPS_Alt'])

    t2 = perf_counter()
    print(f'\n\n\t| Convert coordinates time: {t2-t1}\n')

##########################################################################

    # Interpolate values
    # df = df.interpolate(method='linear')

##########################################################################

    # Add time-step velocities/accelerations/headings
    t1 = perf_counter()
    print('#'*80 + '\n')

    df['dt'] = df.Time.diff()
    df['VelX'] = df.GPS_Long.diff() / df.dt
    df['VelY'] = df.GPS_Lat.diff() / df.dt
    df['VelZ'] = df.GPS_Alt.diff() / df.dt

    #df['def_heading'] = ()

    df = df.replace(' None', 0)
    #df = df.astype('float')

    t2 = perf_counter()
    print(F'\n\n\t| Additions data added (vel/acc/headings): {t2-t1}\n')

    # Trim first 2 values in df (holds null vels/accs)
    df = df.drop(index=0)

##########################################################################

    # Remove values below certain velocities
    # insert lambda function to trim all rows below a set velocity (ex. 0.1m/s)

##########################################################################

    '''
    set initial heading to be at index 0. 
    
    Start rotating frame of reference by this value
    '''

##########################################################################

    '''
    if GNSS SDn/u/e is too high, move the GNSS towards an IMU derived track that
    is proportional to the GNSS error value
    '''

##########################################################################

    # Plotted data assumes no null values
    t1 = perf_counter()
    print('#'*80 + '\n')

    plot_vel(df)
    #plot_track(df)

    t2 = perf_counter()
    print(f'\n\n\t| Plot time: {t2-t1}\n')


#if __name__ == __main__:
main()


