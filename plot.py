import matplotlib.pyplot as plt
#import geopandas as gpd

def plot_vel(df):

    # Plot GNSS derived velocities 

    plt.figure(figsize=(20, 5))
    plt.title('GNSS Derived Velocities')
    plt.scatter(df.Time, df.VelX*3.6, color='red', s=0.5)
    plt.scatter(df.Time, df.VelY*3.6, color='green', s=0.5)
    plt.scatter(df.Time, df.Abs_Vel*3.6, color='black', s=0.5)
    plt.scatter(df.Time, df.VelZ*3.6, color='blue', s=0.5)
    plt.xlabel('Time (s)')
    plt.ylabel('Velocity (km/hr)')
    plt.show() 


def plot_track(df):

    # Plot a nadir view of GNSS track

    plt.title("Track")
    plt.xlabel("longitude")
    plt.ylabel("latitude")
    plt.plot(df.GPS_Long, df.GPS_Lat, color='black')
    plt.scatter(df.GPS_Long, df.GPS_Lat, c=df.SDn, cmap='copper_r')
    plt.show()


def plot_PRY(df):

    # Plot Pitch, Roll, and Yaw (derived from IMU)

    plt.figure(figsize=(20, 5))
    plt.title('IMU derived Pitch, Roll, Yaw (orientation)')
    plt.plot(df.Time, df.Pitch, color='red')
    plt.plot(df.Time, df.Roll, color='green')
    plt.plot(df.Time, df.Yaw, color='blue')
    plt.xlabel('Time (s)')
    plt.ylabel('Deg')
    plt.show() 


def geo_track(df):
    pass

