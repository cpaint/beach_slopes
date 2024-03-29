"""
1. load in lidar data
2. transpose to a new local coordinate system & rotate to shore normal 
coordinate system using rotation trig
4. select for subset of lidar data at the beach
5. select cross-shore transects
6. fit a linear regression to the transect data

7. load in LZMST data to compare
"""
from typing import List
import numpy as np
import laspy
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline

def import_lidar_las(filename: str) -> pd.DataFrame:
    """Load lidar (.las) point data in UTM coordinates.
    
    This file should be in UTM coordinates and NAVD88 vertical coordinates, which should
    be in meters. Data portal: NOAA Data Viewer website.

    Args:
        filename: path to .las file to load

    Returns:
        pd.DataFrame containing columns for:
            easting: meters east of known origin
            northing: meters north of known origin
            elevation_m: height above or below ground
    """
    las = laspy.read(filename)
    coords = np.vstack((las.x, las.y, las.z)).transpose()
    df = pd.DataFrame(coords, columns=["easting", "northing", "elevation_m"])

    return df


def transform_coordinates(
    df: pd.DataFrame,
    # northing: pd.Series,
    # easting: pd.Series,
    new_origin_north: float,
    new_origin_east: float,
    theta_deg: float
) -> pd.DataFrame:
    """Transpose to a local coordinate system & rotate coordinates to be shore normal

    You will likely need to iterate over both the assigned coordiante origin and 
    rotation angle to find the cleanest transformation. 

    Args:
        df: dataframe needs to have a columns for easting and northing
        new_origin_north: location (in UTM) ideally along the shoreline
        new_origin_east: location (in UTM) ideally along the shoreline
        theta_deg: the angle that the shoreline sits at - degrees from true north
    
    Returns:
        df: which now also includes a column for rotated_x and rotated_y
    """
    shifted_northing = df.northing - new_origin_north
    shifted_easting = df.easting - new_origin_east

    theta_rad = np.radians(theta_deg) 

    df['rotated_x'] = shifted_northing * np.sin(theta_rad) + shifted_easting*np.cos(theta_rad)
    df['rotated_y'] = shifted_northing * np.cos(theta_rad) - shifted_easting*np.sin(theta_rad)
    
    return df


def build_transects(
    df: pd.DataFrame,
    y_min: float,
    y_max: float,
    y_transect_width: float,
    y_transect_gap: float
) -> pd.DataFrame:
    """ Creates a dataframe subset from input df beach transects based on input metrics.

    The transect width and transect gap will vary depending on the resolution of 
    data and size of beach slice you are interogating.

    Args:
        df: input dataframe with at minimum rotated_y rotated_y, elevation_m columns
        y_min: the minimun x cooridante that you want included in your beach section
        y_max: the minimun x cooridante that you want included in your beach section
        Y_transect_width: how wide (in meters) do you want the transects to be?
        y_transect_gap: how much space (in meters) between transects?

    Returns:
        pd.DataFrame with subset of df rows and an additional transect_id column 
    """
    count = 0
    y_current = y_min
    transects: List[pd.DataFrame] = []
    while y_current < y_max:
        transect_y_min = y_current
        transect_y_max = transect_y_min + y_transect_width
        is_transect = (df.rotated_y >= transect_y_min) & (df.rotated_y <= transect_y_max)

        transect_df = df.loc[is_transect, :].copy()
        transect_df.loc[:, "transect_id"] = count
        transects.append(transect_df)

        y_current = y_current + y_transect_gap
        count = count + 1
        # count += 1

    transects_df = pd.concat(transects)
    transects_df = transects_df.sort_values(["transect_id", "rotated_x"])
    return transects_df


def plot_x_depth_transects(
    df: pd.DataFrame,
    title: str,
    regression_slope: float,
    regression_intercept: float,
    xlim: List[float],
    ylim: List[float],
    export_filename: str,
) -> None:
    """ Plot cross-shore transects along beach or surf-zone sections of data


    Args:
        df: needs rotated_x, and elevation_m columns
        Title: Plot title
        regression_slope: 
        regression_intercept: y intercept
        xlim: the min and max numbers you want plotted on the x axis
        ylim: the min and max numbers you want plotted on the y axis
        export_filename: the filename and location

    Returns:
        Figure plot 
    """
    plt.suptitle(title)
    plt.title(f'Linear fit slope: {regression_slope:.02}')
    plt.xlim(xlim)
    plt.ylim(ylim)
    plt.xlabel('Cross-shore Distance (m)')
    plt.ylabel('Elevation (m)')

    transect_ids = df.transect_id.unique()
    for transect_id in transect_ids:
        is_transect = df.transect_id == transect_id
        transect_df = df.loc[is_transect, :]
        plt.plot(transect_df.rotated_x, transect_df.elevation_m)
       

    plt.axline(xy1 = (0, regression_intercept), xy2 = None, slope = regression_slope, color = 'black' )
    plt.grid()
    plt.savefig(export_filename, dpi = 300)
    plt.close()

