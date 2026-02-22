import pandas as pd  # also requires: pip install openpyxl for Excel
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import matplotlib.dates as mdates
import matplotlib as mpl
import moviepy.video.io.ImageSequenceClip  # to produce mp4 video
from PIL import Image  # for some basic image processing
import datetime as dt

mpl.rcParams['axes.linewidth'] = 0.3
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 'x-small'

# pip install cartopy pgeocode geopandas shapely
import pgeocode
nomi = pgeocode.Nominatim("us")  # US ZIPs

import cartopy.crs as ccrs
import cartopy.feature as cfeature
proj = ccrs.LambertConformal()


#-- util function

def update_hash(hash, key, count):
    if key in hash:
        hash[key] += count
    else:
        hash[key] = count
    return()


def update_nestedHash(hash, key, nested_key, count): 
    if key in hash:
        nested_hash = hash[key]
        update_hash(nested_hash, nested_key, count)
    else:
        nested_hash = { nested_key: count }
    hash[key] = nested_hash
    return(hash)


def read_zip_table(file):
    # zipcode data from census 
    hzip_census = {}
    with open(file, 'r', encoding='utf-8') as f:
        for line in f:
            fields = line.strip().split('\t')
            zipc = fields[1]
            zipc = zipc.split(" ")
            zipc = zipc[1]    # zipcode
            size = fields[2]  # population
            hzip_census[zipc] = size
    return(hzip_census)


def generate_map(zipcodes, colors, dot_sizes, proj, nomi, frame, show):

    df = pd.DataFrame({"zipcode": zipcodes, "color": colors, "size": dot_sizes})
    loc = nomi.query_postal_code(df["zipcode"].tolist())
    df["lat"] = loc["latitude"].values
    df["lon"] = loc["longitude"].values  
    df = df.dropna(subset=["lat", "lon"]) # Drop ZIPs without coordinates

    fig = plt.figure(figsize=(6.5, 4.5))
    ax = plt.axes(projection=proj)

    # Add basic US features
    ax.add_feature(cfeature.COASTLINE, linewidth=0.2)
    ax.add_feature(cfeature.BORDERS, linewidth=0.5)
    ax.add_feature(cfeature.STATES, linewidth=0.2)

    # Limit extent roughly to continental US (lon_min, lon_max, lat_min, lat_max)
    ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())

    # Scatter ZIPs as colored dots
    for index, row in df.iterrows():
        ax.scatter(row["lon"], row["lat"],color=row["color"],s= row["size"],  
                   transform=ccrs.PlateCarree(),  # because lat/lon are in PlateCarree
                   edgecolor="none",linewidth=0.5,alpha=0.6, zorder=5)
    plt.text(0.01, 0.99, str(frame), fontsize=6,
         horizontalalignment='left',
         verticalalignment='top',
         transform=plt.gca().transAxes)
    plt.tight_layout()
    file = "map_" + str(frame) + ".png"
    plt.savefig(file, dpi=300, bbox_inches='tight') # transparent=False
    if show:
        plt.show() 
    else: 
        plt.close() 
    return(file)


#-- Main functions

def get_zip_details(df): 

    import pandas as pd
    df['Time'] = pd.to_datetime(df['Date & Time'])
    hzip_details = {}
    htimes = {}
    hzips = {}
    for index, row in df.iterrows():
        zip = row['Zipcode']
        time = row['Time']  
        date = time.date()
        update_hash(htimes, date, 1)
        update_hash(hzips, zip, 1)
        key = (zip, date)
        update_hash(hzip_details, key, 1)  # add one click to that entry
    return(hzip_details, hzips, htimes)


def get_IP_details(df):

    hIPs_details = {}
    df['Time'] = pd.to_datetime(df['Date & Time'])
    for index, row in df.iterrows():
        zip = row['Zipcode']
        IP = row['IP']
        time = row['Time']  
        date = time.date()
        ISP = row['ISP']
        browser = str(row['Browser'])
        browser = browser.lower()
        mobileFlag = ''
        if 'mobile' in browser:
            mobileFlag = 'mobile'
        if IP in hIPs_details:
            arr = hIPs_details[IP]
            first_date = arr[2]
            last_date = arr[3]
            ndays = arr[4]
            clicks = arr[5]
            if last_date != date:
                last_date = date
                ndays += 1
            hIPs_details[IP] = [zip, ISP, first_date, last_date, ndays, clicks+1, mobileFlag]
        else:
            first_date = date
            last_date = date
            hIPs_details[IP] = [zip, ISP, first_date, last_date, 1, 1, mobileFlag]
    return(hIPs_details)


