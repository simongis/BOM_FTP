import ftplib
import os, sys
import gzip
import shutil
import arcpy
from arcgis.gis import GIS
import arcgis.gis.admin

# =============================================================================
# Outstanding tasks:
#     Publish an Image Web Layer that references the Mosaic Dataset & Processing Templates
#     Setup pretty processing templates
#     Incorporate downloading IDZ71071_AUS_WindMagKmh_SFC.nc + IDZ71089_AUS_Wind_Dir_SFC.nc
#     Add/remove/sync above two similar to how T_SFC is done below
#     Ensure all files are being deleted + look into clearing MD Log file Guenter mentioned
#     Deploy & test on Esri Australia Demo site
# =============================================================================

# Globals
host = 'ftp.bom.gov.au'
source_dir = '/register/bom630/adfd'
# others to test with - IDZ71094_AUS_WxThunderstorms_SFC.nc.gz    IDZ71144_AUS_GrassFuelLoad_SFC.nc.gz  IDZ71117_AUS_FFDI_SFC.nc.gz
filename = 'IDZ71000_AUS_T_SFC.nc.gz'  
username = ''
password = ''
dest_dir = r"E:\ArcGIS_Projects\BOM\download_from_ftp"  #ToDo: Make relative
arcpy.env.workspace = os.path.join(os.path.dirname(sys.argv[0]), "BOM_FTP.gdb")
gis = GIS("https://simongis.yourdomain.com.au/portal", "", "")

def main():
    # Stop service
    stop()
    # download file from FTP
    downloadFile()
    # unzip file and delete zip
    unZip()
    # sync mosaic dataset
    syncMD()
    #start service
    start()
    print('Finished')

def downloadFile():
    # connect to FTP
    print("downloading zip: " + filename)
    try:
        ftp = ftplib.FTP(host)
        ftp.login(username,  password)
        ftp.cwd(source_dir)
    except ftplib.all_errors as e:
        print('Ftp error = ', e)
        return False

    # ftp.retrlines('LIST') # lists content in FTP dir
    # Check filename exists
    if filename in ftp.nlst():
            local_filename = os.path.join(dest_dir, filename)
            lf = open(local_filename, "wb")
            ftp.retrbinary("RETR " + filename, lf.write)
            lf.close()
            print(filename, ' successfully downloaded')
    else:
            print(filename, ' not found in the path ',  source_dir)
    ftp.quit()

def unZip():
    print("unzipping: " + filename)
    # Extract zip
    with gzip.open(os.path.join(dest_dir, filename), 'rb') as infile, open(os.path.join(dest_dir, filename[:-3]), 'wb') as outfile:
        shutil.copyfileobj(infile, outfile)
        print('Unzipped ',  filename[:-3]) # ToDo: switch to use RegEx

    # Delete Original gzip
    os.remove(os.path.join(dest_dir, filename))
    print(filename, ' deleted')

def syncMD():
    # ToDo: STOP image service that references this MD
    #stop()    
    print("Removing Rasters & Footprints")  # Was hoping to avoid removing/adding rasters, but Hong thinks there is a bug with SyncMD in Pro
    arcpy.management.RemoveRastersFromMosaicDataset("T_SFC", "OBJECTID >= 0", "UPDATE_BOUNDARY", "MARK_OVERVIEW_ITEMS", "DELETE_OVERVIEW_IMAGES", "DELETE_ITEM_CACHE", "REMOVE_MOSAICDATASET_ITEMS", "UPDATE_CELL_SIZES")
    print("Removed Rasters & Footprints")
    print("Adding Rasters: " + filename[:-3])
    arcpy.management.AddRastersToMosaicDataset("T_SFC", "NetCDF", dest_dir, "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", None, 0, 1500, None, "*.nc;*.nc4", "NO_SUBFOLDERS", "OVERWRITE_DUPLICATES", "NO_PYRAMIDS", "CALCULATE_STATISTICS", "NO_THUMBNAILS", None, "NO_FORCE_SPATIAL_REFERENCE", "NO_STATISTICS", None, "NO_PIXEL_CACHE", "")
    print("Finished adding " + filename[:-3])
    print("syncing mosaic dataset")
    arcpy.management.SynchronizeMosaicDataset("T_SFC", None, "UPDATE_WITH_NEW_ITEMS", "SYNC_STALE", "UPDATE_CELL_SIZES", "UPDATE_BOUNDARY", "NO_OVERVIEWS", "NO_PYRAMIDS", "NO_STATISTICS", "NO_THUMBNAILS", "NO_ITEM_CACHE", "REBUILD_RASTER", "UPDATE_FIELDS", "CenterX;CenterY;Dimensions;GroupName;ProductName;Raster;Shape;StdTime;Tag;Variable;ZOrder", "IGNORE_EXISTING_ITEMS", "IGNORE_BROKEN_ITEMS", "SKIP_EXISTING_ITEMS", "REFRESH_INFO", "NO_STATISTICS")
    print('Finished syncing Mosaic Dataset') 
    # ToDo: START image service that references this MD
    #start()

def stop():
    # Get the ArcGIS Server federated to the Portal (might need to check this when other sites are federated)
    gis_server = gis.admin.servers.list()[0]
    for service in gis_server.services.list(folder='BOM'):
        print("Stopping ", service.properties.serviceName)
        service.stop() 
        print("Stopped ", service.properties.serviceName)
        
def start():
    # Get the ArcGIS Server federated to the Portal (might need to check this when other sites are federated)
    gis_server = gis.admin.servers.list()[0]
    for service in gis_server.services.list(folder='BOM'):
        print("Starting ", service.properties.serviceName)
        service.start()
        print("Started ", service.properties.serviceName)

if __name__ == '__main__':
    main()
