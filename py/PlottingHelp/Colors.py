#-------------------------------------------------------------------------------

""" Functions and classes to help with colors in plotting.
"""

#-------------------------------------------------------------------------------

from matplotlib import cm


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
    return self.colormap(float(index)/float(self.n_colors-1))
    
#-------------------------------------------------------------------------------

class ColorSpectrum:
  """ A colormap class using a matplotlib color map to draw colors for a range 
      of values between given minimum and maximum.
  """
  def __init__(self,cm_name,v_min,v_max):
    self.colormap = cm.get_cmap(cm_name)
    self.v_min = v_min
    self.v_max = v_max
    
  def __getitem__(self,index):
    """ Define what happens when the [] operator is applied (only reading).
    """
    if (index < self.v_min) or (index > self.v_max):
      raise ValueError("Requested color for index {} out of range [{},{}].".format(index,self.v_min,self.v_max))
    return self.colormap(float(index)/float(self.v_max - self.v_min))
    
#-------------------------------------------------------------------------------