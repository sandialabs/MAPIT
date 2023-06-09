from scipy.io import loadmat
import numpy as np

datpath = '/Users/nshoman/Documents/MAPIT/data/fuel_fab/Normal/data.mat'

x = loadmat(datpath)

inputs = np.squeeze(x['in']['data'])
inputsT = np.squeeze(x['in']['time'])

inventories = np.squeeze(x['invn']['data'])
inventoriesT = np.squeeze(x['invn']['time'])

out = np.squeeze(x['outn']['data'])
outT = np.squeeze(x['outn']['time'])


for i in range(len(inputs)):
    outdir = '/Users/nshoman/Documents/MAPIT/debug_data/csv/input/'+'in'+str(i)+'.csv'
    xout = np.concatenate((inputsT[i],inputs[i]),axis=1)
    np.savetxt(outdir,xout,delimiter=',')


for i in range(len(inventories)):
    outdir = '/Users/nshoman/Documents/MAPIT/debug_data/csv/inventory/'+'invn'+str(i)+'.csv'
    xout = np.concatenate((inventoriesT[i],inventories[i]),axis=1)
    np.savetxt(outdir,xout,delimiter=',')


for i in range(len(out)):
    outdir = '/Users/nshoman/Documents/MAPIT/debug_data/csv/output/'+'out'+str(i)+'.csv'
    xout = np.concatenate((outT[i],out[i]),axis=1)
    np.savetxt(outdir,xout,delimiter=',')