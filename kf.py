#import pykalman  #numpy, scipy, pykalman
import os

#os.chdir(r'C:/Users/mikeh/OneDrive/Documents/GitHub/school/Semester 2/GISY 6044')

dir = os.getcwd()
print(f'\n\ndirectory: {dir}\n\n')


infile = 'C2_IMU.txt'


def kf():
    with open(infile, 'r') as f:
        for line in f:
            data = line.readline()
            print(data)
    return

kf()




















