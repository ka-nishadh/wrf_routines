import datetime
import numpy as np
import xarray as xr
import json
import os

from helper_jc import get_precep_array
from helper_jc import for_windspeed
from helper_jc import for_winddirection
from helper_jc import get_lightning_cape_array



def get_date_array(ds):
    fcdate=str(ds.attrs['SDATE'])
    wtm=datetime.datetime.strptime(fcdate, "%Y%j").date()
    year=int(wtm.strftime('%Y'))
    month=int(wtm.strftime('%m'))
    day=int(wtm.strftime('%d'))
    base=datetime.datetime(year,month,day,6)
    arr = np.array([base + datetime.timedelta(hours=i) for i in range(96)])
    return arr


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
    var_ds2=var_ds1-273.15
    nctime=get_date_array(ds)
    return var_ds2,nctime



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
    return x_min,y_min,nx,ny

def round_floats(o):
    if isinstance(o, float): return round(o, 2)
    if isinstance(o, dict): return {k: round_floats(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)): return [round_floats(x) for x in o]
    return o


def metadata_creator(var,db,binfullname):
    metadata={}
    metadata['region_name']='isc'
    metadata['ll_lat']=float(db.attrs['YORIG'])
    metadata['ll_lon']=float(db.attrs['XORIG'])
    metadata['ny']=float(db.attrs['NROWS'])
    metadata['nx']=float(db.attrs['NCOLS'])
    metadata['resolution_gridx']=float(db.attrs['XCELL'])
    metadata['resolution_gridy']=float(db.attrs['YCELL'])
    metadata['conversion_factor']=1
    xbash = np.fromfile(binfullname, dtype='float32')
    xbash1=xbash.reshape(int(db.attrs['NROWS']),int(db.attrs['NCOLS']))
    metadata['min']=float(xbash1.min())
    metadata['max']=float(xbash1.max())
    return metadata
    

       
def json_dump(metadata,outputfolder,jsonfilename):
    data1={}
    data1['region_name']=metadata['region_name']
    data1['ll_lat']=metadata['ll_lat']
    data1['ll_lon']=metadata['ll_lon']
    data1['ny']=metadata['ny']
    data1['nx']=metadata['nx']
    data1['resolution_gridx']=metadata['resolution_gridx']
    data1['resolution_gridy']=metadata['resolution_gridy']
    data1['min']=round_floats(metadata['min'])
    data1['max']=round_floats(metadata['max'])
    data1['unit']=metadata['unit']
    data1['name']=metadata['name']
    data1['label']=metadata['label']
    data1['date']=metadata['date']
    data1['hour']=metadata['hour']
    data1['color']=metadata['color']
    data1['data_array']=round_floats(metadata['data_array'])
    with open(outputfolder+'{}.json'.format(jsonfilename), 'w') as f:
            json.dump(data1,f)


def bin_create(params,var_array,var_nctime,timestep,db):
    bindata=var_array[timestep,:,:]
    bindata_xr=bindata
    nctime_format=var_nctime[timestep].strftime('%Y%m%d%H')
    date=var_nctime[timestep].strftime('%Y%m%d')
    hour=var_nctime[timestep].strftime('%H')
    binfolder='{}{}/{}/'.format(params.outputfolder.format(params.date),params.varname,params.run)
    foldercreator(binfolder)
    binfilename='{}.bin'.format(str(nctime_format))
    bindata_xr.astype('float32').tofile(binfolder+binfilename)
    binfullname=binfolder+binfilename
    metadata=metadata_creator(bindata_xr,db,binfullname)
    metadata['unit']=params.unit
    metadata['name']=params.varname
    metadata['data_array']=bindata_xr.tolist()
    metadata['date']=date
    metadata['hour']=hour
    metadata['color']={'red':153, 'green':0,'blue':0}
    metadata['label']=params.label
    print(metadata)
    jsonfilename=binfilename.split('.')[0]+'_'+metadata['region_name']
    json_dump(metadata,binfolder,jsonfilename)
    os.remove(binfullname)

