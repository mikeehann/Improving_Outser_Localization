import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
#import geopandas as gpd

def plot_vel(df):

    # Plot GNSS derived velocities 
    plt.figure(figsize=(20, 5))
    plt.title('GNSS Derived Velocities')
    plt.scatter(df.Time, df.VelX*3.6, color='red', s=0.5)
    plt.scatter(df.Time, df.VelY*3.6, color='green', s=0.5)
    plt.scatter(df.Time, np.sqrt(df.VelX**2 + df.VelY**2 + df.VelZ**2)*3.6, color='black', s=0.5)
    plt.scatter(df.Time, df.VelZ*3.6, color='blue', s=0.5)
    #plt.scatter(df.Time, df.GPS_Alt, color='orange')
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (km/hr)')
    plt.show() 

    # Plot GNSS derived accelerations
    '''plt.figure(figsize=(20, 5))
    plt.title('GNSS Derived Accelerations')
    plt.plot(df.Time, df.AccX, color='red')
    plt.plot(df.Time, df.AccY, color='green')
    plt.plot(df.Time, sqrt(df.AccX**2 + df.AccY**2 + df.AccZ**2), color='black')
    plt.plot(df.Time, df.AccZ, color='blue')
    plt.xlabel('IMU Time')
    plt.ylabel('Acceleration (m/s2)')
    plt.show()'''


def plot_track(df):

    plt.title("Tracks")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.scatter(df.GPS_Long, df.GPS_Lat, c=df.SDn, cmap='copper_r')
    plt.show()


def geo_track(df):
    pass

