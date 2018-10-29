import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
sns.set(style="white")

from netCDF4 import Dataset
from mpl_toolkits.basemap import Basemap, cm, interp

import cmocean
import warnings; warnings.filterwarnings('ignore')


import argparse
import scipy.io as sio

# Code adapted from Ryan Cooper (https://github.com/Coopss/EMNIST)
def load_emnist(mat_file_path, width=28, height=28, max_=None, verbose=False):
    ''' Load data in from .mat file as specified by the paper.
        Arguments:
            mat_file_path: path to the .mat, should be in sample/
        Optional Arguments:
            width: specified width
            height: specified height
            max_: the max number of samples to load
            verbose: enable verbose printing
        Returns:
            A tuple of training and test data, and the mapping for class code to ascii value,
            in the following format:
                - ((training_images, training_labels), (testing_images, testing_labels), mapping)
    '''
    # Local functions
    def rotate(img):
        # Used to rotate images (for some reason they are transposed on read-in)
        flipped = np.fliplr(img)
        return np.rot90(flipped)

    def display(img, threshold=0.5):
        # Debugging only
        render = ''
        for row in img:
            for col in row:
                if col > threshold:
                    render += '@'
                else:
                    render += '.'
            render += '\n'
        return render

    # Load convoluted list structure form loadmat
    mat = sio.loadmat(mat_file_path)

    # Load char mapping
    mapping = {kv[0]:kv[1:][0] for kv in mat['dataset'][0][0][2]}
    #pickle.dump(mapping, open('mapping.p', 'wb' ))

    # Load training data
    if max_ == None:
        max_ = len(mat['dataset'][0][0][0][0][0][0])
    training_images = mat['dataset'][0][0][0][0][0][0][:max_].reshape(max_, height, width, 1)
    training_labels = mat['dataset'][0][0][0][0][0][1][:max_].flatten()

    # Load testing data
    if max_ == None:
        max_ = len(mat['dataset'][0][0][1][0][0][0])
    else:
        max_ = int(max_ / 6)
    testing_images = mat['dataset'][0][0][1][0][0][0][:max_].reshape(max_, height, width, 1)
    testing_labels = mat['dataset'][0][0][1][0][0][1][:max_].flatten()

    # Reshape training data to be valid
    if verbose == True: _len = len(training_images)
    for i in range(len(training_images)):
        if verbose == True: print('%d/%d (%.2lf%%)' % (i + 1, _len, ((i + 1)/_len) * 100), end='\r')
        training_images[i] = rotate(training_images[i])
    if verbose == True: print('')

    # Reshape testing data to be valid
    if verbose == True: _len = len(testing_images)
    for i in range(len(testing_images)):
        if verbose == True: print('%d/%d (%.2lf%%)' % (i + 1, _len, ((i + 1)/_len) * 100), end='\r')
        testing_images[i] = rotate(testing_images[i])
    if verbose == True: print('')

    # Convert type to float32
    training_images = training_images.astype('float32')
    testing_images = testing_images.astype('float32')

    # Normalize to prevent issues with model
    training_images /= 255
    testing_images /= 255
    
    training_images = training_images.reshape(112800,28*28)
    testing_images = testing_images.reshape(18800,28*28)
    
    training_labels_char = []
    for i in training_labels: 
        training_labels_char.append(mapping[i].tostring().decode("utf-8"))
    testing_labels_char = []
    for i in testing_labels: 
        testing_labels_char.append(mapping[i].tostring().decode("utf-8"))   
    
    return (training_images, training_labels, testing_images, testing_labels, training_labels_char, testing_labels_char)


def plot_frames(input_data, x, y):    
    
    #******************************************************************************
    # Read land mask
    #******************************************************************************
    data_land_mask = '/mnt/data/lsmask.oisst.v2.nc'
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
    fig, ax = plt.subplots(x,y, figsize=(20, 10))
    
    # plot the digits: each image is 28x28 pixels
    mm = np.max(np.abs(B))
    index = 0
    for i in range(x):
        for j in range(y):
            ax[i,j].imshow(B.T[index,:].reshape(28,28), cmap=cmocean.cm.delta, vmin=-mm, vmax=mm)
            ax[i,j].set_xticks([])
            ax[i,j].set_yticks([])
            index +=1
    plt.show()
    
    
def plot_digits(features, target, x, y):    
    # set up the figure
    fig, ax = plt.subplots(x,y, figsize=(20, 10))
    
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
    
 

def plot_emnist(features, target, x, y):    
    # set up the figure
    fig, ax = plt.subplots(x,y, figsize=(20, 10))
    
    # plot the digits: each image is 28x28 pixels
    index = 0
    for i in range(x):
        for j in range(y):
            ax[i,j].imshow(features[index,:].reshape(28,28), cmap=plt.cm.binary)
            ax[i,j].set_xticks([])
            ax[i,j].set_yticks([])
    
            # label the image with the target value
            ax[i,j].text(0, 7, str(target[index]))
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
