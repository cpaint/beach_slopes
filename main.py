# 
#
"""
1. load in lidar data
2. transpose to a new local coordinate system
3. transform into shore normal coordinate system using rotation trig
4. select for subset of lidar data at the beach

5. select every ?X meters and create cross-shore transects
6. fit a line to the transects
7. load in LZMST data to compare
"""
import numpy as np
import laspy
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress


#UTM
las = laspy.read('Data/ca2014_usace_ncmp_ca_Job821632/ca2014_usace_ncmp_ca_Job821632.las')
coords = np.vstack((las.x, las.y, las.z)).transpose()
df = pd.DataFrame(coords, columns=["easting", "northing", "elevation_m"])
#df = pd.DataFrame([[3600000, 460000, 0 ],[3600000, 460000-100,-10]], columns=[ "northing", 'easting', "depth"])
print(df)

# define a new coordinate system origin that sits along red beach
# I want to choose the new origin along the beach at the southern point

new_origin_north = 3678000
new_origin_east = 460000
new_origin_east = 460000 + 500

#subtract out the new origin so that the origin is 0,0 and the other points are 
#relative to the origin
df['origin_north'] = df.northing - new_origin_north
df['origin_east'] = df.easting - new_origin_east

# rotate the coords
theta = np.radians(35) 
df['rotated_x'] = df.origin_north * np.sin(theta) + df.origin_east*np.cos(theta)
df['rotated_y'] = df.origin_north * np.cos(theta) - df.origin_east*np.sin(theta)

print(df)



# #_______________________________________________________________________________


#plot a sample of the points

# section = df.loc[(df.northing > 3684000 ) & (df.northing < 3686000 ) ]

# #slice in y and x
# section = df.loc[(df.rotated_y < 8000 ) 
#             & (df.rotated_y > 5000 ) 
#             & (df.elevation_m < 3 ) 
#             & (df.elevation_m > -5 )
#             & (df.rotated_x > -300)
#             & (df.rotated_x < 65)]

# section.plot.scatter(x = 'rotated_x', y='rotated_y', c = 'elevation_m',cmap = 'RdBu')
# plt.title('Camp Pendleton AVTB Beach 2014 USACE LiDAR Survey')
# plt.xlabel('Rotated coords Cross-shore (m)')
# plt.ylabel('Rotated coords Along-shore (m)')
# # plt.grid()
# plt.show()


# RED BEACH ________________
# section = df.loc[(df.rotated_y > 5000 ) & (df.rotated_y < 5500 ) ]

# slice in y and x
# section = df.loc[(df.rotated_y > 5000 ) 
#             & (df.rotated_y < 5500 ) 
#             & (df.elevation_m < 5 ) 
#             & (df.elevation_m > -5 )#]
#             & (df.rotated_x > -100)
#             & (df.rotated_x < 65)]


# section.plot.scatter(x = 'rotated_x', y='rotated_y', c = 'elevation_m',cmap = 'RdBu')

# # plt.scatter(section['rotated_x'], section['rotated_y'], c = section['depth'])
# # plt.xlim(-200,100)
# plt.title('Camp Pendleton 2014 USACE LiDAR Survey')
# plt.xlabel('Rotated coords Cross-shore (m)')
# plt.ylabel('Rotated coords Along-shore (m)')
# # plt.grid()
# plt.show()

#____________________________________________________________

# plt.plot(transect3['rotated_x'], transect3['depth'])
# plt.plot(transect4['rotated_x'], transect4['depth'])
# plt.xlim([-400,200])
# plt.ylim([-4,5])
# plt.grid()
# #plt.show()
# plt.savefig('figures/Pendleton_slope_transects')

#isolate the points with depth = 0 so we can plot the shoreline to see what our
#old & new coordinate system looks like and confirm it seems reasonable
#After checking the new coordinate system, iterate on rotation theta if needed
# zero_depth = (df.loc[(df.depth > -0.2) & (df.depth < 0.2)])
# print('zerodepth:', zero_depth)

