import os
import pandas as pd

def load_single_file(filepath, names, skiprows=1):
    return pd.read_csv(filepath, names=names, skiprows=skiprows)

def load_bulk(folderpath, names, amount=1, skiprows=1):
    filelist = os.listdir(folderpath)
    filelist = filelist[0:amount]
    data = pd.concat([pd.read_csv(os.path.join(folderpath, item), names=names, skiprows=skiprows) for item in filelist])

    return data