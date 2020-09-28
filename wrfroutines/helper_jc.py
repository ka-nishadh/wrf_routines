import sys
sys.path.append('..')
import datetime

from shapely.geometry import Polygon
import numpy as np
import pandas as pd

import metpy.calc as metpcalc
from metpy.units import units



import glob

def map_extent(plot_extent):
    """
    To get the extent geom

    Parameters
    ----------
    plot_extent : dict
        contains min and max of lat and long extent
    
    Returns
    -------
    shapely.geometry.polygon.Polygon
    geometry details

    """ 
    geo_fe= Polygon([[plot_extent['w'],plot_extent['s']], [plot_extent['w'],plot_extent['n']], [plot_extent['e'],plot_extent['n']],[plot_extent['e'],plot_extent['s']]])
    return geo_fe



def get_date_array(ds):
    fcdate=str(ds.attrs['SDATE'])
    wtm=datetime.datetime.strptime(fcdate, "%Y%j").date()
    year=int(wtm.strftime('%Y'))
    month=int(wtm.strftime('%m'))
    day=int(wtm.strftime('%d'))
    base=datetime.datetime(year,month,day,6)
    arr = np.array([base + datetime.timedelta(hours=i) for i in range(96)])
    return arr


def creategrid(db):
    x_min=db.attrs['XORIG']
    y_min=db.attrs['YORIG']
    nx=db.attrs['NCOLS']
    ny=db.attrs['NROWS']
    cell=db.attrs['XCELL']
    x_max=x_min+(cell*nx)
    y_max=y_min+(cell*ny)
    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    xv, yv = np.meshgrid(x, y)
    #yv1=np.flipud(yv) 
    return x_min,y_min,x_max,y_max


def get_lat_long(db):
    x_min=db.attrs['XORIG']
    y_min=db.attrs['YORIG']
    nx=db.attrs['NCOLS']
    ny=db.attrs['NROWS']
    cell=db.attrs['XCELL']
    x_max=x_min+(cell*nx)
    y_max=y_min+(cell*ny)
    x = np.linspace(x_min, x_max, nx)
    y = np.linspace(y_min, y_max, ny)
    xv, yv = np.meshgrid(x, y)
    #yv1=np.flipud(yv) 
    return xv, yv


def get_temp_array(ds):
    """
    Converts .nc sst file of sentinel into DataArray


    Parameters
    ----------
    ncfile : file path
        .nc file path
    
    Returns
    -------
    DataArray, string
    DataArray of sea_surface_temperature
    Date in string format

    """
    var_ds=ds['T2_K'].values
    var_ds1=var_ds[:,0,:,:]
    nctime=get_date_array(ds)
    return var_ds1,nctime



def get_precep_array(ds):
    """
    Converts .nc sst file of sentinel into DataArray


    Parameters
    ----------
    ncfile : file path
        .nc file path
    
    Returns
    -------
    DataArray, string
    DataArray of sea_surface_temperature
    Date in string format

    """
    var_ds=ds['PRATE_MMpH'].values
    var_ds1=var_ds[:,0,:,:]
    nctime=get_date_array(ds)
    return var_ds1,nctime


def for_windspeed(ds,timestep):
    u_da = ds.U10_MpS
    u_da2=u_da.isel(TSTEP=[timestep])
    u_pdata=u_da2.values
    u_pdata1=u_pdata[0,0,:,:]
    v_da = ds.V10_MpS
    v_da2=v_da.isel(TSTEP=[timestep])
    v_pdata=v_da2.values
    v_pdata1=v_pdata[0,0,:,:]    
    u_pdata2=u_pdata1* units.meter / units.second
    v_pdata2=v_pdata1* units.meter / units.second
    windspeed=metpcalc.wind_speed(u_pdata2,v_pdata2)
    nctime=get_date_array(ds)
    return windspeed.magnitude,nctime


def for_windmap(ds,timestep):
    u_da = ds.U10_MpS
    u_da2=u_da.isel(TSTEP=[timestep])
    u_pdata=u_da2.values
    u_pdata1=u_pdata[0,0,:,:]
    v_da = ds.V10_MpS
    v_da2=v_da.isel(TSTEP=[timestep])
    v_pdata=v_da2.values
    v_pdata1=v_pdata[0,0,:,:]    
    nctime=get_date_array(ds)
    ncx,ncy=get_lat_long(ds)
    return ncx,ncy,u_pdata1,v_pdata1,nctime


def for_winddirection(ds,timestep):
    u_da = ds.U10_MpS
    u_da2=u_da.isel(TSTEP=[timestep])
    u_pdata=u_da2.values
    u_pdata1=u_pdata[0,0,:,:]
    v_da = ds.V10_MpS
    v_da2=v_da.isel(TSTEP=[timestep])
    v_pdata=v_da2.values
    v_pdata1=v_pdata[0,0,:,:]    
    u_pdata2=u_pdata1* units.meter / units.second
    v_pdata2=v_pdata1* units.meter / units.second
    winddirection=metpcalc.wind_direction(u_pdata2,v_pdata2, convention='to')
    nctime=get_date_array(ds)
    return winddirection.magnitude,nctime



def get_cloudod_array(ds):
    """
    Converts .nc sst file of sentinel into DataArray


    Parameters
    ----------
    ncfile : file path
        .nc file path
    
    Returns
    -------
    DataArray, string
    DataArray of sea_surface_temperature
    Date in string format

    """
    var_ds=ds['CLOUD_OD'].values
    var_ds1=var_ds[:,0,:,:]
    nctime=get_date_array(ds)
    return var_ds1,nctime


def get_lightning_cape_array(ds):
    var_ds=ds['CAPE'].values
    var_ds1=var_ds[:,0,:,:]
    nctime=get_date_array(ds)
    return var_ds1,nctime