#original coordinate system:  depth = 0 contour 
# zero_depth.head(10000).plot.scatter(x = 'easting', y='northing')
# plt.show()

# new cooridnate systemL depth = 0 contour
# zero_depth.head(10000).plot.scatter(x = 'rotated_x', y='rotated_y')
# plt.show()

#get rid of the topo lidar
is_litoral = df["elevation_m"] < 5

# #samp
# df.loc[is_litoral, :].sample(500).sort_values("rotated_x").plot.line(x = 'rotated_x', y = 'depth' )
# plt.show()

df = df.loc[is_litoral, :]

# print(max(df.rotated_y)) # 9346
# print(min(df.rotated_y)) # -1277

# bin my data.... 

# idx = []
# bathy_transects = []
# #while i < df.rotated_y.max() :
# #for i in range(2000,3000):
# for i in range(2000,2060):
#     ii = i+1
#     transects = df.loc[(df.rotated_y > i ) & (df.rotated_y < ii )]
#     transects = transects.sort_values('rotated_x')
#     #need to create a way to index by the slices I am creating here....
#     bathy_transects.append(transects.sort_values('rotated_x'))
#     idx.append(i)
#     i = i + 20
# print('_____________________________________')

# print(idx)
# print(bathy_transects)
# # bathy_transects['transect_idx'] = idx
# # type(bathy_transects)
# # print(bathy_transects)

# for j in range(len(bathy_transects)):
#     plt.plot(bathy_transects['rotated_x'], transect4['depth'])
# plt.title('Camp Pendleton Cross-shore Transects from 2014 USACE LiDAR Survey')
# plt.xlabel('distance (m)')
# plt.ylabel('Depth (m)')
# plt.grid()
# plt.savefig('figures/1m_transections')


# PLOTS ____________________________________________________________________

# get transects RED BEACH

# transect1 = df.loc[(df.rotated_y > 5470 ) & (df.rotated_y < 5471 )]
# transect1 = transect1.sort_values('rotated_x')

# transect2 = df.loc[(df.rotated_y > 5400 ) & (df.rotated_y < 5401 )]
# transect2 = transect2.sort_values('rotated_x') 

# transect3 = df.loc[(df.rotated_y > 5350 ) & (df.rotated_y < 5351 )]
# transect3 = transect3.sort_values('rotated_x')

# transect4 = df.loc[(df.rotated_y > 5300 ) & (df.rotated_y < 5301 )]
# transect4 = transect4.sort_values('rotated_x')

# transect5 = df.loc[(df.rotated_y > 5250 ) & (df.rotated_y < 5251 )]
# transect5 = transect5.sort_values('rotated_x')

# transect6 = df.loc[(df.rotated_y > 5200 ) & (df.rotated_y < 5201 )]
# transect6 = transect6.sort_values('rotated_x')

# transect7 = df.loc[(df.rotated_y > 5150 ) & (df.rotated_y < 5151 )]
# transect7 = transect7.sort_values('rotated_x')

# transect8 = df.loc[(df.rotated_y > 5100 ) & (df.rotated_y < 5101 )]
# transect8 = transect8.sort_values('rotated_x')


# ACTB Beach

transect1 = df.loc[(df.rotated_y > 6520 ) & (df.rotated_y < 6521 )]
transect1 = transect1.sort_values('rotated_x')

transect2 = df.loc[(df.rotated_y > 6600 ) & (df.rotated_y < 6601 )]
transect2 = transect2.sort_values('rotated_x') 

transect3 = df.loc[(df.rotated_y > 6700 ) & (df.rotated_y < 6701 )]
transect3 = transect3.sort_values('rotated_x')

transect4 = df.loc[(df.rotated_y > 6800 ) & (df.rotated_y < 6801 )]
transect4 = transect4.sort_values('rotated_x')

transect5 = df.loc[(df.rotated_y > 6900 ) & (df.rotated_y < 6901 )]
transect5 = transect5.sort_values('rotated_x')

