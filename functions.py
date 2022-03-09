# CONVERT GNSS DD TO METRES

import numpy as np

# Sampled from YeO 
# (https://codereview.stackexchange.com/questions/195933/convert-geodetic-coordinates-to-geocentric-cartesian)

# Ellipsoid Parameters as tuples (semi major axis, inverse flattening)
#grs80 = (6378137, 298.257222100882711)
wgs84 = (6378137, 298.257223563)


def geodetic_to_geocentric(lat, lon, h, ellps=wgs84):

    # Compute the Geocentric (Cartesian) Coordinates X, Y, Z
    # given the Geodetic Coordinates lat, lon + Ellipsoid Height h
    
    a, rf = ellps
    lat_rad = np.radians(lat)
    lon_rad = np.radians(lon)
    N = a / np.sqrt(1 - (1 - (1 - 1 / rf) ** 2) * (np.sin(lat_rad)) ** 2)
    X = (N + h) * np.cos(lat_rad) * np.cos(lon_rad)
    Y = (N + h) * np.cos(lat_rad) * np.sin(lon_rad)
    Z = ((1 - 1 / rf) ** 2 * N + h) * np.sin(lat_rad)

    return X, Y, Z