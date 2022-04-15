
import pandas as pd

from functions import *

'''
TO DO

* What if linear acc from IMU equal gravity vector magnit1ude early on (limited horizontal noise)

1. Finish plot_track_from_vel function
    Steps inside the function - In progress...

1. make sure the geodetic to geocentric conversion is accurate
'''

def main():

    infile = r'data\C2_IMU.txt'
    programs = ['Delete and then interpolate GNSS values (no IMU req.)', 'Fix GNSS based on outlier velocities (no IMU req.)']
    plot_names = ['Plot GNSS track']
    plot_choice = None

    ## All for user input

    print('\n\n\n')
    for i, prog in enumerate(programs):
        print(f'\t{i+1}: {prog}')
    
    good_input = False
    while not good_input:
        try:
            prog_choice = int(input(f'\nWhat program would you like to run? (Enter #):'))
            if prog_choice in [1, 2]:
                good_input = True
        except Exception as e:
            print('Error encountered\n')
            print(e)
            print('\nPlease try again...\n')

    good_input = False
    while not good_input:
        try:
            plot_input = input(f'\n  Would you like plots too? (Enter Y/N)')
            if plot_input[0].upper() == 'Y':
                for i, plot_name in enumerate(plot_names):
                    print(f'\t{i+1}. {plot_name}')
                plot_choice = int(input(f'\nWhat plot would you like to create? (Enter #):'))
                if plot_choice in [1]:
                    good_input = True
            elif plot_input[0].upper() == 'N':
                good_input = True
            else:
                pass
        except TypeError as e:
            print('Error encountered\n')
            print(e)
            print('\nPlease try again...\n')

    ## Actually running the programs

    if prog_choice == 1:
        new_program = del_then_inter(infile, True, False, plot_choice)
        new_program.delete_vals()
        new_program.interpolate()
        new_program.write_to_file('improved_gnss')

    elif prog_choice == 2:
        new_program = fix_from_vel(infile, True, plot_choice)

if __name__ == '__main__':
    main()


