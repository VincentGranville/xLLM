import wfdb
import numpy as np
import matplotlib.pyplot as plt
import matplotlib as mpl
import matplotlib.colors as mcolors

mpl.rcParams['axes.linewidth'] = 0.5
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 'x-small' 

# First, put the following files in your local directory to do little test:
#
#  p04000_s00.hea
#  p04000_s00.atr
#  p04000_s00.dat
#
# Source: https://physionet.org/content/icentia11k-continuous-ecg/1.0/p04/p04000/#files-panel

record = wfdb.rdrecord('p04000_s00') 

#--- Or to read data straight from Physionet website rather than locally as above
# record_name = '100'
# physionet_database_directory = 'mitdb'
# record = wfdb.rdrecord(record_name, pn_dir=physionet_database_directory)

#--- Info about record:
#  record.p_signal: The signal data in physical units (if available).
#  record.d_signal: The signal data in digital units.
#  record.fs: The sampling frequency.
#  record.sig_name: The names of the signals.
#  record.units: The units of the signals.

#--- Other stuff you can do
# wfdb.plot_wfdb(record, title='Record p04000_s00 from Physionet Apnea ECG') 
# for item in record.__dict__:
#     print(item)

signal = record.p_signal[:,0]
x_time = range(len(signal))  
print("Signal lenth:", len(x_time))
print("Frequency:", record.fs)  # value is 250/second

start = 10000
end = 990000 

#--- Compute quantiles

arr_q = []
xval = []
incr = 0.001
for p in np.arange(0, 1, incr):
    q = np.quantile(signal[start:end], p)
    arr_q.append(q)
    xval.append(p)
plt.plot(xval, arr_q, linewidth=0.6)  


#--- Thresholds detection

def dist_to_line(P, A, B):
    # distance between point P and line containing points A, B
    num = (P[0]-A[0])*(B[1]-A[1]) - (P[1]-A[1])*(B[0]-A[0])
    denum = np.sqrt((B[0]-A[0])**2 + (B[1]-A[1])**2)
    return(num/denum)

arr_thresh = np.zeros(len(arr_q))
offset = 2
for k in range(offset, len(arr_q)-offset):
    P = [xval[k], arr_q[k]]
    A = [xval[k-offset], arr_q[k-offset]] 
    B = [xval[k+offset], arr_q[k+offset]]
    arr_thresh[k] = dist_to_line(P, A, B)

pary = 4
for k in range(len(arr_thresh)): 
    thresh = arr_thresh[k]
    k1_min = max(0, k-pary)
    k1_max = min(len(arr_thresh)-1, k+pary)
    tmax = np.max(arr_thresh[k1_min:k1_max])
    k2_min = max(0, k-offset)
    k2_max = min(len(arr_thresh)-1, k+offset)
    dy = arr_q[k2_max] - arr_q[k2_min]
    if thresh == tmax and thresh > 0.0005 and dy > 0.04:
        plt.axhline(y=arr_q[k], color='r', linewidth = 0.3,  dashes=[10, 10]) 
plt.axhline(y=0, color='g', linewidth = 0.3, dashes=[10, 10]) 
plt.show()


#---- Compressing the signal

def update_hash(hash, key, count):
    if key in hash:
        hash[key] += count
    else:
        hash[key] = 1
    return(hash)

arr_delta = signal[start:end] - signal[start-1:end-1]

hash_delta = {}
t = 0
block_size = 8 
while t + block_size < len(arr_delta):
    vector = ()
    for idx in range(block_size):
        vector = (*vector, arr_delta[t+idx])
    update_hash(hash_delta, vector, 1)
    t += block_size

hash_delta = dict(sorted(hash_delta.items(), key=lambda item: item[1], reverse=True))
print("Number of unique blocks:", len(hash_delta))

 
#--- Detect heart beats (called "events")

def get_events(threshold, low):

    events = []
    t = start
    old_t_start = -1
    while t < end:
        if signal[t] > threshold:
            t_start = t
            width = 1
            max = - 1 
            min = 9999.99
            lows = 0
            while t < end and signal[t] > threshold:
                if signal[t] > max:
                    max = signal[t]
                width += 1
                t += 1
            while t < end and signal[t] <= threshold:
                if signal[t] < min:
                    min = signal[t]
                if signal[t] < low:
                    lows += 1
                t += 1
            duration = t - t_start
            plows = lows/duration
            events.append([t_start, width, max, duration, min, lows])
            old_t_start = t_start
        else:
            t += 1
    events = np.array(events)
    return(events)

threshold1 = 0.25 ### 0.50
threshold2 = -0.05
events = get_events(threshold1, threshold2)

#--- Events clustering

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler

X = events[:, -5:]
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Generate 20 distinct colors (RGB tuples, values 0-1)
cmap = plt.get_cmap('tab20')
colors_rgb = [cmap(i) for i in range(20)]
events_color = []

ngroups = 8
if ngroups > 20:
    print("Not enough colors to show the categories")
    exit()
kmeans = KMeans(n_clusters=ngroups, random_state=0, n_init=10) 
kmeans.fit(X_scaled)
labels = kmeans.labels_ ### predict(X)
centroids = kmeans.cluster_centers_

for k in range(len(labels)):
    label = labels[k]
    color = colors_rgb[label]
    events_color.append(color)
    print("%5d %3d %4d %5.3f %3d %5.3f %2d" % 
           (k, label, events[k,1], events[k,2], events[k,3], events[k,4],events[k,5]))

plt.scatter(events[:,0], events[:, 3], s=2.6, c=events_color) 
plt.show()



