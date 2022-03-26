
import matplotlib.pyplot as plt
from functions import write_to_csv
#import geopandas as gpd

def plot_vel(df):

    # Plot GNSS derived velocities 

    plt.figure(figsize=(15, 5))
    plt.title('GNSS Derived Velocities')
    plt.scatter(df.Time, df.VelX*3.6, color='red', s=0.5)
    plt.scatter(df.Time, df.VelY*3.6, color='green', s=0.5)
    plt.scatter(df.Time, df.Abs_Vel*3.6, color='black', s=0.5)
    plt.scatter(df.Time, df.VelZ*3.6, color='blue', s=0.5)
    plt.ylim([-100, 100])
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (km/hr)')
    plt.show() 


def plot_acc(df):

    # Plot GNSS Derived accelerations

    plt.figure(figsize=(15, 5))
    plt.title('GNSS Derived Accelerations')
    plt.scatter(df.Time, df.AccX, color='red', s=0.5)
    plt.scatter(df.Time, df.AccY, color='green', s=0.5)
    plt.scatter(df.Time, df.Abs_Acc, color='black', s=0.5)
    plt.scatter(df.Time, df.AccZ, color='blue', s=0.5)
    plt.xlabel('Time (s)')
    plt.ylabel('Acceleration (ms^-2)')
    plt.show() 


def plot_track(df):

    # Plot a nadir view of GNSS track

    plt.title("Track")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.plot(df.GPS_Long, df.GPS_Lat, color='black')
    plt.scatter(df.GPS_Long, df.GPS_Lat, c=df.SDn, cmap='copper_r')
    plt.show()


def plot_track_from_vel(df):

    # Plot a GNSS track integrated from velocity

    df.VelX = df.VelX * df.dt
    df.VelY = df.VelY * df.dt
    #df.VelZ = df.VelZ * df.dt

    write_to_csv(df, 'before')

    '''
    The issue currently is the rolling sum is not doing what I thought
    Need to continuously add to the initial GNSS value, not roll sum

    Create a for loop and IF that works, find an optimization
    '''

    df.loc[587, 'VelX'] = df.loc[587, 'GPS_Long']
    df.loc[587, 'VelY'] = df.loc[587, 'GPS_Lat']

    df.GPS_Long = df.VelX.rolling(2).sum()
    df.GPS_Lat = df.VelY.rolling(2).sum()

    write_to_csv(df, 'after')

    plt.title("Track")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.plot(df.GPS_Long, df.GPS_Lat, color='black')
    plt.scatter(df.GPS_Long, df.GPS_Lat, c=df.SDn, cmap='copper_r')
    plt.show()

def plot_PRY(df):

    # Plot Pitch, Roll, and Yaw (derived from IMU)

    plt.figure(figsize=(15, 5))
    plt.title('IMU derived Pitch, Roll, Yaw (orientation)')
    plt.plot(df.Time, df.Pitch, color='red')
    plt.plot(df.Time, df.Roll, color='green')
    plt.plot(df.Time, df.Yaw, color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Deg')
    plt.show() 


def geo_track(df):
    pass

