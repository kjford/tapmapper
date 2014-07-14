'''
time stats
compute mean and standard deviation for time measurements in 24 hour format
'''

import numpy as np

def timestats(inarray):
    # compute the mean of time measurements as the average angle
    # convert 24 to [-pi pi]
    tarray=np.array(inarray)
    tarray=(tarray-12.0)*np.pi/12.0
    # get cosine and sine
    c=np.cos(tarray)
    s=np.sin(tarray)
    zvec=np.zeros(len(c),dtype=np.complex_)
    for i in xrange(len(c)):
        zvec[i]=np.complex(c[i],s[i])
    # mean
    meanz=np.mean(zvec)
    meanangle=np.angle(meanz)
    meantime=12.0+meanangle*12.0/np.pi
    # std
    stdangle=np.sqrt(-2.0*np.log(np.absolute(meanz)))
    stdtime=stdangle*12.0/np.pi
    return (meantime,stdtime)
    
        