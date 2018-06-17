import ftplib
import os
import gzip
import shutil
import arcpy

host = 'ftp.bom.gov.au'
source_dir = '/register/bom630/adfd'
filename = 'IDZ71117_AUS_FFDI_SFC.nc.gz'  # Max Fire Danger Index NetCDF
username = 'yourusername'
password = 'yourpassword'
dest_dir = r"D:\Work\BOM\download_from_ftp"
arcpy.env.workspace = "D:\Work\BOM\workings"

def downloadFile():
    # connect to FTP
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
    mdname = "BOM_FTP.gdb/MaxFireIndex"
    query = "#"
    updatenew = "UPDATE_WITH_NEW_ITEMS"
    syncstale = "SYNC_STALE"
    updatecs = "#"
    updatebnd = "#"
    updateovr = "#"
    buildpy = "NO_PYRAMIDS"
    calcstats = "CALCULATE_STATISTICS"
    buildthumb = "NO_THUMBNAILS"
    buildcache = "NO_ITEM_CACHE"
    updateras = "NO_RASTER"
    updatefield = "NO_FIELDS"
    fields = "#"

    arcpy.SynchronizeMosaicDataset_management(
        mdname, query, updatenew, syncstale, updatecs, updatebnd,
        updateovr, buildpy, calcstats, buildthumb, buildcache,
        updateras, updatefield, fields)


    print('Finished syncing Mosaic Dataset')



def main():
    # download file from FTP
    downloadFile()
    # unzip file and delete zip
    unZip()
    # sync mosaic dataset
    syncMD()

    print('Finished')

if __name__ == '__main__':
    main()
