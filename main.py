
from os import chdir, getcwd
from time import perf_counter

import pandas as pd
from numpy import sqrt

from functions import geodetic_to_geocentric, orient_imu, get_PRY, write_to_csv
from plot import plot_PRY, plot_track, plot_vel, plot_acc, plot_track_from_vel

#from ux import ui

#from datetime import datetime


'''
TO DO
1. Finish plot_track_from_vel function
    Steps inside the function
2. Increase accuracy of the GNSS derived acceleration
    to make the rotational matrix more accurate
3. Keep working on orient_imu function. See if the rotational matrix will work

1. make sure the geodetic to geocentric conversion is accurate...
2. create a UI
2. convert time to datetime dtype
3. make everything a tuple?
'''

def setup(infile, has_imu) -> pd.DataFrame:

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
        df['Time'] = df['Time'].str.extract('(\d+)').astype('float')

        #gnss_df.Time = gnss_df.Time.map(lambda x: datetime.fromtimestamp(x))

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

    # If the dataframe contains IMU data, split the dataframes into separate components
    if has_imu:
        gnss_gnss_df = df.iloc[:, :8].dropna()
        imu_df = df.iloc[:, [0,8,9,10,11,12,13]].dropna()

        return gnss_gnss_df, imu_df
    # Otherwise just return the GNSS gnss_df
    else:
        return df


def main():

    t1 = perf_counter()
    print('\n' + '#'*80 + '\n')

    # Set the input file (full, small, or just GNSS)
    infile = [r'data\C2_IMU.txt', r'data\less_data.txt', r'data\GNSS.txt']

    # Make sure to update variabe assignments for different infiles
    gnss_df, imu_df = setup(infile[0], True)

    print(f'\n\t| Setup done, time: {perf_counter()-t1}\n')

##########################################################################

    # Convert geodetic coordinates into geocentric (lat/lon to m)

    t1 = perf_counter()
    print('#'*80 + '\n')

    # Loop through every entry in the dataframe (zipping the 3 vals into a tuple), converting each GNSS coord to geocentric metres

    gnss_df.loc[:, 'GPS_Long':'GPS_Lat'] = [geodetic_to_geocentric(*a) for a in tuple(zip(gnss_df['GPS_Long'], gnss_df['GPS_Lat'], gnss_df['GPS_Alt']))]

    print(f'\n\t| Convert coordinates done, time: {perf_counter()-t1}\n')

##########################################################################

    # Add velocities and accelerations to the data frame

    t1 = perf_counter()
    print('#'*80 + '\n')

    def add_vectors(df) -> pd.DataFrame:

        df['dt'] = df.Time.diff()
        df['VelX'] = df.GPS_Long.diff() / df.dt
        df['VelY'] = df.GPS_Lat.diff() / df.dt
        df['VelZ'] = df.GPS_Alt.diff() / df.dt

        # Smooth the velocity datasets by running a rolling mean over the series    
        df.VelX = df.VelX.rolling(10).mean()

        df['AccX'] = df.VelX.diff() / df.dt
        df['AccY'] = df.VelY.diff() / df.dt
        df['AccZ'] = df.VelZ.diff() / df.dt

        df['Abs_Vel'] = sqrt(df.VelX**2 + df.VelY**2 + df.VelZ**2)
        df['Abs_Acc'] = sqrt(df.AccX**2 + df.AccY**2 + df.AccZ**2)

        print(f'\n\t| Vectors added, time: {perf_counter()-t1}\n')

        # Trim first value in gnss_df (holds null vels/accs)
        df = df.drop(index=0)

        return df

    gnss_df = add_vectors(gnss_df)

##########################################################################

    # Remove values below certain velocities

    def trim_df_vel(df, time, min_vel) -> pd.DataFrame:

        df = df.drop(df[(df.Time < time) & (df.Abs_Vel < min_vel)].index, axis=0)

    gnss_df = trim_df_vel(gnss_df, 10, 1)

##########################################################################

    # Merge the data frames back together, sort by time, interpolate values, orient IMU
  
    t1 = perf_counter()
    print('#'*80 + '\n')

    def merge_dfs(df1, df2) -> pd.DataFrame:
        
        df = df1.append(df2)
        df = df.sort_values(by=['Time'])

        df = df.interpolate(method='linear')

        # Remove previously deleted values
        df = df.dropna()

        return df

    df = merge_dfs(gnss_df, imu_df)

    orient_imu(df)

    print(f'\n\t| Merged and interpolated, time: {perf_counter()-t1}\n')

##########################################################################

    '''
    If the difference between Velocities is too great, take the average of the 
    velocity before and after the outlier
    '''

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

    # Use the 'hacky' function to delete bad values and then interpolate? (not guaranteed to work well)
    '''
    from functions import del_interpol

    t1 = perf_counter()

    df = del_interpol(df)

    t2 = perf_counter()
    print(f'\n\n\t| deletion and interpolation done, time: {t2-t1}\n')
    '''
##########################################################################

    # Plotted data assumes no null values
    t1 = perf_counter()
    print('#'*80 + '\n')

    #plot_vel(df)
    plot_track_from_vel(df)
    #plot_track(df)
    #plot_PRY(df)
    #plot_acc(df)

    print(f'\n\t| Plots done, time: {perf_counter()-t1}\n')


#if __name__ == __main__:
main()


