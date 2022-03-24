
from functions import geodetic_to_geocentric, write_to_csv, get_PRY
from plot import plot_vel, plot_track, plot_PRY
#from ux import ui

from os import chdir, getcwd
from time import perf_counter
#from datetime import datetime

import pandas as pd
from numpy import sqrt

'''
TO DO
1. make sure the geodetic to geocentric conversion is accurate...
2. convert time to datetime dtype
3. make everything a tuple?
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

    #df.Time = df.Time.map(lambda x: datetime.fromtimestamp(x))

    # Convert Time into seconds from onset
    t0 = df['Time'][0]
    df['Time'] = (df['Time']-t0)/10**9

    # Forcing proper data types for each column
    df = df.apply(lambda x: pd.to_numeric(x, errors='coerce'))

    # Forward fill standard deviations, so they are not linearly interpolated later
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].interpolate(method='ffill')

    return df


def main():

    t1 = perf_counter()
    print('\n' + '#'*80 + '\n')

    # Set the input file (full, small, or just GNSS)
    #infile = r'data\C2_IMU.txt'
    #infile = r'data\less_data.txt'
    infile = r'data\GNSS.txt'

    df = setup(infile)

    print(f'\n\n\t| Setup done, time: {perf_counter()-t1}\n')

##########################################################################

    # Convert geodetic coordinates into geocentric (lat/lon to m)

    t1 = perf_counter()
    print('#'*80 + '\n')

    # Loop through every entry in the dataframe (zipping the 3 vals into a tuple), converting each GNSS coord to geocentric metres

    df.loc[:, 'GPS_Long':'GPS_Lat'] = [geodetic_to_geocentric(*a) for a in tuple(zip(df['GPS_Long'], df['GPS_Lat'], df['GPS_Alt']))]

    print(f'\n\n\t| Convert coordinates done, time: {perf_counter()-t1}\n')

##########################################################################

    # Add velocities to the data frame

    t1 = perf_counter()
    print('#'*80 + '\n')

    df['dt'] = df.Time.diff()
    df['VelX'] = df.GPS_Long.diff() / df.dt
    df['VelY'] = df.GPS_Lat.diff() / df.dt
    df['VelZ'] = df.GPS_Alt.diff() / df.dt
    df['Abs_Vel'] = sqrt(df.VelX**2 + df.VelY**2 + df.VelZ**2)

    print(F'\n\n\t| Velocities added, time: {perf_counter()-t1}\n')

    # Trim first value in df (holds null vels/accs)
    df = df.drop(index=0)

##########################################################################

    # Remove values below certain velocities

    df = df.drop(df[(df.Time < 10) & (df.Abs_Vel < 1)].index, axis=0)

##########################################################################

    '''
    set initial heading to be at index 0. 
    
    Start rotating frame of reference by this value

    Heading is defined as a rotation from true north tangent to the geoid
    ENU world reference frame
    tuple is represented as (alpha, beta, gamma) <- Euler/Tait-Bryan Angles (Yaw, Roll, Yaw)

    RPY is used in in the body frame,
    ENU is used in the world frame
    '''
    get_PRY(df)

    #df['Heading'] = (df.,    ,   )

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
    df = df.interpolate(linear=True)

##########################################################################

    # Use the 'hacky' delete bad values and then interpolate? (not guaranteed to work well)

    from functions import del_interpol
    df = del_interpol(df)

##########################################################################

    # Plotted data assumes no null values
    t1 = perf_counter()
    print('#'*80 + '\n')

    print(df.info())

    #plot_vel(df)
    plot_track(df)
    #plot_PRY(df)

    print(f'\n\n\t| Plots done, time: {perf_counter()-t1}\n')


#if __name__ == __main__:
main()


