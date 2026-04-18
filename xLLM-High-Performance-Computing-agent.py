import random
import numpy as np
import gmpy2
import matplotlib.pyplot as plt
import matplotlib as mpl

mpl.rcParams['axes.linewidth'] = 0.5
plt.rcParams['xtick.labelsize'] = 8
plt.rcParams['ytick.labelsize'] = 8
plt.rcParams['legend.fontsize'] = 'x-small'

def extract_roots(N, xbin, a, b):

    arr_re = []
    arr_im = []
    delta = 0
    prop = xbin.count('1')/N
    arr_coeffs = []
    for k in range(N): 
        digit = int(xbin[k])
        arr_coeffs.append(a*digit+b)  
    # coefficients in that order: 1 + 3x + 5x^2 --> [1, 3, 5] 
    roots = np.polynomial.polynomial.polyroots(arr_coeffs)

    checksum = 1
    for r in roots:
        re = r.real
        im = r.imag
        norm = (re**2 + im**2)**0.5
        arr_re.append(re)    
        arr_im.append(im)    
        delta += abs(norm-1)
        checksum *= norm
    if len(roots) == 0:
        delta = 0
    else:
        delta /= len(roots)
    return(arr_re, arr_im, delta, checksum)


def generate_bit_string(N, prop):

    num_ones = int(0.5 + (N-2) * prop) 
    num_zeros =  (N-2) - num_ones
    bits = ['1'] * num_ones + ['0'] * num_zeros
    random.shuffle(bits)
    xbin = "".join(bits)
    xbin = '1' + xbin + '1'
    return(xbin)


def f_bin(k, N, options):

    constant = options[0]
    formula = options[1]

    if constant == 0:
        cst = gmpy2.const_pi()
    elif constant == 1:  
        cst = gmpy2.exp(1)
    elif constant == 2:
        cst = gmpy2.log(2)
    elif constant == 3:
        cst = gmpy2.mpfr(4)/gmpy2.mpfr(7)

    if formula == 0:
        eta = cst + k 
    elif formula == 1:
        eta = cst + k*k
    elif formula == 2:
        eta = cst + gmpy2.mpfr(1)/k 
    elif formula == 3:
        eta = cst * k

    x = gmpy2.mpz(2**(2*ndigits) * eta)
    xbin = bin(x)[2:N+2]
    return(xbin)


#--- Core function

def set_of_polynomials(K, N, a, b, mode, f_options):

    arr_delta = []
    arr_prop = []
    arr_col = []

    for k in np.arange(1, K):
    
        p = k/K
        color = [p, 4*p*(1-p), 0.25+0.75*(1-p)]
        if mode == 'random':
            xbin = generate_bit_string(N, p)
        elif mode == 'deterministic':
            xbin = f_bin(k, N, f_options)
        elif mode == 'full':
            string = bin(k)[2:]
            xbin = string + "0" * (N - len(string))

        p1 = xbin.count('1')/N  # should be close to prop
        arr_re, arr_im, delta, checksum = extract_roots(N, xbin, a, b)

        # checksum (product of all roots) must be equal to 1
        if k % 100 == 0:
            string = xbin
            if len(string) > 60:
                string = string[:60] + "..."
            print("%5.3f %5d %5.3f %9.7f %s" % (p, k, p1, checksum, string))
        arr_prop.append(p1)
        arr_delta.append(np.sqrt(N)*np.log(N)*delta)
        arr_col.append(color)
        ax.scatter(arr_re, arr_im, s=0.6, color=color, edgecolors='none') 

    return(arr_prop, arr_delta, arr_col)


#--- Main

width_px, height_px = 800, 800
dpi = 100
width_in = width_px / dpi
height_in = height_px / dpi
random.seed(42)

show_axes = False   
show_spectrum = False 
save_spectrum = True
show_roots = False 
save_roots = True
saved_frames = [] 

