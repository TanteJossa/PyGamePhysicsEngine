import matplotlib as plt
import os

#select the object that is going to display its settings in the menu
def set_selected_obj(obj):
    selected_obj = obj
    return selected_obj


#OTHER
#make a graph with a x and y arrays
def plot_data(name, objectName, dataX, dataY, xlabelname, ylabelname):
    plt.figure()
    plt.plot(dataX, dataY)
    plt.ylabel(ylabelname)
    plt.xlabel(xlabelname)
    plt.xlim(left=0)
    plt.grid(which='both')
    plt.savefig(str(name) +  '-' + str(objectName) + '.png')
    os.startfile(str(name) + '-' + str(objectName) + '.png')

def clamp(n, smallest, largest): 
    return max(smallest, min(n, largest))
