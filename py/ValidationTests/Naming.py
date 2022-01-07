""" Naming maps and conventions for nicer labeling.
"""

#-------------------------------------------------------------------------------

def eM_chirality(chirality_int):
  """ Transform the e^- chirality integer to the corresponding string.
  """
  if chirality_int == -1:
    return r"e_{L}^{-}"
  elif chirality_int == +1:
    return r"e_{R}^{-}"
  else:
    raise ValueError("Unknown e- chirality {}".format(chirality_int))

def eP_chirality(chirality_int):
  """ Transform the e^+ chirality integer to the corresponding string.
  """
  if chirality_int == -1:
    return r"e_{L}^{+}"
  elif chirality_int == +1:
    return r"e_{R}^{+}"
  else:
    raise ValueError("Unknown e+ chirality {}".format(chirality_int))

#-------------------------------------------------------------------------------

def determine_finalstate(name):
  """ Determine the final state from a metadata process name.
  """
  fs = None
  if "WW" in name:
    if "muminus" in name:
      fs = "\\mu^-\\nu qq$"
    elif "muplus" in name:
      fs = "\\mu^+\\nu qq$"
  elif "2f_mu" in name:
    mass_str = None
    if "81to101" in name:
      mass_str = "$Z$-return"
    elif "180to275" in name:
      mass_str = "high-$\\sqrt{{s*}}$"
    
    dir_str = None
    if "BZ" in name:
      dir_str = "p_z^{{\\mu\\mu}}<0"
    elif "FZ" in name:
      dir_str = "p_z^{{\\mu\\mu}}>0"
    
    if mass_str:
      fs = "\\mu^+\\mu^- "
      if dir_str:
        fs += "$({}, ${}$)".format(mass_str, dir_str)
      else:
        fs += "$({})".format(mass_str)
    
  if fs is None:
    raise Exception("Did not recognize process name ", name)
  else:
    return fs

def metadata_to_process(reader):
  """ Translate the metadata to a process string.
  """
  initial_state = "{}{}".format(eM_chirality(reader["e-Chirality"]),eP_chirality(reader["e+Chirality"]))
  final_state = determine_finalstate(reader["Name"])
  return "${}\\rightarrow{}".format(initial_state,final_state)

#-------------------------------------------------------------------------------

def name_to_coord(name):
  """ Transform the name of a coordinate to its string.
  """
  if name == "costh_f_star":
    return "\\cos\\theta_f^*"
  elif name == "costh_l_star":
    return "\\cos\\theta_l^*"
  elif name == "costh_Wminus_star":
    return "\\cos\\theta_{{W^-}}^*"
  elif name == "phi_l_star":
    return "\\phi_l^*"
    return
  else:
    raise Exception("Unknown coordinate ", name)

#-------------------------------------------------------------------------------


