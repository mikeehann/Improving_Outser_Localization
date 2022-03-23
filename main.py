
from numpy import sqrt
from functions import geodetic_to_geocentric, del_interpol, write_to_csv
from plot import plot_vel, plot_track
import matplotlib.pyplot as plt

from os import chdir, getcwd
from time import perf_counter

import pandas as pd


'''
TO DO
1. make everything a tuple?
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

    # Set any future interpolated standard deviations as to value of previous GNSS
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].replace(' None', pd.NA)
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].astype('string').interpolate(method='ffill').astype('float')

    # Set all values GNSS and IMU 'None' values to null, convert all object data types to presumed data types
    df = df.replace(' None', pd.NA).convert_dtypes(infer_objects=True)
    df.loc[:, 'GPS_Long':'GPS_Alt'] = df.loc[:, 'GPS_Long':'GPS_Alt'].astype('float')

    return df


def main():

    t1 = perf_counter()
    print('\n' + '#'*80 + '\n')

    # Set the input file (full, small, or just GNSS)
    infile = r'data\C2_IMU.txt'
    #infile = r'data\less_data.txt'
    #infile = r'data\GNSS.txt'

    df = setup(infile)
    print(df.info())

    t2 = perf_counter()
    print(f'\n\n\t| Setup done, time: {t2-t1}\n')

##########################################################################

    # Convert geodetic coordinates into geocentric (lat/lon to m)

    t1 = perf_counter()
    print('#'*80 + '\n')

    # Loop through every entry in the dataframe (zipping the 3 vals into a tuple), converting each GNSS coord to geocentric metres

    df.loc[:, 'GPS_Long':'GPS_Lat'] = [geodetic_to_geocentric(*a) for a in tuple(zip(df['GPS_Long'], df['GPS_Lat'], df['GPS_Alt']))]

    t2 = perf_counter()
    print(f'\n\n\t| Convert coordinates done, time: {t2-t1}\n')

##########################################################################

    # Add velocities to the data frame

    t1 = perf_counter()
    print('#'*80 + '\n')

    df['dt'] = df.Time.diff()
    df['VelX'] = df.GPS_Long.diff() / df.dt
    df['VelY'] = df.GPS_Lat.diff() / df.dt
    df['VelZ'] = df.GPS_Alt.diff() / df.dt
    df['Abs_Vel'] = sqrt(df.VelX**2 + df.VelY**2 + df.VelZ**2)

    t2 = perf_counter()
    print(F'\n\n\t| Velocities added, time: {t2-t1}\n')

    # Trim first value in df (holds null vels/accs)
    df = df.drop(index=0)

##########################################################################

    # Remove values below certain velocities

    df = df.drop(df[(df.Time < 10) & (df.Abs_Vel < 1)].index, axis=0)

##########################################################################

    '''
    set initial heading to be at index 0. 
    
    Start rotating frame of reference by this value
    '''
    # Heading is defined as a rotational matrix from true north tangent to the geoid
    # tuple is represented as (alpha, beta, gamma) <- Euler Angles
    #df['Heading'] = (df.   ,    ,   )

##########################################################################

    '''
    if GNSS SDn/u/e is too high, move the GNSS towards an IMU derived track that
    is proportional to the GNSS error value
    '''

##########################################################################

    '''
    Drop all non-critical columns
    '''

##########################################################################

    '''
    Interpolate the updated GNSS track. Ideally the Lidar IMU should have corrected
    some of the ugly GNSS points
    '''
    # df = df.interpolate(linear=True)

##########################################################################

    # Use the 'hacky' delete bad values and then interpolate? (not guaranteed to work well)

    df = del_interpol(df)

##########################################################################

    # Plotted data assumes no null values
    t1 = perf_counter()
    print('#'*80 + '\n')

    print(df.info())

    #plot_vel(df)
    plot_track(df)

    t2 = perf_counter()
    print(f'\n\n\t| Plots done, time: {t2-t1}\n')


#if __name__ == __main__:
main()


