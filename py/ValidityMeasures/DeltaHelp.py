#-------------------------------------------------------------------------------

""" Helper functions related to the delta=(delta-c,delta-w) that describes the
    deviation points.
"""

#-------------------------------------------------------------------------------

import numpy as np

#-------------------------------------------------------------------------------

def delta_metric(deltas):
  """ Get the combined delta "metrix" (~combined length of deviation).
      Defined as sqrt(delta-c^2 + delta-w^2).
  """
  if deltas.ndim == 1:
    deltas = np.array([deltas]) # Allow giving a single c,w pair
  return np.sqrt(np.sum(deltas**2,axis=1))

#-------------------------------------------------------------------------------