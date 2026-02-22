import dns.resolver
import dns.reversename
import pandas as pd  # also requires: pip install openpyxl for Excel
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.transforms as mtrans
import matplotlib.dates as mdates
import datetime as dt


#-- util function
def update_hash(hash, key, count):
    if key in hash:
        hash[key] += count
    else:
        hash[key] = count
    return()


#--
def map_IP_to_dev(df_dev, n_IPs_thresh):

    # Output: IP_clicks: hash with number of clicks per IP
    # Output: IP_flag1: IPs attached to device ID with multiple IPs 
    # Input:  n_IPs_thresh: number of IPs per device

    dev_hash = {}
    IP_clicks = {}
    clicks_hash = {}
    for index, row in df_dev.iterrows():
        IP = row['IP']
        dev = row['Device Id']
        clicks = row['Clicks']
        update_hash(IP_clicks, IP, clicks)
        update_hash(clicks_hash, dev, clicks)
        if dev in dev_hash:
            local_hash = dev_hash[dev]
            update_hash(local_hash, IP, clicks)
            dev_hash[dev] = local_hash
        else:
            dev_hash[dev] = { IP:clicks }

    IP_flag1 = {}
    for dev in dev_hash:
        n_IPs = len(dev_hash[dev]) 
        # n_clicks = clicks_hash[dev]
        if n_IPs > n_IPs_thresh: 
            for IP in dev_hash[dev]:
                update_hash(IP_flag1, IP, 1)  # flag the IP in question
    return(IP_flag1, IP_clicks)


#--
def map_zipcodes(df, IP_flag1, IP_clicks, ratio_thresh, zip_thresh, zip_list):

    # Input: IP_flag1: IPs attached to device with multiple IPs
    # Input: IP_clicks: clicks per IP
    # Input: ratio_thresh: proportion of clicks from a flagged IP, in a zipcode

    import pandas as pd
    df['Time'] = pd.to_datetime(df['Date & Time'])
    zipcodes = []
    colors = []
    dot_sizes = []
    zip_hash = {}   # number of clicks per zip (key = zipcode)  
    flagged_zips = {}
    for index, row in df.iterrows():
        zip = row['Zipcode']
        IP = row['IP']
        clicks = IP_clicks[IP]
        if IP in IP_flag1:
            update_hash(flagged_zips, zip, clicks)
        update_hash(zip_hash, zip, 1)  

    #--- gather data to produce zipcode map

    print("\nTop zipcodes, clicks:\n")
    for zip in zip_hash:
        if zip_hash[zip] > 5:
            click_count = zip_hash[zip]
            # if click_count > zip_thresh:
            if zip in zip_list:
                print(zip, click_count) 
            zipcodes.append(zip) # exclude non-US zipcodes?
            if zip in flagged_zips:
                ratio = flagged_zips[zip]/click_count
                if ratio > ratio_thresh:  
                    colors.append([1, 0, 0]) 
                else:
                    colors.append([1, 1, 0])
            else:
                colors.append([0, 1, 0])
            dot_sizes.append(click_count**0.75)

    #--- produce the map

    # pip install cartopy pgeocode geopandas shapely
    import pgeocode
    import pandas as pd
    nomi = pgeocode.Nominatim("us")  # US ZIPs
    df = pd.DataFrame({"zipcode": zipcodes, "color": colors, "size": dot_sizes})
    loc = nomi.query_postal_code(df["zipcode"].tolist())
    df["lat"] = loc["latitude"].values
    df["lon"] = loc["longitude"].values    
    df = df.dropna(subset=["lat", "lon"]) # Drop ZIPs without coordinates

    import cartopy.crs as ccrs
    import cartopy.feature as cfeature

    proj = ccrs.LambertConformal()
    fig = plt.figure(figsize=(6.5, 4.5))
    ax = plt.axes(projection=proj)

    # Add basic US features
    ax.add_feature(cfeature.COASTLINE)
    ax.add_feature(cfeature.BORDERS)
    ax.add_feature(cfeature.STATES, linewidth=0.5)

    # Limit extent roughly to continental US (lon_min, lon_max, lat_min, lat_max)
    ax.set_extent([-125, -66.5, 24, 50], crs=ccrs.PlateCarree())

    # Scatter ZIPs as colored dots
    for index, row in df.iterrows():
        ax.scatter(row["lon"], row["lat"],color=row["color"],s= row["size"],  
                   transform=ccrs.PlateCarree(),  # because lat/lon are in PlateCarree
                   edgecolor="black",linewidth=0.5,zorder=5,)
    plt.title("Selected US ZIP Codes")
    plt.tight_layout()
    plt.show()
    return()


#--
def plot_time_series(df, threshold):

    # import pandas as pd 
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
            colors.append([1,0,0])
            print(hours[k], clicks[k])
        else:
            colors.append([0,0,0.98])
 
    for i in range(1,len(hours)):
         plt.plot(hours[i-1:i+1], clicks[i-1:i+1], color='gray', linestyle='-', linewidth=0.1)
         plt.plot(hours[i], clicks[i], marker='o', color=colors[i], markersize=0.4, linewidth = 0.1)

    ax = plt.gca()
    plt.ylabel('Hourly Clicks')
    plt.gcf().autofmt_xdate() # Automatically format date labels
    date_format = mdates.DateFormatter("%Y-%m")
    plt.gca().xaxis.set_major_formatter(date_format)
    current_ticks = plt.xticks()[0]
    new_ticks = current_ticks[::2]
    plt.xticks(new_ticks) 
    plt.xticks(rotation=0, fontsize=8)
    plt.yticks(fontsize=8)
    plt.grid(True, linewidth=0.2)
    plt.axhline(y=0, color='gray', linewidth=0.2)
    trans = mtrans.Affine2D().translate(30, 0)
    for t in ax.get_xticklabels():
        t.set_transform(t.get_transform() + trans)
    plt.show()
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

#--

year = 2022  # options: 2019 or 2022
n_IPs_thresh = { 2019:10, 2022: 1}      # IPs per device
ratio_thresh = { 2019:0.1, 2022:0.01 }  # prop. of flagged clicks per zip
spike_thresh = { 2019:60, 2022:180}     # hourly clicks
zip_thresh   = { 2019:400, 2022:900}    # clicks per zipcode
zip_list     = ('02143', '07175', '07921', '08054', '10081', '10116', '15295', '20149',
                '22226', '31139', '33231', '64468', '80259', '85001', '90001', '90189', 
                '97501', '98004', '98073', '98164', '77494')

(df, df_dev) = collect_data(year)

IP_flag1, IP_clicks = map_IP_to_dev(df_dev, n_IPs_thresh[year])
map_zipcodes(df, IP_flag1, IP_clicks, ratio_thresh[year], zip_thresh[year], zip_list)
plot_time_series(df, spike_thresh[year])