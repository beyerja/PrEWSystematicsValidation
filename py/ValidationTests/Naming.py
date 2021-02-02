""" Naming maps and conventions for nicer labeling.
"""

#-------------------------------------------------------------------------------

def eM_chirality(chirality_int):
  """ Transform the e^- chirality integer to the corresponding string.
  """
  if chirality_int == -1:
    return r"$e_{L}^{-}$"
  elif chirality_int == +1:
    return r"$e_{R}^{-}$"
  else:
    raise ValueError("Unknown e- chirality {}".format(chirality_int))

def eP_chirality(chirality_int):
  """ Transform the e^+ chirality integer to the corresponding string.
  """
  if chirality_int == -1:
    return r"$e_{L}^{+}$"
  elif chirality_int == +1:
    return r"$e_{R}^{+}$"
  else:
    raise ValueError("Unknown e+ chirality {}".format(chirality_int))

#-------------------------------------------------------------------------------