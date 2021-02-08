#-------------------------------------------------------------------------------

""" Helper functions for the pandas dataframe that describes the histograms
    at different deviation points.
"""

#-------------------------------------------------------------------------------

import numpy as np

#-------------------------------------------------------------------------------

def delta_pairs(df):
  """ Return the [delta-c, delta-w] pairs of each row.
  """
  return np.transpose(np.array([df["Delta-c"].values,df["Delta-w"].values]))

#-------------------------------------------------------------------------------
