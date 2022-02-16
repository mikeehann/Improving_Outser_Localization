# -*- coding: utf-8 -*-
"""
Created on Tue Feb 15 13:13:27 2022

@author: mikeh
"""

import os
import math
import numpy as np
import pandas as pd
from time import perf_counter
import matplotlib.pyplot as plt


# REWRITE FILE TO INTERPOLATE GNSS DATA

# Set and Get directory
os.chdir(r'C:\Users\mikeh\OneDrive\Documents\GitHub\kalmanFilter')
dir = os.getcwd()
print(f'\n\ndirectory: {dir}\n\n')

# Set the input file (full or small)
infile = 'C2_IMU.txt'
#infile = 'less_data.txt'

# Import the comma delimited .txt file as a pandas dataframe
df = pd.read_csv(f'{dir}\\{infile}', delimiter=',')

# Extract only the number from the 'Time' column using a reg ex
df['Time'] = df['Time'].str.extract('(\d+)')

# Set any future interpolated GNSS values to status 99
df['GPS_Status'].replace('None', '99')

print(df['GPS_Status'].head())

# Interpolate all values in the dataframe
#df.interpolate()


# pd.NA

#print(df.head())