import os
import matplotlib.pyplot as plt
import numpy as np

#Time,GPS_Long,GPS_Lat,GPS_Alt,SDn,SDe,SDu,GPS_Status,IMU_AngVelX,IMU_AngVelY,IMU_AngVelZ,IMU_LinearAccX,IMU_LinearAccY,IMU_LinearAccZ

dir = os.getcwd()
print(f'\n\ndirectory: {dir}\n\n')

infile = 'C2_IMU.txt'

time, lon, lat, alt, gnss_sd, status, imu_ang_vel, imu_lin_acc = [], [], [], [], [], [], [], []


def in_data():
    with open(infile, 'r') as f:
        f.readline()
        for line in f:
            t, lo, la, al, sd_n, sd_e, sd_u, stat, ia_velx, ia_vely, ia_velz, il_accx, il_accy, il_accz  = line.replace(' ', '').strip().split(',')
            if lo != 'None':
                time.append(t)
                status.append(stat)
                lon.append(float(lo))
                lat.append(float(la))
                alt.append(float(al))
                #gnss_sd.append([sd_n], [sd_e], [sd_u])
                #imu_ang_vel.append((ia_velx, ia_vely, ia_velz))
                #imu_lin_acc.append((il_accx, il_accy, il_accz))
    plt.plot(lat, lon)
    print(np.mean(lon))
    return


def kf():
    return

def main():
    in_data()
    kf()


main()



