#_____________________________________________________
#_____________________________________________________l

#####################################################################


df = import_lidar_las('/Users/rdchlcap/repos/beachslopes/data/pendleton/ca2014_usace_ncmp_ca_Job821632/ca2014_usace_ncmp_ca_Job821632.las')
df = transform_coordinates(df, new_origin_north=3678000, new_origin_east=460000 + 500, theta_deg=35)

plot_avtb = False
plot_red = False
plot_noname = True
if plot_avtb:
    # ACTB Beach
    df_actb = build_transects(df, y_min=6520, y_max=7200, y_transect_width=1, y_transect_gap=100)

    is_beach = (df_actb.rotated_x < 65) & (df_actb.rotated_x > -100)
    is_surf = (df_actb.rotated_x < 10) & (df_actb.rotated_x > -800)
    beach = df_actb.loc[is_beach,:]
    surf = df_actb.loc[is_surf, :]

    beach_slope, beach_intercept, r, p, se = linregress(beach.rotated_x, beach.elevation_m)
    surf_slope, surf_intercept, r, p, se = linregress(surf.rotated_x, surf.elevation_m)

    plot_x_depth_transects(
        df=df_actb,
        title="Camp Pendleton AVTB Beach cross-shore Beach transects",
        regression_slope = beach_slope,
        regression_intercept = beach_intercept,
        xlim=[-150, 100],
        ylim=[-5, 6], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/newpendleton_beachTransects_AVTB'
    )

    plot_x_depth_transects(
        df=df_actb,
        title="Camp Pendleton AVTB Beach cross-shore surf-zone transects",
        regression_slope = surf_slope,
        regression_intercept = surf_intercept,
        xlim=[-800, 50],
        ylim=[-12, 4], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/newpendleton_surfzoneTransects_AVTB'
    )
if plot_red:
    # Red Beach
    df_red = build_transects(df,y_min = 5100, y_max = 5500, y_transect_width=1, y_transect_gap= 50)

    is_beach = (df_red.rotated_x < 65) & (df_red.rotated_x > -100)
    is_surf = (df_red.rotated_x < 10) & (df_red.rotated_x > -800)
    beach = df_red.loc[is_beach,:]
    surf = df_red.loc[is_surf, :]

    beach_slope, beach_intercept, r, p, se = linregress(beach.rotated_x, beach.elevation_m)
    surf_slope, surf_intercept, r, p, se = linregress(surf.rotated_x, surf.elevation_m)

    plot_x_depth_transects(
        df=df_red,
        title="Camp Pendleton Red Beach cross-shore Beach transects",
        regression_slope=beach_slope,
        regression_intercept=beach_intercept,
        xlim=[-150, 100],
        ylim=[-5, 6], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/newpendleton_beachTransects_red'
    )

    plot_x_depth_transects(
        df=df_red,
        title="Camp Pendleton Red Beach cross-shore surf-zone transects",
        regression_slope=surf_slope,
        regression_intercept=surf_intercept,
        xlim=[-800, 50],
        ylim=[-12, 4], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/newpendleton_surfTransects_red'
    )
