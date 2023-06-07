from typing import List
import numpy as np
import laspy
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import linregress
from scipy.interpolate import make_interp_spline, interp1d
import matplotlib.patches as mpatches

import main_refactor

def slope(x1, y1, x2, y2):
    return (y2-y1)/(x2-x1)

df = main_refactor.import_lidar_las('/Users/rdchlcap/repos/beachslopes/data/pendleton/ca2014_usace_ncmp_ca_Job821632/ca2014_usace_ncmp_ca_Job821632.las')
df = main_refactor.transform_coordinates(df, new_origin_north=3678000, new_origin_east=460000 + 500, theta_deg=35)

plot_infograph = False
plot_slopes = False

# Northern beach by 7000-7500 where there aren't data gaps
df_red = main_refactor.build_transects(df,y_min = 7100, y_max = 7400, y_transect_width=1, y_transect_gap= 20)

#mirror x axis so cross-shore distance increases offshore
df_red['rotated_x'] = df_red['rotated_x']*-1

is_beach = (df_red.rotated_x > -35) & (df_red.rotated_x < 78)
is_beach2 = (df_red.elevation_m < 1.1) & (df_red.elevation_m > -1) # tidal range of +- 1m
is_surf = (df_red.rotated_x > -10) & (df_red.rotated_x < 800)
is_surf2 = (df_red.rotated_x > 0) & (df_red.rotated_x < 280) # out to bbar
is_bar = (df_red.rotated_x > 190) & (df_red.rotated_x < 350)
is_littoral = (df_red.rotated_x > 0) & (df_red.rotated_x < 1200)
#is_nearshore

beach = df_red.loc[is_beach,:]
beach2 = df_red.loc[is_beach2,:]
surf = df_red.loc[is_surf, :]
surf2 = df_red.loc[is_surf2, :]
bar = df_red.loc[is_bar,:]
littoral = df_red.loc[is_littoral]

beach_slope, beach_intercept, r, p, se = linregress(beach.rotated_x, beach.elevation_m)
beach_slope2, beach_intercept2, r, p, se = linregress(beach2.rotated_x, beach2.elevation_m)
surf_slope, surf_intercept, r, p, se = linregress(surf.rotated_x, surf.elevation_m)
surf_slope2, surf_intercept2, r, p, se = linregress(surf2.rotated_x, surf2.elevation_m)
bar_slope, bar_intercept, r, p, se = linregress(bar.rotated_x, bar.elevation_m)
litt_slope, litt_intercept, r, p, se = linregress(littoral.rotated_x,littoral.elevation_m)


plot_slopes = False
if plot_slopes:
    #set plot variables
    df=df_red.copy()
    title="Camp Pendleton no name Beach cross-shore Beach transects"
    # regression_slope=beach_slope
    # regression_intercept=beach_intercept,

    export_filename='/Users/rdchlcap/repos/pmaaa_wavelit_figs/littoral_slopes/pendleton_transect_smooth_linfits'

    #plot
    plt.suptitle(title) 
    plt.xlim(-90, 40)
    plt.ylim(-4, 4)
    plt.xlabel('Cross-shore Distance (m)')
    plt.ylabel('Elevation (m)')

    
    #plot just one transect
    transect_id = 2
    is_transect = df.transect_id == transect_id
    transect_df = df.loc[is_transect, :]
    # plt.plot(transect_df.rotated_x, transect_df.elevation_m, color = 'black')

    #smooth line plot with a rolling average
    rolling=transect_df[['rotated_x', 'elevation_m']].rolling(10).mean()
    #plt.plot(transect_df.rotated_x, transect_df.elevation_m, color = 'red') #actual data
    plt.plot(rolling.rotated_x, rolling.elevation_m, color = 'black') #smoothed line

    # all_rolling=df[['rotated_x', 'elevation_m']].sort_values('rotated_x').rolling(20).mean()
    # plt.plot(all_rolling.rotated_x, all_rolling.elevation_m, color = 'black')



    #linear slope interpolations       
    # plt.axline(xy1 = (0, beach_intercept), xy2 = None, slope = beach_slope, color = 'aqua' )
    # plt.axline(xy1 = (0, beach_intercept2), xy2 = None, slope = beach_slope2, color = 'green' )
    # plt.axline(xy1 = (0, surf_intercept), xy2 = None, slope = surf_slope, color = 'grey' )
    # plt.axline(xy1 = (0, surf_intercept2), xy2 = None, slope = surf_slope2, color = 'orange' )
    # plt.axline(xy1 = (0, bar_intercept), xy2 = None, slope = bar_slope, color = 'red' )
    # plt.axline(xy1 = (0, litt_intercept), xy2 = None, slope = litt_slope, color = 'blue' )
    plt.grid()
    plt.savefig(export_filename, dpi = 300)
    plt.close()

    print(f'beach1 {beach_slope} beach2 {beach_slope2}')
    print(f'surf1 {surf_slope} surf2 {surf_slope2}')
    print('bar slope',bar_slope)
    print('littoral slope',litt_slope)

