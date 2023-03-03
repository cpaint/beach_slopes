# 
#
"""

1. load in lidar data
2. transform into shore normal coordinate system using matrix transformation
3. select every ?X meters and create cross-shore transects
4. fit a line to the transects
5.
"""
import numpy as np
import laspy
import pandas as pd
from haversine import haversine, Unit, haversine_vector
import matplotlib.pyplot as plt

#reads the entire file. will need to update to be able to read & process
#in chunks for larger files

#lat lon
#las = laspy.read('ca2014_usace_ncmp_ca_Job821324/ca2014_usace_ncmp_ca_Job821324.las')
#coords = np.vstack((las.x, las.y, las.z)).transpose()
#df = pd.DataFrame(coords, columns=["longitude", "latitude", "depth"])
#UTM
las = laspy.read('ca2014_usace_ncmp_ca_Job821632/ca2014_usace_ncmp_ca_Job821632.las')


coords = np.vstack((las.x, las.y, las.z)).transpose()
# print(coords)

df = pd.DataFrame(coords, columns=["easting", "northing", "depth"])
print(df)


# define a new coordinate system origin that sits along red beach
# I want to choose the new origin along the beach at the southern point

zero_depth = (df.loc[df.depth == 0])
new_origin = zero_depth.loc[zero_depth.northing == min(zero_depth.northing)]
print('new origin:',new_origin)
test_point = zero_depth.loc[zero_depth.northing == max(zero_depth.northing)]
print('test points:',test_point)

print('neworigin:', new_origin)

#subtract out the new origin so that the origin is 0,0 and the other points are 
#relative to the origin
new_north = df.northing - float(new_origin.northing)
new_east = df.easting - float(new_origin.easting)

df['new_north_coord'] = new_north
df['new_east_coord'] = new_east

#use the haversine package to calculate the distance between each point and the origin

# distance = haversine(
#     (float(new_origin['latitude']), float(new_origin['longitude'])),
#     (float(test_point['latitude']), float(test_point['longitude'])),
#     unit=Unit.METERS
# )

# distances = haversine_vector(
#     new_origin[["latitude", "longitude"]],
#     df[["latitude", "longitude"]],
#     unit=Unit.METERS,
#     comb=True
# )
# df["distance_from_origin_in_meters"] = distances
# print(df.loc[new_origin.index, :]) # sanity check - should be zero


angle = np.arctan(df.northing / df.easting) #get the angle
print('angle:', np.degrees(angle))

df['original_angle'] = np.degrees(angle)

rotate_theta = np.radians(40) # starting to test at 40 degrees rotation

transform_matrix = [(np.cos(rotate_theta), np.sin(rotate_theta)),
                     (-np.sin(rotate_theta), np.cos(rotate_theta))
]
matrixdf = pd.DataFrame(data = transform_matrix)

#for i in range(len(df))
 #   original_coords = (df.easting[i], df.northing[i])

coords_new_origin = (df.new_east_coord, df.new_north_coord)

coords_transformed = matrixdf.dot(coords_new_origin)

df['transform_east'] = coords_transformed.loc[0,:]
df['transform_north'] = coords_transformed.loc[1,:]

# add the angles together to get the new angle... 

# new_lat = np.sin(newtheta) * df.distance_from_origin_in_meters
#lon new  = np.cos(newtheta) * df.distance_from_origin_in_meters 

#plot
df.head(10000).plot.scatter(x = 'transform_east', y='transform_north')
plt.show()

# df.head(10000).plot.scatter(x = 'easting', y='northing')
# plt.show()