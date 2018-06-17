import ftplib
import os
import gzip
import shutil

host = 'ftp.bom.gov.au'
source_dir = '/register/bom630/adfd'
filename = 'IDZ71117_AUS_FFDI_SFC.nc.gz'  # Max Fire Danger Index NetCDF
username = 'yourusername'
password = 'yourpassword'
dest_dir = r"D:\Work\BOM\download_from_ftp"

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


def main():
    # download file from FTP
    downloadFile()
    # unzip file and delete zip
    unZip()
    # update mosaic dataset

    print('Finished')

if __name__ == '__main__':
    main()