def get_dev_details(df_dev, hIPs_details): 

    dev_to_IP = {} 
    hdev = {}

    for index, row in df_dev.iterrows():

        IP = row['IP']
        clicks = row['Clicks']
        queries = str(row['Queries'])
        queries = queries.replace("\n","|")
        queries = queries.strip()
        devices = row['Device Id']
        devices = devices.split("\n")
        del devices[0]
        ndev = len(devices) 
        arr = hIPs_details[IP]
        arr.append(queries)
        arr.append(ndev)
        hIPs_details[IP] = arr

        for dev in devices:
            # IP_ clicks is estimate of share of clicks attached to dev
            # if ndev = 1 (typical), IP has only 1 dev attached to it
            IP_clicks = float(clicks / ndev)  
            update_hash(hdev, dev, IP_clicks)
            update_nestedHash(dev_to_IP, dev, IP, IP_clicks)
    return(hdev, dev_to_IP, hIPs_details)


def ISP_summary(hIPs_details):

    hISPs = {}
    ISP_to_IP = {}

    for IP in hIPs_details:
        arr = hIPs_details[IP]
        ISP = arr[1]
        clicks = arr[5]
        update_hash(hISPs, ISP, clicks)
        update_nestedHash(ISP_to_IP, ISP, IP, clicks)

    for ISP in hISPs:
        nIPs = len(ISP_to_IP[ISP])
        clicks = hISPs[ISP]
        if nIPs > 50 or 'nevada' in ISP.lower():
            print("Top ISP or Nevada:", ISP, clicks, nIPs, "\n") 

    return(hISPs, ISP_to_IP)


def dev_summary(dev_to_IP, hIPs_details, ISP_to_IP, threshold):

    hdev_details = {}

    for dev in dev_to_IP:

        # hash is the list of IPs attached to dev
        hash = dev_to_IP[dev]
        nIPs = len(hash)
        hdev_dates = {}
        local_hash = {}

        for IP in hash:
            dev_clicks = hash[IP]
            arr = hIPs_details[IP]
            zip = arr[0]
            ISP = arr[1]
            first_date = arr[2]
            last_date = arr[3]
            ndays = arr[4]
            clicks = arr[5]
            mobileFlag = arr[6]
            queries = arr[7]
            ndev = arr[8]  # number of devices attached to IP
            if ndev == 1: 
                # IP has only 1 dev attached to it
                update_hash(hdev_dates, first_date, 1)
                update_hash(hdev_dates, last_date, 1)
            nIPs_in_ISP = len(ISP_to_IP[ISP])
            IP = "'" + IP + "'"
            zip = "'" + zip + "'"
            if queries == 'nan':
                queries = ''
            else:
                queries = "'" + queries + "'"
            local_hash[IP] = [dev, mobileFlag, nIPs, year, dev_clicks, zip, ISP, nIPs_in_ISP, IP, ndays, clicks, ndev, queries]

        for IP in local_hash:
            arr = local_hash[IP]
            # dev_ndays is minimum number of distinct active days across all IPs in dev
            # same for each IP within a same dev
            dev_ndays = len(hdev_dates)  
            arr.append(dev_ndays) 
            local_hash[IP] = arr
        hdev_details[dev] = local_hash

    OUT_dev = open("cf_dev.txt", "wt")
    for dev in hdev_details:
        hash = hdev_details[dev]
        nIPs = len(hash)
        if nIPs > threshold:
            for IP in hash:
                print("Dev with several IPs", hash[IP]) 
                arr = hash[IP]
                for k in range(len(arr)):
                    print(arr[k], end='\t', file=OUT_dev)
                print('', file=OUT_dev)
            print('', file=OUT_dev)
            print("\n")
    OUT_dev.close()

    return(hdev_details) 