transect6 = df.loc[(df.rotated_y > 7000 ) & (df.rotated_y < 7001 )]
transect6 = transect6.sort_values('rotated_x')

transect7 = df.loc[(df.rotated_y > 7200 ) & (df.rotated_y < 7201 )]
transect7 = transect7.sort_values('rotated_x')

transect8 = df.loc[(df.rotated_y > 7100 ) & (df.rotated_y < 7101)]
transect8 = transect8.sort_values('rotated_x')


#isolate beach and surf zone
is_beach = (df.rotated_x < 65) & (df.rotated_x > -100)
is_surf = (df.rotated_x < 10) & (df.rotated_x > -800)
#transects filtered over the beach
# transect4 = transect4.loc[is_beach,:]
# transect3 = transect3.loc[is_beach,:]
# transect2 = transect2.loc[is_beach,:]
# transect1 = transect1.loc[is_beach,:]

#transects filtered over the surf
# transect4 = transect4.loc[is_surf,:]
# transect3 = transect3.loc[is_surf,:]
# transect2 = transect2.loc[is_surf,:]
# transects = transects.loc[is_surf,:]
#combine transects for stats
all_transects = pd.concat([transect1, transect2,transect3,
                        transect4, transect5, transect6,
                        transect7, transect8])


# is_beach = (all_transects.rotated_x < 65) & (all_transects.rotated_x > -100)
# beach = all_transects.loc[is_beach, :]
beach = all_transects.loc[is_beach,:]
surf = all_transects.loc[is_surf, :]

#Get the average slope of the transects
slope, intercept, r, p, se = linregress(beach.rotated_x, beach.elevation_m)
#slope, intercept, r, p, se = linregress(surf.rotated_x, surf.elevation_m)
#draw line with the slope intercept using matplotlib
print('slope:',slope)
slp = round(slope,ndigits=3)
print('intercept',intercept)


# plt.suptitle('Camp Pendleton Red Beach cross-shore surf-zone transects')
# plt.text(-700,2,'Linear fit slope:')
# plt.text(-500,2, slp )
# plt.xlim([-800,50])

plt.suptitle('Camp Pendleton AVTB Beach cross-shore Beach transects')
plt.text(-125,2,'Linear fit slope:')
plt.text(-55,2, slp )
plt.xlim([-150,100])
plt.ylim([-5,6])
plt.xlabel('Cross-shore Distance (m)')
plt.ylabel('Elevation (m)')
plt.axline(xy1 = (0, intercept), xy2 = None, slope = slope, color = 'black' )
plt.plot(transect1['rotated_x'], transect1['elevation_m'])
plt.plot(transect2['rotated_x'], transect2['elevation_m'])
plt.plot(transect3['rotated_x'], transect3['elevation_m'])
plt.plot(transect4['rotated_x'], transect4['elevation_m'])
plt.plot(transect5['rotated_x'], transect5['elevation_m'])
plt.plot(transect6['rotated_x'], transect6['elevation_m'])
plt.plot(transect7['rotated_x'], transect7['elevation_m'])
plt.plot(transect8['rotated_x'], transect8['elevation_m'])


plt.grid()
plt.savefig('figures/pendleton_beachTransects_AVTB',dpi = 700)
#plt.savefig('figures/pendleton_surfzoneTransects_Red',dpi = 700)








# plt.plot(transects['rotated_x'], transects['elevation_m'])
# plt.plot(transect2['rotated_x'], transect2['elevation_m'])
# plt.plot(transect3['rotated_x'], transect3['elevation_m'])
# plt.plot(transect4['rotated_x'], transect4['elevation_m'])
# plt.xlim([-400,200])
# plt.ylim([-4,5])
# plt.grid()
# plt.show()
#plt.savefig('figures/Pendleton_slope_transects2')

# df.head(80000).plot.scatter(x = 'rotated_x', y='rotated_y')
# plt.show()


