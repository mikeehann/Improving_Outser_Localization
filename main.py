
from functions import geodetic_to_geocentric
from plot import plot_vel, plot_track

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
    print(f'\n\ndirectory: {dir}\n\n')

    print('\treading file...\n')
    # Import the comma delimited .txt file as a pandas dataframe
    df = pd.read_csv(f'{dir}\\{infile}', delimiter=',')

    print('\tediting data types...\n')
    # Extract only the numbers from the 'Time' column using a reg ex, convert to long integer
    df['Time'] = df['Time'].str.extract('(\d+)').astype('float')

    # Convert Time into seconds from onset
    t0 = df.Time[0]
    df.Time = (df.Time-t0)/10**9

    # Set any future interpolated GNSS values to status 99
    # Set any future interpolated standard deviations as to value of previous GNSS
    df['GPS_Status'] = df['GPS_Status'].replace(' None', '99')
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].replace(' None', pd.NA)
    df.loc[:, 'SDn':'SDu'] = df.loc[:, 'SDn':'SDu'].astype('string').interpolate(method='ffill').astype(float)

    # Set all values GNSS and IMU 'None' values to null, convert all object data types to presumed data types
    df = df.replace(' None', pd.NA).convert_dtypes(infer_objects=True)
    df.loc[:, 'GPS_Long':'GPS_Alt'] = df.loc[:, 'GPS_Long':'GPS_Alt'].astype('float')

    print(df.info())

    return df


def main():

    t1 = perf_counter()

    # Set the input file (full or small)
    #infile = r'data\C2_IMU.txt'
    #infile = r'data\less_data.txt'
    infile = r'data\GNSS.txt'
    df = setup(infile)

    t2 = perf_counter()
    print(f'\t| Setup time: {t2-t1}\n')

##########################################################################

    # Convert geodetic coordinates into geocentric (lat/lon to m)
    t1 = perf_counter()

    for i in range(len(df.GPS_Long)): # Change to be a generalized column
        df.GPS_Long[i], df.GPS_Lat[i], df.GPS_Alt[i] = geodetic_to_geocentric(df.GPS_Long[i], df.GPS_Lat[i], df.GPS_Alt[i])
        ## SETTING WITH COPY WARNING ##

    t2 = perf_counter()
    print(f'\t| Convert coordinates time: {t2-t1}\n')

##########################################################################

    # Interpolate values
    # df = df.interpolate(method='linear')

##########################################################################

    # Add time-step velocities/accelerations/headings
    t1 = perf_counter()

    df['dt'] = df.Time.diff()
    df['VelX'] = df.GPS_Long.diff()
    df['VelY'] = df.GPS_Lat.diff()
    df['heading'] = ()
    # MUST DIVIDE ALL VELX AND VELY VARIABLES BY RESPECTIVE DT
    # LAMBDA FUNCTION?
    # ADD HEADINGS

    df = df.replace(' None', 0)
    #df = df.astype('float')

    t2 = perf_counter()
    print(F'\t| Additions data added (vel/acc/headings): {t2-t1}\n')

    # Trim first 2 values in df (holds null vels/accs)
    df = df.drop(index=0)

##########################################################################

    # Remove values below certain velocities
    # insert lambda function to trim all rows below a set velocity (ex. 0.1m/s)

##########################################################################

    # Plotted data assumes no null values
    t1 = perf_counter()

    print(df.info())
    print(df.VelX.head())

    plot_vel(df)
    plot_track(df)

    t2 = perf_counter()
    print(f'| Plot time: {t2-t1}\n')


#if __name__ == __main__:
main()










