import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")

from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap, cm, interp

import cmocean
import warnings; warnings.filterwarnings('ignore')


def plot_frames(input_data, x, y):    
    
    #******************************************************************************
    # Read land mask
    #******************************************************************************
    data_land_mask = './data/lsmask.oisst.v2.nc'
    ncLAND = Dataset(data_land_mask, mode='r')
    sst_land = np.asarray(ncLAND.variables['lsmask'][:].squeeze())

    # read lats and lons (representing centers of grid boxes).
    lats_global = ncLAND.variables['lat'][:]
    lons_global = ncLAND.variables['lon'][:]

    ncLAND.close()

    lons_global, lats_global = np.meshgrid(lons_global,lats_global)    
    
    m, n = 720, 1440
    
    
    # set up the figure
    fig, ax = plt.subplots(x,y, figsize=(20, 8))
    
    # plot frames: each image is 28x28 pixels
    index = 0
    for i in range(x):
        for j in range(y):
            
            # Display the the first snapshot
            frame = np.zeros((m*n)).reshape(-1)
            frame[np.where(sst_land.flatten()==1)]  = input_data[:, index]
            mm = np.max(np.abs(frame))
            basemap_img = Basemap(projection='mill',lon_0=180) 
            im = basemap_img.pcolormesh(lons_global, lats_global, frame.reshape(m,n), 
                                   vmin=-mm, vmax=mm, cmap=cmocean.cm.balance, latlon=True, ax=ax[i,j])
            basemap_img.drawcoastlines(ax=ax[i,j])
            basemap_img.colorbar(im, "bottom", size="5%", pad="2%", ax=ax[i,j])
            index += 1
    plt.show()            
            



def plot_components(B, x, y):
    # set up the figure
    fig, ax = plt.subplots(x,y)
    
    # plot the digits: each image is 28x28 pixels
    mm = np.max(np.abs(B))
    index = 0
    for i in range(x):
        for j in range(y):
            ax[i,j].imshow(B.T[index,:].reshape(28,28), cmap=plt.cm.gray, vmin=-mm, vmax=mm)
            ax[i,j].set_xticks([])
            ax[i,j].set_yticks([])
            index +=1
    plt.show()
    
    
def plot_digits(features, target, x, y):    
    # set up the figure
    fig, ax = plt.subplots(x,y)
    
    # plot the digits: each image is 28x28 pixels
    index = 0
    for i in range(x):
        for j in range(y):
            ax[i,j].imshow(features[index,:].reshape(28,28), cmap=plt.cm.binary)
            ax[i,j].set_xticks([])
            ax[i,j].set_yticks([])
    
            # label the image with the target value
            ax[i,j].text(0, 7, str(int(target[index])))
            index +=1
    plt.show()    
    
    
    

def plot_digits_kdeplot(Z, target, first_digit, second_digit, first_name, second_name): 

    # Set up the figure
    f, ax = plt.subplots(figsize=(9, 9))
    ax.set_aspect("equal")
    
    # Draw the two density plots
    ax = sns.kdeplot(Z[:,0][target==first_digit], Z[:,1][target==first_digit],
                     cmap="Reds", shade=True, shade_lowest=False, label=first_name)
    
    ax = sns.kdeplot(Z[:,0][target==second_digit], Z[:,1][target==second_digit],
                     cmap="Blues", shade=True, shade_lowest=False, label=second_name)
    
    
    # Add labels to the plot
    red = sns.color_palette("Reds")[-2]
    blue = sns.color_palette("Blues")[-2]
    #ax.text(-1000, -600, first_name, size=16, color=red)
    #ax.text(700, -100, second_name, size=16, color=blue)
    plt.legend(fontsize=16)
    plt.xlabel('First principal component')
    plt.ylabel('Second principal component')    
    
    
def noisy(noise_typ, image, amount = 0.05):
   
    if noise_typ == "s&p":
        row,col = image.shape
        mins = np.min(image)
        maxs = np.max(image)
        s_vs_p = 0.5
        amount = amount
        out = np.copy(image)
        # Salt mode
        num_salt = np.ceil(amount * image.size * s_vs_p)
        coords = [np.random.randint(0, i - 1, int(num_salt)) for i in image.shape]
        out[coords] = mins
    
        # Pepper mode
        num_pepper = np.ceil(amount* image.size * (1. - s_vs_p))
        coords = [np.random.randint(0, i - 1, int(num_pepper)) for i in image.shape]
        out[coords] = maxs
        return out
          
    
    elif noise_typ =="speckle":
        row,col = image.shape
        gauss = np.random.randn(row,col)
        gauss = gauss.reshape(row,col)        
        noisy = image + np.maximum(0, image * gauss)
        return noisy    