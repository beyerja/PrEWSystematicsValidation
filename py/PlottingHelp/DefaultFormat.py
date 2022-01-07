import matplotlib

def set_default_mpl_format():
  matplotlib.style.use('tableau-colorblind10') 
  matplotlib.rcParams.update({'font.size': 22})
  matplotlib.rc('image', cmap='cividis')