if plot_noname:
    # Northern beach by 7000-7500 where there aren't data gaps
    df_red = build_transects(df,y_min = 7100, y_max = 7400, y_transect_width=1, y_transect_gap= 50)

    is_beach = (df_red.rotated_x < 65) & (df_red.rotated_x > -100)
    is_surf = (df_red.rotated_x < 10) & (df_red.rotated_x > -800)
    beach = df_red.loc[is_beach,:]
    surf = df_red.loc[is_surf, :]

    beach_slope, beach_intercept, r, p, se = linregress(beach.rotated_x, beach.elevation_m)
    surf_slope, surf_intercept, r, p, se = linregress(surf.rotated_x, surf.elevation_m)

    plot_x_depth_transects(
        df=df_red,
        title="Camp Pendleton no name Beach cross-shore Beach transects",
        regression_slope=beach_slope,
        regression_intercept=beach_intercept,
        xlim=[-150, 100],
        ylim=[-5, 6], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/Pendleton_beachTransects_noname2'
    )

    plot_x_depth_transects(
        df=df_red,
        title="Camp Pendleton Red Beach cross-shore surf-zone transects",
        regression_slope=surf_slope,
        regression_intercept=surf_intercept,
        xlim=[-1200, 500],
        ylim=[-12, 20], 
        export_filename='/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/Pendleton_surfTransects_noname2'
    )
print('done plotting')
#_______________________________________________________________________________
# Plots to check data along the way:

#isolate the points with depth = 0 so we can plot the shoreline to see what our
#old & new coordinate system looks like and confirm it seems reasonable
#After checking the new coordinate system shoreline (as defined by dep = 0) 
## iterate on rotation theta if needed
# zero_depth = (df.loc[(df.elevation_m > -0.2) & (df.elevation_m < 0.2)])
# zero_depth.head(10000).plot.scatter(x = 'easting', y='northing')
# plt.show()


#plot a map in rotated cooridnates, beach slice can be IDed by either the rotated
#or original coordinate system

orig_map=plt.cm.get_cmap('RdBu')
colormap = orig_map.reversed()

section = df.loc[(df.northing > 3684000 ) & (df.northing < 3686000 ) ]

section = df.loc[(df.rotated_y < 7200 ) 
            & (df.rotated_y > 6500 ) 
            # & (df.elevation_m < 5 ) 
            # & (df.elevation_m > -5 )
            & (df.rotated_x > -300)
            & (df.rotated_x < 90)]

section.plot.scatter(x = 'rotated_x', y='rotated_y', c = 'elevation_m',cmap = colormap, vmin=-4,vmax = 4)
plt.title('Camp Pendleton AVTB Beach 2014 USACE LiDAR Survey')
plt.xlabel('Rotated coords Cross-shore (m)')
plt.ylabel('Rotated coords Along-shore (m)')
# plt.grid()
#plt.show()
plt.savefig('/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/AVTB_beach_lidarpts', dpi = 300)


# RED BEACH ________________
section = df.loc[(df.rotated_y > 5000 ) & (df.rotated_y < 5500 ) ]

section = df.loc[(df.rotated_y > 5000 ) 
            & (df.rotated_y < 5500 ) 
            # & (df.elevation_m < 5 ) 
            # & (df.elevation_m > -5 )#]
            & (df.rotated_x > -300)
            & (df.rotated_x < 90)]

section.plot.scatter(x = 'rotated_x', y='rotated_y', c = 'elevation_m',cmap = colormap, vmin=-4,vmax = 4)

# plt.scatter(section['rotated_x'], section['rotated_y'], c = section['depth'])
# plt.xlim(-200,100)
plt.title('Camp Pendleton Red 2014 USACE LiDAR Survey')
plt.xlabel('Rotated coords Cross-shore (m)')
plt.ylabel('Rotated coords Along-shore (m)')
# plt.grid()
#plt.show()
plt.savefig('/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/Red_beach_lidarpts', dpi = 300)

# ALLL THE BEACH ________________
section = df.loc[(df.rotated_y > 4000 ) & (df.rotated_y < 8000 ) ]

section = df.loc[(df.rotated_y > 4000 ) 
            & (df.rotated_y < 8000 ) 
            & (df.rotated_x > -600)
            & (df.rotated_x < 150)]

section.plot.scatter(x = 'rotated_x', y='rotated_y', c = 'elevation_m',cmap = colormap, vmin=-4,vmax = 4)

# plt.scatter(section['rotated_x'], section['rotated_y'], c = section['depth'])
# plt.xlim(-200,100)
plt.title('Camp Pendleton 2014 USACE LiDAR Survey')
plt.xlabel('Rotated coords Cross-shore (m)')
plt.ylabel('Rotated coords Along-shore (m)')
# plt.grid()
#plt.show()
plt.savefig('/Users/rdchlcap/repos/beachslopes/figures/pendletonfig/newALL_beach_lidarpts', dpi = 300)