if plot_infograph:
    #Plot info graphic of slopes
    title="Anatomy of a Sandy Beach"
    export_filename='/Users/rdchlcap/repos/pmaaa_wavelit_figs/littoral_slopes/Anatomy_of_sandy'#_expl'
    df=df_red.copy()
    #plot
    plt.suptitle(title) 
    plt.xlabel('Cross-shore Distance (m)')
    plt.ylabel('Elevation (m)')
    plt.xlim(-100, 1000)
    plt.ylim(-12, 7)
    #explore
    # plt.xlim(0, 600)
    # plt.ylim(-9, 0)
    # plt.minorticks_on()
    # plt.grid(which='major', linestyle='-', linewidth='0.5', color='grey')
    # plt.grid(which='minor', linestyle=':', linewidth='0.5', color='black')


    #plot just one transect *smoothed with a rolling average
    transect_id = 2
    is_transect = df.transect_id == transect_id
    transect_df = df.loc[is_transect, :]
    rolling=transect_df[['rotated_x', 'elevation_m']].rolling(10).mean()
    #plt.plot(transect_df.rotated_x, transect_df.elevation_m, color = 'red') #actual data
    plt.plot(rolling.rotated_x, rolling.elevation_m, color = 'black') #smoothed line

    #plot tidal info
    msl_x = [1000,-100]
    msl_y = [0,0]
    htide_x = [1000,-100]
    htide_y = [1,1]
    ltide_x = [1000,-100]
    ltide_y = [-1,-1]
    shore_x = [0,0]
    shore_y = [-12,8]
    plt.plot(shore_x,shore_y, color='grey', alpha = .85)
    plt.plot(msl_x,msl_y, color='grey', alpha = .85)
    plt.plot(htide_x,htide_y, color='grey', alpha = .5,linestyle=':')
    plt.plot(ltide_x,ltide_y, color='grey', alpha = .5,linestyle=':')
    plt.tight_layout()

    #text info
    plt.text(880,1,'high tide',fontsize='small',alpha = .9)
    plt.text(885,-1,'low tide',fontsize='small',alpha = .9)
    plt.text(800,.1,'mean sea level',fontsize='small',alpha = .9)
    plt.text(2,4,'shoreline',fontsize='small')
    plt.text

    #littoral slope
    plt.plot([0,1250],[0,-11.8],color= 'blue',alpha = .6)
    #surf slope
    plt.plot([0,340],[0,-4],color = 'green',alpha = .6)
    #beach slope
    plt.plot([71,-43],[-1,1],color= 'red',alpha = .6)
    #bar slope
    plt.plot([190,350],[-1.9,-6],color= 'orange',alpha = .6)

    #legend #handles, labels
    legend_lit = mpatches.Patch(color='blue', label=f'{np.abs(np.round(slope(0,0,1250,-11.8),3))} littoral slope')
    legend_surf = mpatches.Patch(color='green', label=f'{np.abs(np.round(slope(0,0,340,-4),3))} surf zone slope')
    legend_beach = mpatches.Patch(color='red', label=f'{np.abs(np.round(slope(71,-1,-43,1),3))} beach slope')
    legend_bar = mpatches.Patch(color='orange', label=f'{np.abs(np.round(slope(190,-1.9,350,-6),3))} sand bar slope')
    plt.legend(handles=[legend_lit,legend_surf,legend_beach,legend_bar],bbox_to_anchor=(.15, .2),fontsize='xx-small')

    plt.savefig(export_filename, dpi = 300)
    plt.close()
    print(f'beach1 {beach_slope} beach2 {beach_slope2}')
    print(f'surf1 {surf_slope} surf2 {surf_slope2}')
    print('bar slope',bar_slope)
    print('littoral slope',litt_slope)


print(' ')