def video(year, htimes, hzips, hzip_census, hzips_details): 

    frame = 0
    flist = []     # list of image filenames for the video

    for time in htimes:

        zipcodes = [] 
        colors = [] 
        dot_sizes = []

        for zip in hzip_census:
            size = float(hzip_census[zip])
            if size > 60000:
                zipcodes.append(zip)
                dot_sizes.append(max(4,size/2500))
                colors.append('lightgray')

        for zip in hzips:
            key = (zip, time)
            if key in hzip_details:
                clicks = hzip_details[key]
                zipcodes.append(zip)
                intensity = clicks/htimes[time]
                dot_sizes.append(3000*intensity) 
                if zip in hzip_census:
                    size = float(hzip_census[zip])
                    if intensity > 0.01:
                        colors.append('red')
                    else:
                        colors.append('green')
                else:
                    size = 1
                    colors.append('darkorange')

        print("Frame:", frame, time, len(zipcodes))
        image = generate_map(zipcodes, colors, dot_sizes, proj, nomi, time, False)

        im = Image.open(image)
        if frame==0:  
            width, height = im.size  # determines the size of all future images
            width=2*int(width/2)
            height=2*int(height/2)
            fixedSize=(width,height) # even number of pixels for video production 
        im = im.resize(fixedSize)  # all images must have same size to produce video
        im.save(image,"PNG") # save resized image for video production

        flist.append(image)
        frame += 1
    clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(flist, fps=5)  
    clip.write_videofile('clickfraud'+str(year)+'.mp4')
    return()


#--
def click_spikes(df, threshold):  

    hash_spike = {}
    df['Time'] = pd.to_datetime(df['Date & Time'])    
    by_hour = df.groupby(pd.Grouper(key='Time', freq='h')).size() # time series data
    by_hour = by_hour.reset_index()  # dataframe format
    arr_by_hour = by_hour.to_numpy() # numpy format

    hours = arr_by_hour[:,0]
    clicks = arr_by_hour[:,1]
    colors = []
    print("\nHourly spikes\n")
    for k in range(len(clicks)):
        if clicks[k] > threshold:
            print(hours[k], clicks[k])
            time = hours[k]
            hash_spike[time] = 1

    for index, row in df.iterrows():
        zip = row['Zipcode']
        IP = row['IP']
        IP = "'" + IP + "'"
        ISP = row['ISP']
        time = row['Time']  
        hour = time.replace(minute=0, second=0, microsecond=0)
        if hour in hash_spike:
            print("Click spike", time, zip, ISP, IP) 
        date = time.date()

    return()


#--- Main ---

def collect_data(year):

    if year == 2019:
        file1 = 'MOTORP~1.xls'
        file2 = 'MOTORP~2.xls'
    elif year == 2022:
        file1 = 'MOTORP~3.xls'
        file2 = 'MOTORP~4.xls'

    df1 = pd.read_excel(file1,sheet_name='Web logs') 
    df2 = pd.read_excel(file2,sheet_name='Web logs')
    df12 = pd.concat([df1,df2], axis=0) 
    df1_dev = pd.read_excel(file1,sheet_name='IPs by number of clicks')
    df2_dev = pd.read_excel(file2,sheet_name='IPs by number of clicks')
    df12_dev = pd.concat([df1_dev,df2_dev], axis=0) 

    return(df12, df12_dev)


#---

year = 2022  # options: 2019 or 2022  
spike_thresh = { 2019:60, 2022:180 }     # hourly clicks
dev_nIPs_thresh = { 2019:5, 2022:2 }

(df, df_dev) = collect_data(year)
click_spikes(df, spike_thresh[year])  

hIPs_details = get_IP_details(df)
hdev, dev_to_IP, hIPs_details = get_dev_details(df_dev, hIPs_details)  
hISPs, ISP_to_IP = ISP_summary(hIPs_details)
dev_summary(dev_to_IP, hIPs_details, ISP_to_IP, dev_nIPs_thresh[year]) 

hzip_details, hzips, htimes = get_zip_details(df) 
hzip_census = read_zip_table('zipcodes-census.txt')
video(year, htimes, hzips, hzip_census, hzip_details)