"""
param entry: [N, K, a, b, mode, frame_ID, f_options]

     • N: number of digits (polynomial degree < N)
     • K: number of polynomials used in a set or video frame
     • a, b: binary digit replaced by a*digit+b 
     • mode: 'deterministic' or 'random'
     • frame_ID: index number attached to video frame
     • f_options: parameters (u, v) used in function f_bin:
         • u: 0 for Pi, 1 for exp(1), 2 for log(2), 3 for 4/7
         • v: 0 for u+k, 1 for u+k*k, 2 for u+(1/k), 3 for u*k,   
"""

params = []
frame_ID = 0
mode = 'deterministic'
K = 2000
a = 4

for b in range(-7, 2, 1):  
    for u in range(0, 4):   
        for v in range(0, 3):  
            for N in range(20, 61, 5):
                f_options = (u, v)
                param = [N, K, a, b, mode, frame_ID, f_options]
                params.append(param)
                frame_ID += 1

N = 200
K = 2000
param = [N, K, 1, 0, 'random', frame_ID, (0,0)]
params.append(param)
frame_ID += 1

N = 14
K = 12000  
param = [N, K, 1, 0, 'random', frame_ID, (0,0)]
params.append(param)
frame_ID+=1

N = 14  
K = 2**N
param = [N, K, 2, -1, 'full', frame_ID, (0,0)]
params.append(param)
frame_ID+=1

nframes = len(params)
print(nframes, "frames")

for param in params:

    N = param[0]
    K = param[1]
    a = param[2]
    b = param[3]
    mode = param[4]      
    frame_ID = param[5]
    f_options = param[6]

    # ndigits (precision) must be larger than N
    ndigits = 5*N // 4 
    ctx = gmpy2.get_context()  
    ctx.precision = ndigits 

    if frame_ID in (0, 165, nframes-3, nframes-2, nframes-1): 

        print("\n----------------\nFrame:", frame_ID, "/", nframes)
        print("\ndegree: N = %d\nnumber of ξ's: K = %d\na: %7.4f\nb: %7.4f\nmode: %s\nf_options: %s" %(N, K, a, b, mode,str(f_options))) 
        print("\n./...    k    p    checksum   digits of ξ_k") 
        if not show_axes:
            plt.style.use('dark_background')
        fig, ax = plt.subplots(figsize=(width_in, height_in))
        arr_prop, arr_delta, arr_col = set_of_polynomials(K, N, a, b, mode, f_options)
        ax.text(0.95, 0.95, 'BongingAI.io', transform=ax.transAxes, ha='right', va='top', fontsize=12, color='white')
        ax.text(0.95, 0.92, 'frame ' + str(frame_ID), transform=ax.transAxes, ha='right', va='top', fontsize=12, color='white')

        plt.xlim(-1.5, 1.5)
        plt.ylim(-1.5, 1.5)
        if not show_axes:
            plt.axis('off') 
            plt.margins(0) 
            plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0) 
        else:
            ax.set_facecolor('black') 
        if save_roots:
            filename = 'nroots' + str(frame_ID) + '.png'
            plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=dpi)
            saved_frames.append(filename) 
        if show_roots:
            plt.show()
        else:
            plt.close()

        plt.rcParams['axes.facecolor'] = 'black' 
        plt.scatter(arr_prop, arr_delta, s=0.8, c = arr_col, edgecolors = 'none')
        if save_spectrum:
            filename = 'nroots_spectrum' + str(frame_ID) + '.png' 
            plt.savefig(filename, bbox_inches='tight', pad_inches=0, dpi=dpi)
        if show_spectrum:
            plt.show()
        else:
            plt.close()


#--- Produce video: slow and fast versions

import moviepy.video.io.ImageSequenceClip 
clip = moviepy.video.io.ImageSequenceClip.ImageSequenceClip(saved_frames, fps=4)  
clip.write_videofile('nroots_v1.mp4')

