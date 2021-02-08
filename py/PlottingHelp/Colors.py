#-------------------------------------------------------------------------------

""" Functions and classes to help with colors in plotting.
"""

#-------------------------------------------------------------------------------

from matplotlib import cm

#-------------------------------------------------------------------------------

class ColorMap:
  """ A colormap class using a matplotlib color map to draw colors for a given 
      number of points.
  """
  def __init__(self,cm_name,n_colors):
    self.colormap = cm.get_cmap(cm_name)
    self.n_colors = n_colors
    
  def __getitem__(self,index):
    """ Define what happens when the [] operator is applied (only reading).
    """
    return self.colormap(float(index)/float(self.n_colors))
    
#-------------------------------------------------------------------------------