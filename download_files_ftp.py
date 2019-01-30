import ftplib
import os
import gzip
import shutil
import arcpy

# Globals
host = 'ftp.bom.gov.au'
source_dir = '/register/bom630/adfd'
# others to test with - IDZ71094_AUS_WxThunderstorms_SFC.nc.gz    IDZ71144_AUS_GrassFuelLoad_SFC.nc.gz  IDZ71117_AUS_FFDI_SFC.nc.gz
filename = 'IDZ71000_AUS_T_SFC.nc.gz'  # Surface tempoerature
username = 'yourusername'
password = 'yourpassword'
dest_dir = r"D:\Work\BOM\download_from_ftp"
arcpy.env.workspace = r"D:\Work\BOM\workings"


def main():
    # download file from FTP
    downloadFile()
    # unzip file and delete zip
    unZip()
    # sync mosaic dataset
    syncMD()

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
    # Should we not delete the existing NetCDF with same filename before unzipping?
    # Extract zip
    with gzip.open(os.path.join(dest_dir, filename), 'rb') as infile, open(os.path.join(dest_dir, filename[:-3]), 'wb') as outfile:
        shutil.copyfileobj(infile, outfile)
        print('Unzipped ',  filename[:-3]) # ToDo: switch to use RegEx

    # Delete Original gzip
    os.remove(os.path.join(dest_dir, filename))
    print(filename, ' deleted')

def syncMD():
    # script assumes that MD already exists from setup guide
    # ToDo - automate creating the MD if it does not already exist?

    # Synchronize source and add new data
#    mdname = "BOM_FTP.gdb/MaxTemp" #ToDo - Make this a global variable
#    query = "#"
#    updatenew = "UPDATE_WITH_NEW_ITEMS"
#    syncstale = "SYNC_STALE"
#    updatecs = "#"
#    updatebnd = "#"
#    updateovr = "#"
#    buildpy = "NO_PYRAMIDS"
#    calcstats = "CALCULATE_STATISTICS"
#    buildthumb = "NO_THUMBNAILS"
#    buildcache = "NO_ITEM_CACHE"
#    updateras = "NO_RASTER"
#    updatefield = "NO_FIELDS"
#    fields = "#"

    print("syncing mosaic dataset with : " + filename)

    arcpy.SynchronizeMosaicDataset_management(in_mosaic_dataset=r"D:\Work\BOM\workings\BOM_FTP.gdb\T_SFC_ArcMap", where_clause="", new_items="UPDATE_WITH_NEW_ITEMS", sync_only_stale="SYNC_STALE", update_cellsize_ranges="UPDATE_CELL_SIZES", update_boundary="UPDATE_BOUNDARY", update_overviews="UPDATE_OVERVIEWS", build_pyramids="NO_PYRAMIDS", calculate_statistics="CALCULATE_STATISTICS", build_thumbnails="NO_THUMBNAILS", build_item_cache="NO_ITEM_CACHE", rebuild_raster="REBUILD_RASTER", update_fields="UPDATE_FIELDS", fields_to_update="CenterX;CenterY;Dimensions;GroupName;ProductName;Raster;Shape;StdTime;Tag;Variable;ZOrder", existing_items="UPDATE_EXISTING_ITEMS", broken_items="REMOVE_BROKEN_ITEMS", skip_existing_items="SKIP_EXISTING_ITEMS", refresh_aggregate_info="NO_REFRESH_INFO", estimate_statistics="NO_STATISTICS")

    print('Finished syncing Mosaic Dataset')

if __name__ == '__main__':
    main()