def bin_create_light(params,var_array,var_nctime,timestep,db):
    bindata=var_array[timestep,:,:]
    bindata_xr=bindata
    nctime_format=var_nctime[timestep].strftime('%Y%m%d%H')
    date=var_nctime[timestep].strftime('%Y%m%d')
    hour=var_nctime[timestep].strftime('%H')
    binfolder='{}{}/{}/'.format(params.outputfolder.format(params.date),params.varname,params.run)
    foldercreator(binfolder)
    binfilename='{}.bin'.format(str(nctime_format))
    bindata_xr.astype('float32').tofile(binfolder+binfilename)
    binfullname=binfolder+binfilename
    metadata=metadata_creator(bindata_xr,db,binfullname)
    metadata['unit']=params.unit
    metadata['name']=params.varname
    metadata['date']=date
    metadata['hour']=hour
    metadata['color']={'red':153,'green':0,'blue':0}
    metadata['label']=params.label
    metadata['data_array']=bindata_xr.tolist()
    print(metadata)
    jsonfilename=binfilename.split('.')[0]+'_'+metadata['region_name']
    json_dump(metadata,binfolder,jsonfilename)
    os.remove(binfullname)    
          
def bin_create_wind(params,var_array,var_nctime,timestep,db):
    bindata_xr=var_array
    bindata_xr_float=bindata_xr.astype('float32')
    nctime_format=var_nctime[timestep].strftime('%Y%m%d%H')
    date=var_nctime[timestep].strftime('%Y%m%d')
    hour=var_nctime[timestep].strftime('%H')
    binfolder='{}{}/{}/'.format(params.outputfolder.format(params.date),params.varname,params.run)
    foldercreator(binfolder)
    binfilename='{}.bin'.format(str(nctime_format))
    bindata_xr_float.tofile(binfolder+binfilename)
    binfullname=binfolder+binfilename
    metadata=metadata_creator(bindata_xr_float,db,binfullname)
    metadata['unit']=params.unit
    metadata['name']=params.varname
    metadata['data_array']=bindata_xr_float.tolist()
    metadata['date']=date
    metadata['hour']=hour
    metadata['color']={'red':153,'green':0,'blue':0}
    metadata['label']=params.label
    print(metadata)
    jsonfilename=binfilename.split('.')[0]+'_'+metadata['region_name']
    json_dump(metadata,binfolder,jsonfilename)
    os.remove(binfullname)
            
            
def foldercreator(path):
   """
    creates a folder

    Parameters
    ----------
    path : folder path
            
    Returns
    -------
    creates a folder
    """
   if not os.path.exists(path):
        os.makedirs(path)




class bin_create_params:
    date='20200904'   
    run='00'
    bucket='wrf-daily-output-dump'
    filedirectory='{}/wrfindia-{}-{}Z'.format(bucket,date,run)
    fulltimestep=np.arange(0,96)
    varname='temperature'
    label='Temperature'
    unit='°C'
    output_bucket='ofish-data'
    output_fd='{}/{}/{}/{}'.format(bucket,date,varname,run)
    outputfolder='/tmp/{}'




def make_var_jsons(params,db):
    for timestep in params.fulltimestep:
        params.varname='temperature'
        params.unit='Degree Celcius'
        temp,nctime=get_temp_array(db)   
        bin_create(params,temp,nctime,timestep,db)
        params.varname='precipitation'
        params.label='Precipitation'
        params.unit='mm/hr'
        precp,nctime=get_precep_array(db)
        bin_create(params,precp,nctime,timestep,db)
        params.varname='lightning'
        params.label='Lightning'
        params.unit='ppmV'
        light_ind,nctime=get_lightning_cape_array(db)
        bin_create_light(params,light_ind,nctime,timestep,db)
        params.varname='windspeed'
        params.label='Wind speed'
        params.unit='m/sec'
        windspeed,nctime=for_windspeed(db,timestep)
        bin_create_wind(params,windspeed,nctime,timestep,db)
        params.varname='winddirection'
        params.label='Wind direction'
        params.unit='angle in 360 degree'
        winddirection,nctime=for_winddirection(db,timestep)
        bin_create_wind(params,winddirection,nctime,timestep,db)
    
    
